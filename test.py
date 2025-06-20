from langchain_core.messages import SystemMessage, AIMessage, ToolMessage, HumanMessage
from agent.implementation import compiled_agent
from dotenv import load_dotenv


load_dotenv()


if __name__ == "__main__":
    config = {
        "configurable": {
            "test_config_1": "Hi",
            "test_config_2": "請以繁體中文回答",
        }
    }

    for chunk in compiled_agent.stream(
        {
            "messages": [HumanMessage(content="排六月的前28天班表")],
        },
        config=config,
        stream_mode="values",
    ):
        chunk["messages"][-1].pretty_print()
