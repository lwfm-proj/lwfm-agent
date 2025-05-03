import asyncio

from mcp_agent.core.fastagent import FastAgent

# Create the application
fast = FastAgent("Agent Chaining")


@fast.agent(
    "url_fetcher",
    instruction="Given a URL, provide a complete and comprehensive summary",
    servers=["fetch"],
)
@fast.agent(
    "page_summary_executive",
    instruction="""
    Write a 280 character executive summary for any given text. 
    Respond only with the post, never use hashtags.
    """,
)
@fast.agent(
    "filesystem",
    servers=["filesystem"]
)
@fast.agent(
    "windows_cli",
    servers=["windows-cli"]
)
#@fast.agent(
#    "lwfm_agent",
#    servers=["lwfm-agent", "windows-cli", "filesystem"]
#)


@fast.chain(
    name="post_writer",
    sequence=["url_fetcher", "page_summary_executive"],
)
#@fast.chain(
#    name="initialize_workflow",
#    sequence=["lwfm_agent", "windows_cli", "filesystem"]
#)



async def main() -> None:
    """
    main
    """
    async with fast.run() as agent:
        await agent.interactive()


if __name__ == "__main__":
    asyncio.run(main())
