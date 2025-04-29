from __future__ import annotations
from typing_extensions import TypedDict
from typing import Literal, Optional, Annotated, Type, TypeVar
from pydantic import BaseModel, Field
from langchain_core.runnables.config import RunnableConfig, ensure_config
from agent import prompts


class AgentConfig(BaseModel):
    """Azure-GPT-4o and Anthropic are also available, but let's test with OpenAI first."""

    shift_scheduling_agent_model: Literal[
        "gpt-4o",
        "gpt-4.1",
        "gpt-4.1-mini",
        "gpt-4.1-nano",
    ] = Field(
        default="gpt-4.1",
        json_schema_extra={"langgraph_nodes": ["shift_scheduling_agent"]},
    )

    shift_scheduling_agent_system_prompt: Optional[str] = Field(
        default=prompts.SHIFT_SCHEDULING_AGENT_SYSTEM_PROMPT,
        json_schema_extra={"langgraph_nodes": ["shift_scheduling_agent"]},
    )

    @classmethod
    def from_runnable_config(
        cls: Type[T], config: Optional[RunnableConfig] = None
    ) -> T:
        """Create an IndexConfiguration instance from a RunnableConfig object.

        Args:
            cls (Type[T]): The class itself.
            config (Optional[RunnableConfig]): The configuration object to use.

        Returns:
            T: An instance of IndexConfiguration with the specified configuration.
        """
        config = ensure_config(config)
        configurable = config.get("configurable") or {}

        fields_set = set(cls.model_fields.keys())

        return cls(**{k: v for k, v in configurable.items() if k in fields_set})


T = TypeVar("T", bound=AgentConfig)
