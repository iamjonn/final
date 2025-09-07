from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())

class Configuration:
    _dict_env: dict[str, str] = {}

    @staticmethod
    def load_env():
        """Load environment variables, and those are set at a private dict,
        to access it use Configuration.get('key')"""

        warnings = []
        AWS_ACCESS_KEY_ID: str = os.getenv(
            "AWS_ACCESS_KEY_ID", os.getenv("aws_access_key_id", "")
        )
        AWS_SECRET_ACCESS_KEY: str = os.getenv(
            "AWS_SECRET_ACCESS_KEY", os.getenv("aws_secret_access_key", "")
        )
        AWS_SESSION_TOKEN: str = os.getenv(
            "AWS_SESSION_TOKEN", os.getenv("aws_session_token", "")
        )
        AWS_REGION: str = os.getenv("AWS_REGION", os.getenv("aws_region", "us-east-2"))
        S3_BUCKET: str = os.getenv("S3_BUCKET", "")
        S3_PREFIX: str = os.getenv("S3_PREFIX", "dataset")
        DATASET_DIR: str = os.getenv("DATASET_DIR", "./dataset")
        CHROMA_DIR: str = os.getenv("CHROMA_DIR", "./.chroma")
        TELEGRAM_TOKEN: str = os.getenv("TELEGRAM_TOKEN", "")
        PUBLIC_URL: str = os.getenv("PUBLIC_URL", "")
        WEBHOOK_SECRET: str = os.getenv("WEBHOOK_SECRET", "telegram-webhook")
        LOG_GROUP: str = os.getenv("LOG_GROUP", "/chatbot/rag-telegram")
        MODEL_EMBED: str = os.getenv("MODEL_EMBED", "amazon.titan-embed-text-v2:0")
        MODEL_CHAT: str = os.getenv("MODEL_CHAT", "us.amazon.nova-micro-v1:0")
        Configuration._dict_env = {
            "AWS_ACCESS_KEY_ID": AWS_ACCESS_KEY_ID,
            "AWS_SECRET_ACCESS_KEY": AWS_SECRET_ACCESS_KEY,
            "AWS_SESSION_TOKEN": AWS_SESSION_TOKEN,
            "AWS_REGION": AWS_REGION,
            "S3_BUCKET": S3_BUCKET,
            "S3_PREFIX": S3_PREFIX,
            "DATASET_DIR": DATASET_DIR,
            "CHROMA_DIR": CHROMA_DIR,
            "TELEGRAM_TOKEN": TELEGRAM_TOKEN,
            "PUBLIC_URL": PUBLIC_URL,
            "WEBHOOK_SECRET": WEBHOOK_SECRET,
            "LOG_GROUP": LOG_GROUP,
            "MODEL_EMBED": MODEL_EMBED,
            "MODEL_CHAT": MODEL_CHAT,
        }
        for k, v in Configuration._dict_env.items():
            if v == "":
                warnings.append(f"Warning: {k} is not set")
        return {
            "loaded": True,
            "warnings": warnings,
        }

    @staticmethod
    def get(key: str) -> str:
        return Configuration._dict_env.get(key, "None")


if __name__ == "__main__":
    for k, v in Configuration.load_env().items() and Configuration._dict_env.items():
        print(f"{k}={v}")
