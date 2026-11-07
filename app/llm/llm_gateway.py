from app.llm.ollama_client import OllamaClient


class LLMGateway:

    def __init__(self):
        self.client = OllamaClient(
            model="llama3.2",
        )

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> dict:

        content = self.client.generate(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )

        return {
            "content": content,
            "model": self.client.model,
            "provider": "ollama",
        }