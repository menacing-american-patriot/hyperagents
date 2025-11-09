"""
Market analysis agent for technical and fundamental analysis.
"""
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import numpy as np
from backend.agents.base_agent import BaseAgent
from backend.hyperliquid.client import HyperliquidClient


class MarketAnalysisAgent(BaseAgent):
    """Agent specialized in market analysis and signal generation."""
    
    def __init__(self):
        super().__init__(
            name="market_analyst",
            description="Analyzes market data, identifies trends, and generates trading signals"
        )
        self.hyperliquid_client = HyperliquidClient()
        self.price_history: Dict[str, List[float]] = {}
        self.analysis_cache: Dict[str, Dict[str, Any]] = {}
        self.watched_symbols = ["BTC", "ETH", "SOL", "AVAX"]  # Default symbols to watch
        
    async def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming messages."""
        message_type = message.get("type")
        
        if message_type == "analyze_symbol":
            symbol = message.get("symbol")
            return await self.analyze_symbol(symbol)
        elif message_type == "market_update":
            return await self._handle_market_update(message)
        elif message_type == "get_signals":
            return await self.get_trading_signals()
        else:
            return {"status": "unknown_message_type"}
    
    async def analyze_symbol(self, symbol: str) -> Dict[str, Any]:
        """Perform comprehensive analysis of a trading symbol."""
        try:
            # Get current market data
            market_data = await self.hyperliquid_client.get_market_data(symbol)
            current_price = market_data["price"]
            
            # Update price history
            if symbol not in self.price_history:
                self.price_history[symbol] = []
            
            self.price_history[symbol].append(current_price)
            
            # Keep only last 100 prices for analysis
            if len(self.price_history[symbol]) > 100:
                self.price_history[symbol] = self.price_history[symbol][-100:]
            
            # Perform technical analysis
            technical_analysis = await self._technical_analysis(symbol, self.price_history[symbol])
            
            # Generate AI-powered market sentiment analysis
            sentiment_analysis = await self._ai_sentiment_analysis(symbol, market_data)
            
            analysis_result = {
                "symbol": symbol,
                "current_price": current_price,
                "timestamp": datetime.now().isoformat(),
                "technical_analysis": technical_analysis,
                "sentiment_analysis": sentiment_analysis,
                "recommendation": self._generate_recommendation(technical_analysis, sentiment_analysis)
            }
            
            # Cache the analysis
            self.analysis_cache[symbol] = analysis_result
            
            self.log_action("symbol_analysis", {"symbol": symbol, "price": current_price})
            
            return analysis_result
            
        except Exception as e:
            self.logger.error(f"Error analyzing symbol {symbol}: {e}")
            return {"error": str(e), "symbol": symbol}
    
    async def _technical_analysis(self, symbol: str, prices: List[float]) -> Dict[str, Any]:
        """Perform technical analysis on price data."""
        if len(prices) < 20:
            return {"status": "insufficient_data", "data_points": len(prices)}
        
        prices_array = np.array(prices)
        
        # Calculate moving averages
        sma_20 = np.mean(prices_array[-20:])
        sma_50 = np.mean(prices_array[-50:]) if len(prices) >= 50 else None
        
        # Calculate RSI (simplified)
        price_changes = np.diff(prices_array)
        gains = np.where(price_changes > 0, price_changes, 0)
        losses = np.where(price_changes < 0, -price_changes, 0)
        
        avg_gain = np.mean(gains[-14:]) if len(gains) >= 14 else 0
        avg_loss = np.mean(losses[-14:]) if len(losses) >= 14 else 0
        
        rs = avg_gain / avg_loss if avg_loss != 0 else 100
        rsi = 100 - (100 / (1 + rs))
        
        # Support and resistance levels
        recent_prices = prices_array[-20:]
        support_level = np.min(recent_prices)
        resistance_level = np.max(recent_prices)
        
        # Trend analysis
        current_price = prices[-1]
        trend = "neutral"
        if current_price > sma_20:
            trend = "bullish"
        elif current_price < sma_20:
            trend = "bearish"
        
        return {
            "sma_20": float(sma_20),
            "sma_50": float(sma_50) if sma_50 else None,
            "rsi": float(rsi),
            "support_level": float(support_level),
            "resistance_level": float(resistance_level),
            "trend": trend,
            "volatility": float(np.std(recent_prices))
        }
    
    async def _ai_sentiment_analysis(self, symbol: str, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Use AI to analyze market sentiment and conditions."""
        prompt = f"""
        Analyze the current market conditions for {symbol} and provide a sentiment assessment.
        
        Current price: {market_data['price']}
        Market info: {market_data.get('info', {})}
        
        Consider:
        1. Overall market sentiment
        2. Volume patterns
        3. Recent price action
        4. Market structure
        5. Risk factors
        
        Provide a sentiment score from -1 (very bearish) to 1 (very bullish) and reasoning.
        """
        
        try:
            response = await self.llm.ainvoke([{"role": "user", "content": prompt}])
            
            # Parse AI response for sentiment score and reasoning
            content = response.content
            
            # Simple sentiment extraction (in production, use more sophisticated parsing)
            sentiment_score = 0.0
            if "bullish" in content.lower():
                sentiment_score += 0.3
            if "bearish" in content.lower():
                sentiment_score -= 0.3
            if "very bullish" in content.lower():
                sentiment_score = 0.8
            if "very bearish" in content.lower():
                sentiment_score = -0.8
            
            return {
                "sentiment_score": sentiment_score,
                "ai_analysis": content,
                "confidence": 0.7  # Default confidence
            }
            
        except Exception as e:
            self.logger.error(f"Error in AI sentiment analysis: {e}")
            return {
                "sentiment_score": 0.0,
                "ai_analysis": "Analysis unavailable",
                "confidence": 0.0
            }
    
    def _generate_recommendation(self, technical: Dict[str, Any], sentiment: Dict[str, Any]) -> Dict[str, Any]:
        """Generate trading recommendation based on analysis."""
        # Combine technical and sentiment signals
        tech_score = 0.0
        
        # Technical scoring
        if technical.get("trend") == "bullish":
            tech_score += 0.3
        elif technical.get("trend") == "bearish":
            tech_score -= 0.3
        
        rsi = technical.get("rsi", 50)
        if rsi < 30:  # Oversold
            tech_score += 0.2
        elif rsi > 70:  # Overbought
            tech_score -= 0.2
        
        # Combine with sentiment
        sentiment_score = sentiment.get("sentiment_score", 0.0)
        combined_score = (tech_score + sentiment_score) / 2
        
        # Generate recommendation
        if combined_score > 0.3:
            action = "BUY"
            confidence = min(abs(combined_score), 1.0)
        elif combined_score < -0.3:
            action = "SELL"
            confidence = min(abs(combined_score), 1.0)
        else:
            action = "HOLD"
            confidence = 0.5
        
        return {
            "action": action,
            "confidence": confidence,
            "combined_score": combined_score,
            "technical_score": tech_score,
            "sentiment_score": sentiment_score
        }
    
    async def get_trading_signals(self) -> Dict[str, Any]:
        """Get trading signals for all watched symbols."""
        signals = {}
        
        for symbol in self.watched_symbols:
            try:
                analysis = await self.analyze_symbol(symbol)
                if "recommendation" in analysis:
                    signals[symbol] = analysis["recommendation"]
            except Exception as e:
                self.logger.error(f"Error getting signal for {symbol}: {e}")
        
        return {
            "signals": signals,
            "timestamp": datetime.now().isoformat(),
            "symbols_analyzed": len(signals)
        }
    
    async def _handle_market_update(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle real-time market updates."""
        symbol = message.get("symbol")
        price = message.get("price")
        
        if symbol and price:
            if symbol not in self.price_history:
                self.price_history[symbol] = []
            self.price_history[symbol].append(price)
        
        return {"status": "market_update_processed"}
    
    async def get_status(self) -> Dict[str, Any]:
        """Get current status of the market analysis agent."""
        return {
            **self.get_base_status(),
            "watched_symbols": self.watched_symbols,
            "symbols_with_data": list(self.price_history.keys()),
            "cached_analyses": list(self.analysis_cache.keys()),
            "total_price_points": sum(len(prices) for prices in self.price_history.values())
        }
