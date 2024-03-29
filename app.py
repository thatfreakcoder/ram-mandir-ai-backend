import os
from time import sleep
from packaging import version
from flask import Flask, request, jsonify
import openai
from openai import OpenAI
from flask_cors import CORS, cross_origin
from dotenv import load_dotenv

load_dotenv()

# Check OpenAI version is correct
# required_version = version.parse("1.1.1")
# current_version = version.parse(openai.__version__)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# if current_version < required_version:
#     raise ValueError(
#         f"Error: OpenAI version {openai.__version__}"
#         " is less than the required version 1.1.1"
#     )
# else:
#     print("OpenAI version is compatible.")

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["http://localhost:5500", "https://chatwithshriram.in", "http://chatwithshriram.in"]}})

# Init client
client = OpenAI(api_key=OPENAI_API_KEY)

# Create new assistant or load existing
assistant_id = "asst_WiAcF2rfjQyix3xUtdcwhZRq"

@app.route("/")
def index():
    return {
        "message": "Welcome to Shree Ram AI"
    }

# Start conversation thread
@app.route("/start", methods=["GET"])
def start_conversation():
    try:
        print("Starting a new conversation...")
        thread = client.beta.threads.create()
        print(f"New thread created with ID: {thread.id}")
        return jsonify({"thread_id": thread.id})
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500

# Generate response
@app.route("/chat", methods=["POST"])
@cross_origin(supports_credentials=True)
def chat():
    try:
        data = request.json
        thread_id = data.get("thread_id")
        user_input = data.get("message", "")

        if not thread_id:
            print("Error: Missing thread_id")
            return jsonify({"error": "Missing thread_id"}), 400

        print(f"Received message: {user_input} for thread ID: {thread_id}")

        # Add the user's message to the thread
        client.beta.threads.messages.create(
            thread_id=thread_id, role="user", content=user_input
        )

        # Run the Assistant
        run = client.beta.threads.runs.create(
            thread_id=thread_id, assistant_id=assistant_id
        )

        # Check if the Run requires action (function call)
        while True:
            run_status = client.beta.threads.runs.retrieve(
                thread_id=thread_id, run_id=run.id
            )
            print(f"Run status: {run_status.status}")
            if run_status.status == "completed":
                break
            sleep(1)  # Wait for a second before checking again

        # Retrieve and return the latest message from the assistant
        messages = client.beta.threads.messages.list(thread_id=thread_id)
        response = messages.data[0].content[0].text.value

        print(f"Assistant response: {response}")
        return jsonify({"response": response})
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500