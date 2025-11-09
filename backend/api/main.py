"""
FastAPI main application for HyperAgents trading system.
"""
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Dict, List, Any
import asyncio
import json
import logging
from datetime import datetime

from backend.config.settings import settings
from backend.agents.coordination_agent import CoordinationAgent
from backend.agents.market_analysis_agent import MarketAnalysisAgent
from backend.agents.risk_management_agent import RiskManagementAgent
from backend.agents.strategy_agent import StrategyAgent
from backend.agents.execution_agent import ExecutionAgent

# Configure logging
logging.basicConfig(level=getattr(logging, settings.system.log_level))
logger = logging.getLogger("api.main")

# Initialize FastAPI app
app = FastAPI(
    title="HyperAgents Trading API",
    description="AI-powered trading agents for Hyperliquid exchange",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.system.frontend_url, "http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global agent instances
coordinator: CoordinationAgent = None
agents: Dict[str, Any] = {}
websocket_connections: List[WebSocket] = []


@app.on_event("startup")
async def startup_event():
    """Initialize agents on startup."""
    global coordinator, agents
    
    logger.info("Initializing HyperAgents system...")
    
    # Initialize all agents
    coordinator = CoordinationAgent()
    market_analyst = MarketAnalysisAgent()
    risk_manager = RiskManagementAgent()
    strategy_agent = StrategyAgent()
    execution_agent = ExecutionAgent()
    
    # Register agents with coordinator
    coordinator.register_agent(market_analyst)
    coordinator.register_agent(risk_manager)
    coordinator.register_agent(strategy_agent)
    coordinator.register_agent(execution_agent)
    
    # Store agents for direct access
    agents = {
        "coordinator": coordinator,
        "market_analyst": market_analyst,
        "risk_manager": risk_manager,
        "strategy_agent": strategy_agent,
        "execution_agent": execution_agent
    }
    
    logger.info("HyperAgents system initialized successfully")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "HyperAgents Trading API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "agents_initialized": len(agents),
        "coordinator_active": coordinator is not None,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/agents/status")
async def get_agents_status():
    """Get status of all agents."""
    if not coordinator:
        raise HTTPException(status_code=503, detail="Agents not initialized")
    
    try:
        status = await coordinator.get_status()
        return status
    except Exception as e:
        logger.error(f"Error getting agents status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/trading/start")
async def start_trading():
    """Start trading session."""
    if not coordinator:
        raise HTTPException(status_code=503, detail="Coordinator not initialized")
    
    try:
        result = await coordinator.start_trading_session()
        
        # Broadcast to WebSocket clients
        await broadcast_to_websockets({
            "type": "trading_session",
            "action": "started",
            "data": result
        })
        
        return result
    except Exception as e:
        logger.error(f"Error starting trading session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/trading/stop")
async def stop_trading():
    """Stop trading session."""
    if not coordinator:
        raise HTTPException(status_code=503, detail="Coordinator not initialized")
    
    try:
        result = await coordinator.stop_trading_session()
        
        # Broadcast to WebSocket clients
        await broadcast_to_websockets({
            "type": "trading_session",
            "action": "stopped",
            "data": result
        })
        
        return result
    except Exception as e:
        logger.error(f"Error stopping trading session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/market/analysis/{symbol}")
async def get_market_analysis(symbol: str):
    """Get market analysis for a symbol."""
    if "market_analyst" not in agents:
        raise HTTPException(status_code=503, detail="Market analyst not initialized")
    
    try:
        analysis = await agents["market_analyst"].analyze_symbol(symbol)
        return analysis
    except Exception as e:
        logger.error(f"Error getting market analysis for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/market/signals")
async def get_trading_signals():
    """Get current trading signals."""
    if "market_analyst" not in agents:
        raise HTTPException(status_code=503, detail="Market analyst not initialized")
    
    try:
        signals = await agents["market_analyst"].get_trading_signals()
        return signals
    except Exception as e:
        logger.error(f"Error getting trading signals: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/positions")
async def get_positions():
    """Get current positions."""
    if "execution_agent" not in agents:
        raise HTTPException(status_code=503, detail="Execution agent not initialized")
    
    try:
        positions = await agents["execution_agent"].get_current_positions()
        return positions
    except Exception as e:
        logger.error(f"Error getting positions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/risk/status")
async def get_risk_status():
    """Get risk management status."""
    if "risk_manager" not in agents:
        raise HTTPException(status_code=503, detail="Risk manager not initialized")
    
    try:
        risk_status = await agents["risk_manager"].check_risk_limits()
        return risk_status
    except Exception as e:
        logger.error(f"Error getting risk status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/strategies/develop")
async def develop_strategy(parameters: Dict[str, Any] = None):
    """Develop a new trading strategy."""
    if "strategy_agent" not in agents:
        raise HTTPException(status_code=503, detail="Strategy agent not initialized")
    
    try:
        strategy = await agents["strategy_agent"].develop_strategy(parameters or {})
        return strategy
    except Exception as e:
        logger.error(f"Error developing strategy: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates."""
    await websocket.accept()
    websocket_connections.append(websocket)
    
    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            if message.get("type") == "ping":
                await websocket.send_text(json.dumps({"type": "pong"}))
            
    except WebSocketDisconnect:
        websocket_connections.remove(websocket)
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        if websocket in websocket_connections:
            websocket_connections.remove(websocket)


async def broadcast_to_websockets(message: Dict[str, Any]):
    """Broadcast message to all connected WebSocket clients."""
    if not websocket_connections:
        return
    
    message_str = json.dumps(message)
    disconnected = []
    
    for websocket in websocket_connections:
        try:
            await websocket.send_text(message_str)
        except Exception as e:
            logger.error(f"Error sending WebSocket message: {e}")
            disconnected.append(websocket)
    
    # Remove disconnected clients
    for websocket in disconnected:
        websocket_connections.remove(websocket)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.api.main:app",
        host=settings.system.api_host,
        port=settings.system.api_port,
        reload=settings.system.debug
    )
