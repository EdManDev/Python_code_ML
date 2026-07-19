import os
from openai import OpenAI

client = OpenAI(
    api_key="sk-yuoo7oDK0YnEXekXa0ZbkEQEqyLsZvdhkyPQbJjs2KHzZnk2",
    base_url="https://api.moonshot.ai/v1"
)

response = client.chat.completions.create(
    model="kimi-k2",
    messages=[
        {
            "role": "user",
            "content": "Hello!"
        }
    ]
)

print(response.choices[0].message.content)
