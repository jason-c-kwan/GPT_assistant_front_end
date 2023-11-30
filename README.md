# GPT_assistant_front_end

A simple front-end website for the GPT API, largely written by GPT-4-turbo. To use, you need to make a file called `config.py` in the root directory, with the following contents:

```
OPENAI_API_KEY = 'your_openai_api_key'
ASSISTANT_ID = 'assistant_id' # You can find this in your platform.openai.com
GITHUB_API_KEY = 'your_fine_grained_api_key'
```

...replacing `'your_openai_api_key`` with your API key, of course, as well as the assistant_id and github_api_key.

Allows access to an existing assistant made through [platform.openai.com](platform.openai.com). Make sure to instruct the assistant to output a json when it detects you 
want to make an API call to github in the form:

```json
{
    'API_Request': {
         # Request details, currently supports pulls, releases, issues
     }
}
```

To create the environment you need:

```bash
conda create -n flask python=3.9
conda install pip
pip install flask openai requests re
```

To run the server:

```bash
cd GPT_assistant_front_end
flask run
```
