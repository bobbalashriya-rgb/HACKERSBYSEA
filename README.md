# Finolitics AI

Finolitics AI is a modern, AI-powered investment research assistant designed to turn raw financial data into understandable, explainable investment research. It bridges the gap between hard quantitative data and qualitative AI synthesis, operating under strict data-integrity rules to prevent hallucination.

## 🏗️ Architecture

The application uses a decoupled architecture:

*   **Frontend**: React (Vite), Tailwind CSS for styling, and Recharts for data visualization. 
*   **Backend**: Python, FastAPI, and SQLAlchemy (SQLite) for the API and configuration storage.
*   **Data Source**: `yfinance` is the exclusive provider of raw financial statements, historical pricing, and company metadata.
*   **AI Engine**: Google Gemini 1.5 Flash. It is isolated from the internet and operates strictly on the JSON context fed to it by the backend calculation engine.

## 🛡️ Data Integrity & Security Rules

1.  **No Hallucinations**: Gemini is strictly prohibited from inventing financial data. It only receives and interprets pre-calculated metrics.
2.  **Explicit Unavailable States**: If `yfinance` omits a metric (e.g., Debt to Equity for certain sectors), the system explicitly flags it as `null` in JSON and `"Data unavailable"` on the UI. The AI agent will also state that the data is unavailable.
3.  **Traceability**: Every financial number displayed in the UI is either explicitly rendered from `yfinance` raw data or derived using standard accounting math in `backend/app/services/financial_metrics.py`.
4.  **Security**: The `GEMINI_API_KEY` is completely hidden from the frontend, securely injected only into the backend process via environment variables.

## 🚀 Setup Instructions

### Prerequisites
*   Node.js (v18+)
*   Python (3.9+)

### 1. Backend Setup
Navigate to the `backend/` directory, create a virtual environment, and install the requirements:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Environment Variables**:
Create a `.env` file in the `backend/` directory:
```env
PORT=8000
ENVIRONMENT=development
DATABASE_URL=sqlite:///./finolitics.db
GEMINI_API_KEY=your_real_gemini_api_key_here
```

**Run the Backend**:
```bash
uvicorn app.main:app --reload
```
*(The API documentation will be available at http://localhost:8000/docs)*

### 2. Frontend Setup
Navigate to the `frontend/` directory and install the Node modules:
```bash
cd frontend
npm install
```

**Environment Variables**:
Create a `.env` file in the `frontend/` directory:
```env
VITE_API_BASE_URL=http://localhost:8000/api
```

**Run the Frontend**:
```bash
npm run dev
```
*(The dashboard will be available at http://localhost:5173)*

## 📡 API Endpoints

### Data & Analysis
*   `GET /api/company/{ticker}`: Retrieves the raw normalized `yfinance` company profile.
*   `POST /api/analyze`: The primary orchestrator. Takes `{ "ticker": "TCS.NS" }` and returns the company profile, explicit metric calculations, principle evaluation results, and the Gemini AI generated thesis.

### Configurable Principles
*   `GET /api/principles`: Lists all active user-configured rules.
*   `PUT /api/principles/{identifier}`: Updates the threshold of an investment principle, instantly persisting it to SQLite.

### AI & Comparisons
*   `POST /api/ask`: An interactive Q&A endpoint. It accepts the full analyzed context and a user question to interrogate the data via Gemini.
*   `POST /api/compare`: Accepts a list of two tickers, runs the entire calculation pipeline independently for both, and outputs a combined data matrix alongside a synthesized AI comparison.

## 📊 Evaluation & Testing Workflows

The application handles edge cases cleanly:
*   **Valid Tickers (e.g. TCS.NS, INFY.NS, RELIANCE.NS)**: Will display full metric cards, historical charts (in red), dynamic evaluation badges, and the explainable thesis.
*   **Invalid Tickers**: Caught immediately by a heuristic. Yields a friendly frontend alert.
*   **Missing Metrics**: Will not break the math engine. Missing source data yields a null field, causing the frontend formatter to fallback to `"Data unavailable"` and the principle engine to fallback to a neutral `"Unavailable"` state.
*   **Dynamic Rule Updates**: Clicking "Configure Criteria" allows you to change a threshold (e.g., ROE > 20%). The backend instantly saves this and regenerates the AI investment thesis context to match your stricter rules.

*   <img width="1440" height="809" alt="Screenshot 2026-10-07 at 5 26 45 PM" src="https://github.com/user-attachments/assets/ef1dc49d-cd01-4bf3-987b-55cf5637c9cc" />
<img width="1440" height="809" alt="Screenshot 2026-10-07 at 5 27 26 PM" src="https://github.com/user-attachments/assets/463f35fc-8bce-4be3-9d84-f65d1e2e83f7" />


