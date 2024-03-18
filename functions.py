# Import needed packages

import json
import requests
import os
import requests
import re
# import pinecone
from openai import OpenAI
from prompts import formatter_prompt, assistant_instructions

OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
# AIRTABLE_API_KEY = os.environ['AIRTABLE_API_KEY']
# Set up Pinecone
# pinecone_api_key = 'e98bd3a7-0cd4-45d7-93bc-5f9371866fb1'
# pinecone_index_name = 'montero'

# pinecone.init(api_key=pinecone_api_key, environment='gcp-starter')
# index = pinecone.Index(pinecone_index_name)
# index.describe_index_stats()

# Init OpenAI Client
client = OpenAI(api_key=OPENAI_API_KEY)

# Add lead to Airtable
# def create_lead(name, phone, address):
#   url = "https://api.airtable.com/v0/appehbkHTnrLOU4ol/Accelerator%20Leads"  # Change this to your Airtable API URL
#   headers = {
#       "Authorization": AIRTABLE_API_KEY,
#       "Content-Type": "application/json"
#   }
#   data = {
#       "records": [{
#           "fields": {
#               "Name": name,
#               "Phone": phone,
#           }
#       }]
#   }
#   response = requests.post(url, headers=headers, json=data)
#   if response.status_code == 200:
#     print("Lead created successfully."
#           )  # this one create if a user enter their name and address.
#     return response.json()
#   else:
#     print(f"Failed to create lead: {response.text}")
#   pass


# Create or load assistant
def create_assistant(client):
  assistant_file_path = 'assistant.json'

  # If there is an assistant.json file already, then load that assistant
  if os.path.exists(assistant_file_path):
    with open(assistant_file_path, 'r') as file:
      assistant_data = json.load(file)
      assistant_id = assistant_data['assistant_id']
      print("Loaded existing assistant ID.")
  else:
    
    # If no assistant.json is present, create a new assistant 


    file = client.files.create(file=open("ExternalWordPressDeveloperGuide.txt", "rb"),
                               purpose='assistants')

    assistant = client.beta.assistants.create(
        # Getting assistant prompt from "prompts.py" file, edit on left panel if you want to change the prompt
        instructions=assistant_instructions,
        model="gpt-3.5-turbo",
        tools=[
            {
                "type": "retrieval"
            },
            {
                "type": "function",  # This adds the lead capture as a tool
                "function": {
                    "name": "create_lead",
                    "description":
                    "Capture lead details and save to Airtable.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "Name of the lead."
                            },
                            "phone": {
                                "type": "string",
                                "description": "Phone number of the lead."
                            }
                        },
                        "required": ["name", "phone"]
                    }
                }
            }
        ],
        file_ids=[file.id])

    # Create a new assistant.json file to load on future runs
    with open(assistant_file_path, 'w') as file:
      json.dump({'assistant_id': assistant.id}, file)
      print("Created a new assistant and saved the ID.")

    assistant_id = assistant.id

  return assistant_id
