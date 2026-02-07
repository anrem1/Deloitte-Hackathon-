const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';

export const askAgent = async (menuText: string): Promise<string> => {
  const response = await fetch(`${BACKEND_URL}/api/ask`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ question: menuText })
  });

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || 'Analysis failed');
  }

  const data = await response.json();
  if (!data?.answer) {
    throw new Error('No answer returned');
  }

  return data.answer;
};