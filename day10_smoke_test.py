import os
from dotenv import load_dotenv
from google import genai
from app.agent.loop import run_agent

load_dotenv()

client = genai.Client(
    api_key=os.environ["GEMINI_API_KEY"]
)

result = run_agent(
    client=client,
    model_name=os.environ["GEMINI_MODEL"],
    question=(
        "Use lookup_offering to check offer 104. "
        "Tell me its destination, duration, and availability. "
        "Do not invent a price."
    )
)

print("Status:", result["status"])

if result["status"] == "final":
    print("Answer:", result["interaction"].output_text)
    print("Model calls:", result["model_calls"])
    print("Tool steps:", result["tool_steps"])
else:
    print("Details:", result)