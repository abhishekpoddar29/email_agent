import asyncio
import os
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content
from dotenv import load_dotenv
from openai import AsyncOpenAI
from typing import Dict, Any

from agents import Agent, Runner, trace, function_tool
from agents import OpenAIChatCompletionsModel

# ─── Load environment variables ───────────────────────────────────────────────
load_dotenv(override=True)

# ─── Model setup (Gemini via OpenAI-compatible API) ───────────────────────────
google_api_key = os.getenv("GOOGLE_API_KEY")

gemini = AsyncOpenAI(
    api_key=google_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

model_name = "gemma-4-26b-a4b-it"

model = OpenAIChatCompletionsModel(
    model=model_name,
    openai_client=gemini,
)

# ─── Sales Agent instructions ──────────────────────────────────────────────────
instructions1 = (
    "You are a sales agent working for ComplAI, "
    "a company that provides a SaaS tool for ensuring SOC2 compliance and preparing for audits, powered by AI. "
    "You write professional, serious cold emails."
)

instructions2 = (
    "You are a humorous, engaging sales agent working for ComplAI, "
    "a company that provides a SaaS tool for ensuring SOC2 compliance and preparing for audits, powered by AI. "
    "You write witty, engaging cold emails that are likely to get a response."
)

instructions3 = (
    "You are a busy sales agent working for ComplAI, "
    "a company that provides a SaaS tool for ensuring SOC2 compliance and preparing for audits, powered by AI. "
    "You write concise, to the point cold emails."
)

# ─── Three sales agents ────────────────────────────────────────────────────────
sales_agent1 = Agent(name="Professional Sales Agent", instructions=instructions1, model=model)
sales_agent2 = Agent(name="Engaging Sales Agent",     instructions=instructions2, model=model)
sales_agent3 = Agent(name="Busy Sales Agent",         instructions=instructions3, model=model)

# ─── Convert sales agents to tools ────────────────────────────────────────────
description = "Write a cold sales email"
tool1 = sales_agent1.as_tool(tool_name="sales_agent1", tool_description=description)
tool2 = sales_agent2.as_tool(tool_name="sales_agent2", tool_description=description)
tool3 = sales_agent3.as_tool(tool_name="sales_agent3", tool_description=description)

# ─── Subject writer + HTML converter agents ───────────────────────────────────
subject_instructions = (
    "You can write a subject for a cold sales email. "
    "You are given a message and you need to write a subject for an email that is likely to get a response."
)

html_instructions = (
    "You can convert a text email body to an HTML email body. "
    "You are given a text email body which might have some markdown "
    "and you need to convert it to an HTML email body with simple, clear, compelling layout and design."
)

subject_writer = Agent(name="Email subject writer",      instructions=subject_instructions, model=model)
html_converter = Agent(name="HTML email body converter", instructions=html_instructions,    model=model)

subject_tool = subject_writer.as_tool(
    tool_name="subject_writer",
    tool_description="Write a subject for a cold sales email",
)
html_tool = html_converter.as_tool(
    tool_name="html_converter",
    tool_description="Convert a text email body to an HTML email body",
)

# ─── send_html_email tool ─────────────────────────────────────────────────────
@function_tool
def send_html_email(subject: str, html_body: str) -> Dict[str, str]:
    """Send out an email with the given subject and HTML body to all sales prospects."""
    sg         = sendgrid.SendGridAPIClient(api_key=os.environ.get("SENDGRID_API_KEY"))
    from_email = Email("abhiramos5829@gmail.com")   # ← change to your verified SendGrid sender
    to_email   = To("abhishekpoddar5829@gmail.com")            # ← change to your recipient
    content    = Content("text/html", html_body)
    mail       = Mail(from_email, to_email, subject, content).get()
    response   = sg.client.mail.send.post(request_body=mail)
    print(f"Email sent — status code: {response.status_code}")
    return {"status": "success"}

# ─── Emailer agent (formats + sends via handoff) ──────────────────────────────
emailer_instructions = (
    "You are an email formatter and sender. You receive the body of an email to be sent. "
    "You first use the subject_writer tool to write a subject for the email, "
    "then use the html_converter tool to convert the body to HTML. "
    "Finally, you use the send_html_email tool to send the email with the subject and HTML body."
)

emailer_agent = Agent(
    name="Email Manager",
    instructions=emailer_instructions,
    tools=[subject_tool, html_tool, send_html_email],
    model=model,
    handoff_description="Convert an email to HTML and send it",
)

# ─── Sales Manager agent (orchestrator) ───────────────────────────────────────
sales_manager_instructions = """
You are a Sales Manager at ComplAI. Your goal is to find the single best cold sales email using the sales_agent tools.

Follow these steps carefully:
1. Generate Drafts: Use all three sales_agent tools to generate three different email drafts. Do not proceed until all three drafts are ready.

2. Evaluate and Select: Review the drafts and choose the single best email using your judgment of which one is most effective.
   You can use the tools multiple times if you're not satisfied with the results from the first try.

3. Handoff for Sending: Pass ONLY the winning email draft to the 'Email Manager' agent.
   The Email Manager will take care of formatting and sending.

Crucial Rules:
- You must use the sales agent tools to generate the drafts — do not write them yourself.
- You must hand off exactly ONE email to the Email Manager — never more than one.
"""

sales_manager = Agent(
    name="Sales Manager",
    instructions=sales_manager_instructions,
    tools=[tool1, tool2, tool3],
    handoffs=[emailer_agent],
    model=model,
)

# ─── Run ───────────────────────────────────────────────────────────────────────
async def main():
    message = "Send out a cold sales email addressed to Dear CEO from Alice"
    with trace("Automated SDR"):
        result = await Runner.run(sales_manager, message)
    print("\n=== Final output ===")
    print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())