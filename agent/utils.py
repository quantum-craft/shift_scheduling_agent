import os
from functools import lru_cache
from langchain_openai import AzureChatOpenAI
from agent.shift_scheduling_tools import shift_scheduling_tool_list


@lru_cache(maxsize=16)
def get_model_with_shift_scheduling_tool(model_name: str):
    model = get_model(model_name)

    model = model.bind_tools(shift_scheduling_tool_list, parallel_tool_calls=False)

    return model


@lru_cache(maxsize=16)
def get_model(model_name: str):
    """Ref: https://python.langchain.com/docs/integrations/chat"""

    model = AzureChatOpenAI(
        model=model_name, azure_deployment=os.getenv("AZURE_DEPLOYMENT")
    )

    return model
