"""Methodology Agent package."""

from .agent import (
    create_methodology_agent,
    format_prompt_for_methodology,
    MethodologyAgent
)
from .prompt import SYSTEM_INSTRUCTION, USER_CONTEXT_TEMPLATE

__all__ = [
    "create_methodology_agent",
    "format_prompt_for_methodology",
    "MethodologyAgent",
    "SYSTEM_INSTRUCTION",
    "USER_CONTEXT_TEMPLATE"
]

