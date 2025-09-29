"""
Base agent class for the multi-agent system
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pydantic import BaseModel
import httpx
import os

class AgentMessage(BaseModel):
    """Message format for agent communication"""
    content: str
    metadata: Dict[str, Any] = {}
    agent_id: str
    timestamp: str

class BaseAgent(ABC):
    """Base class for all agents in the system"""
    
    def __init__(self, agent_id: str, name: str, description: str):
        self.agent_id = agent_id
        self.name = name
        self.description = description
        self.storage_service_url = os.getenv("STORAGE_SERVICE_URL", "http://localhost:8001")
    
    @abstractmethod
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input and return output"""
        pass
    
    async def send_to_storage(self, endpoint: str, data: Dict[str, Any], token: str) -> Dict[str, Any]:
        """Send data to storage service"""
        headers = {"Authorization": f"Bearer {token}"}
        
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{self.storage_service_url}{endpoint}",
                json=data,
                headers=headers
            )
            response.raise_for_status()
            return response.json()
    
    async def get_from_storage(self, endpoint: str, token: str) -> Dict[str, Any]:
        """Get data from storage service"""
        headers = {"Authorization": f"Bearer {token}"}
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.storage_service_url}{endpoint}",
                headers=headers
            )
            response.raise_for_status()
            return response.json()
    
    def create_message(self, content: str, metadata: Dict[str, Any] = None) -> AgentMessage:
        """Create a standardized agent message"""
        from datetime import datetime
        
        return AgentMessage(
            content=content,
            metadata=metadata or {},
            agent_id=self.agent_id,
            timestamp=datetime.utcnow().isoformat()
        )