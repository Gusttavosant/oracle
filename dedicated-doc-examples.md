# OCI Generative AI — Custom Model via API Key

## Como chamar um modelo custom/imported em Dedicated AI Cluster usando openai compat

### Python SDK

```python
from openai import OpenAI

client = OpenAI(
    api_key="sk-COLE_A_CHAVE_AQUI",
    base_url="https://inference.generativeai.<region>.oci.oraclecloud.com/openai/v1",
)

response = client.chat.completions.create(
    model="<GENAI_ENDPOINT_OCID>",
    messages=[
        {
            "role": "user",
            "content": "O que é um modelo dedicado na OCI?"
        }
    ],
)

print(response.choices[0].message.content)
```

### Curl

curl -X POST \
  "https://inference.generativeai.<region>.oci.oraclecloud.com/openai/v1/chat/completions" \
  -H "Authorization: Bearer sk-COLE_A_CHAVE_AQUI" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "<GENAI_ENDPOINT_OCID>",
    "messages": [
      {
        "role": "user",
        "content": "O que é um modelo dedicado na OCI?"
      }
    ]
  }'