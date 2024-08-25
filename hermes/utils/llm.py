from typing import Dict, Any
from litellm import completion
from hermes.config import CONFIG

class LLMProcessor:
    def __init__(self):
        self.config = CONFIG['llm']
        if not self.config['api_key']:
            raise ValueError(f"API key for {self.config['provider']} is required. Set it in config.yml or as an environment variable.")

    def process(self, text: str, prompt: str, **kwargs) -> str:
        """
        Process the given text with a language model using the provided prompt.

        :param text: The text to process (e.g., transcription)
        :param prompt: The prompt to send to the language model
        :param kwargs: Additional arguments for the LLM API call
        :return: The processed result from the language model
        """
        full_prompt = f"{prompt}\n\nText: {text}"
        
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": full_prompt}
        ]

        # Use a valid model string format
        model = f"{self.config['provider']}/{self.config['model']}"

        response = completion(
            model=model,
            messages=messages,
            api_key=self.config['api_key'],
            **kwargs
        )

        return response.choices[0].message.content.strip()