"""
Tests for AI agents functionality.
"""
import pytest
import asyncio
from unittest.mock import Mock, patch
from backend.agents.coordination_agent import CoordinationAgent
from backend.agents.market_analysis_agent import MarketAnalysisAgent
from backend.agents.risk_management_agent import RiskManagementAgent


class TestCoordinationAgent:
    """Test cases for the coordination agent."""
    
    @pytest.fixture
    def coordinator(self):
        return CoordinationAgent()
    
    def test_coordinator_initialization(self, coordinator):
        """Test coordinator initializes correctly."""
        assert coordinator.name == "coordinator"
        assert coordinator.trading_session_active == False
        assert coordinator.daily_pnl == 0.0
        assert coordinator.total_trades == 0
    
    @pytest.mark.asyncio
    async def test_start_trading_session(self, coordinator):
        """Test starting a trading session."""
        result = await coordinator.start_trading_session()
        
        assert result["status"] == "started"
        assert coordinator.trading_session_active == True
        assert "timestamp" in result
        assert "active_agents" in result
    
    @pytest.mark.asyncio
    async def test_stop_trading_session(self, coordinator):
        """Test stopping a trading session."""
        # First start a session
        await coordinator.start_trading_session()
        
        # Then stop it
        result = await coordinator.stop_trading_session()
        
        assert result["status"] == "stopped"
        assert coordinator.trading_session_active == False
        assert "session_pnl" in result
        assert "total_trades" in result


class TestMarketAnalysisAgent:
    """Test cases for the market analysis agent."""
    
    @pytest.fixture
    def market_agent(self):
        return MarketAnalysisAgent()
    
    def test_market_agent_initialization(self, market_agent):
        """Test market agent initializes correctly."""
        assert market_agent.name == "market_analyst"
        assert isinstance(market_agent.watched_symbols, list)
        assert len(market_agent.watched_symbols) > 0
    
    def test_technical_analysis_insufficient_data(self, market_agent):
        """Test technical analysis with insufficient data."""
        prices = [100.0, 101.0, 99.0]  # Only 3 data points
        
        result = asyncio.run(market_agent._technical_analysis("BTC", prices))
        
        assert result["status"] == "insufficient_data"
        assert result["data_points"] == 3
    
    @pytest.mark.asyncio
    async def test_technical_analysis_sufficient_data(self, market_agent):
        """Test technical analysis with sufficient data."""
        # Generate 25 price points
        prices = [100.0 + i * 0.5 for i in range(25)]
        
        result = await market_agent._technical_analysis("BTC", prices)
        
        assert "sma_20" in result
        assert "rsi" in result
        assert "support_level" in result
        assert "resistance_level" in result
        assert "trend" in result
        assert result["trend"] in ["bullish", "bearish", "neutral"]
    
    def test_generate_recommendation(self, market_agent):
        """Test recommendation generation."""
        technical = {
            "trend": "bullish",
            "rsi": 45.0
        }
        sentiment = {
            "sentiment_score": 0.6
        }
        
        result = market_agent._generate_recommendation(technical, sentiment)
        
        assert "action" in result
        assert "confidence" in result
        assert result["action"] in ["BUY", "SELL", "HOLD"]
        assert 0 <= result["confidence"] <= 1


class TestRiskManagementAgent:
    """Test cases for the risk management agent."""
    
    @pytest.fixture
    def risk_agent(self):
        return RiskManagementAgent()
    
    def test_risk_agent_initialization(self, risk_agent):
        """Test risk agent initializes correctly."""
        assert risk_agent.name == "risk_manager"
        assert risk_agent.daily_loss == 0.0
        assert risk_agent.daily_trades == 0
    
    @pytest.mark.asyncio
    async def test_validate_signal_missing_data(self, risk_agent):
        """Test signal validation with missing data."""
        signal = {"action": "BUY"}  # Missing symbol
        
        result = await risk_agent.validate_trading_signal(signal)
        
        assert result["status"] == "rejected"
        assert result["reason"] == "missing_signal_data"
    
    @pytest.mark.asyncio
    async def test_validate_signal_daily_loss_limit(self, risk_agent):
        """Test signal validation when daily loss limit is exceeded."""
        # Set daily loss to exceed limit
        risk_agent.daily_loss = 1000.0  # Assuming this exceeds the limit
        
        signal = {
            "symbol": "BTC",
            "action": "BUY",
            "confidence": 0.8
        }
        
        result = await risk_agent.validate_trading_signal(signal)
        
        assert result["status"] == "rejected"
        assert result["reason"] == "daily_loss_limit_exceeded"
    
    def test_calculate_stop_loss(self, risk_agent):
        """Test stop loss calculation."""
        result = risk_agent._calculate_stop_loss("BTC", "BUY")
        
        assert result["type"] == "percentage"
        assert "percentage" in result
        assert result["side"] == "sell"  # Opposite of BUY
    
    def test_calculate_take_profit(self, risk_agent):
        """Test take profit calculation."""
        result = risk_agent._calculate_take_profit("BTC", "BUY")
        
        assert result["type"] == "percentage"
        assert "percentage" in result
        assert result["side"] == "sell"  # Opposite of BUY


@pytest.mark.asyncio
async def test_agent_communication():
    """Test communication between agents."""
    coordinator = CoordinationAgent()
    market_agent = MarketAnalysisAgent()
    
    # Register market agent with coordinator
    coordinator.register_agent(market_agent)
    
    assert "market_analyst" in coordinator.agents
    assert coordinator.agents["market_analyst"] == market_agent


if __name__ == "__main__":
    pytest.main([__file__])
