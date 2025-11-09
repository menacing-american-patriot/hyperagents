"""
Configuration settings for the HyperAgents trading system.
"""
import os
from typing import Optional
from pydantic import BaseSettings, Field


class OpenAISettings(BaseSettings):
    """OpenAI API configuration with support for custom base URLs."""
    
    api_key: str = Field(..., env="OPENAI_API_KEY")
    base_url: Optional[str] = Field(None, env="OPENAI_BASE_URL")
    model: str = Field("gpt-4", env="OPENAI_MODEL")
    temperature: float = Field(0.1, env="OPENAI_TEMPERATURE")
    max_tokens: int = Field(2000, env="OPENAI_MAX_TOKENS")


class HyperliquidSettings(BaseSettings):
    """Hyperliquid exchange configuration."""
    
    private_key: Optional[str] = Field(None, env="HYPERLIQUID_PRIVATE_KEY")
    testnet: bool = Field(True, env="HYPERLIQUID_TESTNET")
    base_url: str = Field("https://api.hyperliquid.xyz", env="HYPERLIQUID_BASE_URL")


class TradingSettings(BaseSettings):
    """Trading strategy and risk management settings."""
    
    initial_capital: float = Field(1000.0, env="INITIAL_CAPITAL")
    max_position_size: float = Field(0.1, env="MAX_POSITION_SIZE")  # 10% of capital
    max_daily_loss: float = Field(0.05, env="MAX_DAILY_LOSS")  # 5% daily loss limit
    stop_loss_percentage: float = Field(0.02, env="STOP_LOSS_PERCENTAGE")  # 2% stop loss
    take_profit_percentage: float = Field(0.04, env="TAKE_PROFIT_PERCENTAGE")  # 4% take profit


class SystemSettings(BaseSettings):
    """System-wide configuration."""
    
    debug: bool = Field(False, env="DEBUG")
    log_level: str = Field("INFO", env="LOG_LEVEL")
    api_host: str = Field("localhost", env="API_HOST")
    api_port: int = Field(8000, env="API_PORT")
    frontend_url: str = Field("http://localhost:4200", env="FRONTEND_URL")


class Settings(BaseSettings):
    """Main settings class combining all configuration sections."""
    
    openai: OpenAISettings = OpenAISettings()
    hyperliquid: HyperliquidSettings = HyperliquidSettings()
    trading: TradingSettings = TradingSettings()
    system: SystemSettings = SystemSettings()
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()
