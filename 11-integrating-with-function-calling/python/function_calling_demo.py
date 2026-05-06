from __future__ import annotations

import json
from pathlib import Path

from openai import OpenAI


KEY_PATH = Path(r"C:\OpenaiKey.txt")
MODEL = "gpt-4o-mini"


CATALOG = [
    {
        "title": "Azure Fundamentals for Beginners",
        "role": "developer",
        "product": "Azure",
        "level": "beginner",
        "url": "https://learn.microsoft.com/training/paths/azure-fundamentals/"
    },
    {
        "title": "Build AI Apps with Azure OpenAI",
        "role": "developer",
        "product": "Azure OpenAI",
        "level": "intermediate",
        "url": "https://learn.microsoft.com/azure/ai-services/openai/"
    },
    {
        "title": "Introduction to Machine Learning",
        "role": "student",
        "product": "machine learning",
        "level": "beginner",
        "url": "https://learn.microsoft.com/training/paths/introduction-machine-learning/"
    },
]


def load_client() -> OpenAI:
    assert KEY_PATH.exists(), f"Key file not found: {KEY_PATH}"
    api_key = KEY_PATH.read_text(encoding="utf-8").strip()
    assert api_key, f"Key file is empty: {KEY_PATH}"
    return OpenAI(api_key=api_key)


def search_courses(role: str, product: str | None = None, level: str | None = None) -> str:
    matches = []
    for item in CATALOG:
        if role and item["role"].lower() != role.lower():
            continue
        if product and product.lower() not in item["product"].lower():
            continue
        if level and item["level"].lower() != level.lower():
            continue
        matches.append(item)

    if not matches:
        matches = CATALOG[:2]

    return json.dumps(matches, ensure_ascii=False)


def main() -> None:
    client = load_client()

    tools = [
        {
            "type": "function",
            "function": {
                "name": "search_courses",
                "description": "Find technical courses for a learner based on role, product, and skill level.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "role": {
                            "type": "string",
                            "description": "The learner role, for example developer or student."
                        },
                        "product": {
                            "type": "string",
                            "description": "The technology or product of interest, for example Azure."
                        },
                        "level": {
                            "type": "string",
                            "description": "The learner level, for example beginner, intermediate, or advanced."
                        },
                    },
                    "required": ["role"],
                },
            },
        }
    ]

    messages = [
        {
            "role": "system",
            "content": "You help learners find suitable technical courses. Use tools when course lookup is needed."
        },
        {
            "role": "user",
            "content": "I am a beginner developer and I want to learn Azure. Recommend a good course."
        },
    ]

    first_response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=tools,
        tool_choice="auto",
        temperature=0,
    )

    assistant_message = first_response.choices[0].message
    print("First model response:")
    print(assistant_message)

    if not assistant_message.tool_calls:
        print("\nThe model did not request a tool call.")
        return

    tool_call = assistant_message.tool_calls[0]
    arguments = json.loads(tool_call.function.arguments)
    tool_result = search_courses(
        role=arguments.get("role", ""),
        product=arguments.get("product"),
        level=arguments.get("level"),
    )

    messages.append(assistant_message)
    messages.append(
        {
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": tool_result,
        }
    )

    second_response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=tools,
        tool_choice="auto",
        temperature=0,
    )

    print("\nTool result:")
    print(tool_result)
    print("\nFinal answer:")
    print(second_response.choices[0].message.content)


if __name__ == "__main__":
    main()
