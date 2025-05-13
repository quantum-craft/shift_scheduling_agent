from langgraph_sdk import get_client
import asyncio


async def client_test():
    """This client is used to test the server.
    Do this after 'uv run langgraph dev' or other means to start the langgraph api server like:
    LangGraph Platform (SaaS) or Enterprise Self-Hosted."""

    # Try without a token (should fail)
    client = get_client(url="http://localhost:2024")

    try:
        thread = await client.threads.create()
        print("❌ Should have failed without token!")
    except Exception as e:
        print("✅ Correctly blocked access:", e)

    # # Try with a valid token
    # client = get_client(
    #     url="http://localhost:2024", headers={"Authorization": "Bearer user1-token"}
    # )

    # Create a thread and chat
    thread = await client.threads.create()

    print(f"✅ Created thread as Alice: {thread['thread_id']}")

    response = await client.runs.create(
        thread_id=thread["thread_id"],
        assistant_id="shift_scheduling_agent",
        input={"messages": [{"role": "user", "content": "Hello!"}]},
    )

    print("✅ Bot responded:")
    print(response.content)


if __name__ == "__main__":
    asyncio.run(client_test())
