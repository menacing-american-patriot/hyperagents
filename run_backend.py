#!/usr/bin/env python3
"""
Script to run the HyperAgents backend server.
"""
import uvicorn
from backend.config.settings import settings

if __name__ == "__main__":
    uvicorn.run(
        "backend.api.main:app",
        host=settings.system.api_host,
        port=settings.system.api_port,
        reload=settings.system.debug,
        log_level=settings.system.log_level.lower()
    )
