import os
import json
import base64

import streamlit as st

from groq import Groq
from dotenv import load_dotenv


# LOAD ENV
load_dotenv()


# API KEY (Local + Streamlit Cloud)
try:
    api_key = st.secrets["GROQ_API_KEY"]
except Exception:
    api_key = os.getenv("GROQ_API_KEY")


# GROQ CLIENT
client = Groq(
    api_key=api_key
)


# IMAGE → BASE64
def encode_image(image_path):

    with open(image_path, "rb") as image_file:

        return base64.b64encode(
            image_file.read()
        ).decode("utf-8")


# VISION EXTRACTION
def extract_document_details(
    image_path,
    document_type
):

    base64_image = encode_image(image_path)

    prompt = f"""
You are an AI document extraction assistant.

Analyze this {document_type} image.

Extract all important fields accurately. Detect whether the uploaded image matches the expected document type.
Detect missing or unreadable fields. Reject random images or unrelated uploads.

Return ONLY valid JSON.

Examples:

For Passport:
{{
  "name": "",
  "passport_number": "",
  "nationality": "",
  "expiry_date": ""
}}

For Visa Copy:
{{
  "visa_number": "",
  "visa_type": "",
  "name": "",
  "nationality": "",
  "expiry_date": ""
}}

For Emirates ID:
{{
  "emirates_id_number": "",
  "name": "",
  "nationality": "",
  "expiry_date": ""
}}
Rules:
- If image is invalid/random/unreadable:
  set is_valid_document = false
- If fields are missing:
  include them in missing_fields
- Return ONLY JSON
"""

    try:

        completion = client.chat.completions.create(

            model="meta-llama/llama-4-scout-17b-16e-instruct",

            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],

            temperature=0.1
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
            "error": str(e)
        }