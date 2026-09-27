import os
from openai import OpenAI

client = OpenAI(
    base_url=os.environ["OCI_OPENAI_BASE_URL"],
    api_key=os.environ["OCI_GENAI_API_KEY"],
    project=os.environ["OCI_GENAI_PROJECT_OCID"],
)

response = client.responses.create(
    model=os.environ["OCI_MODEL_ID"],
    input="Use the F1 MCP server to summarize the race and recommend a pit strategy for NOR.",
    tools=[
        {
            "type": "mcp",
            "server_label": "f1_race_server",
            "server_description": "MCP server exposing simulated F1 race data and strategy tools",
            "server_url": os.environ["F1_MCP_SERVER_URL"],
            "require_approval": "never",
            "allowed_tools": [
                "get_session_overview",
                "get_driver_position",
                "compare_drivers",
                "recommend_strategy",
            ],
        }
    ],
    stream=False,
)

print(response.output_text)
