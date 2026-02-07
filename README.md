# Deloitte-Hackathon-
Deloitte x AUC Hackathon
Flavor Flow Craft — Menu Engineering

This repository contains the Menu Engineering prototype built for the Deloitte x AUC Hackathon. The implementation focuses exclusively on Menu Engineering: analyzing menus and generating pricing, wording, add-on, and promotion recommendations.


Summary

- Frontend UI: React + TypeScript (Vite) — user uploads a menu file and views suggested changes.
- Mock API: `src/frontend/utils/api.ts` returns a realistic mock analysis used by the UI.
- Backend: `src/backend/main.py` (ADD)
- Database: PostgreSQL (via Xata).
- External APIs: Gemini API for AI-powered recommendations.

Features

Core Analytics
- Menu Matrix Analysis — classifies items into Stars (high revenue, high margin), Plowhorses (high revenue, low margin), Puzzles (low revenue, high margin), and Dogs (low revenue, low margin) for strategic decision-making.
- Profitability Calculations — computes gross margin, contribution margin, and revenue per item where cost data is available.
- Price Elasticity Estimation — suggests optimal price points based on historical demand patterns and competitor benchmarking.

 Recommendations
- Pricing Optimization — identifies underpriced bestsellers and overpriced underperformers with expected revenue lift.
- Wording Enhancements — AI-powered description suggestions to increase perceived value and conversion rates (via Gemini API).
- Add-on Strategy — detects high-margin add-on opportunities and suggests optimal attachment pricing.
- Promotional Bundles — recommends promotional combinations to move low-margin items and increase average order value.

User Experience
- Drag-and-drop file upload — accepts CSV, XLSX, and other menu formats.
- Interactive results dashboard — displays menu matrix, per-item recommendations, and expected financial impact.
- Export functionality — generates CSV and JSON reports for merchant integration and A/B testing.
- Demo-ready mock mode — frontend works immediately without backend for prototyping.

 Screenshots:
 <img width="1674" height="535" alt="image (1)" src="https://github.com/user-attachments/assets/05e17e16-09d9-426c-bd24-d08064491f8c" />
 <img width="1851" height="869" alt="image (2)" src="https://github.com/user-attachments/assets/e8ed73ef-0f2f-4a2d-b41f-d44119d51327" />
 <img width="1767" height="824" alt="image" src="https://github.com/user-attachments/assets/d3b89a49-736d-4a44-9d3e-5f4e8036b46f" />


 Technologies Used

- Frontend: React 18.2.0, TypeScript 5.2.2, Vite 5.0.8
- UI Framework: Lucide React (icons)
- Backend (Recommended): Python 3.x, FastAPI, uvicorn
- Data Processing:  pandas, numpy
- ML/Analytics: scikit-learn, statsmodels
- Database:  PostgreSQL (via Xata)
- External APIs: Google Gemini API (for AI-powered recommendations)
- Dev Tools: ESLint, TypeScript, npm
- Build & Runtime:  Vite (frontend), uvicorn (backend)


Installation:
pip install -r requirements.txt
Usage: 
uvicorn backend.agent:app --host 0.0.0.0 --port 8000

Architecture
High-Level Design Philosophy
The solution follows a layered analytics architecture that separates raw data ingestion, data transformation, analytics logic, and decision intelligence. This ensures scalability, explainability, and clean separation of concerns — similar to real-world consulting and data platform designs.
Raw Data (CSV)
      ↓
Staging Layer (PostgreSQL)
      ↓
Clean Fact Layer
      ↓
Analytics Views
      ↓
AI Decision Agent

Data Ingestion & Staging Layer
Components
raw_fct_order_items (PostgreSQL table)


load_raw_and_clean.py


Purpose
Safely ingest large, wide CSV files (~2M rows, 20+ columns)


Preserve raw data exactly as received


Avoid schema assumptions during ingestion


Why this matters
Real client data is often messy and inconsistent


A raw staging layer prevents data loss and enables reprocessing


Mirrors best practices in enterprise data platforms

