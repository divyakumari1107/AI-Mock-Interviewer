# AI Mock Technical Interviewer & Code Evaluator

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0%2B-black.svg?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Google Gemini](https://img.shields.io/badge/Google%20Gemini-API%20Enabled-orange.svg?logo=google&logoColor=white)](https://ai.google.dev/)
[![ReportLab](https://img.shields.io/badge/ReportLab-PDF%20Generation-red.svg)](https://www.reportlab.com/)
[![Web Speech API](https://img.shields.io/badge/Web%20Speech-Voice%20Enabled-purple.svg)](https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An autonomous AI-powered technical coding interview platform designed for engineering students and job candidates. It simulates a senior engineer conducting live FAANG coding interviews with real-time conversational problem clarification, progressive 3-tier hints, sandboxed multi-case code execution, Big-O computational complexity analysis, and downloadable hiring scorecards.

---

## 🌟 Key Features

### 1. 🤖 Conversational AI Interviewer (Google Gemini)
- Simulates realistic FAANG interview personas (Google, Amazon, Meta, Microsoft, Apple).
- Prompts candidates to discuss their approach, clarify assumptions, and verify constraints before writing code.
- Integrated with the **HTML5 Web Speech API** for natural voice-to-text dictation and speech-synthesis audio responses.

### 2. 💡 Progressive 3-Tier Hint State Machine
- Avoids spoon-feeding solutions while keeping candidates unblocked:
  - **Tier 1 (Nudge)**: Conceptual data structure suggestion.
  - **Tier 2 (Structural Hint)**: Algorithmic technique (e.g., Two Pointers, Sliding Window).
  - **Tier 3 (Pseudocode)**: High-level logic walk-through without revealing complete code.

### 3. 🛡️ Isolated Code Execution Sandbox
- Executes candidate Python code in an isolated subprocess scope with safety limits:
  - **2.5-second hard watchdog timeout** (neutralizes infinite loops like `while True: pass`).
  - Evaluates both public sample test cases and hidden edge test cases (empty inputs, negative values, large sets).

### 4. 📊 Multi-Pillar Candidate Evaluation Engine
Evaluates candidates across four core dimensions (scored 0–100):
1. **Algorithmic Correctness (40%)**: Ratio of sample and hidden edge cases passed.
2. **Computational Complexity (25%)**: Real-time Time & Space complexity ($O(N)$, $O(N \log N)$) vs. optimal target.
3. **Code Quality & Modularity (20%)**: Abstract Syntax Tree (AST) structure, naming conventions, and PEP8 standards.
4. **Communication & Independence (15%)**: Active clarification questions and independence from hints.

### 5. 🏆 Objective Hiring Verdict & PDF Scorecard
- Outputs an industry-standard hiring recommendation:
  - **Strong Hire (85–100)**
  - **Hire (70–84)**
  - **Lean No-Hire (50–69)**
  - **No-Hire (< 50)**
- Generates a publication-grade, downloadable **ReportLab PDF Scorecard** with code diffs against the optimal reference solution.

---

## 📂 Project Structure

```text
AI-Mock-Interviewer/
│
├── app.py                  # Main Flask routes & WebSocket/API controllers
├── config.py               # Application configuration & environment loader
├── database.py             # SQLite persistence (questions, sessions, chats, scorecards)
├── code_executor.py        # Process-isolated sandboxed code runner & test evaluator
├── interviewer_ai.py       # Gemini API conversation engine & 3-tier hint generator
├── evaluation_engine.py    # AST syntax auditor, Big-O derivation, & hiring verdict
├── scorecard_pdf.py        # ReportLab programmatic PDF scorecard generator
├── test_suite.py           # Automated unit & integration test suite
│
├── templates/              # Jinja2 HTML5 UI templates
│   ├── base.html           # Master layout with responsive sidebar & top navbar
│   ├── index.html          # High-converting landing page
│   ├── dashboard.html      # Candidate metrics & recent sessions hub
│   ├── setup.html          # Interview configuration & problem selector
│   ├── interview.html      # Live interview room (code editor, terminal, voice chat)
│   ├── scorecard.html      # Detailed candidate performance scorecard & code diff
│   ├── questions.html      # Curated technical problem bank
│   ├── history.html        # Past scorecards & review transcripts
│   └── about.html          # Academic viva defense guide & architecture breakdown
│
├── static/
│   ├── css/
│   │   └── style.css       # Deep navy & royal blue design system
│   └── js/
│       └── script.js       # Live stopwatch, speech synthesis, & editor bindings
│
├── generated_scorecards/   # Downloadable ReportLab PDFs
├── requirements.txt        # Python dependency manifest
├── .env                    # Local environment variables
├── .env.example            # Environment template
├── .gitignore              # Git ignore rules
├── run.bat                 # One-click Windows startup script
└── README.md               # Complete project documentation
```

---

## 🚀 Installation & Local Execution (Windows CMD)

### 1. Open Windows Command Prompt
```cmd
cd /d "D:\cloudand devopsproject\AI-Mock-Interviewer"
```

### 2. Run the Application
The application is pre-configured and ready to run using the installed Python environment:
```cmd
python app.py
```
*(Or simply double-click [`run.bat`](file:///D:/cloudand%20devopsproject/AI-Mock-Interviewer/run.bat)).*

### 3. Open in Your Browser
Navigate to:
```
http://127.0.0.1:5001
```
*(Runs on port **5001** so it can run alongside your Resume Enhancer on port 5000 without conflict).*

---

## 🧪 Automated Testing

To run the complete automated test suite (verifying problem seeding, sandboxed execution, infinite loop detection, progressive hints, evaluation scoring, ReportLab PDF generation, and all Flask routes):

```cmd
python test_suite.py
```

Expected output:
```text
Ran 6 tests in 25.5s

OK
✓ Question Bank seeding and queries verified.
✓ Code execution: Correct code passed 5/5 test cases.
✓ Sandbox security: Infinite loop caught and terminated within timeout limit.
✓ Session lifecycle, conversation history, and 3-tier hints verified.
✓ Evaluation Engine: Score 91/100, Verdict: Strong Hire
✓ ReportLab Scorecard PDF generated and verified successfully.
✓ All 11 Flask routes & API endpoints tested with HTTP 200!
```

---

## 🎓 Academic Viva Defense Guide (For Final Year Projects)

When presenting this project to your college professors and external examiners:
- **Novelty vs. LeetCode**: Highlight that traditional platforms only perform compiler/test case checks. This system evaluates **verbal reasoning, thought process, Big-O derivation, and clean architecture**.
- **Sandboxing & Security**: Explain that student code runs inside an isolated worker process with strict **2.5s execution limits** preventing system compromise or CPU starvation.
- **Explainable Scoring**: Walk through the weighted evaluation formula:
  $$\text{Overall Score} = (\text{Correctness} \times 40\%) + (\text{Complexity} \times 25\%) + (\text{Code Quality} \times 20\%) + (\text{Communication} \times 15\%)$$
