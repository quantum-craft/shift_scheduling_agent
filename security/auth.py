from langgraph_sdk import Auth
import httpx
from async_lru import alru_cache
import os

auth = Auth()


@auth.authenticate
async def authenticate(headers: dict) -> Auth.types.MinimalUserDict:
    default_token = os.getenv("DEFAULT_TOKEN")
    token = headers.get("Authorization", default_token)

    if not token:
        raise Auth.exceptions.HTTPException(
            status_code=401,
            detail="Authorization token is required."
        )

    user_dict = await __get_user_dict(token)

    return user_dict

# # Matches the "thread" resource and all actions - create, read, update, delete, search
# # Since this is **more specific** than the generic @auth.on handler, it will take precedence
# # over the generic handler for all actions on the "threads" resource
# @auth.on.threads
# async def on_thread(
#     ctx: Auth.types.AuthContext,
#     value: Auth.types.threads.create.value
# ):
#     if "write" not in ctx.permissions:
#         raise Auth.exceptions.HTTPException(
#             status_code=403,
#             detail="User lacks the required permissions."
#         )
#     # Setting metadata on the thread being created
#     # will ensure that the resource contains an "owner" field
#     # Then any time a user tries to access this thread or runs within the thread,
#     # we can filter by owner
#     metadata = value.setdefault("metadata", {})
#     metadata["owner"] = ctx.user.identity
#     return {"owner": ctx.user.identity}

# The `authenticate` decorator tells LangGraph to call this function as middleware
# for every request. This will determine whether the request is allowed or not

# def _default(ctx: Auth.types.AuthContext, value: dict):
#     metadata = value.setdefault("metadata", {})
#     metadata["owner"] = ctx.user.identity

#     return {"owner": ctx.user.identity}


# @auth.on.threads.read
# async def rbac_create(ctx: Auth.types.AuthContext, value: dict):
#     if "threads:read" not in ctx.permissions or "threads:write" not in ctx.permissions:
#         raise Auth.exceptions.HTTPException(
#             status_code=482, detail="Hallo.QQ Unauthorized"
#         )

#     return _default(ctx, value)


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


@alru_cache(typed=True, ttl=60)
async def __get_user_dict(token: str) -> Auth.types.MinimalUserDict:
    """ 驗證並取得使用者資訊 """
    async with httpx.AsyncClient() as client:

        my_headers = {
            "Authorization": token
        }

        response = await client.get(
            os.getenv("HRM_TOOL_PATH"),
            headers=my_headers
        )

        if response.status_code != 200:
            print(f"請求失敗，狀態碼: {response.status_code}")
            return {
                "identity": "None",
                "is_authenticated": False,
                "permissions": []
            }

        user_info = response.json().get("data")

        user_dict = {
            "identity": user_info.get("employeeId"),
            "display_name": user_info.get("employeeName"),
            "is_authenticated": True,
            "permissions": ["threads:read", "threads:write"],
            "user_info": {
                "companyId": user_info.get("companyId"),
                "employeeId": user_info.get("employeeId"),
                "employeeNumber": user_info.get("employeeNumber"),
                "employeeName": user_info.get("employeeName"),
                "departmentId": user_info.get("departmentId")
            },
            "authorization_header": token
        }

        return user_dict
