# RAG com Autonomous AI Database 26ai

Tutorial para criar um pipeline de Knowledge Base no Autonomous AI Database 26ai usando tabela com vetor, embeddings, ingestão, busca por similaridade e chamada via Python.

---

## 1. Objetivo

```text
Apresentar os comandos para criação de um fluxo simples de RAG para criar sua própria base de conhecimento utilizando o banco Autonomous 26ai. Os termos desse método não serão explicados nesse arquivo.
```

---

## 2. Autorizações (se for admin, iniciar do passo 3)

Criando um usuário chamado `kb_app` com permissões necessárias para executar os comandos necessários.

```sql
CREATE USER kb_app IDENTIFIED BY "<SUA_SENHA>";

GRANT CREATE SESSION TO kb_app;
GRANT CREATE TABLE TO kb_app;
GRANT CREATE SEQUENCE TO kb_app;
GRANT CREATE PROCEDURE TO kb_app;
GRANT CREATE VIEW TO kb_app;
GRANT CREATE CREDENTIAL TO kb_app;

ALTER USER kb_app QUOTA 10G ON DATA;

GRANT EXECUTE ON DBMS_VECTOR_CHAIN TO kb_app;
GRANT EXECUTE ON DBMS_VECTOR TO kb_app;
```

---

## 3. Conectando modelo de embedding

Execute como `ADMIN` ou usuário com privilégios administrativos.

### 3.1 Liberar ACL de rede

Se usar provider externo para embeddings, libere ACL de rede.

Exemplo Generative AI OCI:

```sql
BEGIN
  DBMS_NETWORK_ACL_ADMIN.APPEND_HOST_ACE(
    host => '*.oraclecloud.com',
    ace  => xs$ace_type(
      privilege_list => xs$name_list('http'),
      principal_name => 'ADMIN',
      principal_type => xs_acl.ptype_db
    )
  );
END;
/
```
### 3.2 Criar credencial para modelo de embedding
Conecte como o usuário que deseja utilizar para criar as credenciais, tabelas e funções, exemplo `admin` ou `kb_app`.

### OCI Generative AI

```sql
DECLARE
  jo JSON_OBJECT_T;
BEGIN
  jo := JSON_OBJECT_T();

  jo.put('user_ocid',        'ocid1.user.oc1..xxx');
  jo.put('tenancy_ocid',     'ocid1.tenancy.oc1..xxx');
  jo.put('compartment_ocid', 'ocid1.compartment.oc1..xxx');
  jo.put('private_key',      '<PRIVATE_KEY_EM_UMA_LINHA>');
  jo.put('fingerprint',      'xx:xx:xx:xx');

  DBMS_VECTOR_CHAIN.CREATE_CREDENTIAL(
    credential_name => 'OCI_CRED',
    params => JSON(jo.to_string)
  );
END;
/
```

Se usar modelo ONNX dentro do banco com `provider: "database"`, não precisa de credential.

---

## 4. Criar tabelas da Knowledge Base

```sql
CREATE TABLE kb_documents (
  doc_id      NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  source_name VARCHAR2(1000),
  source_uri  VARCHAR2(4000),
  mime_type   VARCHAR2(200),
  doc_text    CLOB,
  created_at  TIMESTAMP DEFAULT SYSTIMESTAMP
);

CREATE TABLE kb_chunks (
  chunk_id   NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  doc_id     NUMBER NOT NULL,
  chunk_no   NUMBER NOT NULL,
  chunk_text VARCHAR2(4000),
  embedding  VECTOR,
  created_at TIMESTAMP DEFAULT SYSTIMESTAMP,
  CONSTRAINT kb_chunks_doc_fk
    FOREIGN KEY (doc_id) REFERENCES kb_documents(doc_id)
);
```

Se quiser fixar a dimensão do vetor:

```sql
embedding VECTOR(1536, FLOAT32)
```

---

