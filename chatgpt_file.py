import openai
from openai import OpenAI
import os
import time
import random
import pymongo  
from datetime import datetime
import re

client = OpenAI(
    api_key='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'  # Make sure to replace this with your actual API key
)

file = client.files.create(
  file=open("ProMed & Spine Medical (2) 09.02.21 - Referral for L4-5 ALIF.txt", "rb"),
  purpose="assistants"
)

messages=[
        {"role": "system", "content": """Please analyze the provided medical document and extract essential information for each patient visit. Present the extracted information in a structured list format for each visit, using the '//////////' as a separate header. Instead, include the date of the visit as one of the listed details. Each visit's information should be clear, concise, and organized without unnecessary descriptions or symbols. Follow this template for consistency:
            ///////////////////////
            Patient Name: [patient's full name]
            Doctor Name: [doctor's full name]
            Collaborator Name: [main Collaborator's full name, if not exist then 'not provided']
            Date of Visit: MM/DD/YYYY
            Medical Facility: [name of the medical facility]
            Main Service Provided: [most specific service provided]
            Signed Off By: [name of the person who signed off on the service]
            Sign-off Date: MM/DD/YYYY
            Summary: [brief summary of the services provided organized by these sections.
                - reviewed radiology report (if doesn't exist, then 'not provided')
                - physical examination (if doesn't exist, then 'not provided')
                - assesment (if doesn't exist, then 'not provided')
                - plan (if doesn't exist, then 'not provided')
                - date of accident (if doesn't exist, then 'not provided')
                - history of injury (if doesn't exist, then 'not provided')
                - history of present illness (if doesn't exist, then 'not provided')
                - discussion/plan (if doesn't exist, then 'not provided')]
            The summary should be succinct and informative, capturing the essence of the visit without extraneous details. Ensure that all information respects the document's context and content, with each visit's information clearly separated."""},
    ]

response = client.chat.completions.create(
    model="gpt-4-turbo-preview",
    messages=messages,
    file=file.id,
    frequency_penalty=0,
    temperature=0.5,
    seed=2
)

print(response)