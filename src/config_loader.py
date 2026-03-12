import os
import yaml
from dotenv import load_dotenv

load_dotenv()

def load_config(path="config.yaml"):
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"config.yaml not found. Copy config.yaml.example to config.yaml and fill in your details."
        )
    with open(path, "r") as f:
        raw = f.read()

    # Replace ${ENV_VAR} placeholders with actual env values
    for key, value in os.environ.items():
        raw = raw.replace(f"${{{key}}}", value)

    return yaml.safe_load(raw)


def get_env(key):
    value = os.getenv(key)
    if not value:
        raise EnvironmentError(f"Missing required environment variable: {key}")
    return value