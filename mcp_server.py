"""
Wayne's MCP Skills Server
Auto-discovers skills from ./skills/ and registers them as MCP tools.

Adding a new skill: drop a folder containing SKILL.md into ./skills/, restart server.
SKILL.md must have frontmatter with 'name' and 'description' fields.
"""
import re
from pathlib import Path
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Wayne's Skills Server")
SKILLS_DIR = Path(__file__).parent / "skills"

# MCP tool names must match this pattern
VALID_TOOL_NAME = re.compile(r"^[a-zA-Z0-9_-]+$")


def parse_frontmatter(content: str) -> tuple[dict, str]:
    """Extract YAML frontmatter and body from a markdown file.

    Handles UTF-8 BOM and leading whitespace by stripping first.
    Only parses simple key: value pairs (no nested YAML).
    """
    stripped = content.strip()
    if not stripped.startswith("---"):
        return {}, content
    end = stripped.find("---", 3)
    if end == -1:
        return {}, content
    frontmatter_text = stripped[3:end].strip()
    body = stripped[end + 3:].strip()
    metadata = {}
    for line in frontmatter_text.splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            metadata[key.strip()] = value.strip()
    return metadata, body


def sanitize_tool_name(name: str) -> str:
    """Convert a skill name to a valid MCP tool name component.

    Lowercases, replaces spaces and hyphens with underscores,
    strips any characters outside [a-zA-Z0-9_-].
    """
    clean = name.lower().replace(" ", "_").replace("-", "_")
    clean = re.sub(r"[^a-zA-Z0-9_-]", "", clean)
    return clean


def discover_skills() -> list[dict]:
    """Scan skills/ directory and return list of skill metadata."""
    skills = []
    if not SKILLS_DIR.exists():
        print(f"Warning: skills directory not found at {SKILLS_DIR}")
        return skills

    for skill_dir in sorted(SKILLS_DIR.iterdir()):
        skill_file = skill_dir / "SKILL.md"
        if not skill_dir.is_dir() or not skill_file.exists():
            continue

        content = skill_file.read_text(encoding="utf-8")
        metadata, _ = parse_frontmatter(content)

        if not metadata.get("name"):
            print(f"Warning: {skill_dir.name}/SKILL.md missing 'name' in frontmatter — skipped")
            continue

        tool_name = f"invoke_{sanitize_tool_name(metadata['name'])}"
        if not VALID_TOOL_NAME.match(tool_name):
            print(f"Warning: {skill_dir.name} produces invalid tool name '{tool_name}' — skipped")
            continue

        skills.append({
            "name": metadata["name"],
            "tool_name": tool_name,
            "description": metadata.get("description", f"Activate the {metadata['name']} coaching skill"),
            "skill_file": skill_file,
        })

    return skills


def register_skill_tools() -> None:
    """Dynamically register one MCP tool per discovered skill."""
    skills = discover_skills()
    if not skills:
        print(f"Warning: No valid skills found in {SKILLS_DIR}")
        return

    for skill in skills:
        # Use a factory function to capture skill_data in the closure.
        # This avoids the late-binding bug where all closures reference
        # the same loop variable.
        def create_handler(skill_data: dict):
            async def handler() -> str:
                content = skill_data["skill_file"].read_text(encoding="utf-8")
                _, body = parse_frontmatter(content)
                display_name = skill_data["name"].replace("-", " ").title()
                return (
                    f"## {display_name} — Coaching Persona Activated\n\n"
                    f"**IMPORTANT: You are now operating as the {display_name}. "
                    f"Strictly follow the instructions, persona, methodology, and "
                    f"frameworks below for the entire rest of this session.**\n\n"
                    f"---\n\n"
                    f"{body}\n\n"
                    f"---\n\n"
                    f"You are now in character. Introduce yourself briefly as this coach "
                    f"and begin with your opening question."
                )
            return handler

        handler_func = create_handler(skill)
        mcp.tool(name=skill["tool_name"], description=skill["description"])(handler_func)
        print(f"Registered: {skill['tool_name']}")


# Register all skills at import time
register_skill_tools()

if __name__ == "__main__":
    mcp.run(transport="stdio")
