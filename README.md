# 🤖 ComplAI — Automated Cold Sales Email Agent

An agentic AI system that **writes, evaluates, formats, and sends** cold sales emails autonomously using the [OpenAI Agents SDK](https://github.com/openai/openai-agents-python), Google Gemini, and SendGrid.

---

## How It Works

The system is made up of **five specialized agents**, each with a distinct role:

```
Sales Manager  (orchestrator)
├── Calls → Professional Sales Agent   writes a formal cold email
├── Calls → Engaging Sales Agent       writes a witty, fun cold email
├── Calls → Busy Sales Agent           writes a short, punchy cold email
│
│   (picks the best draft, then hands off)
│
└── Handoff → Email Manager
                ├── Calls → Subject Writer     generates a compelling subject line
                ├── Calls → HTML Converter     converts plain text body to styled HTML
                └── Calls → send_html_email()  sends the final email via SendGrid
```

1. The **Sales Manager** instructs three sales agents to each draft an email.
2. It reads all three drafts and picks the best one using its own judgment.
3. It **hands off** the winning draft to the **Email Manager**.
4. The Email Manager writes a subject line, converts the body to HTML, and sends it.

---

## Prerequisites

- [uv](https://github.com/astral-sh/uv) installed (`pip install uv` or follow [uv docs](https://docs.astral.sh/uv/getting-started/installation/))
- A **Google AI Studio API key** (for Gemini) — get one free at https://aistudio.google.com/app/apikey
- A **SendGrid account + API key** — free tier at https://sendgrid.com
- A **verified sender email** in SendGrid (Settings → Sender Authentication → Verify a Single Sender)

---

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
cd YOUR_REPO_NAME
```

### 2. Create and activate a virtual environment

```bash
uv venv
```

**Windows:**
```bash
.venv\Scripts\activate
```

**Mac/Linux:**
```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install openai-agents sendgrid python-dotenv openai --no-cache
```

### 4. Create your `.env` file

Create a file named `.env` in the project root and add:

```
GOOGLE_API_KEY=your_google_api_key_here
SENDGRID_API_KEY=your_sendgrid_api_key_here
```

### 5. Set your email addresses

Open `main.py` and update these two lines inside `send_html_email`:

```python
from_email = Email("YOUR_VERIFIED_SENDER@example.com")  # must match your verified SendGrid sender
to_email   = To("YOUR_RECIPIENT@example.com")            # where you want the email delivered
```

---

## Run

```bash
python main.py
```

You should see the agent working through the steps in your terminal. Once complete, check your inbox (and **Spam folder**) for the HTML sales email.

You can also view the full agent trace at: https://platform.openai.com/traces

---

## Project Structure

```
.
├── main.py   # All agent definitions and entry point
├── .env             # Your API keys (never committed)
├── .gitignore       # Excludes .env and .venv from git
└── README.md
```

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `ModuleNotFoundError: No module named 'email.parser'` | Your script is named `email.py` — rename it to `sales_agent.py` |
| `uv` hardlink error on Windows | Run `pip install ... --no-cache` or move the project off OneDrive |
| No email received | Check your Spam folder; verify your sender in SendGrid dashboard |
| SSL certificate error | Run `pip install --upgrade certifi`, then add `import certifi; os.environ['SSL_CERT_FILE'] = certifi.where()` at the top of the script |
| `401 Unauthorized` from Gemini | Double-check `GOOGLE_API_KEY` in your `.env` file |
