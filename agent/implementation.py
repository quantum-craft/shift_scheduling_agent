"""This file was generated using `langgraph-gen` version 0.0.3.

This file provides a placeholder implementation for the corresponding stub.

Replace the placeholder implementation with your own logic.
"""

from typing_extensions import TypedDict
from agent.stub import CustomAgent
from agent.state import AgentState
from agent.config import AgentConfig
from langgraph.graph import add_messages, START, END
from langchain_core.messages import SystemMessage, AIMessage, ToolMessage, HumanMessage
from langchain_core.runnables.config import RunnableConfig
from langgraph.prebuilt import ToolNode
from agent.shift_scheduling_tools import shift_scheduling_tool_list
from agent.utils import get_model_with_shift_scheduling_tool


# Nodes
def node_shift_scheduling_agent(state: AgentState, config: RunnableConfig) -> dict:
    agent_config = AgentConfig.from_runnable_config(config)

    model = get_model_with_shift_scheduling_tool(
        agent_config.shift_scheduling_agent_model
    )

    messages = state.messages
    if agent_config.shift_scheduling_agent_system_prompt:
        messages = [
            SystemMessage(content=agent_config.shift_scheduling_agent_system_prompt)
        ] + messages

    response = model.invoke(messages)

    last_message = messages[-1]
    if (
        isinstance(last_message, ToolMessage)
        and last_message.name == "execute_ortools_scheduling_group_solvers"
        and last_message.status == "success"
        and isinstance(response, AIMessage)
        and len(response.tool_calls) == 0
    ):
        response = response.model_copy(
            deep=True,
            update={
                "whisper": "排班成功, 請幫我刷新網頁",
            },
        )

    return {"messages": response}


node_shift_scheduling_tools = ToolNode(shift_scheduling_tool_list)


# Edges
def edge_shift_scheduling_tools(state: AgentState) -> str:
    messages = state.messages
    last_message = messages[-1]

    if last_message.tool_calls:
        return "shift_scheduling_tools"

    return END


agent = CustomAgent(
    state_schema=AgentState,
    config_schema=AgentConfig,
    impl=[
        ("shift_scheduling_agent", node_shift_scheduling_agent),
        ("shift_scheduling_tools", node_shift_scheduling_tools),
        ("edge_shift_scheduling_tools", edge_shift_scheduling_tools),
    ],
)


compiled_agent = agent.compile()


# Test codes
if __name__ == "__main__":
    # config = {
    #     "configurable": {
    #         # "general_model": "OpenAI-GPT-4o",
    #         # "general_agent_system_prompt": "請以繁體中文回答",
    #     }
    # }

    for chunk in compiled_agent.stream(
        {
            "messages": [HumanMessage(content="排六月的班表")],
        },
        # config=config,
        stream_mode="values",
    ):
        chunk["messages"][-1].pretty_print()
