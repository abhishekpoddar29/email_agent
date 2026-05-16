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

## Architecture Deep Dive

Understanding the architecture helps you adapt this system to any domain — not just sales emails.

### The Two Core Concepts: Tools vs Handoffs

This project uses the OpenAI Agents SDK and demonstrates two distinct ways agents can collaborate:

**Agents as Tools** — the calling agent retains control. It fires a sub-agent like a function call, gets the result back, and continues making decisions. Think of it as delegating a task but staying in charge.

**Handoffs** — control is transferred completely. The original agent passes the baton to another agent and steps aside. The new agent takes over and runs to completion independently.

```
┌─────────────────────────────────────────────────────────────────┐
│                        TOOLS (control returns)                  │
│                                                                 │
│   Sales Manager ──calls──► sales_agent1  ──result──► (back)    │
│                  ──calls──► sales_agent2  ──result──► (back)    │
│                  ──calls──► sales_agent3  ──result──► (back)    │
│                        Sales Manager decides the winner         │
└─────────────────────────────────────────────────────────────────┘
                                  │
                                  │  HANDOFF (control transfers)
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                       Email Manager                             │
│                                                                 │
│   Email Manager ──calls──► subject_writer   ──result──► (back) │
│                 ──calls──► html_converter   ──result──► (back)  │
│                 ──calls──► send_html_email()                    │
└─────────────────────────────────────────────────────────────────┘
```

### Why This Pattern Is Powerful

The architecture separates three responsibilities that exist in almost any automated content workflow:

| Layer | Role | Agent in this project |
|---|---|---|
| **Generation** | Produce multiple variations of output | sales_agent1, 2, 3 |
| **Orchestration** | Evaluate options and decide | Sales Manager |
| **Delivery** | Format and dispatch the output | Email Manager |

This separation means each layer can be swapped out or extended independently.

### Adapting This to Any Profession

The cold email is just one use case. The same three-layer architecture applies anywhere you want to generate, evaluate, and deliver content:

| Domain | Generation agents | Orchestrator | Delivery agent |
|---|---|---|---|
| **Recruitment** | Formal JD writer, Casual JD writer, Technical JD writer | HR Manager picks best job description | Posts to LinkedIn / sends to candidates |
| **Marketing** | Brand-voice writer, Trendy writer, Minimalist writer | Marketing Manager picks best ad copy | Publishes to social media or email list |
| **Customer Support** | Empathetic responder, Direct responder, Detailed responder | Support Lead picks best reply | Sends reply via helpdesk API |
| **Legal Drafting** | Aggressive clause writer, Neutral writer, Conservative writer | Senior Partner picks best contract clause | Inserts into document via API |
| **Journalism** | Formal reporter, Conversational blogger, Bullet-point summariser | Editor picks best article draft | Publishes via CMS API |

To adapt the project, you only need to change:
1. The **instructions** given to the three generator agents (their persona and domain)
2. The **delivery function** (`send_html_email`) to point at your target system (Slack, CMS, database, etc.)
3. The **orchestrator's instructions** to reflect the evaluation criteria for your domain

Everything else — the tool/handoff wiring, the runner, the tracing — stays exactly the same.

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
pip install openai-agents sendgrid python-dotenv openai
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
