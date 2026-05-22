import json
import os

import streamlit as st

from groq import Groq
from dotenv import load_dotenv

# LOAD ENV
load_dotenv()

api_key = (
    st.secrets.get("GROQ_API_KEY")
    if "GROQ_API_KEY" in st.secrets
    else os.getenv("GROQ_API_KEY")
)

client = Groq(
    api_key=api_key
)


# ANALYZE QUERY
def analyze_query(
    query,
    chat_history=None
):

    history_text = ""

    if chat_history:

        for msg in chat_history[-6:]:

            history_text += (
                f"{msg['role']}: "
                f"{msg['content']}\n"
            )

    prompt = f"""
You are an AI customer support assistant for a visa processing company.
Talk to the customer in a helpful and professional manner, like a real customer support agent.
Analyze the conversation.
Determine whether the query requires ticket creation.

Simple FAQs and informational questions should NOT create tickets.

Operational issues, complaints, delays, missing documents, or appointment issues SHOULD create tickets.

Conversation history:
{history_text}

Latest customer message:
{query}

Return ONLY valid JSON:

{{
  "category": "",
  "priority": "",
  "department": "",
  "escalated": true or false,
  "response": ""
}}

Possible categories:
- Visa Status Inquiry
- Missing Documents
- Appointment Rescheduling
- Complaint Escalation
- General Inquiry

Possible priorities:
- Low
- Medium
- High

Possible departments:
- Visa Processing
- Documentation Team
- Scheduling Team
- Customer Relations
- Customer Support
"""

    try:

        completion = client.chat.completions.create(

            model="llama-3.1-8b-instant",

            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],

            temperature=0.3
        )

        response = (
            completion.choices[0]
            .message
            .content
        )

        response = response.strip()

        if response.startswith("```"):

            lines = response.splitlines()

            lines = [
                line
                for line in lines
                if not line.strip().startswith("```")
            ]

            response = "\n".join(lines)

        return json.loads(response)

    except Exception as e:

        return {
            "category": "General Inquiry",
            "priority": "Medium",
            "department": "Customer Support",
            "escalated": False,
            "requires_ticket": True,
            "response": (
                "Your request has been received."
            ),
            "error": str(e)
        }