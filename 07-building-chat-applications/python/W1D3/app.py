import glob
import os

from flask import Flask, jsonify, render_template, request

try:
    from openai import OpenAI
except Exception:
    OpenAI = None


app = Flask(__name__)

SYSTEM_PROMPT = "You are a concise and helpful AI tutor."
MODEL_NAME = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


def load_api_key() -> str:
    env_key = os.getenv("OPENAI_API_KEY", "").strip()
    if env_key:
        return env_key

    key_path = r"C:\Openaikey"

    def read_key(path: str) -> str:
        try:
            with open(path, "r", encoding="utf-8") as file:
                content = file.read().strip()
        except Exception:
            return ""

        if not content:
            return ""

        if "OPENAI_API_KEY=" in content:
            for line in content.splitlines():
                if line.startswith("OPENAI_API_KEY="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")

        return content

    if os.path.isfile(key_path):
        value = read_key(key_path)
        if value:
            return value

    txt_path = key_path + ".txt"
    if os.path.isfile(txt_path):
        value = read_key(txt_path)
        if value:
            return value

    for candidate in glob.glob(r"C:\Openaikey*"):
        if os.path.isfile(candidate):
            value = read_key(candidate)
            if value:
                return value

    if os.path.isdir(key_path):
        candidates = [
            "openai_api_key.txt",
            "OPENAI_API_KEY.txt",
            "key.txt",
            "apikey.txt",
            ".env",
        ]
        for name in candidates:
            full = os.path.join(key_path, name)
            if not os.path.isfile(full):
                continue
            value = read_key(full)
            if value:
                return value

    return ""


api_key = load_api_key()
client = OpenAI(api_key=api_key) if OpenAI and api_key else None


def local_fallback_reply(user_message: str) -> str:
    text = user_message.strip()
    if not text:
        return "Please enter a message first."
    return f"[Local fallback mode] You said: {text}"


def model_reply(user_message: str) -> str:
    if client is None:
        return local_fallback_reply(user_message)

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=0.3,
    )
    return response.choices[0].message.content or ""


@app.get("/")
def index():
    return render_template("index.html", model_name=MODEL_NAME, use_model=client is not None)


@app.post("/api/chat")
def chat():
    data = request.get_json(silent=True) or {}
    user_message = str(data.get("message", "")).strip()
    if not user_message:
        return jsonify({"error": "message is required"}), 400

    try:
        reply = model_reply(user_message)
    except Exception as exc:
        return jsonify({"error": f"chat failed: {exc}"}), 500

    return jsonify({"reply": reply})


@app.get("/api/chat")
def chat_get_help():
    return jsonify(
        {
            "message": 'This endpoint expects POST with JSON body: {"message": "..."}',
            "try_ui": "Open http://127.0.0.1:5055/",
        }
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5055, debug=False)
