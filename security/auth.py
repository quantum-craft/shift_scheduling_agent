from langgraph_sdk import Auth

# Warning! This is our toy user database. Do not do this in production
FAKE_VALID_TOKENS = {
    "user1-token": {"id": "user1", "name": "Alice"},
    "user2-token": {"id": "user2", "name": "Bob"},
    "HaHaHa": {"id": "user3", "name": "Charlie"},
}

# The "Auth" object is a container that LangGraph will use to mark our authentication function
auth = Auth()


# The `authenticate` decorator tells LangGraph to call this function as middleware
# for every request. This will determine whether the request is allowed or not
@auth.authenticate
async def get_current_user(authorization: str | None) -> Auth.types.MinimalUserDict:
    """Check if the user's token is valid."""

    print("hello from Auth!")
    print("hello from Auth!")
    print("hello from Auth!")
    print("hello from Auth!")
    print("hello from Auth!")
    print("hello from Auth!")

    assert authorization

    scheme, token = authorization.split()

    print(token)

    assert scheme.lower() == "bearer"

    # Check if token is valid
    if token not in FAKE_VALID_TOKENS:
        raise Auth.exceptions.HTTPException(status_code=401, detail="Invalid token")

    # Return user info if valid
    user_data = FAKE_VALID_TOKENS[token]
    return {
        "identity": user_data["id"],
    }


# @auth.on.assistants
# async def on_assistants(
#     ctx: Auth.types.AuthContext,
#     value: Auth.types.on.assistants.value,
# ):
#     # For illustration purposes, we will deny all requests
#     # that touch the assistants resource
#     # Example value:
#     # {
#     #     'assistant_id': UUID('63ba56c3-b074-4212-96e2-cc333bbc4eb4'),
#     #     'graph_id': 'agent',
#     #     'config': {},
#     #     'metadata': {},
#     #     'name': 'Untitled'
#     # }
#     raise Auth.exceptions.HTTPException(
#         status_code=403,
#         detail="User lacks the required permissions.",
#     )
