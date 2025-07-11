import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    telegram_token: str
    admin_ids: list[int]
    openai_token: str
    github_token: str


def load_config() -> Config:
    return Config(
        telegram_token=os.getenv("TELEGRAM_TOKEN"),
        admin_ids=[int(admin_id) for admin_id in os.getenv("ADMIN_IDS").split(",")],
        openai_token=os.getenv("OPENAI_TOKEN"),
        github_token=os.getenv("GITHUB_TOKEN"),
    )


config = load_config()