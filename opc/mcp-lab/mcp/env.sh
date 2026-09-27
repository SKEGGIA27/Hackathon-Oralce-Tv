#!/bin/bash

export OCI_OPENAI_BASE_URL="https://inference.generativeai.eu-frankfurt-1.oci.oraclecloud.com/openai/v1"
export OCI_GENAI_API_KEY="sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
export OCI_GENAI_PROJECT_OCID="ocid1.generativeaiproject.oc1.eu-frankfurt-1.amaaaaaarbiiusyaffmlskblkvw7klffabqwwokvzos4tdg6tixaeufbgata"
export OCI_MODEL_ID="openai.gpt-oss-120b"
export F1_MCP_SERVER_URL="http://YOUR-COMPUTE-PUBLIC-IP-ADDRESS:8000/mcp"
export F1_MCP_TOKEN="optional-remote-mcp-token"

echo "OCI_OPENAI_BASE_URL is $OCI_OPENAI_BASE_URL"
echo "run the command  source env.sh"
