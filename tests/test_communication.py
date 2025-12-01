"""Unit tests for inter-agent communication."""

import pytest
import os
import json
import shutil
from unittest.mock import MagicMock
from academic_research.communication import AgentMessage, MessageType, MessageBus
from academic_research.agent_registry import AgentRegistry
from academic_research.message_router import MessageRouter, MessageLogger

@pytest.fixture
def clean_logs():
    log_dir = ".gemini/test_logs"
    if os.path.exists(log_dir):
        shutil.rmtree(log_dir)
    yield log_dir
    if os.path.exists(log_dir):
        shutil.rmtree(log_dir)

def test_agent_message_creation():
    """Test creating an AgentMessage."""
    msg = AgentMessage(
        sender="agent_a",
        receiver="agent_b",
        message_type=MessageType.REQUEST,
        content={"key": "value"}
    )
    assert msg.id is not None
    assert msg.timestamp is not None
    assert msg.sender == "agent_a"
    assert msg.content["key"] == "value"

def test_agent_registry():
    """Test registering and retrieving agents."""
    registry = AgentRegistry()
    agent = MagicMock()
    
    registry.register_agent("test_agent", agent, {"version": "1.0"})
    
    assert registry.get_agent("test_agent") == agent
    assert registry.get_metadata("test_agent")["version"] == "1.0"
    assert "test_agent" in registry.list_agents()
    
    registry.unregister_agent("test_agent")
    assert registry.get_agent("test_agent") is None

def test_message_bus():
    """Test pub/sub messaging."""
    bus = MessageBus()
    received = []
    
    def handler(msg):
        received.append(msg)
    
    bus.subscribe("test.topic", handler)
    
    msg = AgentMessage(
        sender="a", receiver="b", 
        message_type=MessageType.EVENT, content={}
    )
    bus.publish("test.topic", msg)
    
    assert len(received) == 1
    assert received[0] == msg

@pytest.mark.asyncio
async def test_message_router_logging(clean_logs):
    """Test that the router logs messages."""
    registry = AgentRegistry()
    bus = MessageBus()
    router = MessageRouter(registry, bus, log_dir=clean_logs)
    
    # Register dummy agent
    registry.register_agent("target", MagicMock())
    
    # Route a message
    await router.route_request("source", "target", {"data": 123})
    
    # Verify log file created
    log_files = os.listdir(clean_logs)
    assert len(log_files) == 1
    
    # Verify log content
    with open(os.path.join(clean_logs, log_files[0]), "r") as f:
        lines = f.readlines()
        assert len(lines) >= 1
        log_entry = json.loads(lines[0])
        assert log_entry["sender"] == "source"
        assert log_entry["receiver"] == "target"
        assert log_entry["content"]["data"] == 123
