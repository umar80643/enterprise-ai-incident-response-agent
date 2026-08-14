from dataclasses import dataclass
from typing import Callable, Any

@dataclass
class MCPTool:
    name:str
    description:str
    input_schema:dict
    handler:Callable[...,Any]
    permission:str

class MCPServer:
    """Minimal in-process MCP-compatible tool registry boundary used by agents."""
    def __init__(self): self.tools={}
    def register(self,tool:MCPTool): self.tools[tool.name]=tool
    def manifest(self):
        return [{"name":t.name,"description":t.description,"inputSchema":t.input_schema,"permission":t.permission} for t in self.tools.values()]
