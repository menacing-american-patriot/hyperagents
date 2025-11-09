"""
Risk management agent for position sizing and risk control.
"""
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import math
from backend.agents.base_agent import BaseAgent
from backend.hyperliquid.client import HyperliquidClient
from backend.config.settings import settings


class RiskManagementAgent(BaseAgent):
    """Agent responsible for risk assessment and position management."""
    
    def __init__(self):
        super().__init__(
            name="risk_manager",
            description="Manages trading risk, position sizing, and portfolio protection"
        )
        self.hyperliquid_client = HyperliquidClient()
        self.daily_loss = 0.0
        self.daily_trades = 0
        self.max_daily_trades = 50
        self.position_limits: Dict[str, float] = {}
        self.active_positions: Dict[str, Dict[str, Any]] = {}
        
    async def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming risk-related messages."""
        message_type = message.get("type")
        
        if message_type == "validate_signal":
            return await self.validate_trading_signal(message.get("signal", {}))
        elif message_type == "position_update":
            return await self._handle_position_update(message)
        elif message_type == "check_risk_limits":
            return await self.check_risk_limits()
        elif message_type == "calculate_position_size":
            return await self.calculate_position_size(message)
        else:
            return {"status": "unknown_message_type"}
    
    async def validate_trading_signal(self, signal: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a trading signal against risk parameters."""
        try:
            symbol = signal.get("symbol")
            action = signal.get("action")
            confidence = signal.get("confidence", 0.5)
            
            if not symbol or not action:
                return {"status": "rejected", "reason": "missing_signal_data"}
            
            # Check daily loss limits
            if self.daily_loss >= settings.trading.max_daily_loss * settings.trading.initial_capital:
                return {
                    "status": "rejected", 
                    "reason": "daily_loss_limit_exceeded",
                    "daily_loss": self.daily_loss
                }
            
            # Check daily trade limits
            if self.daily_trades >= self.max_daily_trades:
                return {
                    "status": "rejected",
                    "reason": "daily_trade_limit_exceeded",
                    "daily_trades": self.daily_trades
                }
            
            # Check position limits
            current_exposure = await self._get_symbol_exposure(symbol)
            max_position = settings.trading.max_position_size * settings.trading.initial_capital
            
            if action in ["BUY", "SELL"] and current_exposure >= max_position:
                return {
                    "status": "rejected",
                    "reason": "position_limit_exceeded",
                    "current_exposure": current_exposure,
                    "max_position": max_position
                }
            
            # Calculate recommended position size
            position_size = await self._calculate_optimal_position_size(symbol, action, confidence)
            
            # Generate risk assessment
            risk_assessment = await self._assess_trade_risk(symbol, action, position_size)
            
            validation_result = {
                "status": "approved",
                "symbol": symbol,
                "action": action,
                "recommended_size": position_size,
                "risk_assessment": risk_assessment,
                "stop_loss": self._calculate_stop_loss(symbol, action),
                "take_profit": self._calculate_take_profit(symbol, action),
                "timestamp": datetime.now().isoformat()
            }
            
            self.log_action("signal_validation", {
                "symbol": symbol,
                "action": action,
                "status": "approved",
                "size": position_size
            })
            
            return validation_result
            
        except Exception as e:
            self.logger.error(f"Error validating signal: {e}")
            return {"status": "error", "reason": str(e)}
    
    async def _get_symbol_exposure(self, symbol: str) -> float:
        """Get current exposure for a symbol."""
        try:
            account_info = await self.hyperliquid_client.get_account_info()
            positions = account_info.get("positions", [])
            
            total_exposure = 0.0
            for position in positions:
                if position.get("coin") == symbol:
                    size = float(position.get("szi", 0))
                    total_exposure += abs(size)
            
            return total_exposure
            
        except Exception as e:
            self.logger.error(f"Error getting exposure for {symbol}: {e}")
            return 0.0
    
    async def _calculate_optimal_position_size(self, symbol: str, action: str, confidence: float) -> float:
        """Calculate optimal position size based on risk parameters."""
        try:
            # Get current market data
            market_data = await self.hyperliquid_client.get_market_data(symbol)
            current_price = market_data["price"]
            
            # Base position size as percentage of capital
            base_size_usd = settings.trading.initial_capital * settings.trading.max_position_size
            
            # Adjust based on confidence
            confidence_multiplier = min(confidence * 2, 1.0)  # Scale confidence to 0-1
            adjusted_size_usd = base_size_usd * confidence_multiplier
            
            # Convert to symbol units
            position_size = adjusted_size_usd / current_price
            
            # Apply additional risk scaling based on volatility
            # (This would be enhanced with actual volatility calculations)
            volatility_adjustment = 0.8  # Conservative default
            final_size = position_size * volatility_adjustment
            
            return round(final_size, 6)
            
        except Exception as e:
            self.logger.error(f"Error calculating position size: {e}")
            return 0.0
    
    async def _assess_trade_risk(self, symbol: str, action: str, size: float) -> Dict[str, Any]:
        """Assess the risk of a proposed trade."""
        try:
            market_data = await self.hyperliquid_client.get_market_data(symbol)
            current_price = market_data["price"]
            
            # Calculate potential loss with stop loss
            stop_loss_pct = settings.trading.stop_loss_percentage
            max_loss_usd = size * current_price * stop_loss_pct
            
            # Calculate risk as percentage of capital
            risk_percentage = max_loss_usd / settings.trading.initial_capital
            
            # Risk level classification
            if risk_percentage < 0.01:
                risk_level = "low"
            elif risk_percentage < 0.03:
                risk_level = "medium"
            else:
                risk_level = "high"
            
            return {
                "risk_level": risk_level,
                "risk_percentage": risk_percentage,
                "max_loss_usd": max_loss_usd,
                "position_value_usd": size * current_price,
                "stop_loss_percentage": stop_loss_pct
            }
            
        except Exception as e:
            self.logger.error(f"Error assessing trade risk: {e}")
            return {"risk_level": "unknown", "error": str(e)}
    
    def _calculate_stop_loss(self, symbol: str, action: str) -> Dict[str, Any]:
        """Calculate stop loss parameters."""
        stop_loss_pct = settings.trading.stop_loss_percentage
        
        return {
            "type": "percentage",
            "percentage": stop_loss_pct,
            "side": "sell" if action == "BUY" else "buy"
        }
    
    def _calculate_take_profit(self, symbol: str, action: str) -> Dict[str, Any]:
        """Calculate take profit parameters."""
        take_profit_pct = settings.trading.take_profit_percentage
        
        return {
            "type": "percentage", 
            "percentage": take_profit_pct,
            "side": "sell" if action == "BUY" else "buy"
        }
    
    async def check_risk_limits(self) -> Dict[str, Any]:
        """Check all current risk limits and positions."""
        try:
            account_info = await self.hyperliquid_client.get_account_info()
            
            # Calculate total exposure
            total_exposure = 0.0
            positions = account_info.get("positions", [])
            
            for position in positions:
                size = float(position.get("szi", 0))
                # This would need the current price to calculate USD value
                total_exposure += abs(size)  # Simplified
            
            # Check against limits
            max_total_exposure = settings.trading.initial_capital * 0.8  # 80% max exposure
            
            risk_status = {
                "total_exposure": total_exposure,
                "max_exposure": max_total_exposure,
                "exposure_percentage": total_exposure / settings.trading.initial_capital,
                "daily_loss": self.daily_loss,
                "daily_trades": self.daily_trades,
                "within_limits": total_exposure <= max_total_exposure and 
                               self.daily_loss <= settings.trading.max_daily_loss * settings.trading.initial_capital,
                "timestamp": datetime.now().isoformat()
            }
            
            if not risk_status["within_limits"]:
                self.log_action("risk_limit_breach", risk_status)
                
                # Send alert to coordinator
                alert_message = {
                    "type": "risk_alert",
                    "level": "critical" if total_exposure > max_total_exposure * 1.2 else "warning",
                    "reason": "risk_limits_exceeded",
                    "details": risk_status
                }
                await self.send_message_to_agent("coordinator", alert_message)
            
            return risk_status
            
        except Exception as e:
            self.logger.error(f"Error checking risk limits: {e}")
            return {"error": str(e)}
    
    async def _handle_position_update(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle position updates from execution agent."""
        symbol = message.get("symbol")
        pnl = message.get("pnl", 0.0)
        
        if pnl < 0:
            self.daily_loss += abs(pnl)
        
        self.daily_trades += 1
        
        return {"status": "position_update_processed"}
    
    async def get_status(self) -> Dict[str, Any]:
        """Get current risk management status."""
        return {
            **self.get_base_status(),
            "daily_loss": self.daily_loss,
            "daily_trades": self.daily_trades,
            "max_daily_trades": self.max_daily_trades,
            "active_positions": len(self.active_positions),
            "risk_limits_status": await self.check_risk_limits()
        }
