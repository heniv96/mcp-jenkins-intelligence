"""Configuration settings for MCP Pipeline Awareness."""

from enum import Enum

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class AIProvider(str, Enum):
    """Supported AI providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


class Settings(BaseSettings):
    """Application settings."""

    # Application
    app_name: str = "MCP Pipeline Awareness"
    app_version: str = "1.0.0"
    debug: bool = Field(default=False, env="DEBUG")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")

    # Jenkins Configuration
    jenkins_url: str = Field(default="https://jenkins.example.com", env="JENKINS_URL")
    jenkins_username: str = Field(default="admin", env="JENKINS_USERNAME")
    jenkins_token: str = Field(default="", env="JENKINS_TOKEN")

    # Jenkins SSL Configuration
    jenkins_verify_ssl: bool = Field(default=True, env="JENKINS_VERIFY_SSL")
    jenkins_ca_cert_path: str | None = Field(default=None, env="JENKINS_CA_CERT_PATH")
    jenkins_client_cert_path: str | None = Field(default=None, env="JENKINS_CLIENT_CERT_PATH")
    jenkins_client_key_path: str | None = Field(default=None, env="JENKINS_CLIENT_KEY_PATH")
    jenkins_timeout: int = Field(default=30, env="JENKINS_TIMEOUT")

    # AI Configuration
    ai_provider: AIProvider = Field(default=AIProvider.OPENAI, env="AI_PROVIDER")
    ai_api_key: str = Field(default="", env="AI_API_KEY")
    ai_model: str = Field(default="gpt-4", env="AI_MODEL")
    ai_temperature: float = Field(default=0.7, env="AI_TEMPERATURE")
    ai_max_tokens: int = Field(default=4000, env="AI_MAX_TOKENS")

    # Pipeline Analysis Configuration
    max_builds_per_pipeline: int = Field(default=100, env="MAX_BUILDS_PER_PIPELINE")
    analysis_timeout: int = Field(default=300, env="ANALYSIS_TIMEOUT")
    cache_ttl: int = Field(default=300, env="CACHE_TTL")  # 5 minutes

    # Export Configuration
    export_formats: list[str] = Field(default=["json", "csv", "html"], env="EXPORT_FORMATS")
    chart_formats: list[str] = Field(default=["png", "svg", "html"], env="CHART_FORMATS")

    # Performance Configuration
    concurrent_requests: int = Field(default=5, env="CONCURRENT_REQUESTS")
    request_timeout: int = Field(default=30, env="REQUEST_TIMEOUT")

    @field_validator("jenkins_url")
    @classmethod
    def validate_jenkins_url(cls, v):
        """Validate Jenkins URL format."""
        if not v.startswith(("http://", "https://")):
            raise ValueError("Jenkins URL must start with http:// or https://")
        return v.rstrip("/")

    @field_validator("ai_api_key")
    @classmethod
    def validate_ai_api_key(cls, v):
        """Validate AI API key is provided."""
        if not v:
            raise ValueError("AI API key is required")
        return v

    @field_validator("jenkins_token")
    @classmethod
    def validate_jenkins_token(cls, v):
        """Validate Jenkins token is provided."""
        if not v:
            raise ValueError("Jenkins token is required")
        return v

    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
_settings: Settings | None = None


def get_settings() -> Settings:
    """Get application settings."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
