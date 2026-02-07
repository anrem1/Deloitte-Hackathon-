"""  
Menu Engineering Agent using LangGraph and MCP Toolbox
This agent connects to the MCP toolbox server and uses LangGraph for orchestration.
Using Google Gemini for LLM with manual tool selection.
"""
import os
import json
import re
from typing import TypedDict

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, END

from backend.apis import build_router

load_dotenv()

# Environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TOOLBOX_URL = os.getenv("TOOLBOX_URL", "http://127.0.0.1:5000")
TOOLBOX_API_KEY = os.getenv("TOOLBOX_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

# Initialize LLM with Gemini
llm = ChatGoogleGenerativeAI(
    model=GEMINI_MODEL,
    google_api_key=GEMINI_API_KEY,
    temperature=0.7,
)


class MCPToolboxClient:
    """Client for interacting with MCP Toolbox server."""
    
    def __init__(self, base_url: str, api_key: str = None):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.client = httpx.Client(timeout=30.0)
        
    def get_tools(self) -> dict:
        """Fetch available tools from toolbox."""
        url = f"{self.base_url}/api/toolset"
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
            
        response = self.client.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data.get("tools", {})
    
    def invoke_tool(self, tool_name: str, params: dict = None) -> dict:
        """Invoke a specific tool with parameters."""
        url = f"{self.base_url}/api/tool/{tool_name}/invoke"
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        payload = params or {}
        response = self.client.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    
    def close(self):
        """Close the HTTP client."""
        self.client.close()


# Initialize MCP Toolbox client
toolbox_client = MCPToolboxClient(TOOLBOX_URL, TOOLBOX_API_KEY)


def format_table(cols, rows) -> str:
    """Format data as a table string."""
    if not rows:
        return "No data returned."
    
    lines = []
    lines.append(" | ".join(str(c) for c in cols))
    lines.append("-" * 80)
    for row in rows[:20]:  # Limit to 20 rows
        lines.append(" | ".join(str(v) for v in row))
    return "\n".join(lines)


def get_tools_description() -> str:
    """Get a formatted description of available tools."""
    tools = toolbox_client.get_tools()
    descriptions = []
    for tool_name, tool_info in tools.items():
        desc = tool_info.get("description", "No description")
        params = tool_info.get("parameters", [])
        param_desc = ""
        if params:
            param_names = [p.get("name", "") for p in params]
            param_desc = f" (params: {', '.join(param_names)})"
        descriptions.append(f"- {tool_name}: {desc}{param_desc}")
    return "\n".join(descriptions)


def list_tools() -> dict:
    """Return raw tools metadata from the toolbox server."""
    return toolbox_client.get_tools()


# Define the agent state
class AgentState(TypedDict):
    question: str
    tool_selected: str
    tool_params: dict
    tool_result: str
    final_answer: str
    step: str


def select_tool(state: AgentState):
    question = state["question"]
    tools_desc = get_tools_description()
    
    prompt = f"""...""" # your prompt

    # Invoke returns an AIMessage object
    ai_msg = llm.invoke([HumanMessage(content=prompt)])
    response_text = ai_msg.content  # <--- Extract the text here
    
    try:
        # Regex to find JSON inside potential markdown code blocks
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            selection = json.loads(json_match.group())
        else:
            selection = json.loads(response_text)
        
        tool_name = selection.get("tool", "top_revenue_items")
        params = selection.get("params", {})
    except Exception as e:
        print(f"JSON Parsing Error: {e}")
        tool_name = "top_revenue_items"
        params = {}
    
    return {
        "tool_selected": tool_name,
        "tool_params": params,
        "step": "execute_tool"
    }


def execute_tool(state: AgentState):
    """Execute the selected tool."""
    tool_name = state["tool_selected"]
    params = state["tool_params"]
    
    try:
        result = toolbox_client.invoke_tool(tool_name, params)
        
        # Format the result
        data = result.get("data") or result.get("result") or result
        
        if isinstance(data, dict) and "columns" in data and "rows" in data:
            cols = data["columns"]
            rows = data["rows"]
            formatted = format_table(cols, rows)
        elif isinstance(data, list) and data and isinstance(data[0], dict):
            cols = list(data[0].keys())
            rows = [[row.get(c) for c in cols] for row in data[:20]]
            formatted = format_table(cols, rows)
        else:
            formatted = str(data)
    except Exception as e:
        formatted = f"Error: {str(e)}"
    
    return {
        "tool_result": formatted,
        "step": "generate_answer"
    }


def generate_answer(state: AgentState):
    """Generate the final answer based on tool results."""
    question = state["question"]
    tool_result = state["tool_result"]
    
    prompt = f"""You are a Menu Engineering data analyst. Analyze the data and provide clear insights.

User question: {question}

Data retrieved:
{tool_result}

Provide a clear, concise answer (3-5 sentences) that:
1. Directly answers the question
2. Highlights key insights from the data
3. Provides one actionable recommendation

Answer:"""

    response = llm.invoke(prompt)
    response_text = response.content if hasattr(response, "content") else str(response)
    
    return {
        "final_answer": response_text,
        "step": "end"
    }


def route_step(state: AgentState) -> str:
    """Route to the next step."""
    step = state.get("step", "select_tool")
    if step == "end":
        return END
    return step


def create_agent_graph():
    """Create the LangGraph workflow."""
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("select_tool", select_tool)
    workflow.add_node("execute_tool", execute_tool)
    workflow.add_node("generate_answer", generate_answer)
    
    # Set entry point
    workflow.set_entry_point("select_tool")
    
    # Add edges
    workflow.add_conditional_edges(
        "select_tool",
        route_step,
        {
            "execute_tool": "execute_tool",
            END: END
        }
    )
    
    workflow.add_conditional_edges(
        "execute_tool",
        route_step,
        {
            "generate_answer": "generate_answer",
            END: END
        }
    )
    
    workflow.add_conditional_edges(
        "generate_answer",
        route_step,
        {
            END: END
        }
    )
    
    return workflow.compile()


def answer_question(question: str) -> str:
    """Process a question using the LangGraph agent."""
    app = create_agent_graph()
    
    # Create initial state
    initial_state = {
        "question": question,
        "tool_selected": "",
        "tool_params": {},
        "tool_result": "",
        "final_answer": "",
        "step": "select_tool"
    }
    
    # Run the graph
    result = app.invoke(initial_state)
    
    # Return the final answer
    return result.get("final_answer", "No answer generated")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(title="Menu Engineering Agent API")
    app.include_router(build_router(answer_question, list_tools), prefix="/api")

    @app.get("/health")
    def health_check():
        return {"status": "ok"}

    @app.on_event("shutdown")
    def shutdown_event():
        toolbox_client.close()

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("backend.agent:app", host="0.0.0.0", port=port, reload=False)