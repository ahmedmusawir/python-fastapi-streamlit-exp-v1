import os
from openai import OpenAI

print(os.environ.get('OPENAI_API_KEY'))

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)

def get_openai_response(prompt: str) -> str:
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "user", "content": prompt},
        ],
        model="gpt-3.5-turbo",
    )
    return chat_completion.choices[0].message
