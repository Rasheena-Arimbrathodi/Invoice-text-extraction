import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Settings:
    app_name: str = "InvoiceFlow"
    app_env: str = os.getenv("APP_ENV", "development")
    tesseract_cmd: str = os.getenv("TESSERACT_CMD", "tesseract")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    default_data_dir: str = os.getenv("DATA_DIR", "data")


settings = Settings()
