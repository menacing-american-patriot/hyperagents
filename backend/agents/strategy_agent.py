"""
Strategy agent for developing and executing trading strategies.
"""
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
from backend.agents.base_agent import BaseAgent
from backend.config.settings import settings


class StrategyAgent(BaseAgent):
    """Agent responsible for developing and executing trading strategies."""
    
    def __init__(self):
        super().__init__(
            name="strategy_agent",
            description="Develops adaptive trading strategies and coordinates execution"
        )
        self.active_strategies: Dict[str, Dict[str, Any]] = {}
        self.strategy_performance: Dict[str, Dict[str, Any]] = {}
        self.market_regime = "neutral"  # bull, bear, neutral, volatile
        
    async def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming strategy-related messages."""
        message_type = message.get("type")
        
        if message_type == "market_analysis":
            return await self._process_market_analysis(message)
        elif message_type == "develop_strategy":
            return await self.develop_strategy(message.get("parameters", {}))
        elif message_type == "execute_strategy":
            return await self.execute_strategy(message.get("strategy_id"))
        elif message_type == "update_performance":
            return await self._update_strategy_performance(message)
        else:
            return {"status": "unknown_message_type"}
    
    async def develop_strategy(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Develop a new trading strategy based on current market conditions."""
        try:
            # Use AI to analyze market conditions and develop strategy
            strategy_prompt = f"""
            Develop a trading strategy for the current market conditions.
            
            Market regime: {self.market_regime}
            Available capital: ${settings.trading.initial_capital}
            Risk tolerance: {settings.trading.max_daily_loss * 100}% daily loss limit
            
            Consider:
            1. Current market volatility and trends
            2. Risk management principles
            3. Position sizing strategies
            4. Entry and exit criteria
            5. Timeframe and holding periods
            
            Provide a detailed strategy with:
            - Strategy name and description
            - Entry conditions
            - Exit conditions
            - Risk management rules
            - Expected performance metrics
            """
            
            response = await self.llm.ainvoke([{"role": "user", "content": strategy_prompt}])
            ai_strategy = response.content
            
            # Create structured strategy object
            strategy_id = f"strategy_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            strategy = {
                "id": strategy_id,
                "name": f"AI Strategy {strategy_id[-6:]}",
                "description": ai_strategy,
                "created_at": datetime.now().isoformat(),
                "market_regime": self.market_regime,
                "parameters": {
                    "max_position_size": settings.trading.max_position_size,
                    "stop_loss": settings.trading.stop_loss_percentage,
                    "take_profit": settings.trading.take_profit_percentage,
                    "timeframe": parameters.get("timeframe", "1h"),
                    "symbols": parameters.get("symbols", ["BTC", "ETH"])
                },
                "entry_conditions": self._extract_entry_conditions(ai_strategy),
                "exit_conditions": self._extract_exit_conditions(ai_strategy),
                "risk_rules": self._extract_risk_rules(ai_strategy),
                "status": "active",
                "performance": {
                    "total_trades": 0,
                    "winning_trades": 0,
                    "total_pnl": 0.0,
                    "max_drawdown": 0.0,
                    "sharpe_ratio": 0.0
                }
            }
            
            self.active_strategies[strategy_id] = strategy
            
            self.log_action("strategy_developed", {
                "strategy_id": strategy_id,
                "market_regime": self.market_regime
            })
            
            return {
                "status": "strategy_created",
                "strategy": strategy
            }
            
        except Exception as e:
            self.logger.error(f"Error developing strategy: {e}")
            return {"status": "error", "reason": str(e)}
    
    def _extract_entry_conditions(self, ai_strategy: str) -> List[str]:
        """Extract entry conditions from AI-generated strategy."""
        # Simplified extraction - in production, use more sophisticated NLP
        conditions = []
        
        if "rsi" in ai_strategy.lower():
            conditions.append("RSI-based signals")
        if "moving average" in ai_strategy.lower():
            conditions.append("Moving average crossover")
        if "breakout" in ai_strategy.lower():
            conditions.append("Price breakout patterns")
        if "volume" in ai_strategy.lower():
            conditions.append("Volume confirmation")
        
        return conditions if conditions else ["Market analysis confirmation"]
    
    def _extract_exit_conditions(self, ai_strategy: str) -> List[str]:
        """Extract exit conditions from AI-generated strategy."""
        conditions = []
        
        if "stop loss" in ai_strategy.lower():
            conditions.append("Stop loss triggered")
        if "take profit" in ai_strategy.lower():
            conditions.append("Take profit target")
        if "trailing" in ai_strategy.lower():
            conditions.append("Trailing stop")
        if "time" in ai_strategy.lower():
            conditions.append("Time-based exit")
        
        return conditions if conditions else ["Risk management rules"]
    
    def _extract_risk_rules(self, ai_strategy: str) -> List[str]:
        """Extract risk management rules from AI-generated strategy."""
        rules = [
            f"Maximum {settings.trading.max_position_size * 100}% position size",
            f"Stop loss at {settings.trading.stop_loss_percentage * 100}%",
            f"Daily loss limit {settings.trading.max_daily_loss * 100}%"
        ]
        
        if "diversification" in ai_strategy.lower():
            rules.append("Portfolio diversification required")
        if "correlation" in ai_strategy.lower():
            rules.append("Asset correlation monitoring")
        
        return rules
    
    async def execute_strategy(self, strategy_id: str) -> Dict[str, Any]:
        """Execute a specific trading strategy."""
        if strategy_id not in self.active_strategies:
            return {"status": "error", "reason": "strategy_not_found"}
        
        strategy = self.active_strategies[strategy_id]
        
        try:
            # Get current market analysis
            market_message = {
                "type": "get_signals",
                "timestamp": datetime.now().isoformat()
            }
            
            # This would be sent to market analysis agent
            # For now, simulate getting signals
            signals = await self._get_market_signals()
            
            # Apply strategy logic to signals
            strategy_decisions = await self._apply_strategy_logic(strategy, signals)
            
            # Send decisions to coordinator for execution
            for decision in strategy_decisions:
                execution_message = {
                    "type": "trading_signal",
                    "sender": self.name,
                    "strategy_id": strategy_id,
                    "signal": decision,
                    "timestamp": datetime.now().isoformat()
                }
                
                await self.send_message_to_agent("coordinator", execution_message)
            
            self.log_action("strategy_executed", {
                "strategy_id": strategy_id,
                "decisions_count": len(strategy_decisions)
            })
            
            return {
                "status": "strategy_executed",
                "strategy_id": strategy_id,
                "decisions": strategy_decisions
            }
            
        except Exception as e:
            self.logger.error(f"Error executing strategy {strategy_id}: {e}")
            return {"status": "error", "reason": str(e)}
    
    async def _get_market_signals(self) -> Dict[str, Any]:
        """Get current market signals (placeholder)."""
        # This would interface with the market analysis agent
        return {
            "BTC": {"action": "BUY", "confidence": 0.7, "price": 45000},
            "ETH": {"action": "HOLD", "confidence": 0.5, "price": 3000}
        }
    
    async def _apply_strategy_logic(self, strategy: Dict[str, Any], signals: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Apply strategy logic to market signals."""
        decisions = []
        
        strategy_symbols = strategy["parameters"]["symbols"]
        
        for symbol in strategy_symbols:
            if symbol in signals:
                signal = signals[symbol]
                
                # Apply strategy-specific filters and logic
                if self._meets_entry_conditions(strategy, signal):
                    decision = {
                        "symbol": symbol,
                        "action": signal["action"],
                        "confidence": signal["confidence"],
                        "strategy_id": strategy["id"],
                        "reasoning": f"Strategy {strategy['name']} entry conditions met"
                    }
                    decisions.append(decision)
        
        return decisions
    
    def _meets_entry_conditions(self, strategy: Dict[str, Any], signal: Dict[str, Any]) -> bool:
        """Check if signal meets strategy entry conditions."""
        # Simplified logic - in production, implement sophisticated strategy rules
        confidence_threshold = 0.6
        
        if signal["confidence"] < confidence_threshold:
            return False
        
        if signal["action"] == "HOLD":
            return False
        
        # Additional strategy-specific conditions would go here
        return True
    
    async def _process_market_analysis(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Process market analysis updates."""
        analysis = message.get("analysis", {})
        
        # Update market regime based on analysis
        if "trend" in analysis:
            trend = analysis["trend"]
            if trend == "bullish":
                self.market_regime = "bull"
            elif trend == "bearish":
                self.market_regime = "bear"
            else:
                self.market_regime = "neutral"
        
        # Trigger strategy adaptation if needed
        await self._adapt_strategies_to_market()
        
        return {"status": "market_analysis_processed"}
    
    async def _adapt_strategies_to_market(self) -> None:
        """Adapt active strategies to current market conditions."""
        for strategy_id, strategy in self.active_strategies.items():
            if strategy["market_regime"] != self.market_regime:
                # Strategy was developed for different market regime
                self.logger.info(f"Market regime changed from {strategy['market_regime']} to {self.market_regime}")
                
                # Could trigger strategy modification or development of new strategy
                # For now, just log the change
                strategy["market_regime_changed"] = True
    
    async def _update_strategy_performance(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Update strategy performance metrics."""
        strategy_id = message.get("strategy_id")
        trade_result = message.get("trade_result", {})
        
        if strategy_id in self.active_strategies:
            strategy = self.active_strategies[strategy_id]
            perf = strategy["performance"]
            
            perf["total_trades"] += 1
            
            pnl = trade_result.get("pnl", 0.0)
            perf["total_pnl"] += pnl
            
            if pnl > 0:
                perf["winning_trades"] += 1
            
            # Update win rate
            perf["win_rate"] = perf["winning_trades"] / perf["total_trades"]
            
            self.log_action("performance_updated", {
                "strategy_id": strategy_id,
                "total_pnl": perf["total_pnl"],
                "win_rate": perf["win_rate"]
            })
        
        return {"status": "performance_updated"}
    
    async def get_status(self) -> Dict[str, Any]:
        """Get current strategy agent status."""
        return {
            **self.get_base_status(),
            "market_regime": self.market_regime,
            "active_strategies": len(self.active_strategies),
            "strategy_ids": list(self.active_strategies.keys()),
            "total_strategy_trades": sum(s["performance"]["total_trades"] for s in self.active_strategies.values()),
            "total_strategy_pnl": sum(s["performance"]["total_pnl"] for s in self.active_strategies.values())
        }
