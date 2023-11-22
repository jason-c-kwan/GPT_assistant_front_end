from flask import Flask, render_template, request, jsonify
from openai import OpenAI  # Import OpenAI
from config import OPENAI_API_KEY

app = Flask(__name__)

# Initialize OpenAI client with your API key
client = OpenAI(api_key=OPENAI_API_KEY)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.json
    user_message = data['message']
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": user_message}],
            model="gpt-4-1106-preview"
        )

        # Adjust this line to correctly access the response
        # Example: reply = chat_completion.get_response()
        reply = chat_completion.choices[0].message.content  # Adjusted line

        return jsonify({'reply': reply, 'error': None})
    except Exception as e:  # Catch any exception
        # Return the error message
        return jsonify({'reply': None, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
