"""Agent registry for discovery and management."""

import logging
from typing import Dict, Any, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AgentRegistry:
    """Central registry for available agents."""
    
    def __init__(self):
        self._agents: Dict[str, Any] = {}
        self._metadata: Dict[str, Dict[str, Any]] = {}
    
    def register_agent(self, name: str, agent_instance: Any, metadata: Dict[str, Any] = None) -> None:
        """
        Register an agent with the registry.
        
        Args:
            name: Unique name of the agent.
            agent_instance: The agent instance.
            metadata: Optional metadata about the agent (capabilities, version, etc.).
        """
        if name in self._agents:
            logger.warning(f"Overwriting existing agent registration: {name}")
        
        self._agents[name] = agent_instance
        self._metadata[name] = metadata or {}
        logger.info(f"Registered agent: {name}")
    
    def get_agent(self, name: str) -> Optional[Any]:
        """
        Get an agent instance by name.
        
        Args:
            name: The name of the agent.
            
        Returns:
            The agent instance or None if not found.
        """
        return self._agents.get(name)
    
    def get_metadata(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for an agent.
        
        Args:
            name: The name of the agent.
            
        Returns:
            The agent metadata or None if not found.
        """
        return self._metadata.get(name)
    
    def list_agents(self) -> List[str]:
        """
        List all registered agent names.
        
        Returns:
            List of agent names.
        """
        return list(self._agents.keys())
    
    def unregister_agent(self, name: str) -> None:
        """
        Unregister an agent.
        
        Args:
            name: The name of the agent to unregister.
        """
        if name in self._agents:
            del self._agents[name]
            del self._metadata[name]
            logger.info(f"Unregistered agent: {name}")
