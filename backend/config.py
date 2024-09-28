import json
import os

def load_config():
    try:
        with open('config/secret.json') as config_file:
            config = json.load(config_file)
        
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_API_KEY"] = config.get("LANGCHAIN_API_KEY", "")
        os.environ["GOOGLE_API_KEY"] = config.get("GEMINI_API_KEY", "")
        os.environ["TOKENIZERS_PARALLELISM"] = "false"
        os.environ["GROQ_API_KEY"] = config.get("GROQ_API_KEY", "")
    except FileNotFoundError:
        print("config.json not found. Please create a config file with your API keys.")
    except json.JSONDecodeError:
        print("Error parsing config.json. Please ensure it's valid JSON.")
