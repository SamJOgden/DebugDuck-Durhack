"""
LLM Router for Debug Duck
Uses OpenRouter to access multiple AI models for different tasks
"""

import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API key from environment
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

# OpenRouter API endpoint
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Your app URL for OpenRouter identification
YOUR_APP_URL = "http://github.com/debug-duck/laptop-client"


class LLMRouter:
    """
    Routes requests to appropriate LLM models via OpenRouter
    """

    def __init__(self):
        if not OPENROUTER_API_KEY:
            raise ValueError("OPENROUTER_API_KEY not set in environment variables.")

        self.api_key = OPENROUTER_API_KEY
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": YOUR_APP_URL,
            "Content-Type": "application/json"
        }

    def _call_openrouter(self, model, messages, max_tokens=150, temperature=0.3):
        """
        Internal method to call OpenRouter API

        Args:
            model (str): The model identifier (e.g., "anthropic/claude-3.5-sonnet")
            messages (list): List of message dictionaries
            max_tokens (int): Maximum tokens in response
            temperature (float): Temperature for response generation

        Returns:
            str: The model's response text, or an error message
        """
        try:
            payload = {
                "model": model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature
            }

            response = requests.post(
                OPENROUTER_API_URL,
                headers=self.headers,
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                return data['choices'][0]['message']['content']
            else:
                error_msg = f"OpenRouter API error: {response.status_code} - {response.text}"
                print(error_msg)
                return None

        except requests.exceptions.Timeout:
            print("OpenRouter API request timed out")
            return None
        except Exception as e:
            print(f"Error calling OpenRouter: {e}")
            return None

    def get_comforting_phrase(self):
        """
        Phase 1: Calls a creative/roleplay model for an empathetic phrase.
        This runs on the Pi's server.
        """
        print("Getting comforting phrase...")

        messages = [
            {
                "role": "system",
                "content": ("You are an empathetic, cute, and slightly quirky Debug Duck. "
                            "A developer is visibly frustrated with their code. "
                            "Your job is to proactively say one short, comforting, "
                            "or funny distracting sentence (less than 15 words) "
                            "to help them reset. DO NOT offer coding help. "
                            "Just be a friend.")
            },
            {"role": "user", "content": "Get me a comforting phrase for a frustrated developer."}
        ]

        response = self._call_openrouter(
            model="deepseek/deepseek-chat",
            messages=messages,
            max_tokens=50,
            temperature=1.2
        )

        return response if response else "You've got this. I believe in you!"

    def get_coding_help(self, code_text):
        """
        Phase 2: Calls a coding model with only OCR'd code.
        This runs on the Laptop client.
        """
        print("Getting coding help for OCR'd text...")

        messages = [
            {
                "role": "system",
                "content": ("You are an expert AI Debug Duck. You are helping a developer. "
                            "You will be given a block of code from their screen. "
                            "Concisely (in 2-3 sentences) identify the most likely bug "
                            "and suggest a fix. Speak in a helpful, friendly tone.")
            },
            {"role": "user", "content": f"Here is the code I'm looking at:\n\n{code_text}"}
        ]

        response = self._call_openrouter(
            model="anthropic/claude-3.5-sonnet",
            messages=messages,
            max_tokens=150,
            temperature=0.3
        )

        return response if response else "Sorry, I had trouble reading that code. Maybe try again?"

    def get_contextual_help(self, code_text, user_question):
        """
        Phase 3: Calls a coding model with BOTH code and a spoken question.
        This runs on the Laptop client.
        """
        print("Getting contextual help for OCR + STT...")

        messages = [
            {
                "role": "system",
                "content": ("You are an expert AI Debug Duck. You are helping a developer. "
                            "You will be given their spoken question AND the code on their screen. "
                            "Directly answer their question, using the code for context. "
                            "Be concise, helpful, and friendly. Speak as a companion.")
            },
            {
                "role": "user",
                "content": (f"My question is: '{user_question}'\n\n"
                            f"Here is the code on my screen:\n{code_text}")
            }
        ]

        response = self._call_openrouter(
            model="anthropic/claude-3.5-sonnet",
            messages=messages,
            max_tokens=150,
            temperature=0.3
        )

        return response if response else "Sorry, I had trouble understanding. Could you ask again?"


# Example usage / testing
if __name__ == "__main__":
    router = LLMRouter()

    # Test Phase 2 (just code)
    print("\n=== Testing Phase 2: Code-only help ===")
    mock_code = "for i in range(len(my_list)):\n    print(my_list[i+1])"
    help_text = router.get_coding_help(mock_code)
    print(f"Duck says: {help_text}")

    # Test Phase 3 (code + question)
    print("\n=== Testing Phase 3: Contextual help ===")
    mock_question = "Why am I getting an 'index out of range' error?"
    contextual_help = router.get_contextual_help(mock_code, mock_question)
    print(f"Duck says: {contextual_help}")
