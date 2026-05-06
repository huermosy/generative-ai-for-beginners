from __future__ import annotations

import json
import re
from pathlib import Path

from openai import OpenAI


KEY_PATH = Path(r"C:\OpenaiKey.txt")
MODEL = "gpt-4o-mini"

STUDENT_DESCRIPTIONS = {
    "student_1": (
        "Emily Johnson is a sophomore majoring in computer science at Duke University. "
        "She has a 3.7 GPA. Emily is an active member of the university's Chess Club "
        "and Debate Team. She hopes to pursue a career in software engineering after graduating."
    ),
    "student_2": (
        "Michael Lee is a sophomore majoring in computer science at Stanford University. "
        "He has a 3.8 GPA. Michael is known for his programming skills and is an active "
        "member of the university's Robotics Club. He hopes to pursue a career in "
        "artificial intelligence after finishing his studies."
    ),
}


def load_client() -> OpenAI:
    assert KEY_PATH.exists(), f"Key file not found: {KEY_PATH}"
    api_key = KEY_PATH.read_text(encoding="utf-8").strip()
    assert api_key, f"Key file is empty: {KEY_PATH}"
    return OpenAI(api_key=api_key)


def parse_json_payload(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)

    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        text = match.group(0)

    return json.loads(text)


def extract_with_prompt(client: OpenAI, description: str) -> tuple[str, dict]:
    prompt = f"""
Please extract the following information from the given text and return it as a JSON object.

name
major
school
grades
club

Return JSON only.

This is the text:
{description}
""".strip()

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": "You extract information from student descriptions.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0,
    )

    content = response.choices[0].message.content or ""
    return content, parse_json_payload(content)


def extract_with_tool(client: OpenAI, description: str) -> dict:
    tools = [
        {
            "type": "function",
            "function": {
                "name": "save_student_profile",
                "description": "Extract a student profile from free-form text.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "The student's full name.",
                        },
                        "major": {
                            "type": "string",
                            "description": "The student's major field of study.",
                        },
                        "school": {
                            "type": "string",
                            "description": "The university or school name.",
                        },
                        "grades": {
                            "type": "string",
                            "description": "The student's GPA or grade information.",
                        },
                        "club": {
                            "type": "string",
                            "description": "One student club or organization explicitly mentioned in the text.",
                        },
                    },
                    "required": ["name", "major", "school", "grades", "club"],
                },
            },
        }
    ]

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": "Extract the student profile by calling the provided function.",
            },
            {"role": "user", "content": description},
        ],
        tools=tools,
        tool_choice={"type": "function", "function": {"name": "save_student_profile"}},
        temperature=0,
    )

    message = response.choices[0].message
    assert message.tool_calls, "The model did not return a tool call."
    arguments = message.tool_calls[0].function.arguments
    return json.loads(arguments)


def print_block(title: str, payload: object) -> None:
    print(f"\n=== {title} ===")
    if isinstance(payload, str):
        print(payload)
    else:
        print(json.dumps(payload, ensure_ascii=False, indent=2))


def main() -> None:
    client = load_client()

    print(f"Model: {MODEL}")
    print("Comparing prompt-only JSON extraction with tool-schema extraction.")

    for name, description in STUDENT_DESCRIPTIONS.items():
        print(f"\n{name}")
        raw_prompt_output, prompt_json = extract_with_prompt(client, description)
        tool_json = extract_with_tool(client, description)

        print_block("Prompt-only raw output", raw_prompt_output)
        print_block("Prompt-only parsed JSON", prompt_json)
        print_block("Tool-schema arguments", tool_json)


if __name__ == "__main__":
    main()
