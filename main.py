# Import needed packages

import json
import os
import openai
import time
import requests
import re
import functions
# import pinecone
from openai import OpenAI
from flask import Flask, request, jsonify, render_template

# Check OpenAI version compatibility
from packaging import version

required_version = version.parse("1.1.1")
current_version = version.parse(openai.__version__)
OPENAI_API_KEY = os.environ['OPENAI_API_KEY']

if current_version < required_version:
  raise ValueError(
      f"Error: OpenAI version {openai.__version__} is less than the required version 1.1.1"
  )
else:
  print("OpenAI version is compatible.")

# Create Flask app
app = Flask(__name__)
# app = Flask(__name__, static_url_path='/static')

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# Create or load assistant
assistant_id = functions.create_assistant(
    client)  # this function comes from "functions.py"
print("assistant_id = ", assistant_id)


# Start conversation thread
@app.route('/')
def index():
  print("Starting a new conversation...")

  # this is created to continue the chat
  thread = client.beta.threads.create()
  print(f"New thread created with ID: {thread.id}")

  return render_template('chat.html',
                         thread_id=thread.id)  # Pass thread_id to the frontend


# Generate response
@app.route('/chat', methods=['GET', 'POST'])
def chat():
  user_input = request.form['user_input']
  thread_id = request.form['thread_id']

  # if thread_id not create,
  if not thread_id:
    print("Error: Missing thread_id")
    return jsonify({"error": "Missing thread_id"}), 400

  print(f"Received message: {user_input} for thread ID: {thread_id}")

  # Add the user's message to the thread
  client.beta.threads.messages.create(thread_id=thread_id,
                                      role="user",
                                      content=user_input)

  # Run the Assistant
  run = client.beta.threads.runs.create(thread_id=thread_id,
                                        assistant_id=assistant_id)
  print("Run Status =", run.status)

  while run.status == "queued" or run.status == "in_progress":
    run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)

  # Retrieve and return the latest message from the assistant

  messages = client.beta.threads.messages.list(thread_id=thread_id)
  response = messages.data[0].content[0].text.value

  print(f"Assistant response: {messages.data[-1]}")
  return jsonify({"response": response})


if __name__ == '__main__':
  app.run(host='0.0.0.0', port=8080)
