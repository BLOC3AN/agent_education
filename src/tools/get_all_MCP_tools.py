from langchain.tools import BaseTool
from typing import List, Dict, Any, Optional
from pydantic import create_model, BaseModel
import requests
import os
import json
from src.utils.logger import Logger

logger = Logger(__name__)

# ---------- Settings ----------
class Settings:
    def __init__(self):
        self.mcp_server_url = os.getenv("MCP_SERVER_URL", "http://mcp-server:9099")

settings = Settings()

# ---------- Helper: Convert schema dict to Pydantic model ----------
def create_pydantic_model_from_schema(name: str, schema_dict: Dict[str, Any]) -> BaseModel:
    fields = {}
    props = schema_dict.get("properties", {})
    required = schema_dict.get("required", [])

    for field_name, prop in props.items():
        field_type = str  # default
        if prop.get("type") == "integer":
            field_type = int
        elif prop.get("type") == "number":
            field_type = float
        elif prop.get("type") == "boolean":
            field_type = bool
        elif prop.get("type") == "array":
            field_type = list
        elif prop.get("type") == "object":
            field_type = dict

        is_required = field_name in required
        fields[field_name] = (field_type, ...) if is_required else (Optional[field_type], None)

    return create_model(name + "Args", **fields) # type: ignore

# ---------- Tool class ----------
class MCPTool(BaseTool):
    """
    Một tool LangChain được gọi qua MCP Service.
    """
    name: str = "mcp_tool"
    description: str = "Tool được gọi qua MCP"
    endpoint: str
    token: str
    user_id: str

    def _run(self, tool_input: Optional[Dict[str, Any]] = None, **kwargs) -> str:
        headers = {"Content-Type": "application/json"}
        full_url = f"{settings.mcp_server_url}{self.endpoint}"

        logger.info(f"🔧 MCPTool '{self.name}' called with endpoint: {self.endpoint}")
        logger.info(f"🔗 Full URL: {full_url}")

        try:
            payload = tool_input if tool_input else kwargs
            if not isinstance(payload, dict):
                return f"⚠️ Invalid input: expected dict, got {type(payload)}"

            payload['token'] = self.token
            payload['user_id'] = self.user_id

            logger.info(f"📦 Final payload: {json.dumps(payload, indent=2, ensure_ascii=False)}")
            response = requests.post(full_url, json=payload, headers=headers)
            response.raise_for_status()

            result = response.json()
            logger.info(f"✅ Received response from MCP: {result}")
            return json.dumps(result, ensure_ascii=False)

        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Request error: {str(e)}")
            return f"❌ MCPTool error: {str(e)}"

# ---------- Main discover function ----------
def discover_and_create_mcp_tools(token: str = "", user_id: str = "") -> List[BaseTool]:
    """
    Tự động fetch MCP capabilities và convert thành LangChain Tool.
    """
    headers = {"Content-Type": "application/json"}
    capabilities_url = f"{settings.mcp_server_url}/capabilities"

    try:
        response = requests.get(capabilities_url, headers=headers)
        response.raise_for_status()
        capabilities = response.json()
        logger.info(f"✅ Capabilities discovered: {[cap['mcp_schema'].get('name', 'unknown') for cap in capabilities]}")
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Error discovering MCP capabilities: {e}")
        return []

    tools = []
    for cap in capabilities:
        try:
            schema = cap.get("mcp_schema", {})
            name = schema.get("name", "unnamed_tool")
            description = schema.get("description", f"Auto-discovered MCP tool: {name}")

            if "endpoint" not in schema or "url" not in schema["endpoint"]:
                logger.warning(f"⚠️ Missing endpoint.url for tool: {name}")
                continue
            endpoint = schema["endpoint"]["url"]

            raw_args_schema = schema.get("args_schema", {"type": "object", "properties": {}})
            pydantic_args_model = create_pydantic_model_from_schema(name, raw_args_schema)

            tool = MCPTool(
                name=name,
                description=description,
                args_schema=pydantic_args_model, # type: ignore
                endpoint=endpoint,
                token=token,
                user_id=user_id
            )
            tools.append(tool)
            logger.info(f"✅ Created MCPTool: {name}")

        except Exception as e:
            logger.error(f"❌ Failed to load tool '{cap}': {e}")
            continue

    logger.info(f"✅ Total MCP tools created: {len(tools)}")
    return tools
