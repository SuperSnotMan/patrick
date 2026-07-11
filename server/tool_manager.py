
from tools.terminal import run_command

class ToolManager:
    def execute(self, tool_name: str, command: str):
        if tool_name == "terminal":
            return run_command(command.split())
        raise ValueError(f"Unknown tool: {tool_name}")
