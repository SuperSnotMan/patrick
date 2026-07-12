from dataclasses import dataclass
from typing import Optional


@dataclass
class ToolCall:
    tool: str
    command: str


def parse_tool_call(text: str) -> Optional[ToolCall]:
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    tool = None
    command = None

    for line in lines:
        if line.startswith("TOOL:"):
            tool = line.replace("TOOL:", "").strip()

        if line.startswith("COMMAND:"):
            command = line.replace("COMMAND:", "").strip()

    if tool and command:
        return ToolCall(tool, command)

    return None