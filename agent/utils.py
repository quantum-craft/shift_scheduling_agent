from functools import lru_cache
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI, AzureChatOpenAI
from agent.shift_scheduling_tools import shift_scheduling_tool_list


@lru_cache(maxsize=16)
def get_model_with_shift_scheduling_tool(model_name: str):
    model = get_model(model_name)

    model = model.bind_tools(shift_scheduling_tool_list, parallel_tool_calls=False)
    # model = model.bind_tools(day_off_tool_list + [{"type": "web_search_preview"}])

    return model


@lru_cache(maxsize=16)
def get_model(model_name: str):
    """AzureChatOpenAI and ChatAnthropic are also available, but let's test with OpenAI first."""

    model = ChatOpenAI(model=model_name)  # , reasoning_effort="medium")

    return model
