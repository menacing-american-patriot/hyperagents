"""
Hyperliquid exchange client wrapper.
"""
import asyncio
from typing import Dict, List, Optional, Any
import logging
from hyperliquid.info import Info
from hyperliquid.exchange import Exchange
from hyperliquid.utils import constants
from backend.config.settings import settings


class HyperliquidClient:
    """Wrapper for Hyperliquid API with enhanced functionality."""
    
    def __init__(self):
        self.logger = logging.getLogger("hyperliquid.client")
        self.testnet = settings.hyperliquid.testnet
        
        # Initialize info client (read-only)
        self.info = Info(base_url=settings.hyperliquid.base_url, skip_ws=True)
        
        # Initialize exchange client (trading) if private key is provided
        self.exchange = None
        if settings.hyperliquid.private_key:
            self.exchange = Exchange(
                private_key=settings.hyperliquid.private_key,
                base_url=settings.hyperliquid.base_url,
                skip_ws=True
            )
            self.logger.info("Initialized Hyperliquid client with trading capabilities")
        else:
            self.logger.warning("No private key provided - trading disabled")
    
    async def get_market_data(self, symbol: str) -> Dict[str, Any]:
        """Get current market data for a symbol."""
        try:
            # Get current price and basic market info
            all_mids = self.info.all_mids()
            
            if symbol not in all_mids:
                raise ValueError(f"Symbol {symbol} not found")
            
            current_price = all_mids[symbol]
            
            # Get 24h stats
            meta = self.info.meta()
            universe = meta.get("universe", [])
            
            symbol_info = None
            for asset in universe:
                if asset.get("name") == symbol:
                    symbol_info = asset
                    break
            
            return {
                "symbol": symbol,
                "price": current_price,
                "timestamp": asyncio.get_event_loop().time(),
                "info": symbol_info
            }
            
        except Exception as e:
            self.logger.error(f"Error fetching market data for {symbol}: {e}")
            raise
    
    async def get_account_info(self) -> Dict[str, Any]:
        """Get account information including balances and positions."""
        if not self.exchange:
            raise RuntimeError("Trading not enabled - no private key provided")
        
        try:
            user_state = self.info.user_state(self.exchange.wallet.address)
            return {
                "address": self.exchange.wallet.address,
                "balances": user_state.get("balances", []),
                "positions": user_state.get("assetPositions", []),
                "margin_summary": user_state.get("marginSummary", {}),
                "cross_margin_summary": user_state.get("crossMarginSummary", {})
            }
        except Exception as e:
            self.logger.error(f"Error fetching account info: {e}")
            raise
    
    async def place_order(self, symbol: str, side: str, size: float, 
                         order_type: str = "Market", price: Optional[float] = None) -> Dict[str, Any]:
        """Place a trading order."""
        if not self.exchange:
            raise RuntimeError("Trading not enabled - no private key provided")
        
        try:
            order_request = {
                "coin": symbol,
                "is_buy": side.lower() == "buy",
                "sz": size,
                "limit_px": price if order_type.lower() == "limit" else None,
                "order_type": {"limit": order_type.lower()}
            }
            
            result = self.exchange.order(order_request)
            self.logger.info(f"Placed {side} order for {size} {symbol}: {result}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error placing order: {e}")
            raise
    
    async def cancel_order(self, order_id: str, symbol: str) -> Dict[str, Any]:
        """Cancel an existing order."""
        if not self.exchange:
            raise RuntimeError("Trading not enabled - no private key provided")
        
        try:
            result = self.exchange.cancel({"coin": symbol, "oid": order_id})
            self.logger.info(f"Cancelled order {order_id}: {result}")
            return result
        except Exception as e:
            self.logger.error(f"Error cancelling order {order_id}: {e}")
            raise
    
    async def get_open_orders(self) -> List[Dict[str, Any]]:
        """Get all open orders."""
        if not self.exchange:
            raise RuntimeError("Trading not enabled - no private key provided")
        
        try:
            user_state = self.info.user_state(self.exchange.wallet.address)
            return user_state.get("orders", [])
        except Exception as e:
            self.logger.error(f"Error fetching open orders: {e}")
            raise
