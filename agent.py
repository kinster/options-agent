import json
import os
from dotenv import load_dotenv
from openai import OpenAI
from price_tool import get_current_price

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_price",
            "description": "Fetch the latest stock price for a given ticker symbol",
            "parameters": {
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock ticker symbol like ASTS or TSLA"
                    }
                },
                "required": ["symbol"]
            }
        }
    }
]


def run_agent(user_message):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": user_message}],
        tools=tools,
        tool_choice="auto"
    )

    message = response.choices[0].message

    # If the model wants to call a tool
    if message.tool_calls:
        tool_call = message.tool_calls[0]
        tool_name = tool_call.function.name
        args = json.loads(tool_call.function.arguments)

        print(f"Agent decided to call tool: {tool_name} with {args}")

        if tool_name == "get_current_price":
            result = get_current_price(**args)
        else:
            result = {"error": "Unknown tool requested"}

        return result

    return {"message": message.content}


if __name__ == "__main__":
    while True:
        user_input = input("Ask the agent: ")
        print(run_agent(user_input))
