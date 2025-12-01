"""Inter-agent communication protocol and message bus."""

import uuid
import logging
from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional, Callable, List
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MessageType(str, Enum):
    """Types of messages exchanged between agents."""
    REQUEST = "request"
    RESPONSE = "response"
    ERROR = "error"
    EVENT = "event"


class AgentMessage(BaseModel):
    """Standardized envelope for agent communication."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    sender: str
    receiver: str
    message_type: MessageType
    content: Dict[str, Any]
    correlation_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class MessageBus:
    """Simple in-memory message bus for pub/sub communication."""
    
    def __init__(self):
        self._subscribers: Dict[str, List[Callable[[AgentMessage], None]]] = {}
        self._history: List[AgentMessage] = []
    
    def subscribe(self, topic: str, handler: Callable[[AgentMessage], None]) -> None:
        """
        Subscribe to a topic.
        
        Args:
            topic: The topic to subscribe to (e.g., "agent.interviewer").
            handler: Callback function to handle messages.
        """
        if topic not in self._subscribers:
            self._subscribers[topic] = []
        self._subscribers[topic].append(handler)
        logger.info(f"Subscribed to topic: {topic}")
    
    def publish(self, topic: str, message: AgentMessage) -> None:
        """
        Publish a message to a topic.
        
        Args:
            topic: The topic to publish to.
            message: The message to publish.
        """
        self._history.append(message)
        
        if topic in self._subscribers:
            for handler in self._subscribers[topic]:
                try:
                    handler(message)
                except Exception as e:
                    logger.error(f"Error handling message on topic {topic}: {e}")
        
        # Also publish to wildcard subscribers (if we implemented them)
        logger.debug(f"Published message {message.id} to {topic}")
    
    def get_history(self) -> List[AgentMessage]:
        """Get the message history."""
        return self._history
