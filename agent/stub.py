"""This is an automatically generated file. Do not modify it.

This file was generated using `langgraph-gen` version 0.0.3.
To regenerate this file, run `langgraph-gen` with the source `yaml` file as an argument.

Usage:

1. Add the generated file to your project.
2. Create a new agent using the stub.

Below is a sample implementation of the generated stub:

```python
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
    ]
)

compiled_agent = agent.compile()

print(compiled_agent.invoke({"foo": "bar"}))
"""

from typing import Callable, Any, Optional, Type

from langgraph.constants import START, END
from langgraph.graph import StateGraph


def CustomAgent(
    *,
    state_schema: Optional[Type[Any]] = None,
    config_schema: Optional[Type[Any]] = None,
    input: Optional[Type[Any]] = None,
    output: Optional[Type[Any]] = None,
    impl: list[tuple[str, Callable]],
) -> StateGraph:
    """Create the state graph for CustomAgent."""
    # Declare the state graph
    builder = StateGraph(
        state_schema, config_schema=config_schema, input=input, output=output
    )

    nodes_by_name = {name: imp for name, imp in impl}

    all_names = set(nodes_by_name)

    expected_implementations = {
        "shift_scheduling_agent",
        "shift_scheduling_tools",
        "edge_shift_scheduling_tools",
    }

    missing_nodes = expected_implementations - all_names
    if missing_nodes:
        raise ValueError(f"Missing implementations for: {missing_nodes}")

    extra_nodes = all_names - expected_implementations

    if extra_nodes:
        raise ValueError(
            f"Extra implementations for: {extra_nodes}. Please regenerate the stub."
        )

    # Add nodes
    builder.add_node("shift_scheduling_agent", nodes_by_name["shift_scheduling_agent"])
    builder.add_node("shift_scheduling_tools", nodes_by_name["shift_scheduling_tools"])

    # Add edges
    builder.add_edge(START, "shift_scheduling_agent")
    builder.add_edge("shift_scheduling_tools", "shift_scheduling_agent")
    builder.add_conditional_edges(
        "shift_scheduling_agent",
        nodes_by_name["edge_shift_scheduling_tools"],
        [
            "shift_scheduling_tools",
            END,
        ],
    )
    return builder
