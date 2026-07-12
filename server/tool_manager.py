
import shlex

from tools.terminal import run_command


class ToolManager:
    """Dispatches tool requests to their handlers.

    The desktop and future clients call these endpoints over HTTP; no tool
    logic lives in the clients themselves.
    """

    def execute(self, tool_name: str, command: str):
        if tool_name == "terminal":
            # shlex preserves quoted arguments (e.g. "my file.txt") instead of
            # naively splitting on whitespace.
            return run_command(shlex.split(command))
        raise ValueError(f"Unknown tool: {tool_name}")
