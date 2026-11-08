from app.llm.ollama_client import OllamaClient


def test_generate_returns_chat_content(monkeypatch):
    class FakeOllama:
        def __init__(self):
            self.chat_args = None

        def chat(self, **kwargs):
            self.chat_args = kwargs
            return {"message": {"content": "Generated summary"}}

    fake_ollama = FakeOllama()
    created_hosts = []

    def create_client(host):
        created_hosts.append(host)
        return fake_ollama

    monkeypatch.setattr(
        "app.llm.ollama_client.ollama.Client",
        create_client,
    )

    client = OllamaClient(model="llama3.2", host="http://ollama")
    result = client.generate(
        system_prompt="System instructions",
        user_prompt="Summarize the evidence",
    )

    assert result == "Generated summary"
    assert created_hosts == ["http://ollama"]
    assert fake_ollama.chat_args == {
        "model": "llama3.2",
        "messages": [
            {"role": "system", "content": "System instructions"},
            {"role": "user", "content": "Summarize the evidence"},
        ],
        "options": {"temperature": 0.1},
    }
