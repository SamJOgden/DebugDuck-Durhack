import os
from openai import OpenAI
from dotenv import load_dotenv

# Load the .env file
load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
YOUR_APP_URL = "http://github.com/your-username/debug-duck" # Change this

if not OPENROUTER_API_KEY:
    print("Error: OPENROUTER_API_KEY not found in .env file.")
else:
    try:
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=OPENROUTER_API_KEY,
            default_headers={"HTTP-Referer": YOUR_APP_URL}
        )
        
        print("Calling OpenRouter (DeepSeek)...")
        
        response = client.chat.completions.create(
            model="deepseek/deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a debug duck. Say 'Quack!'"},
                {"role": "user", "content": "Test call."}
            ]
        )
        
        text = response.choices[0].message.content
        print(f"Success! Duck says: {text}")

    except Exception as e:
        print(f"An error occurred: {e}")