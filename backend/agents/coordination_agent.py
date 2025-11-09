"""
Coordination agent that orchestrates all other agents.
"""
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
from backend.agents.base_agent import BaseAgent
from backend.config.settings import settings


class CoordinationAgent(BaseAgent):
    """Master coordinator that manages all other agents."""
    
    def __init__(self):
        super().__init__(
            name="coordinator",
            description="Master agent that coordinates all trading activities and agent communications"
        )
        self.agents: Dict[str, BaseAgent] = {}
        self.message_queue: List[Dict[str, Any]] = []
        self.trading_session_active = False
        self.daily_pnl = 0.0
        self.total_trades = 0
        
    def register_agent(self, agent: BaseAgent) -> None:
        """Register a new agent with the coordinator."""
        self.agents[agent.name] = agent
        self.logger.info(f"Registered agent: {agent.name}")
    
    async def start_trading_session(self) -> Dict[str, Any]:
        """Start a new trading session."""
        self.trading_session_active = True
        self.daily_pnl = 0.0
        self.total_trades = 0
        
        # Notify all agents that trading session has started
        start_message = {
            "type": "session_start",
            "timestamp": datetime.now().isoformat(),
            "initial_capital": settings.trading.initial_capital
        }
        
        for agent_name in self.agents:
            await self.send_message_to_agent(agent_name, start_message)
        
        self.log_action("start_trading_session", {"capital": settings.trading.initial_capital})
        
        return {
            "status": "started",
            "timestamp": datetime.now().isoformat(),
            "active_agents": list(self.agents.keys())
        }
    
    async def stop_trading_session(self) -> Dict[str, Any]:
        """Stop the current trading session."""
        self.trading_session_active = False
        
        # Notify all agents to stop trading
        stop_message = {
            "type": "session_stop",
            "timestamp": datetime.now().isoformat(),
            "final_pnl": self.daily_pnl,
            "total_trades": self.total_trades
        }
        
        for agent_name in self.agents:
            await self.send_message_to_agent(agent_name, stop_message)
        
        self.log_action("stop_trading_session", {
            "pnl": self.daily_pnl,
            "trades": self.total_trades
        })
        
        return {
            "status": "stopped",
            "timestamp": datetime.now().isoformat(),
            "session_pnl": self.daily_pnl,
            "total_trades": self.total_trades
        }
    
    async def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming messages and coordinate responses."""
        message_type = message.get("type")
        sender = message.get("sender")
        
        if message_type == "trading_signal":
            return await self._handle_trading_signal(message)
        elif message_type == "risk_alert":
            return await self._handle_risk_alert(message)
        elif message_type == "execution_result":
            return await self._handle_execution_result(message)
        elif message_type == "market_update":
            return await self._handle_market_update(message)
        else:
            self.logger.warning(f"Unknown message type: {message_type} from {sender}")
            return {"status": "unknown_message_type"}
    
    async def _handle_trading_signal(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle trading signals from strategy agents."""
        if not self.trading_session_active:
            return {"status": "rejected", "reason": "trading_session_inactive"}
        
        # Forward to risk management for validation
        risk_message = {
            "type": "validate_signal",
            "signal": message,
            "timestamp": datetime.now().isoformat()
        }
        
        if "risk_manager" in self.agents:
            await self.send_message_to_agent("risk_manager", risk_message)
        
        return {"status": "signal_received", "forwarded_to": "risk_manager"}
    
    async def _handle_risk_alert(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle risk alerts and take appropriate action."""
        alert_level = message.get("level", "medium")
        
        if alert_level == "critical":
            # Stop all trading immediately
            await self.stop_trading_session()
            return {"status": "emergency_stop", "reason": message.get("reason")}
        
        return {"status": "alert_acknowledged"}
    
    async def _handle_execution_result(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle trade execution results."""
        result = message.get("result", {})
        if result.get("status") == "filled":
            self.total_trades += 1
            pnl = result.get("pnl", 0)
            self.daily_pnl += pnl
        
        return {"status": "execution_logged"}
    
    async def _handle_market_update(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle market data updates."""
        # Broadcast to all interested agents
        for agent_name in ["market_analyst", "strategy_agent"]:
            if agent_name in self.agents:
                await self.send_message_to_agent(agent_name, message)
        
        return {"status": "market_update_broadcasted"}
    
    async def get_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        agent_statuses = {}
        for name, agent in self.agents.items():
            agent_statuses[name] = await agent.get_status()
        
        return {
            **self.get_base_status(),
            "trading_session_active": self.trading_session_active,
            "daily_pnl": self.daily_pnl,
            "total_trades": self.total_trades,
            "registered_agents": list(self.agents.keys()),
            "agent_statuses": agent_statuses
        }
