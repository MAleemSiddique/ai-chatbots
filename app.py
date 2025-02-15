from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
import requests
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app, resources={
    r"/chat": {
        "origins": ["*"],  # Be more specific in production
        "methods": ["POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Llama 3 API endpoint and headers
LLAMA_API_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"
API_KEY = "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"

@app.route('/chat', methods=['OPTIONS', 'POST'])
def chat():
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type")
        response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
        return response

    if request.method == 'POST':
        data = request.json
        user_message = data.get("message", "")

        if not user_message:
            return jsonify({"reply": "I didn't get that. Can you rephrase?"})

        # System prompt to set chatbot behavior
        system_prompt = "You are roleplaying as a psychologist for this chat. Answer with empathy and provide thoughtful responses."

        try:
            # Make API call to Llama 3 (via Groq)
            response = requests.post(
                LLAMA_API_ENDPOINT,
                headers={
                    "Authorization": f"Bearer {API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama3-8b-8192",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message}
                    ],
                    "temperature": 0.7
                }
            )

            response_data = response.json()

            if 'choices' not in response_data:
                return jsonify({
                    "error": f"Unexpected API response: {json.dumps(response_data)}"
                }), 500

            # Extract chatbot response
            bot_reply = response_data['choices'][0]['message']['content'].strip()

            response = make_response(jsonify({"reply": bot_reply}))
            response.headers.add("Access-Control-Allow-Origin", "*")
            return response

        except Exception as e:
            response = make_response(jsonify({"error": str(e)}), 500)
            response.headers.add("Access-Control-Allow-Origin", "*")
            return response

if __name__ == '__main__':
    app.run(debug=True, port=5000)
