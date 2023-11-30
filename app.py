from flask import Flask, render_template, request, jsonify
from openai import OpenAI  # Import OpenAI
from config import OPENAI_API_KEY
from config import ASSISTANT_ID
from config import GITHUB_API_KEY
import time
import re
import json
import requests

app = Flask(__name__)

# Initialize OpenAI client with your API key
client = OpenAI(api_key=OPENAI_API_KEY)
assistant = client.beta.assistants.retrieve(ASSISTANT_ID)
thread = client.beta.threads.create()

def make_github_api_call(api_request):
    base_url = "https://api.github.com/repos/"
    headers = {"Authorization": "token " + GITHUB_API_KEY}  # Replace with your GitHub token
    # Repository can be stored as repository or repo, depending on how the assistant is feeling.
    repo_key = None
    for param_key in api_request:
        if 'repo' in param_key.lower():
            repo_key = param_key
            break

    # Repo is normally in the form Kwanlan/Autometa (so owner/repo)
    owner = api_request[repo_key].split('/')[0]
    repo_name = api_request[repo_key].split('/')[1]

    if "state" in api_request:
        params = {
            "state": api_request.get("state", "open")
        }

    # Construct the URL based on the request type
    if api_request['type'] == 'pulls':
        url = f"{base_url}{api_request[repo_key]}/pulls"

        response = requests.get(url, headers=headers, params=params)

        return process_github_response(response)

    if api_request['type'] == 'issues':
        url = f"{base_url}{api_request[repo_key]}/issues"

        response = requests.get(url, headers=headers, params=params)

        return process_github_response(response)
    
    if api_request['type'] == 'releases':
        url =f"{base_url}{api_request[repo_key]}/releases"
        params = {
            "owner": owner,
            "repo": repo_name
        }
        response = requests.get(url, headers=headers, params=params)

        return process_github_response(response)
    # Add more conditions for different types of requests
    # ...

    return "Unsupported request type"

def process_github_response(response):
    if response.status_code == 200:
        # Get rid of keys that are too large for the assistant to summarize
        data = response.json()  # Assuming this is a list of dictionaries

        # Process each dictionary in the list
        for item in data:
            # List of keys to be removed, to avoid modifying the dictionary while iterating over it
            keys_to_remove = []
            for key, value in item.items():
                # Check if the value, when converted to a string, is longer than 500 characters
                if len(str(value)) > 500:
                    keys_to_remove.append(key)

            # Remove the identified keys
            for key in keys_to_remove:
                del item[key]

        return data
    else:
        return f"GitHub API error: {response.status_code}"

@app.route('/')
def home():
    # Get the assistant's name and pass it to the template
    assistant_name = assistant.name
    return render_template('index.html', assistant_name=assistant_name)

@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.json
    user_message = data['message']
    
    try:
        message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=user_message
        )

        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant.id
        )

        # Poll every 5 seconds in order to see if run has completed
        completed = False
        failed = False
        while completed == False:
            time.sleep(5)
            run_steps = client.beta.threads.runs.steps.list(
                thread_id=thread.id,
                run_id=run.id
            )
            current_status = run_steps.data[-1].status
            if current_status == 'completed':
                completed = True
                failed = False
            elif current_status == 'expired' or current_status == 'cancelled' or current_status == 'failed':
                completed = True
                failed = True
        
        thread_messages = client.beta.threads.messages.list(thread.id)
        reply = thread_messages.data[0].content[0].text.value
        #breakpoint()
        # Using regular expression to find the JSON snippet when the GPT wants to make an API request
        json_pattern = r'```json\n(.*?)\n```'
        matches = re.search(json_pattern, reply, re.DOTALL)

        if matches:
            json_snippet = matches.group(1)
            try:
                api_request = json.loads(json_snippet)
                if "API_Request" in api_request:
                    github_response = make_github_api_call(api_request["API_Request"])
                    
                    # Format the GitHub response
                    formatted_github_response = str(github_response)
                    # Create a new query for the Assistant
                    new_query = "Here is the response from the GitHub API, can you interpret this into a human-readable form?\n" + formatted_github_response

                    try:
                        new_message = client.beta.threads.messages.create(
                            thread_id=thread.id,
                            role="user",
                            content=new_query
                        )

                        new_run = client.beta.threads.runs.create(
                            thread_id=thread.id,
                            assistant_id=assistant.id
                        )

                        # Poll every 5 seconds in order to see if run has completed
                        completed = False
                        failed = False
                        while completed == False:
                            time.sleep(5)
                            run_steps = client.beta.threads.runs.steps.list(
                                thread_id=thread.id,
                                run_id=new_run.id
                            )
                            current_status = run_steps.data[-1].status
                            if current_status == 'completed':
                                completed = True
                                failed = False
                            elif current_status == 'expired' or current_status == 'cancelled' or current_status == 'failed':
                                completed = True
                                failed = True
                        
                        thread_messages = client.beta.threads.messages.list(thread.id)
                        new_reply = thread_messages.data[0].content[0].text.value

                        return jsonify({'reply': new_reply})
                    except Exception as e:
                        return jsonify({'reply': None, 'error': str(e)})
                    
            except json.JSONDecodeError:
                pass  # Handle invalid JSON here

        return jsonify({'reply': reply, 'error': None})
    except Exception as e:  # Catch any exception
        # Return the error message
        return jsonify({'reply': None, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
