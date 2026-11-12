"""
WebSocket Manager for Real-Time Notifications
Handles instant push notifications to connected clients
"""
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List, Set, Optional
import json
import asyncio
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Manages WebSocket connections for real-time notifications.
    Supports targeting by:
    - User ID (specific user)
    - Store ID (all users in a store)
    - Role (all users with a specific role)
    - Broadcast (all connected users)
    """
    
    def __init__(self):
        # Connection pools
        self.active_connections: Dict[str, WebSocket] = {}  # connection_id -> WebSocket
        self.user_connections: Dict[str, Set[str]] = {}     # user_id -> set of connection_ids
        self.store_connections: Dict[str, Set[str]] = {}    # store_id -> set of connection_ids
        self.role_connections: Dict[str, Set[str]] = {}     # role -> set of connection_ids
        self.connection_metadata: Dict[str, dict] = {}      # connection_id -> metadata
        
    async def connect(
        self, 
        websocket: WebSocket, 
        connection_id: str,
        user_id: Optional[str] = None,
        store_id: Optional[str] = None,
        role: Optional[str] = None
    ):
        """Accept a new WebSocket connection and register it"""
        await websocket.accept()
        
        # Store connection
        self.active_connections[connection_id] = websocket
        
        # Store metadata
        self.connection_metadata[connection_id] = {
            "user_id": user_id,
            "store_id": store_id,
            "role": role,
            "connected_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Register by user
        if user_id:
            if user_id not in self.user_connections:
                self.user_connections[user_id] = set()
            self.user_connections[user_id].add(connection_id)
        
        # Register by store
        if store_id:
            if store_id not in self.store_connections:
                self.store_connections[store_id] = set()
            self.store_connections[store_id].add(connection_id)
        
        # Register by role
        if role:
            if role not in self.role_connections:
                self.role_connections[role] = set()
            self.role_connections[role].add(connection_id)
        
        logger.info(f"WebSocket connected: {connection_id} (user={user_id}, store={store_id}, role={role})")
        
        # Send welcome message
        await self.send_personal_message({
            "type": "connected",
            "message": "WebSocket connection established",
            "connection_id": connection_id
        }, connection_id)
    
    def disconnect(self, connection_id: str):
        """Remove a WebSocket connection"""
        if connection_id not in self.active_connections:
            return
        
        # Get metadata
        metadata = self.connection_metadata.get(connection_id, {})
        user_id = metadata.get("user_id")
        store_id = metadata.get("store_id")
        role = metadata.get("role")
        
        # Remove from user pool
        if user_id and user_id in self.user_connections:
            self.user_connections[user_id].discard(connection_id)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]
        
        # Remove from store pool
        if store_id and store_id in self.store_connections:
            self.store_connections[store_id].discard(connection_id)
            if not self.store_connections[store_id]:
                del self.store_connections[store_id]
        
        # Remove from role pool
        if role and role in self.role_connections:
            self.role_connections[role].discard(connection_id)
            if not self.role_connections[role]:
                del self.role_connections[role]
        
        # Remove connection
        del self.active_connections[connection_id]
        del self.connection_metadata[connection_id]
        
        logger.info(f"WebSocket disconnected: {connection_id}")
    
    async def send_personal_message(self, message: dict, connection_id: str):
        """Send message to a specific connection"""
        if connection_id in self.active_connections:
            try:
                await self.active_connections[connection_id].send_json(message)
            except Exception as e:
                logger.error(f"Failed to send to {connection_id}: {e}")
                self.disconnect(connection_id)
    
    async def send_to_user(self, message: dict, user_id: str):
        """Send message to all connections of a specific user"""
        if user_id not in self.user_connections:
            return 0
        
        sent_count = 0
        disconnected = []
        
        for connection_id in self.user_connections[user_id].copy():
            if connection_id in self.active_connections:
                try:
                    await self.active_connections[connection_id].send_json(message)
                    sent_count += 1
                except Exception as e:
                    logger.error(f"Failed to send to user {user_id} connection {connection_id}: {e}")
                    disconnected.append(connection_id)
        
        # Clean up disconnected
        for conn_id in disconnected:
            self.disconnect(conn_id)
        
        return sent_count
    
    async def send_to_store(self, message: dict, store_id: str):
        """Send message to all connections in a specific store"""
        if store_id not in self.store_connections:
            return 0
        
        sent_count = 0
        disconnected = []
        
        for connection_id in self.store_connections[store_id].copy():
            if connection_id in self.active_connections:
                try:
                    await self.active_connections[connection_id].send_json(message)
                    sent_count += 1
                except Exception as e:
                    logger.error(f"Failed to send to store {store_id} connection {connection_id}: {e}")
                    disconnected.append(connection_id)
        
        # Clean up disconnected
        for conn_id in disconnected:
            self.disconnect(conn_id)
        
        return sent_count
    
    async def send_to_role(self, message: dict, role: str):
        """Send message to all connections with a specific role"""
        if role not in self.role_connections:
            return 0
        
        sent_count = 0
        disconnected = []
        
        for connection_id in self.role_connections[role].copy():
            if connection_id in self.active_connections:
                try:
                    await self.active_connections[connection_id].send_json(message)
                    sent_count += 1
                except Exception as e:
                    logger.error(f"Failed to send to role {role} connection {connection_id}: {e}")
                    disconnected.append(connection_id)
        
        # Clean up disconnected
        for conn_id in disconnected:
            self.disconnect(conn_id)
        
        return sent_count
    
    async def broadcast(self, message: dict):
        """Send message to all connected clients"""
        sent_count = 0
        disconnected = []
        
        for connection_id, websocket in list(self.active_connections.items()):
            try:
                await websocket.send_json(message)
                sent_count += 1
            except Exception as e:
                logger.error(f"Failed to broadcast to {connection_id}: {e}")
                disconnected.append(connection_id)
        
        # Clean up disconnected
        for conn_id in disconnected:
            self.disconnect(conn_id)
        
        return sent_count
    
    def get_connection_count(self) -> dict:
        """Get current connection statistics"""
        return {
            "total_connections": len(self.active_connections),
            "users_connected": len(self.user_connections),
            "stores_connected": len(self.store_connections),
            "roles_connected": list(self.role_connections.keys())
        }


# Global connection manager instance
notification_manager = ConnectionManager()


async def push_notification(notification: dict):
    """
    Push a notification to relevant WebSocket connections.
    Called when a new notification is created.
    """
    message = {
        "type": "notification",
        "data": notification
    }
    
    recipient_type = notification.get("recipient_type")
    sent_count = 0
    
    if recipient_type == "user":
        # Send to specific user
        user_id = notification.get("recipient_id")
        if user_id:
            sent_count = await notification_manager.send_to_user(message, user_id)
    
    elif recipient_type == "store":
        # Send to all users in a store
        store_id = notification.get("recipient_id")
        if store_id:
            sent_count = await notification_manager.send_to_store(message, store_id)
    
    elif recipient_type == "role":
        # Send to all users with a role
        role = notification.get("recipient_role")
        if role:
            sent_count = await notification_manager.send_to_role(message, role)
            
            # Also send to admin and super_admin for most notifications
            if role not in ["admin", "super_admin"]:
                sent_count += await notification_manager.send_to_role(message, "admin")
                sent_count += await notification_manager.send_to_role(message, "super_admin")
    
    elif recipient_type == "broadcast":
        # Send to everyone
        sent_count = await notification_manager.broadcast(message)
    
    logger.info(f"Pushed notification to {sent_count} connections: {notification.get('title', 'N/A')}")
    return sent_count
