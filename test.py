from langchain_core.messages import SystemMessage, AIMessage, ToolMessage, HumanMessage
from agent.implementation import compiled_agent


# Test codes
if __name__ == "__main__":
    config = {
        "configurable": {
            # "general_model": "OpenAI-GPT-4o",
            # "general_agent_system_prompt": "請以繁體中文回答",
        }
    }

    for chunk in compiled_agent.stream(
        {
            "messages": [HumanMessage(content="排六月的班表")],
        },
        # config=config,
        stream_mode="values",
    ):
        chunk["messages"][-1].pretty_print()
