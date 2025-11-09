"""
Execution agent for handling trade execution and order management.
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
import asyncio
from backend.agents.base_agent import BaseAgent
from backend.hyperliquid.client import HyperliquidClient
from backend.config.settings import settings


class ExecutionAgent(BaseAgent):
    """Agent responsible for executing trades and managing orders."""
    
    def __init__(self):
        super().__init__(
            name="execution_agent",
            description="Executes trades, manages orders, and monitors positions"
        )
        self.hyperliquid_client = HyperliquidClient()
        self.active_orders: Dict[str, Dict[str, Any]] = {}
        self.executed_trades: List[Dict[str, Any]] = []
        self.position_monitor_active = False
        
    async def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming execution messages."""
        message_type = message.get("type")
        
        if message_type == "execute_trade":
            return await self.execute_trade(message.get("trade_params", {}))
        elif message_type == "cancel_order":
            return await self.cancel_order(message.get("order_id"), message.get("symbol"))
        elif message_type == "get_positions":
            return await self.get_current_positions()
        elif message_type == "monitor_positions":
            return await self.start_position_monitoring()
        else:
            return {"status": "unknown_message_type"}
    
    async def execute_trade(self, trade_params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a trade based on validated parameters."""
        try:
            symbol = trade_params.get("symbol")
            action = trade_params.get("action")
            size = trade_params.get("size")
            order_type = trade_params.get("order_type", "Market")
            price = trade_params.get("price")
            
            if not all([symbol, action, size]):
                return {"status": "error", "reason": "missing_required_parameters"}
            
            # Convert action to side
            side = "buy" if action == "BUY" else "sell"
            
            # Execute the order
            order_result = await self.hyperliquid_client.place_order(
                symbol=symbol,
                side=side,
                size=size,
                order_type=order_type,
                price=price
            )
            
            # Track the order
            order_id = order_result.get("response", {}).get("data", {}).get("statuses", [{}])[0].get("resting", {}).get("oid")
            
            if order_id:
                self.active_orders[order_id] = {
                    "symbol": symbol,
                    "side": side,
                    "size": size,
                    "order_type": order_type,
                    "price": price,
                    "timestamp": datetime.now().isoformat(),
                    "status": "pending",
                    "strategy_id": trade_params.get("strategy_id"),
                    "original_params": trade_params
                }
            
            # Set up stop loss and take profit if specified
            if trade_params.get("stop_loss"):
                await self._set_stop_loss(symbol, side, size, trade_params["stop_loss"])
            
            if trade_params.get("take_profit"):
                await self._set_take_profit(symbol, side, size, trade_params["take_profit"])
            
            execution_result = {
                "status": "executed",
                "order_id": order_id,
                "symbol": symbol,
                "side": side,
                "size": size,
                "order_result": order_result,
                "timestamp": datetime.now().isoformat()
            }
            
            # Log the execution
            self.executed_trades.append(execution_result)
            
            self.log_action("trade_executed", {
                "symbol": symbol,
                "side": side,
                "size": size,
                "order_id": order_id
            })
            
            # Notify other agents
            await self._notify_execution_result(execution_result, trade_params)
            
            return execution_result
            
        except Exception as e:
            self.logger.error(f"Error executing trade: {e}")
            return {"status": "error", "reason": str(e)}
    
    async def _set_stop_loss(self, symbol: str, original_side: str, size: float, stop_loss_params: Dict[str, Any]) -> None:
        """Set up stop loss order."""
        try:
            # Calculate stop loss price
            market_data = await self.hyperliquid_client.get_market_data(symbol)
            current_price = market_data["price"]
            
            stop_loss_pct = stop_loss_params.get("percentage", settings.trading.stop_loss_percentage)
            
            if original_side == "buy":
                stop_price = current_price * (1 - stop_loss_pct)
                stop_side = "sell"
            else:
                stop_price = current_price * (1 + stop_loss_pct)
                stop_side = "buy"
            
            # Place stop loss order
            stop_order = await self.hyperliquid_client.place_order(
                symbol=symbol,
                side=stop_side,
                size=size,
                order_type="Limit",
                price=stop_price
            )
            
            self.logger.info(f"Stop loss set for {symbol} at {stop_price}")
            
        except Exception as e:
            self.logger.error(f"Error setting stop loss: {e}")
    
    async def _set_take_profit(self, symbol: str, original_side: str, size: float, take_profit_params: Dict[str, Any]) -> None:
        """Set up take profit order."""
        try:
            # Calculate take profit price
            market_data = await self.hyperliquid_client.get_market_data(symbol)
            current_price = market_data["price"]
            
            take_profit_pct = take_profit_params.get("percentage", settings.trading.take_profit_percentage)
            
            if original_side == "buy":
                take_profit_price = current_price * (1 + take_profit_pct)
                take_profit_side = "sell"
            else:
                take_profit_price = current_price * (1 - take_profit_pct)
                take_profit_side = "buy"
            
            # Place take profit order
            tp_order = await self.hyperliquid_client.place_order(
                symbol=symbol,
                side=take_profit_side,
                size=size,
                order_type="Limit",
                price=take_profit_price
            )
            
            self.logger.info(f"Take profit set for {symbol} at {take_profit_price}")
            
        except Exception as e:
            self.logger.error(f"Error setting take profit: {e}")
    
    async def cancel_order(self, order_id: str, symbol: str) -> Dict[str, Any]:
        """Cancel an existing order."""
        try:
            result = await self.hyperliquid_client.cancel_order(order_id, symbol)
            
            # Update order status
            if order_id in self.active_orders:
                self.active_orders[order_id]["status"] = "cancelled"
                self.active_orders[order_id]["cancelled_at"] = datetime.now().isoformat()
            
            self.log_action("order_cancelled", {"order_id": order_id, "symbol": symbol})
            
            return {
                "status": "cancelled",
                "order_id": order_id,
                "result": result
            }
            
        except Exception as e:
            self.logger.error(f"Error cancelling order {order_id}: {e}")
            return {"status": "error", "reason": str(e)}
    
    async def get_current_positions(self) -> Dict[str, Any]:
        """Get current account positions."""
        try:
            account_info = await self.hyperliquid_client.get_account_info()
            positions = account_info.get("positions", [])
            
            # Format positions for easier consumption
            formatted_positions = []
            for position in positions:
                if float(position.get("szi", 0)) != 0:  # Only non-zero positions
                    formatted_positions.append({
                        "symbol": position.get("coin"),
                        "size": float(position.get("szi", 0)),
                        "entry_price": float(position.get("entryPx", 0)),
                        "unrealized_pnl": float(position.get("unrealizedPnl", 0)),
                        "position_value": float(position.get("positionValue", 0))
                    })
            
            return {
                "positions": formatted_positions,
                "total_positions": len(formatted_positions),
                "account_info": account_info,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting positions: {e}")
            return {"status": "error", "reason": str(e)}
    
    async def start_position_monitoring(self) -> Dict[str, Any]:
        """Start monitoring positions for risk management."""
        if self.position_monitor_active:
            return {"status": "already_monitoring"}
        
        self.position_monitor_active = True
        
        # Start background task for position monitoring
        asyncio.create_task(self._position_monitor_loop())
        
        return {"status": "monitoring_started"}
    
    async def _position_monitor_loop(self) -> None:
        """Background loop for monitoring positions."""
        while self.position_monitor_active:
            try:
                positions_data = await self.get_current_positions()
                positions = positions_data.get("positions", [])
                
                for position in positions:
                    await self._check_position_risk(position)
                
                # Check every 30 seconds
                await asyncio.sleep(30)
                
            except Exception as e:
                self.logger.error(f"Error in position monitoring: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def _check_position_risk(self, position: Dict[str, Any]) -> None:
        """Check individual position for risk management."""
        symbol = position["symbol"]
        unrealized_pnl = position["unrealized_pnl"]
        position_value = position["position_value"]
        
        # Calculate percentage loss
        if position_value != 0:
            pnl_percentage = unrealized_pnl / abs(position_value)
            
            # Check if stop loss should be triggered
            if pnl_percentage <= -settings.trading.stop_loss_percentage:
                self.logger.warning(f"Stop loss triggered for {symbol}: {pnl_percentage:.2%}")
                
                # Send alert to risk manager
                alert_message = {
                    "type": "position_alert",
                    "symbol": symbol,
                    "pnl_percentage": pnl_percentage,
                    "unrealized_pnl": unrealized_pnl,
                    "action_required": "close_position"
                }
                
                await self.send_message_to_agent("risk_manager", alert_message)
    
    async def _notify_execution_result(self, execution_result: Dict[str, Any], original_params: Dict[str, Any]) -> None:
        """Notify other agents about execution results."""
        # Notify coordinator
        coordinator_message = {
            "type": "execution_result",
            "result": execution_result,
            "original_params": original_params
        }
        await self.send_message_to_agent("coordinator", coordinator_message)
        
        # Notify risk manager
        risk_message = {
            "type": "position_update",
            "symbol": execution_result["symbol"],
            "side": execution_result["side"],
            "size": execution_result["size"]
        }
        await self.send_message_to_agent("risk_manager", risk_message)
        
        # Notify strategy agent if strategy_id is present
        strategy_id = original_params.get("strategy_id")
        if strategy_id:
            strategy_message = {
                "type": "execution_confirmation",
                "strategy_id": strategy_id,
                "execution_result": execution_result
            }
            await self.send_message_to_agent("strategy_agent", strategy_message)
    
    async def get_status(self) -> Dict[str, Any]:
        """Get current execution agent status."""
        return {
            **self.get_base_status(),
            "active_orders": len(self.active_orders),
            "executed_trades": len(self.executed_trades),
            "position_monitor_active": self.position_monitor_active,
            "recent_trades": self.executed_trades[-5:] if self.executed_trades else []
        }
