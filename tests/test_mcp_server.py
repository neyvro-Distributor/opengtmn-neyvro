import asyncio
import json
import os
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


ROOT = Path(__file__).parents[1]


async def _exercise_protocol() -> None:
    env = dict(os.environ)
    env["PYTHONPATH"] = str(ROOT / "src")
    params = StdioServerParameters(command=sys.executable, args=["-m", "neyvro.mcp_server"], cwd=ROOT, env=env)
    async with stdio_client(params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            tools = await session.list_tools()
            tool_names = {tool.name for tool in tools.tools}
            assert tool_names == {"neyvro_list_skills", "neyvro_get_skill", "neyvro_search_skills"}

            def tool_payload(result):
                if result.structuredContent:
                    structured = result.structuredContent
                    return structured["result"] if set(structured) == {"result"} else structured
                return json.loads(result.content[0].text)

            listed = await session.call_tool("neyvro_list_skills", {"limit": 100})
            skills = tool_payload(listed)
            assert len(skills) == 35
            assert all("path" not in skill for skill in skills)

            fetched = await session.call_tool("neyvro_get_skill", {"name": "evidence-verification"})
            fetched_data = tool_payload(fetched)
            original = (ROOT / "skills/evidence-verification/SKILL.md").read_text(encoding="utf-8")
            assert fetched_data["content"] == original
            assert fetched_data["resource_uri"] == "neyvro://skills/evidence-verification"

            searched = await session.call_tool("neyvro_search_skills", {"query": "evidence", "limit": 5})
            assert tool_payload(searched)

            resources = await session.list_resources()
            resource_names = {str(item.uri) for item in resources.resources}
            assert len(resource_names) == 35
            assert "neyvro://skills/evidence-verification" in resource_names
            resource = await session.read_resource("neyvro://skills/evidence-verification")
            assert resource.contents[0].text == original

            prompts = await session.list_prompts()
            prompt_names = {prompt.name for prompt in prompts.prompts}
            assert len(prompt_names) == 35
            assert "evidence-verification" in prompt_names
            prompt = await session.get_prompt("evidence-verification")
            assert "evidence-verification" in prompt.messages[0].content.text

            unknown = await session.call_tool("neyvro_get_skill", {"name": "does-not-exist"})
            assert unknown.isError is True
            invalid = await session.call_tool("neyvro_list_skills", {"limit": 0})
            assert invalid.isError is True


def test_local_mcp_protocol_surface() -> None:
    asyncio.run(_exercise_protocol())
