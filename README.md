# 🩺 Healthcare Symptom Checker

An AI-powered educational tool that analyzes symptoms and suggests possible
conditions with recommended next steps. Built with FastAPI, Groq LLM, SQLite,
and plain HTML/CSS/JS.

> ⚠️ **Disclaimer:** This tool is for **educational purposes only** and does
> not provide medical diagnoses or professional medical advice. Always consult
> a qualified healthcare professional for proper diagnosis and treatment.

---

## 📸 Demo

> 🎥 [Demo Video Link](#) — 

---

## ✨ Features

- **Symptom Analysis** — Describe symptoms in plain text and get structured AI analysis
- **Probable Conditions** — Returns 3–5 possible conditions with likelihood levels (High / Moderate / Low)
- **Recommended Steps** — Clear, actionable next steps tailored to the symptoms
- **Urgency Level** — Color-coded urgency indicator (Emergency / High / Moderate / Low)
- **Query History** — All past analyses stored in SQLite and viewable in the UI
- **Safety First** — Disclaimers enforced at three levels: prompt, API response, and UI

---

## 🛠️ Tech Stack

| Layer      | Technology                          |
|------------|-------------------------------------|
| Backend    | Python 3.11+, FastAPI, Uvicorn      |
| LLM        | Groq API (LLaMA 3.3 70B Versatile)  |
| Database   | SQLite + SQLAlchemy                 |
| Validation | Pydantic v2                         |
| Frontend   | HTML5, CSS3, Vanilla JavaScript     |

---

## 📁 Project Structure
```
healthcare-symptom-checker/
├── backend/
│   ├── main.py                  # FastAPI app, CORS, lifespan
│   ├── routes/
│   │   └── symptom.py           # API endpoints
│   ├── services/
│   │   └── llm_service.py       # Groq LLM integration & prompt engineering
│   ├── models/
│   │   └── schemas.py           # Pydantic request/response models
│   ├── database/
│   │   ├── db.py                # SQLAlchemy setup & table definitions
│   │   └── crud.py              # Database operations
│   └── requirements.txt
├── frontend/
│   ├── index.html               # Main UI
│   ├── style.css                # Styling
│   └── app.js                   # API calls & DOM logic
├── .env.example                 # Environment variable template
└── README.md
```

---

## ⚙️ Setup & Installation

### Prerequisites
- Python 3.9 or higher
- A free [Groq API key](https://console.groq.com)

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/healthcare-symptom-checker.git
cd healthcare-symptom-checker
```

### 2. Create and activate virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r backend/requirements.txt
```

### 4. Configure environment variables
```bash
# Windows
copy .env.example .env

# Mac/Linux
cp .env.example .env
```

Open `.env` and add your Groq API key:
```
GROQ_API_KEY=your_groq_api_key_here
```

### 5. Start the backend server
```bash
uvicorn backend.main:app --reload
```

Server runs at: `http://127.0.0.1:8000`

### 6. Open the frontend

Open `frontend/index.html` directly in your browser.  
*(Double-click the file or drag it into Chrome/Firefox)*

---

## 🔌 API Reference

Interactive docs available at: `http://127.0.0.1:8000/docs`

### `POST /api/v1/check-symptoms`

Analyzes symptoms and returns probable conditions.

**Request body:**
```json
{
  "symptoms": "I have a severe headache, fever of 102°F, and stiff neck for 2 days"
}
```

**Response:**
```json
{
  "id": 1,
  "symptoms": "I have a severe headache...",
  "conditions": [
    {
      "name": "Meningitis",
      "likelihood": "High",
      "description": "Inflammation of membranes surrounding the brain..."
    }
  ],
  "recommended_steps": [
    "Call emergency services (112 or 108) immediately",
    "Do not drive yourself to the hospital"
  ],
  "urgency_level": "Emergency",
  "disclaimer": "This information is for educational purposes only...",
  "created_at": "2026-03-28T10:30:00"
}
```

### `GET /api/v1/history`

Returns all past symptom queries, newest first.

### `GET /health`

Health check endpoint. Returns `{"status": "ok"}`.

---

## 🧠 LLM Prompt Design

The system prompt enforces:
- Structured JSON-only output (no markdown, no preamble)
- Exactly 3–5 conditions ordered by likelihood
- Urgency classification with defined criteria
- Mandatory safety disclaimer in every response
- No prescription medication suggestions
- No definitive diagnoses

---

## 🛡️ Safety & Disclaimers

Disclaimers are enforced at **three independent levels**:

1. **LLM Prompt** — Model is instructed to always include a disclaimer field
2. **API Response** — `disclaimer` is a required field in the Pydantic schema
3. **UI** — Persistent banner at the top + disclaimer shown with every result

---

## 📋 Checklist

- [x] FastAPI backend with structured LLM responses
- [x] Groq API integration (LLaMA 3.3 70B)
- [x] SQLite database with query history
- [x] Input validation (Pydantic + client-side)
- [x] Safety disclaimers at all levels
- [x] Auto-generated API docs (`/docs`)
- [x] Responsive frontend with no dependencies
- [x] Error handling at every layer
