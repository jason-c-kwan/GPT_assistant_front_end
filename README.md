# GPT_assistant_front_end

A simple front-end website for the GPT API, largely written by GPT-4-turbo. To use, you need to make a file called `config.py` in the root directory, with the following contents:

```
OPENAI_API_KEY = 'your_openai_api_key'
ASSISTANT_ID = 'assistant_id' # You can find this in your platform.openai.com
```

...replacing `'your_openai_api_key`` with your API key, of course, as well as the assistant_id.

Allows access to an existing assistant made through [platform.openai.com](platform.openai.com).

To create the environment you need:

```bash
conda create -n flask python=3.9
conda install pip
pip install flask
pip install openai
```

To run the server:

```bash
cd GPT_assistant_front_end
flask run
```