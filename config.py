import os
from dataclasses import dataclass


@dataclass
class EnvironmentConfig:
    discord_token: str
    discord_client_id: str
    discord_client_secret: str
    discord_redirect_uri: str
    ipc_secret_key: str
    quart_secret_key: str
    database_url: str
    klipy_api_key: str | None
    giphy_api_key: str | None
    log_level: str

    @classmethod
    def from_env(cls) -> "EnvironmentConfig":
        errors: list[str] = []

        discord_token = os.getenv("DISCORD_TOKEN", "")
        if not discord_token:
            errors.append("DISCORD_TOKEN is required")

        discord_client_id = os.getenv("DISCORD_CLIENT_ID", "")
        if not discord_client_id:
            errors.append("DISCORD_CLIENT_ID is required")

        discord_client_secret = os.getenv("DISCORD_CLIENT_SECRET", "")
        if not discord_client_secret:
            errors.append("DISCORD_CLIENT_SECRET is required")

        discord_redirect_uri = os.getenv(
            "DISCORD_REDIRECT_URI", "http://localhost:5000/callback"
        )
        ipc_secret_key = os.getenv("IPC_SECRET_KEY", "")
        if not ipc_secret_key:
            errors.append("IPC_SECRET_KEY is required")

        quart_secret_key = os.getenv("QUART_SECRET_KEY", "")
        if not quart_secret_key:
            errors.append("QUART_SECRET_KEY is required")

        database_url = os.getenv("DATABASE_URL", "sqlite:///bot_data.db")

        klipy_api_key = os.getenv("KLIPY_API_KEY") or None
        giphy_api_key = os.getenv("GIPHY_API_KEY") or None

        log_level = os.getenv("LOG_LEVEL", "INFO")

        if errors:
            raise ValueError(
                f"Missing required environment variables: {', '.join(errors)}"
            )

        return cls(
            discord_token=discord_token,
            discord_client_id=discord_client_id,
            discord_client_secret=discord_client_secret,
            discord_redirect_uri=discord_redirect_uri,
            ipc_secret_key=ipc_secret_key,
            quart_secret_key=quart_secret_key,
            database_url=database_url,
            klipy_api_key=klipy_api_key,
            giphy_api_key=giphy_api_key,
            log_level=log_level,
        )


def validate_environment() -> EnvironmentConfig:
    return EnvironmentConfig.from_env()
