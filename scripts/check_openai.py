from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
reply = OpenAI().chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "user", "content": "Reply with the word OK, I'm working"}
    ],
)
print(reply.choices[0].message.content)
