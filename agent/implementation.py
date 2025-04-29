"""This file was generated using `langgraph-gen` version 0.0.3.

This file provides a placeholder implementation for the corresponding stub.

Replace the placeholder implementation with your own logic.
"""

from typing_extensions import TypedDict

from stub import CustomAgent


class SomeState(TypedDict):
    # define your attributes here
    foo: str


# Define stand-alone functions
def shift_scheduling_agent(state: SomeState) -> dict:
    print("In node: shift_scheduling_agent")
    return {
        # Add your state update logic here
    }


def shift_scheduling_tools(state: SomeState) -> dict:
    print("In node: shift_scheduling_tools")
    return {
        # Add your state update logic here
    }


def edge_shift_scheduling_tools(state: SomeState) -> str:
    print("In condition: edge_shift_scheduling_tools")
    raise NotImplementedError("Implement me.")


agent = CustomAgent(
    state_schema=SomeState,
    impl=[
        ("shift_scheduling_agent", shift_scheduling_agent),
        ("shift_scheduling_tools", shift_scheduling_tools),
        ("edge_shift_scheduling_tools", edge_shift_scheduling_tools),
    ],
)

compiled_agent = agent.compile()

print(compiled_agent.invoke({"foo": "bar"}))
