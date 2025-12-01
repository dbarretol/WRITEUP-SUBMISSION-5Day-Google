"""Message router for inter-agent communication."""

import logging
import json
import os
from typing import Dict, Any, Optional
from datetime import datetime

from .communication import AgentMessage, MessageType, MessageBus
from .agent_registry import AgentRegistry

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MessageLogger:
    """Logs agent communication to a file."""
    
    def __init__(self, log_dir: str = ".gemini/logs"):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        self.log_file = os.path.join(
            log_dir, 
            f"communication_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
        )
    
    def log(self, message: AgentMessage) -> None:
        """
        Log a message to the file.
        
        Args:
            message: The message to log.
        """
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(message.model_dump_json() + "\n")
        except Exception as e:
            logger.error(f"Failed to log message: {e}")


class MessageRouter:
    """Routes messages between agents and logs communication."""
    
    def __init__(self, registry: AgentRegistry, bus: MessageBus, log_dir: str = ".gemini/logs"):
        self.registry = registry
        self.bus = bus
        self.logger = MessageLogger(log_dir)
        
        # Subscribe to all agent topics
        # In a real system, this might be more dynamic
        self.bus.subscribe("router", self._handle_message)
    
    def _handle_message(self, message: AgentMessage) -> None:
        """
        Handle incoming messages.
        
        Args:
            message: The received message.
        """
        self.logger.log(message)
        logger.info(f"Routed message {message.id} from {message.sender} to {message.receiver}")
    
    async def route_request(self, sender: str, receiver: str, content: Dict[str, Any]) -> AgentMessage:
        """
        Route a request from one agent to another and wait for response.
        
        Args:
            sender: Name of the sending agent.
            receiver: Name of the receiving agent.
            content: The request content.
            
        Returns:
            The response message.
        """
        # Create request message
        request = AgentMessage(
            sender=sender,
            receiver=receiver,
            message_type=MessageType.REQUEST,
            content=content
        )
        
        # Log and publish request
        self.logger.log(request)
        self.bus.publish(f"agent.{receiver}", request)
        
        # In a fully async system, we would wait for a response on a reply topic
        # For this implementation, we'll simulate the routing by looking up the agent
        # and calling it directly if possible, or just returning a mock response
        # if the agent isn't callable in this way.
        
        # Check if receiver exists
        agent = self.registry.get_agent(receiver)
        if not agent:
            error_msg = AgentMessage(
                sender="router",
                receiver=sender,
                message_type=MessageType.ERROR,
                content={"error": f"Agent {receiver} not found"},
                correlation_id=request.id
            )
            self.logger.log(error_msg)
            return error_msg
        
        # NOTE: In a real distributed system, we wouldn't call the agent directly here.
        # We would publish to a queue and await a response.
        # Since our agents are currently designed as direct function calls in the orchestrator,
        # this router is a bit of an abstraction layer that we are building *around* them.
        # To make this useful now, we can use it to wrap the direct calls.
        
        return request # Return the request for now as acknowledgement
