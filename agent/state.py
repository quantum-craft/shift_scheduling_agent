from pydantic import BaseModel, Field
from typing import Annotated, Literal
from langchain_core.messages import AnyMessage, BaseMessage
from langgraph.graph import add_messages


class AgentState(BaseModel):
    messages: Annotated[list[BaseMessage], add_messages]
