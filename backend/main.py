"""
Main entry point for the HyperAgents trading system.
"""
import asyncio
import logging
from backend.api.main import app
from backend.config.settings import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.system.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("hyperagents.main")

async def main():
    """Main function to start the HyperAgents system."""
    logger.info("Starting HyperAgents AI Trading System...")
    logger.info(f"API will be available at http://{settings.system.api_host}:{settings.system.api_port}")
    logger.info(f"Frontend should be available at {settings.system.frontend_url}")
    
    # The FastAPI app will be started by uvicorn
    # This is just for any additional startup logic
    
if __name__ == "__main__":
    asyncio.run(main())