## 5. Função de embedding
Substitua a região e modelo dada a disponibilidade do seu ambiente (referência: https://docs.oracle.com/en-us/iaas/Content/generative-ai/model-endpoint-regions.htm).

### Exemplo com OCI Generative AI

```sql
CREATE OR REPLACE FUNCTION kb_embed_text (
  p_text IN CLOB
) RETURN VECTOR
IS
  l_params CLOB;
BEGIN
  l_params := '{
    "provider": "ocigenai",
    "credential_name": "OCI_CRED",
    "url": "https://inference.generativeai.<SUA_REGIAO>.oci.oraclecloud.com/20231130/actions/embedText",
    "model": "<SEU_MODELO>"
  }';

  RETURN DBMS_VECTOR_CHAIN.UTL_TO_EMBEDDING(
    p_text,
    JSON(l_params)
  );
END;
/
```

### Exemplo com modelo ONNX no banco

```sql
CREATE OR REPLACE FUNCTION kb_embed_text (
  p_text IN CLOB
) RETURN VECTOR
IS
BEGIN
  RETURN DBMS_VECTOR_CHAIN.UTL_TO_EMBEDDING(
    p_text,
    JSON('{
      "provider": "database",
      "model": "<DOC_MODEL>"
    }')
  );
END;
/
```

---

## 6. Procedure de ingestão

```sql
CREATE OR REPLACE PROCEDURE kb_ingest_text (
  p_source_name IN VARCHAR2,
  p_source_uri  IN VARCHAR2 DEFAULT NULL,
  p_mime_type   IN VARCHAR2 DEFAULT 'text/plain',
  p_text        IN CLOB
)
IS
  l_doc_id NUMBER;
  l_embed_params CLOB;
  l_chunk_params CLOB;
BEGIN
  INSERT INTO kb_documents (
    source_name,
    source_uri,
    mime_type,
    doc_text
  )
  VALUES (
    p_source_name,
    p_source_uri,
    p_mime_type,
    p_text
  )
  RETURNING doc_id INTO l_doc_id;

  l_chunk_params := '{
    "by": "words",
    "max": "300",
    "overlap": "40",
    "split": "sentence",
    "normalize": "all"
  }';

  l_embed_params := '{
    "provider": "ocigenai",
    "credential_name": "OCI_CRED",
    "url": "https://inference.generativeai.<SUA_REGIAO>.oci.oraclecloud.com/20231130/actions/embedText",
    "model": "<SEU_MODELO>"
  }';

  INSERT INTO kb_chunks (
    doc_id,
    chunk_no,
    chunk_text,
    embedding
  )
  SELECT
    l_doc_id,
    jt.embed_id,
    jt.embed_data,
    TO_VECTOR(jt.embed_vector)
  FROM
    DBMS_VECTOR_CHAIN.UTL_TO_EMBEDDINGS(
      DBMS_VECTOR_CHAIN.UTL_TO_CHUNKS(
        p_text,
        JSON(l_chunk_params)
      ),
      JSON(l_embed_params)
    ) e,
    JSON_TABLE(
      e.column_value,
      '$[*]'
      COLUMNS (
        embed_id     NUMBER         PATH '$.embed_id',
        embed_data   VARCHAR2(4000) PATH '$.embed_data',
        embed_vector CLOB           PATH '$.embed_vector'
      )
    ) jt;

  COMMIT;
END;
/
```

---

## 7. Índice vetorial

```sql
CREATE VECTOR INDEX kb_chunks_vec_idx
ON kb_chunks (embedding)
ORGANIZATION INMEMORY NEIGHBOR GRAPH
DISTANCE COSINE;
```

Use a mesma métrica no índice e na query.

---

## 8. Função de busca por similaridade

```sql
CREATE OR REPLACE FUNCTION kb_search (
  p_question IN CLOB,
  p_top_k    IN NUMBER DEFAULT 5
) RETURN SYS_REFCURSOR
IS
  l_query_vector VECTOR;
  l_rc SYS_REFCURSOR;
BEGIN
  l_query_vector := kb_embed_text(p_question);

  OPEN l_rc FOR
    SELECT
      c.chunk_id,
      c.doc_id,
      d.source_name,
      d.source_uri,
      c.chunk_no,
      c.chunk_text,
      VECTOR_DISTANCE(c.embedding, l_query_vector, COSINE) AS distance
    FROM kb_chunks c
    JOIN kb_documents d
      ON d.doc_id = c.doc_id
    ORDER BY VECTOR_DISTANCE(c.embedding, l_query_vector, COSINE)
    FETCH FIRST p_top_k ROWS ONLY;

  RETURN l_rc;
END;
/
```

---

## 9. Teste no SQL

### Ingestão

```sql
BEGIN
  kb_ingest_text(
    p_source_name => 'politica_suporte.txt',
    p_source_uri  => 'https://exemplo/politica_suporte',
    p_mime_type   => 'text/plain',
    p_text        => 'Chamados P1 devem ser respondidos em até 15 minutos. Chamados P2 devem ser respondidos em até 2 horas.'
  );
END;
/
```

### Busca

```sql
VAR rc REFCURSOR;

BEGIN
  :rc := kb_search(
    p_question => 'Qual é o SLA para chamado P1?',
    p_top_k    => 3
  );
END;
/

PRINT rc;
```

---

## 10. Chamar ingestão no Python

```python
import os
import oracledb

DB_USER = os.environ["ADB_USER"]
DB_PASSWORD = os.environ["ADB_PASSWORD"]
DB_DSN = os.environ["ADB_DSN"]


def get_connection():
    return oracledb.connect(
        user=DB_USER,
        password=DB_PASSWORD,
        dsn=DB_DSN,
        config_dir=os.environ.get("TNS_ADMIN"),
        wallet_location=os.environ.get("TNS_ADMIN"),
        wallet_password=os.environ.get("ADB_WALLET_PASSWORD"),
    )


def ingest_text(source_name: str, text: str, source_uri: str | None = None):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.callproc(
                "KB_INGEST_TEXT",
                keywordParameters={
                    "P_SOURCE_NAME": source_name,
                    "P_SOURCE_URI": source_uri,
                    "P_MIME_TYPE": "text/plain",
                    "P_TEXT": text,
                },
            )
        conn.commit()
```

---

## 11. Chamar busca no Python

```python
def semantic_search(question: str, top_k: int = 5) -> list[dict]:
    with get_connection() as conn:
        with conn.cursor() as cur:
            out_cursor = cur.var(oracledb.CURSOR)

            cur.execute(
                """
                BEGIN
                  :rc := kb_search(
                    p_question => :question,
                    p_top_k    => :top_k
                  );
                END;
                """,
                rc=out_cursor,
                question=question,
                top_k=top_k,
            )

            rows_cursor = out_cursor.getvalue()
            columns = [d[0].lower() for d in rows_cursor.description]

            return [dict(zip(columns, row)) for row in rows_cursor]
```

---

## 12. Montar prompt RAG no Python

```python
def build_rag_prompt(question: str, hits: list[dict]) -> str:
    context_blocks = []

    for i, h in enumerate(hits, start=1):
        source = h.get("source_name") or "fonte_desconhecida"
        uri = h.get("source_uri") or ""
        text = h["chunk_text"]

        context_blocks.append(
            f"[Fonte {i}: {source} {uri}]\n{text}"
        )

    context = "\n\n---\n\n".join(context_blocks)

    return f"""
Você é um assistente de Knowledge Base.
Responda usando apenas o contexto abaixo.
Se o contexto não tiver a resposta, diga que não encontrou informação suficiente.

Contexto:
{context}

Pergunta:
{question}

Resposta:
""".strip()


def answer_with_rag(question: str):
    hits = semantic_search(question, top_k=5)
    prompt = build_rag_prompt(question, hits)

    # Chame aqui o LLM de sua escolha (referência: https://docs.oracle.com/en-us/iaas/Content/generative-ai/openai-compatible-api.htm)
    # Exemplo:
    # import openai
    # client = openai(base_url="https://inference.generativeai.${region}.oci.oraclecloud.com/openai/v1", api_key='sk-...')
    # response = client.chat.completions.create(...)
    # return response.choices[0].message.content
    return prompt
```


## 13. Pontos de atenção:

- Use o mesmo modelo de embedding para toda a Knowledge Base.
- Não misture embeddings de modelos diferentes na mesma coluna.
- Comece com `top_k = 5`.
- Use `COSINE` para embeddings textuais, salvo motivo específico.
- Guarde metadados como fonte, URI, área, dono e nível de acesso.
- Filtre permissões antes de enviar contexto para o LLM.
- Para PDF complexo, considere extrair texto no Python antes de enviar ao banco.

---

## 14. Fluxo final

```python
texto = "Chamados P1 devem ser respondidos em até 15 minutos."

ingest_text(
    source_name="politica_suporte.txt",
    source_uri="https://exemplo/politica_suporte",
    text=texto,
)

hits = semantic_search("Qual é o SLA de P1?", top_k=3)
prompt = build_rag_prompt("Qual é o SLA de P1?", hits)

print(prompt)
```

---

# Complemento: Expor RAG como MCP nativo do Autonomous AI Database 26ai

## MCP (Model Context Protocol)
Referência: https://docs.oracle.com/pt-br/iaas/autonomous-database-serverless/doc/mcp-server.html  

### 1. Habilitar MCP

Na própria console da OCI, adicione uma tag que faz a permissão de uso do MCP no banco:

Autonomous Database → Tags

```
Key: adb$feature
Value: {"name":"mcp_server","enable":true}
```

---

### 2. Usuário MCP

Crie um usuário exclusivo para o MCP e dê acesso aos elementos necessários.

```sql
CREATE USER MCP_USER IDENTIFIED BY "senha";

GRANT CREATE SESSION TO MCP_USER;

GRANT EXECUTE ON retrieval_func TO MCP_USER;
GRANT EXECUTE ON ingest_text TO MCP_USER;
GRANT EXECUTE ON gen_embedding TO MCP_USER;

GRANT SELECT ON kb_chunks TO MCP_USER;
GRANT SELECT ON kb_documents TO MCP_USER;

GRANT INSERT ON kb_chunks TO MCP_USER;
GRANT INSERT ON kb_documents TO MCP_USER;

GRANT EXECUTE ON DBMS_CLOUD_AI_AGENT TO MCP_USER;
```

---

### 3. Crie as tools para o MCP

Crie a ferramenta e aponte para a função que você deseja expor no MCP. 
`Dica: Quanto melhor for a sua descrição, maior são as chances da sua ferramenta ser acionada nos momentos pertinentes.`

#### 3.1 Tool de Retrieval

```sql
BEGIN
  DBMS_CLOUD_AI_AGENT.CREATE_TOOL(
    tool_name => 'search_kb',
    description => 'Busca semântica',
    implementation_type => 'PLSQL',
    implementation_name => 'RETRIEVAL_FUNC'
  );
END;
/
```

---

#### 3.2 Tool de Ingestão

```sql
BEGIN
  DBMS_CLOUD_AI_AGENT.CREATE_TOOL(
    tool_name => 'ingest_document',
    description => 'Ingestão com embedding',
    implementation_type => 'PLSQL',
    implementation_name => 'INGEST_TEXT'
  );
END;
/
```

---

### 4. Endpoint MCP
Substitua no endpoint a `região`, exemplo `us-chicago-1`, e `database_ocid`, exemplo `ocid1.autonomousdatabase.oc1.us-chicago-1...`.

```
https://dataaccess.adb.<region>.oraclecloudapps.com/adb/mcp/v1/databases/<database_ocid>
```

---

### 5. Endpoint do token para autenticação do MCP

```bash
curl -X POST \
"https://dataaccess.adb.<region>.oraclecloudapps.com/adb/auth/v1/databases/<database_ocid>/token" \
-H "Content-Type: application/json" \
-d '{
  "grant_type":"password",
  "username":"MCP_USER",
  "password":"senha"
}'
```

---

### 6. Exemplo de python (teste retrieval)

```python
import requests

REGION = "sa-saopaulo-1"
DB_OCID = "<database_ocid>"

BASE = f"https://dataaccess.adb.{REGION}.oraclecloudapps.com"

# token
t = requests.post(
    f"{BASE}/adb/auth/v1/databases/{DB_OCID}/token",
    json={
        "grant_type":"password",
        "username":"MCP_USER",
        "password":"senha"
    }
).json()["access_token"]

headers = {
    "Authorization": f"Bearer {t}",
    "Content-Type": "application/json"
}

# list tools
print(requests.post(
    f"{BASE}/adb/mcp/v1/databases/{DB_OCID}",
    headers=headers,
    json={"jsonrpc":"2.0","id":1,"method":"tools/list"}
).json())

# call retrieval
print(requests.post(
    f"{BASE}/adb/mcp/v1/databases/{DB_OCID}",
    headers=headers,
    json={
        "jsonrpc":"2.0",
        "id":2,
        "method":"tools/call",
        "params":{
            "name":"search_kb",
            "arguments":{
                "p_query":"Qual o SLA de P1?",
                "top_k":3
            }
        }
    }
).json())
```

---

### 7. Claude Code
O MCP também pode ser conectado a ferramentas externas, como por exemplo, Claude Code. Para isso, basta adicionar a configuração do MCP na ferramenta e fazer a autenticação com o usuário de MCP criado anteriormente.

Config MCP:

```json
{
  "mcpServers": {
    "oracle": {
      "url": "https://dataaccess.adb.<region>.oraclecloudapps.com/adb/mcp/v1/databases/<database_ocid>"
    }
  }
}
```

Login:

```
user: MCP_USER
password: senha
```