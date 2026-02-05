import requests

from config import Config


class OpenAICompatibleClient:
    """OpenAI兼容接口客户端，支持DeepSeek等API网关。"""

    def __init__(self, api_base=None, api_key=None, timeout=None):
        self.api_base = (api_base or Config.OPENAI_API_BASE).rstrip("/")
        self.api_key = api_key or Config.OPENAI_API_KEY
        self.timeout = timeout or Config.OPENAI_TIMEOUT
        self.session = requests.Session()
        if self.api_key:
            self.session.headers.update({"Authorization": f"Bearer {self.api_key}"})
        self.session.headers.update({"Content-Type": "application/json"})

    def list_models(self):
        return self._request("GET", "/v1/models")

    def chat(self, model, messages, temperature=0.7):
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature
        }
        return self._request("POST", "/v1/chat/completions", payload)

    def _request(self, method, path, payload=None):
        url = f"{self.api_base}{path}"
        response = self.session.request(method, url, json=payload, timeout=self.timeout)
        response.raise_for_status()
        return response.json()
