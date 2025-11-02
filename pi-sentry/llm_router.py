"""
LLM Router for Debug Duck Pi-Sentry
Uses OpenRouter to get comforting phrases for emotional support
"""

import requests
import os
from dotenv import load_dotenv
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Get API key from environment
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

# OpenRouter API endpoint
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Your app URL for OpenRouter identification
YOUR_APP_URL = "http://github.com/debug-duck/pi-sentry"


class LLMRouter:
    """
    Routes requests to appropriate LLM models via OpenRouter
    Used for generating comforting phrases when frustration is detected
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
        logger.info("LLMRouter initialized successfully")

    def _call_openrouter(self, model, messages, max_tokens=150, temperature=0.3):
        """
        Internal method to call OpenRouter API

        Args:
            model (str): The model identifier
            messages (list): List of message dictionaries
            max_tokens (int): Maximum tokens in response
            temperature (float): Temperature for response generation

        Returns:
            str: The model's response text, or None on error
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
                logger.error(error_msg)
                return None

        except requests.exceptions.Timeout:
            logger.error("OpenRouter API request timed out")
            return None
        except Exception as e:
            logger.error(f"Error calling OpenRouter: {e}")
            return None

    def get_comforting_phrase(self):
        """
        Phase 1: Calls a creative/roleplay model for an empathetic phrase.
        This is used when FER detects frustration.

        Returns:
            str: A comforting phrase from the duck
        """
        logger.info("Getting comforting phrase from LLM...")

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
            temperature=1.2  # High temperature for creative/varied responses
        )

        if response:
            logger.info(f"LLM responded: {response}")
            return response
        else:
            # Fallback phrases if LLM fails
            fallback_phrases = [
                "You've got this. I believe in you!",
                "Hey, take a deep breath. Every bug has a solution!",
                "Sometimes the best debugging happens after a short break.",
                "You're smarter than this bug. Trust yourself!",
                "Quack! Remember, even the best coders hit walls sometimes."
            ]
            import random
            fallback = random.choice(fallback_phrases)
            logger.warning(f"LLM failed, using fallback: {fallback}")
            return fallback


# Test the LLM router
if __name__ == "__main__":
    try:
        router = LLMRouter()

        print("\n=== Testing LLM Router ===")
        print("Getting comforting phrase...")

        phrase = router.get_comforting_phrase()
        print(f"\nDuck says: {phrase}")

    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure:")
        print("1. .env file exists in this directory")
        print("2. OPENROUTER_API_KEY is set in .env")
        print("3. You have internet connection")
