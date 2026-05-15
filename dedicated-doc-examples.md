# OCI Generative AI — Custom Model via API Key

## Requisito

Dar permissão para o serviço de generative ai para usar API Key como metodo de autenticação. Para isso, vá em Identity > Policy e crie uma nova policy com a seguinte permissão:

```
allow any-user to use generative-ai-family  in compartment <compartment-name>  where ALL {request.principal.type='generativeaiapikey'}
```

## Como criar sua Api Key
<img width="2642" height="1021" alt="image" src="https://github.com/user-attachments/assets/0050854a-75e0-41b8-8c33-4e659ebc6e37" />

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
```bash
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
```
