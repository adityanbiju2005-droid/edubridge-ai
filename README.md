# 🌉 EduBridge AI

> A multi-agent AI pipeline that transforms textbook content into culturally localized lessons, quizzes, and teacher rubrics — for any language and region in the world.

Built for **CSRBOX** · Powered by **LangGraph + Groq LLaMA 3.3 70B + FastAPI**

---

## ✨ Features

- **4-Stage Agentic Pipeline** (LangGraph state machine)
  - 🔀 Supervisor Router — validates & orchestrates flow
  - 📚 Pedagogical Structurer — extracts learning objectives & concepts
  - 🌍 Localization Agent — translates & culturally adapts content
  - 📝 Quiz Generator — creates worksheets & teacher rubrics
- **17+ supported languages** (Hindi, Tamil, Bengali, Swahili, Arabic…)
- **16+ target regions** (Rural Bihar, Sub-Saharan Africa, Rural Brazil…)
- **Stunning dark glassmorphism frontend** with animated pipeline visualization
- **FastAPI REST backend** with interactive Swagger docs

---

## 🗂️ Project Structure

```
edubridge-ai/
├── EduBridge AI.py          ← Original agent script
│
├── backend/
│   ├── agent.py             ← Importable LangGraph pipeline
│   ├── main.py              ← FastAPI REST API
│   ├── requirements.txt     ← Python dependencies
│   └── .env.example         ← Environment variable template
│
├── frontend/
│   ├── index.html           ← Single-page app
│   ├── style.css            ← Dark glassmorphism design
│   └── app.js               ← Fetch, animations, tabs
│
├── start_backend.bat        ← One-click backend launcher (Windows)
├── start_frontend.bat       ← One-click frontend launcher (Windows)
└── .gitignore
```

---

## 🚀 Getting Started

### 1. Clone the repo
```bash
git clone https://github.com/adityanbiju2005-droid/edubridge-ai.git
cd edubridge-ai
```

### 2. Set up the backend
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your GROQ_API_KEY
```

### 3. Run the backend
```bash
# From the backend/ folder:
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```
Or double-click **`start_backend.bat`**

### 4. Run the frontend
```bash
# From the frontend/ folder:
python -m http.server 5500
```
Or double-click **`start_frontend.bat`**

### 5. Open the app
Navigate to **http://127.0.0.1:5500** in your browser.

> 📖 **API Docs:** http://127.0.0.1:8000/docs

---

## 🔑 Environment Variables

| Variable | Description |
|---|---|
| `GROQ_API_KEY` | Your API key from [console.groq.com](https://console.groq.com) |

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| LLM | Groq LLaMA 3.3 70B Versatile |
| Agent Framework | LangGraph + LangChain |
| Backend API | FastAPI + Uvicorn |
| Frontend | Vanilla HTML / CSS / JS |
| Design | Dark Glassmorphism + Google Fonts |

---

## 📄 License

MIT License — built for CSRBOX educational initiatives.
