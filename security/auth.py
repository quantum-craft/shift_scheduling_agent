from langgraph_sdk import Auth
import os
from hrm.webapi.unified.employees import employees

# from mayoapis.ubff import AuthenticatedClient
# from mayoapis.ubff.models import EmployeeViewModelIEnumerableAPIResponse
# from mayoapis.ubff.api.employee import get_api_employees_me
# from mayoapis.ubff.types import Response

auth = Auth()


@auth.authenticate
async def authenticate(headers: dict) -> Auth.types.MinimalUserDict:
    default_token = os.getenv("DEFAULT_TOKEN")
    token = headers.get("Authorization", default_token)

    if not token:
        raise Auth.exceptions.HTTPException(
            status_code=401, detail="Authorization token is required."
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

# async def __get_user_dict(token: str) -> Auth.types.MinimalUserDict:
#     """驗證並取得使用者資訊"""

#     # user_info = await employees.get_my_employee_info(token)
    
#     base_url = os.getenv("HRM_TOOL_ENDPOINT")

#     client = AuthenticatedClient(
#         base_url=base_url,
#         prefix="", 
#         token=token
#         )

#     async with client as client:
#         # user_info: EmployeeViewModelIEnumerableAPIResponse = await get_api_employees_me.asyncio(client=client)
#         response: Response[EmployeeViewModelIEnumerableAPIResponse] = await get_api_employees_me.asyncio_detailed(client=client)
        
#     user_info = response.parsed
    
#     print(f"status_code:{response.status_code}")

#     user_dict = {
#         "identity": user_info.data.employeeId,
#         "display_name": user_info.data.employeeName,
#         "is_authenticated": True,
#         "permissions": ["threads:read", "threads:write"],
#         "user_info": {
#             "companyId": user_info.data.companyId,
#             "employeeId": user_info.data.employeeId,
#             "employeeNumber": user_info.data.employeeNumber,
#             "employeeName": user_info.data.employeeName,
#             "departmentId": user_info.data.departmentId,
#         },
#         "authorization_header": token,
#     }

#     return user_dict

async def __get_user_dict(token: str) -> Auth.types.MinimalUserDict:
    """驗證並取得使用者資訊"""

    user_info = await employees.get_my_employee_info(token)
    
    user_dict = {
        "identity": user_info.data.employeeId,
        "display_name": user_info.data.employeeName,
        "is_authenticated": True,
        "permissions": ["threads:read", "threads:write"],
        "user_info": {
            "companyId": user_info.data.companyId,
            "employeeId": user_info.data.employeeId,
            "employeeNumber": user_info.data.employeeNumber,
            "employeeName": user_info.data.employeeName,
            "departmentId": user_info.data.departmentId,
        },
        "authorization_header": token,
    }

    return user_dict
