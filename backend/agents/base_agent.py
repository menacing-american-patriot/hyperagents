"""
Base agent class for the HyperAgents trading system.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from datetime import datetime
import logging
from langchain.agents import AgentExecutor
from langchain.schema import BaseMessage
from langchain_openai import ChatOpenAI
from backend.config.settings import settings


class BaseAgent(ABC):
    """Abstract base class for all trading agents."""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.logger = logging.getLogger(f"agents.{name}")
        self.created_at = datetime.now()
        self.last_action_at: Optional[datetime] = None
        self.message_history: List[BaseMessage] = []
        
        # Initialize OpenAI client with custom base URL support
        self.llm = ChatOpenAI(
            api_key=settings.openai.api_key,
            base_url=settings.openai.base_url,
            model=settings.openai.model,
            temperature=settings.openai.temperature,
            max_tokens=settings.openai.max_tokens
        )
        
        self.logger.info(f"Initialized {self.name} agent")
    
    @abstractmethod
    async def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Process an incoming message and return a response."""
        pass
    
    @abstractmethod
    async def get_status(self) -> Dict[str, Any]:
        """Get the current status of the agent."""
        pass
    
    async def send_message_to_agent(self, target_agent: str, message: Dict[str, Any]) -> None:
        """Send a message to another agent."""
        # This will be implemented by the coordination system
        self.logger.info(f"Sending message to {target_agent}: {message}")
    
    def log_action(self, action: str, details: Dict[str, Any] = None) -> None:
        """Log an action taken by the agent."""
        self.last_action_at = datetime.now()
        log_data = {
            "agent": self.name,
            "action": action,
            "timestamp": self.last_action_at.isoformat(),
            "details": details or {}
        }
        self.logger.info(f"Action: {action}", extra=log_data)
    
    def get_base_status(self) -> Dict[str, Any]:
        """Get base status information common to all agents."""
        return {
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "last_action_at": self.last_action_at.isoformat() if self.last_action_at else None,
            "message_count": len(self.message_history)
        }
