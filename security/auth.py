from langgraph_sdk import Auth

# Warning! This is our toy user database. Do not do this in production
FAKE_VALID_TOKENS = {
    "user1-token": {"id": "user1", "name": "Alice"},
    "user2-token": {"id": "user2", "name": "Bob"},
    "HaHaHa": {"id": "user3", "name": "Charlie"},
}

# The "Auth" object is a container that LangGraph will use to mark our authentication function
auth = Auth()


def is_valid_key(api_key: str) -> bool:
    return False


# The `authenticate` decorator tells LangGraph to call this function as middleware
# for every request. This will determine whether the request is allowed or not
@auth.authenticate
async def authenticate(headers: dict) -> Auth.types.MinimalUserDict:
    print("======================================")
    print("Hello from Auth!")

    api_key = headers.get("x-api-key")
    # if not api_key:
    #     raise Auth.exceptions.HTTPException(
    #         status_code=401, detail="Hallo182 x-api-key not in headers"
    #     )

    # if not is_valid_key(api_key):
    #     raise Auth.exceptions.HTTPException(
    #         status_code=401, detail="Hallo182 Invalid API key"
    #     )

    return {
        "identity": "hallo-123",
        "is_authenticated": True,
        "permissions": ["threads:read"],
        "role": "hallo god",
        "org_id": "org-mayohr",
    }


def _default(ctx: Auth.types.AuthContext, value: dict):
    metadata = value.setdefault("metadata", {})
    metadata["owner"] = ctx.user.identity

    return {"owner": ctx.user.identity}


@auth.on.threads.read
async def rbac_create(ctx: Auth.types.AuthContext, value: dict):
    if "threads:read" not in ctx.permissions or "threads:write" not in ctx.permissions:
        raise Auth.exceptions.HTTPException(
            status_code=482, detail="Hallo.QQ Unauthorized"
        )

    return _default(ctx, value)


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
