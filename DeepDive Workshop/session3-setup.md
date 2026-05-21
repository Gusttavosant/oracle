## Session 3 - Setup

### Criar uma API key no seu ambiente:
<img width="2642" height="1021" alt="image" src="https://github.com/user-attachments/assets/0050854a-75e0-41b8-8c33-4e659ebc6e37" />

### No mesmo serviço, crie um projeto e habilite o short-term memory e o long-term memory
<img width="3310" height="1021" alt="image" src="https://github.com/user-attachments/assets/ea7563db-4549-448e-870d-54a5957c5d3f" />

### Agora crie uma chave IAM seguindo os passos
<img width="2965" height="1028" alt="image" src="https://github.com/user-attachments/assets/518ead2f-2c81-430a-aa73-fff18fa00e86" />

Salve todos os ids em um bloco de notas para usar no arquivo `.env` onde você vai rolar o código. 


## RAG no Autonomous com PDF publico

Este roteiro cria um fluxo RAG direto no banco: registra credencial de embedding, baixa um PDF publico, extrai texto, gera chunks, gera embeddings vetoriais e faz consulta semantica por similaridade.

## 1) ACL de rede
Concede acesso de saida para baixar o PDF publico e chamar o endpoint de embedding do OCI GenAI.

```sql
begin
  dbms_network_acl_admin.append_host_ace(
    host => 'raw.githubusercontent.com',
    ace  => xs$ace_type(
      privilege_list => xs$name_list('resolve'),
      principal_name => 'ADMIN',
      principal_type => xs_acl.ptype_db
    )
  );
end;
/

begin
  dbms_network_acl_admin.append_host_ace(
    host       => 'raw.githubusercontent.com',
    lower_port => 443,
    upper_port => 443,
    ace        => xs$ace_type(
      privilege_list => xs$name_list('connect'),
      principal_name => 'ADMIN',
      principal_type => xs_acl.ptype_db
    )
  );
end;
/

begin
  dbms_network_acl_admin.append_host_ace(
    host => 'inference.generativeai.<REGIAO>.oci.oraclecloud.com',
    ace  => xs$ace_type(
      privilege_list => xs$name_list('resolve'),
      principal_name => 'ADMIN',
      principal_type => xs_acl.ptype_db
    )
  );
end;
/

begin
  dbms_network_acl_admin.append_host_ace(
    host       => 'inference.generativeai.<REGIAO>.oci.oraclecloud.com',
    lower_port => 443,
    upper_port => 443,
    ace        => xs$ace_type(
      privilege_list => xs$name_list('connect'),
      principal_name => 'ADMIN',
      principal_type => xs_acl.ptype_db
    )
  );
end;
/
```

## 2) Credencial OCI GenAI
Cria a credencial IAM usada pelo `DBMS_VECTOR_CHAIN` para gerar embedding.

```sql
begin
  dbms_vector_chain.drop_credential('OCI_CRED');
exception when others then null;
end;
/

begin
  dbms_vector_chain.create_credential(
    credential_name => 'OCI_CRED',
    params => json('{
      "user_ocid":"<USER_OCID>",
      "tenancy_ocid":"<TENANCY_OCID>",
      "compartment_ocid":"<COMPARTMENT_OCID>",
      "fingerprint":"<FINGERPRINT>",
      "private_key":"<PRIVATE_KEY_PEM_COM_\\n>"
    }')
  );
end;
/
```
Atenção: Private key sempre deve ser em uma linha, remova todos as quebras de linha para funcionar. 

## 3) Ingestão do PDF
Cria tabela de documentos e baixa o PDF via URL RAW.

```sql
begin execute immediate 'drop table admin.wc_docs purge'; exception when others then null; end;
/

create table admin.wc_docs (
  doc_id      number generated always as identity primary key,
  source_url  varchar2(2000),
  doc_blob    blob
);

insert into admin.wc_docs (source_url, doc_blob)
select
  'https://raw.githubusercontent.com/MachadoAmanda/oracle/main/DeepDive%20Workshop/regulations_for_fifa_world_cup_2026.pdf',
  dbms_cloud.get_object(
    credential_name => null,
    object_uri      => 'https://raw.githubusercontent.com/MachadoAmanda/oracle/main/DeepDive%20Workshop/regulations_for_fifa_world_cup_2026.pdf'
  )
from dual;

commit;
```

## 4) Chunk + embedding (raw)
Extrai texto, divide em chunks e chama embedding (`cohere.embed-multilingual-v3.0`).
Não esqueça de substituir a região pela região desejada, por exemplo `sa-saopaulo-1` ou `us-chicago-1`.

```sql
begin execute immediate 'drop table admin.wc_chunks_raw purge'; exception when others then null; end;
/

create table admin.wc_chunks_raw as
select
  d.doc_id,
  jt.embed_id       as chunk_id,
  jt.embed_data     as chunk_text,
  jt.embed_vector   as embed_vector_raw
from admin.wc_docs d,
     dbms_vector_chain.utl_to_embeddings(
       dbms_vector_chain.utl_to_chunks(
         dbms_vector_chain.utl_to_text(d.doc_blob),
         json('{"by":"words","max":"200","overlap":"40","normalize":"all"}')
       ),
       json('{
         "provider":"ocigenai",
         "credential_name":"OCI_CRED",
         "url":"https://inference.generativeai.<REGIAO>.oci.oraclecloud.com/20231130/actions/embedText",
         "model":"cohere.embed-multilingual-v3.0"
       }')
     ) e,
     json_table(
       e.column_value, '$[*]'
       columns (
         embed_id     number path '$.embed_id',
         embed_data   clob   path '$.embed_data',
         embed_vector clob   path '$.embed_vector'
       )
     ) jt;
```

## 5) Conversão para tabela vetorial final
Converte a saida raw para coluna vetorial (`VECTOR`).

```sql
begin execute immediate 'drop table admin.wc_chunks purge'; exception when others then null; end;
/

create table admin.wc_chunks as
select
  doc_id,
  chunk_id,
  chunk_text,
  to_vector(
    replace(
      replace(
        dbms_lob.substr(embed_vector_raw, 32767, 1),
        '"[','['
      ),
      ']"',']'
    )
  ) as embed_vector
from admin.wc_chunks_raw;
```

## 6) Consulta semantica (retrieval)
Gera embedding da pergunta e retorna os chunks mais próximos por cosseno.
Não esqueça de substituir a região pela região desejada, por exemplo `sa-saopaulo-1` ou `us-chicago-1`.

```sql
with qv as (
  select dbms_vector_chain.utl_to_embedding(
    'Quais s�o os crit�rios de desempate na fase de grupos da Copa 2026?',
    json('{
      "provider":"ocigenai",
      "credential_name":"OCI_CRED",
      "url":"https://inference.generativeai.<REGIAO>.oci.oraclecloud.com/20231130/actions/embedText",
      "model":"cohere.embed-multilingual-v3.0"
    }')
  ) as qvec
  from dual
)
select
  c.chunk_id,
  substr(c.chunk_text,1,500) as trecho,
  vector_distance(c.embed_vector, qv.qvec, cosine) as dist
from admin.wc_chunks c, qv
order by dist
fetch first 5 rows only;
```
