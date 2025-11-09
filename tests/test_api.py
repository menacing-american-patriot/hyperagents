"""
Tests for the FastAPI endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from backend.api.main import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


def test_root_endpoint(client):
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    
    data = response.json()
    assert data["message"] == "HyperAgents Trading API"
    assert data["version"] == "1.0.0"
    assert data["status"] == "running"
    assert "timestamp" in data


def test_health_endpoint(client):
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "healthy"
    assert "agents_initialized" in data
    assert "coordinator_active" in data
    assert "timestamp" in data


@patch('backend.api.main.coordinator')
def test_agents_status_endpoint(mock_coordinator, client):
    """Test the agents status endpoint."""
    # Mock coordinator response
    mock_coordinator.get_status.return_value = {
        "name": "coordinator",
        "trading_session_active": False,
        "daily_pnl": 0.0,
        "total_trades": 0
    }
    
    response = client.get("/agents/status")
    assert response.status_code == 200


@patch('backend.api.main.coordinator')
def test_start_trading_endpoint(mock_coordinator, client):
    """Test the start trading endpoint."""
    # Mock coordinator response
    mock_coordinator.start_trading_session.return_value = {
        "status": "started",
        "timestamp": "2024-01-01T00:00:00",
        "active_agents": ["market_analyst", "risk_manager"]
    }
    
    response = client.post("/trading/start")
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "started"


@patch('backend.api.main.coordinator')
def test_stop_trading_endpoint(mock_coordinator, client):
    """Test the stop trading endpoint."""
    # Mock coordinator response
    mock_coordinator.stop_trading_session.return_value = {
        "status": "stopped",
        "timestamp": "2024-01-01T00:00:00",
        "session_pnl": 0.0,
        "total_trades": 0
    }
    
    response = client.post("/trading/stop")
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "stopped"


@patch('backend.api.main.agents')
def test_market_analysis_endpoint(mock_agents, client):
    """Test the market analysis endpoint."""
    # Mock market analyst response
    mock_market_analyst = Mock()
    mock_market_analyst.analyze_symbol.return_value = {
        "symbol": "BTC",
        "current_price": 45000.0,
        "recommendation": {
            "action": "BUY",
            "confidence": 0.75
        }
    }
    mock_agents.__getitem__.return_value = mock_market_analyst
    
    response = client.get("/market/analysis/BTC")
    assert response.status_code == 200
    
    data = response.json()
    assert data["symbol"] == "BTC"
    assert "recommendation" in data


@patch('backend.api.main.agents')
def test_trading_signals_endpoint(mock_agents, client):
    """Test the trading signals endpoint."""
    # Mock market analyst response
    mock_market_analyst = Mock()
    mock_market_analyst.get_trading_signals.return_value = {
        "signals": {
            "BTC": {"action": "BUY", "confidence": 0.8},
            "ETH": {"action": "HOLD", "confidence": 0.5}
        },
        "timestamp": "2024-01-01T00:00:00"
    }
    mock_agents.__getitem__.return_value = mock_market_analyst
    
    response = client.get("/market/signals")
    assert response.status_code == 200
    
    data = response.json()
    assert "signals" in data
    assert "BTC" in data["signals"]


@patch('backend.api.main.agents')
def test_positions_endpoint(mock_agents, client):
    """Test the positions endpoint."""
    # Mock execution agent response
    mock_execution_agent = Mock()
    mock_execution_agent.get_current_positions.return_value = {
        "positions": [
            {
                "symbol": "BTC",
                "size": 0.1,
                "entry_price": 44000.0,
                "unrealized_pnl": 100.0
            }
        ],
        "total_positions": 1
    }
    mock_agents.__getitem__.return_value = mock_execution_agent
    
    response = client.get("/positions")
    assert response.status_code == 200
    
    data = response.json()
    assert "positions" in data
    assert len(data["positions"]) == 1


@patch('backend.api.main.agents')
def test_risk_status_endpoint(mock_agents, client):
    """Test the risk status endpoint."""
    # Mock risk manager response
    mock_risk_manager = Mock()
    mock_risk_manager.check_risk_limits.return_value = {
        "total_exposure": 500.0,
        "max_exposure": 800.0,
        "within_limits": True,
        "daily_loss": 0.0
    }
    mock_agents.__getitem__.return_value = mock_risk_manager
    
    response = client.get("/risk/status")
    assert response.status_code == 200
    
    data = response.json()
    assert "within_limits" in data
    assert data["within_limits"] == True


@patch('backend.api.main.agents')
def test_develop_strategy_endpoint(mock_agents, client):
    """Test the develop strategy endpoint."""
    # Mock strategy agent response
    mock_strategy_agent = Mock()
    mock_strategy_agent.develop_strategy.return_value = {
        "status": "strategy_created",
        "strategy": {
            "id": "strategy_123",
            "name": "AI Strategy 123",
            "description": "Test strategy"
        }
    }
    mock_agents.__getitem__.return_value = mock_strategy_agent
    
    response = client.post("/strategies/develop")
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "strategy_created"
    assert "strategy" in data


def test_agents_status_not_initialized(client):
    """Test agents status when coordinator is not initialized."""
    # This test assumes coordinator is None initially
    response = client.get("/agents/status")
    assert response.status_code == 503


if __name__ == "__main__":
    pytest.main([__file__])
