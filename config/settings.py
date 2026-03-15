import json

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    discord_token: str
    openai_api_key: str
    prompt_path: str = "config/prompt_2025-12-22.txt"
    prompt: str = ""
    servers_config_path: str = "config/servers.json"
    servers: dict = {}

    @property
    def allowed_guilds(self) -> set[int]:
        return {int(g) for g in self.servers.keys()}

    class Config:
        env_file = ".env"


settings = Settings()

with open(settings.prompt_path, "r", encoding="utf-8") as f:
    settings.prompt = f.read()

with open(settings.servers_config_path, "r", encoding="utf-8") as f:
    settings.servers = json.load(f)
