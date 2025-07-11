"""
TON Connect Integration for I3lani Bot
Based on TON Connect SDK research and best practices
"""

import asyncio
import json
import logging
from typing import Dict, Optional, Any
from dataclasses import dataclass
from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import aiohttp
import secrets
import base64
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

@dataclass
class WalletInfo:
    """TON Connect wallet information"""
    name: str
    bridge_url: str
    universal_url: str
    app_name: str
    icon_url: str
    supported_features: list

@dataclass
class ConnectionSession:
    """TON Connect connection session"""
    session_id: str
    user_id: int
    wallet_info: Optional[WalletInfo]
    connection_url: str
    connected_at: Optional[datetime]
    expires_at: datetime
    public_key: Optional[str]
    wallet_address: Optional[str]

class TONConnectIntegration:
    """
    TON Connect integration for seamless wallet connection
    Based on TON Connect 2.0 protocol
    """
    
    # Popular TON wallets with their connection details
    SUPPORTED_WALLETS = {
        'tonkeeper': {
            'name': 'Tonkeeper',
            'bridge_url': 'https://bridge.tonapi.io/bridge',
            'universal_url': 'https://app.tonkeeper.com/ton-connect',
            'app_name': 'Tonkeeper',
            'icon_url': 'https://tonkeeper.com/assets/tonconnect-icon.png',
            'supported_features': ['SendTransaction', 'SignData']
        },
        'tonhub': {
            'name': 'TonHub',
            'bridge_url': 'https://connect.tonhubapi.com/tonconnect',
            'universal_url': 'https://tonhub.com/ton-connect',
            'app_name': 'TonHub',
            'icon_url': 'https://tonhub.com/tonconnect-icon.png',
            'supported_features': ['SendTransaction', 'SignData']
        },
        'mytonwallet': {
            'name': 'MyTonWallet',
            'bridge_url': 'https://bridge.mytonwallet.io/bridge',
            'universal_url': 'https://connect.mytonwallet.org',
            'app_name': 'MyTonWallet',
            'icon_url': 'https://mytonwallet.io/icon.png',
            'supported_features': ['SendTransaction', 'SignData']
        }
    }
    
    def __init__(self, bot: Bot, manifest_url: str):
        self.bot = bot
        self.manifest_url = manifest_url
        self.connections: Dict[int, ConnectionSession] = {}
        self.session_timeout = timedelta(minutes=10)
        
    async def get_wallet_list(self) -> Dict[str, WalletInfo]:
        """Get list of supported wallets"""
        wallets = {}
        for wallet_id, wallet_config in self.SUPPORTED_WALLETS.items():
            wallets[wallet_id] = WalletInfo(**wallet_config)
        return wallets
    
    async def create_connection_session(self, user_id: int) -> ConnectionSession:
        """Create new TON Connect connection session"""
        session_id = secrets.token_urlsafe(32)
        expires_at = datetime.now() + self.session_timeout
        
        # Generate connection URL with session parameters
        connection_url = await self._generate_connection_url(session_id, user_id)
        
        session = ConnectionSession(
            session_id=session_id,
            user_id=user_id,
            wallet_info=None,
            connection_url=connection_url,
            connected_at=None,
            expires_at=expires_at,
            public_key=None,
            wallet_address=None
        )
        
        self.connections[user_id] = session
        return session
    
    async def _generate_connection_url(self, session_id: str, user_id: int) -> str:
        """Generate TON Connect connection URL"""
        # Connection request parameters
        connect_request = {
            'manifestUrl': self.manifest_url,
            'items': [
                {
                    'name': 'ton_addr',
                    'network': 'mainnet'
                },
                {
                    'name': 'ton_proof',
                    'payload': f'i3lani-bot-{user_id}-{session_id}'
                }
            ]
        }
        
        # Encode request
        encoded_request = base64.urlsafe_b64encode(
            json.dumps(connect_request).encode()
        ).decode().rstrip('=')
        
        # Create universal link
        connection_url = f"tc://connect?v=2&id={session_id}&r={encoded_request}"
        
        return connection_url
    
    async def create_wallet_selection_keyboard(self, user_id: int) -> InlineKeyboardMarkup:
        """Create wallet selection keyboard"""
        keyboard = InlineKeyboardMarkup(inline_keyboard=[])
        
        # Get connection session
        session = await self.create_connection_session(user_id)
        
        # Add wallet buttons
        for wallet_id, wallet_info in self.SUPPORTED_WALLETS.items():
            keyboard.inline_keyboard.append([
                InlineKeyboardButton(
                    text=f"💎 {wallet_info['name']}",
                    callback_data=f"connect_wallet:{wallet_id}:{session.session_id}"
                )
            ])
        
        # Add QR code option
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(
                text="📱 Show QR Code",
                callback_data=f"show_qr:{session.session_id}"
            )
        ])
        
        # Add manual connection option
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(
                text="🔗 Manual Connection",
                callback_data=f"manual_connect:{session.session_id}"
            )
        ])
        
        return keyboard
    
    async def handle_wallet_connection(self, user_id: int, wallet_id: str, session_id: str):
        """Handle wallet connection request"""
        if user_id not in self.connections:
            raise Exception("No active connection session")
        
        session = self.connections[user_id]
        if session.session_id != session_id:
            raise Exception("Invalid session ID")
        
        if datetime.now() > session.expires_at:
            raise Exception("Session expired")
        
        # Get wallet info
        wallet_config = self.SUPPORTED_WALLETS.get(wallet_id)
        if not wallet_config:
            raise Exception("Unsupported wallet")
        
        wallet_info = WalletInfo(**wallet_config)
        
        # Create connection URL for specific wallet
        connection_url = await self._create_wallet_specific_url(wallet_info, session_id)
        
        # Update session
        session.wallet_info = wallet_info
        session.connection_url = connection_url
        
        return connection_url
    
    async def _create_wallet_specific_url(self, wallet_info: WalletInfo, session_id: str) -> str:
        """Create wallet-specific connection URL"""
        # Create universal link for specific wallet
        base_url = wallet_info.universal_url
        connection_params = {
            'v': '2',
            'id': session_id,
            'r': base64.urlsafe_b64encode(
                json.dumps({
                    'manifestUrl': self.manifest_url,
                    'items': [
                        {'name': 'ton_addr', 'network': 'mainnet'},
                        {'name': 'ton_proof', 'payload': f'i3lani-{session_id}'}
                    ]
                }).encode()
            ).decode().rstrip('=')
        }
        
        # Build URL
        params_str = '&'.join([f"{k}={v}" for k, v in connection_params.items()])
        return f"{base_url}?{params_str}"
    
    async def process_wallet_connection(self, user_id: int, wallet_response: dict) -> bool:
        """Process wallet connection response"""
        try:
            if user_id not in self.connections:
                return False
            
            session = self.connections[user_id]
            
            # Validate response
            if not await self._validate_connection_response(wallet_response, session):
                return False
            
            # Extract wallet information
            wallet_address = wallet_response.get('address')
            public_key = wallet_response.get('publicKey')
            
            # Update session
            session.wallet_address = wallet_address
            session.public_key = public_key
            session.connected_at = datetime.now()
            
            # Store in database
            await self._store_wallet_connection(user_id, session)
            
            logger.info(f"✅ TON Connect: Wallet connected for user {user_id}")
            logger.info(f"   Address: {wallet_address}")
            logger.info(f"   Wallet: {session.wallet_info.name if session.wallet_info else 'Unknown'}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ TON Connect: Connection failed for user {user_id}: {e}")
            return False
    
    async def _validate_connection_response(self, response: dict, session: ConnectionSession) -> bool:
        """Validate wallet connection response"""
        # Check required fields
        required_fields = ['address', 'publicKey', 'proof']
        for field in required_fields:
            if field not in response:
                logger.error(f"Missing required field: {field}")
                return False
        
        # Validate proof
        proof = response.get('proof', {})
        if not await self._validate_ton_proof(proof, session):
            logger.error("Invalid TON proof")
            return False
        
        return True
    
    async def _validate_ton_proof(self, proof: dict, session: ConnectionSession) -> bool:
        """Validate TON proof"""
        try:
            # Extract proof components
            timestamp = proof.get('timestamp')
            domain = proof.get('domain')
            signature = proof.get('signature')
            payload = proof.get('payload')
            
            # Basic validation
            if not all([timestamp, domain, signature, payload]):
                return False
            
            # Check timestamp (should be within 5 minutes)
            proof_time = datetime.fromtimestamp(timestamp)
            if abs((datetime.now() - proof_time).total_seconds()) > 300:
                return False
            
            # Check payload matches session
            expected_payload = f'i3lani-{session.session_id}'
            if payload != expected_payload:
                return False
            
            # TODO: Implement full cryptographic signature verification
            # For now, basic validation passes
            return True
            
        except Exception as e:
            logger.error(f"TON proof validation error: {e}")
            return False
    
    async def _store_wallet_connection(self, user_id: int, session: ConnectionSession):
        """Store wallet connection in database"""
        try:
            from database import db
            
            # Update user's wallet information
            await db.execute("""
                UPDATE users 
                SET ton_wallet_address = ?, 
                    ton_wallet_public_key = ?,
                    ton_wallet_connected_at = ?,
                    ton_wallet_type = ?
                WHERE user_id = ?
            """, (
                session.wallet_address,
                session.public_key,
                session.connected_at,
                session.wallet_info.name if session.wallet_info else None,
                user_id
            ))
            
            logger.info(f"✅ Stored TON Connect wallet info for user {user_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to store wallet connection: {e}")
    
    async def get_user_wallet_info(self, user_id: int) -> Optional[dict]:
        """Get user's connected wallet information"""
        try:
            from database import db
            
            result = await db.fetchone("""
                SELECT ton_wallet_address, ton_wallet_public_key, 
                       ton_wallet_connected_at, ton_wallet_type
                FROM users 
                WHERE user_id = ?
            """, (user_id,))
            
            if result:
                return {
                    'address': result[0],
                    'public_key': result[1],
                    'connected_at': result[2],
                    'wallet_type': result[3]
                }
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to get wallet info: {e}")
            return None
    
    async def disconnect_wallet(self, user_id: int) -> bool:
        """Disconnect user's wallet"""
        try:
            from database import db
            
            # Clear wallet information
            await db.execute("""
                UPDATE users 
                SET ton_wallet_address = NULL, 
                    ton_wallet_public_key = NULL,
                    ton_wallet_connected_at = NULL,
                    ton_wallet_type = NULL
                WHERE user_id = ?
            """, (user_id,))
            
            # Remove from active connections
            if user_id in self.connections:
                del self.connections[user_id]
            
            logger.info(f"✅ Disconnected TON wallet for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to disconnect wallet: {e}")
            return False
    
    async def request_transaction(self, user_id: int, amount: float, memo: str, recipient: str) -> Optional[dict]:
        """Request transaction through connected wallet"""
        try:
            wallet_info = await self.get_user_wallet_info(user_id)
            if not wallet_info:
                raise Exception("No wallet connected")
            
            # Create transaction request
            transaction = {
                'valid_until': int((datetime.now() + timedelta(minutes=10)).timestamp()),
                'messages': [
                    {
                        'address': recipient,
                        'amount': str(int(amount * 1_000_000_000)),  # Convert to nanotons
                        'payload': memo
                    }
                ]
            }
            
            # Send transaction request to wallet
            # This would typically be done through the wallet's bridge
            # For now, we return the transaction for manual processing
            
            return {
                'transaction': transaction,
                'wallet_address': wallet_info['address'],
                'wallet_type': wallet_info['wallet_type']
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to request transaction: {e}")
            return None
    
    async def cleanup_expired_sessions(self):
        """Clean up expired connection sessions"""
        now = datetime.now()
        expired_sessions = [
            user_id for user_id, session in self.connections.items()
            if now > session.expires_at
        ]
        
        for user_id in expired_sessions:
            del self.connections[user_id]
            logger.info(f"🧹 Cleaned up expired session for user {user_id}")
    
    async def get_connection_status(self, user_id: int) -> dict:
        """Get user's connection status"""
        wallet_info = await self.get_user_wallet_info(user_id)
        session = self.connections.get(user_id)
        
        return {
            'connected': wallet_info is not None,
            'wallet_info': wallet_info,
            'active_session': session is not None,
            'session_expires': session.expires_at if session else None
        }

# Global instance
ton_connect = None

def get_ton_connect_integration(bot: Bot, manifest_url: str) -> TONConnectIntegration:
    """Get or create TON Connect integration instance"""
    global ton_connect
    if ton_connect is None:
        ton_connect = TONConnectIntegration(bot, manifest_url)
    return ton_connect

async def init_ton_connect_integration(bot: Bot) -> TONConnectIntegration:
    """Initialize TON Connect integration"""
    manifest_url = "https://i3lani-bot.com/tonconnect-manifest.json"  # Replace with actual URL
    
    integration = get_ton_connect_integration(bot, manifest_url)
    
    # Start cleanup task
    asyncio.create_task(periodic_cleanup(integration))
    
    logger.info("✅ TON Connect integration initialized")
    logger.info(f"   Manifest URL: {manifest_url}")
    logger.info(f"   Supported wallets: {len(integration.SUPPORTED_WALLETS)}")
    
    return integration

async def periodic_cleanup(integration: TONConnectIntegration):
    """Periodic cleanup of expired sessions"""
    while True:
        try:
            await integration.cleanup_expired_sessions()
            await asyncio.sleep(300)  # Clean up every 5 minutes
        except Exception as e:
            logger.error(f"❌ TON Connect cleanup error: {e}")
            await asyncio.sleep(300)