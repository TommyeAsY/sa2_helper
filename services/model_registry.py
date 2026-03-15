from dataclasses import dataclass

import requests

from config.settings import settings


@dataclass
class ModelInfo:
    index: int
    name: str
    model_id: str
    context_length: int


class ModelRegistry:
    MODELS_URL = "https://openrouter.ai/api/v1/models"

    def __init__(self):
        self.api_key = settings.openai_api_key
        self.models: list[ModelInfo] = []
        self.current_model: ModelInfo | None = None

    def fetch_models(self) -> None:
        headers = {"Authorization": f"Bearer {self.api_key}"}
        response = requests.get(self.MODELS_URL, headers=headers)
        response.raise_for_status()

        data = response.json().get("data", [])

        free_models = []
        for m in data:
            name = m["name"]
            if not name.endswith("(free)"):
                continue

            clean_name = name.replace("(free)", "").strip()

            free_models.append(
                (clean_name, m["id"], m["context_length"])
            )

        free_models.sort(key=lambda x: x[2], reverse=True)

        self.models = [
            ModelInfo(
                index=i,
                name=name,
                model_id=model_id,
                context_length=context,
            )
            for i, (name, model_id, context) in enumerate(free_models, start=1)
        ]

        qwen_models = [m for m in self.models if "qwen" in m.model_id.lower()]

        if qwen_models:
            self.current_model = qwen_models[0]
        else:
            self.current_model = self.models[0] if self.models else None

        print(f"{'№':>3} | {'Model name':40} | {'ID':46} | {'Context'}")
        print("-" * 105)
        for m in self.models:
            print(f"{m.index:3} | {m.name:40} | {m.model_id:46} | {m.context_length}")

        if self.current_model:
            print(f"\nSelected model: {self.current_model.name} ({self.current_model.model_id})")

    def switch_model(self, index: int) -> bool:
        for m in self.models:
            if m.index == index:
                self.current_model = m
                print(f"Switched model to: {m.name} ({m.model_id})")
                return True
        return False

    def get_current_model(self) -> ModelInfo | None:
        return self.current_model

    def get_models(self) -> list[ModelInfo]:
        return self.models
