import ollama


class OllamaClient:

    def __init__(
        self,
        model: str = "llama3.2",
        host: str = "http://localhost:11434",
    ):
        self.model = model
        self.client = ollama.Client(host=host)

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> str:

        response = self.client.chat(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
            options={
                "temperature": 0.1,
            },
        )

        return response["message"]["content"]

    def generate_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        output_schema: dict,
    ) -> str:

        response = self.client.chat(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
            format=output_schema,
            options={
                "temperature": 0.1,
            },
        )

        return response["message"]["content"]