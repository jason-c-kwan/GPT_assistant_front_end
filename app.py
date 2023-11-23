from flask import Flask, render_template, request, jsonify
from openai import OpenAI  # Import OpenAI
from config import OPENAI_API_KEY
from config import ASSISTANT_ID
import time

app = Flask(__name__)

# Initialize OpenAI client with your API key
client = OpenAI(api_key=OPENAI_API_KEY)
assistant = client.beta.assistants.retrieve(ASSISTANT_ID)
thread = client.beta.threads.create()

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

        return jsonify({'reply': reply, 'error': None})
    except Exception as e:  # Catch any exception
        # Return the error message
        return jsonify({'reply': None, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
