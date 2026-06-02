# Benchmark Generative AI

Este repositório foi preparado para facilitar a execução de benchmarks de modelos
na OCI usando a API OpenAI-compatible com `api_key`.

A ideia aqui é ser simples de reproduzir: configurar as credenciais, rodar o
benchmark e gerar um resumo final das métricas.

## O que tem nesta pasta

- `oci_benchmark.sh`
  Script principal que executa o benchmark no endpoint da OCI.
- `.env.example`
  Arquivo de exemplo com as variáveis que precisam ser preenchidas.
- `setup_genai_bench.sh`
  Script de instalação do `genai-bench` em um ambiente virtual local.
- `patch_genai_bench.py`
  Ajuste automático para evitar que o benchmark falhe quando algumas métricas,
  como `TPOT`, não estiverem disponíveis.
- `export_oracle_style_summary.py`
  Gera uma tabela de resumo no estilo Oracle a partir dos arquivos JSON do
  benchmark.

## Como usar

### 1. Criar o arquivo de configuração

Copie o arquivo de exemplo:

```bash
cp .env.example .env
```

Depois preencha os dados principais:

```bash
OCI_GENAI_API_KEY="sk-..."
REGION="us-chicago-1"
MODEL_ID="ocid1.generativeaiendpoint.oc1...."
```

## 2. Instalar o genai-bench

```bash
bash ./setup_genai_bench.sh
export GENAI_BENCH_BIN="$(pwd)/.venv-genai-bench/bin/genai-bench"
```

Esse passo cria um ambiente virtual local e instala o `genai-bench` já com o
ajuste necessário para esse tipo de benchmark.

## 3. Rodar o benchmark

```bash
bash ./oci_benchmark.sh
```

Ao final, será criada uma pasta com nome parecido com este:

```bash
benchmark_run_YYYYMMDD_HHMMSS
```

É nessa pasta que ficam os resultados completos da execução.

## 4. Gerar o resumo final

Depois da execução, rode:

```bash
python3 ./export_oracle_style_summary.py ./benchmark_run_YYYYMMDD_HHMMSS
```

Esse comando gera dois arquivos:

- `oracle_style_summary.md`
- `oracle_style_summary.csv`

Esses arquivos trazem um resumo mais fácil de usar em apresentações, relatórios
e comparações.

## O que pode ser ajustado

No arquivo `.env`, você pode alterar:

- `TRAFFIC_SCENARIO`
  para mudar o perfil de carga
- `CONCURRENCY_LEVELS`
  para testar mais ou menos concorrência
- `MAX_TIME_PER_RUN`
  para aumentar ou reduzir a duração de cada rodada
- `MAX_REQUESTS_PER_RUN`
  para controlar o volume máximo de requests
- `MODEL_TOKENIZER`
  para usar o tokenizer mais adequado ao modelo testado

## Observações importantes

- O endpoint usado aqui é o da API OpenAI-compatible da OCI.
- O valor de `OPENAI_BASE_URL` deve terminar em `/openai`, porque o
  `genai-bench` já adiciona o caminho de `chat/completions`.
- Em alguns modelos/endpoints, a métrica de `TPOT` pode não sair de forma
  confiável. Quando isso acontece, o benchmark continua rodando e deixa essa
  métrica vazia, em vez de falhar.
- O resumo final gerado pelo script usa os dados das requisições individuais,
  o que ajuda a manter as médias consistentes mesmo quando algumas métricas não
  estão disponíveis.

## Resultado esperado

Ao final, você terá:

- os arquivos brutos da execução em JSON
- os gráficos e artefatos gerados pelo `genai-bench`
- uma tabela resumida em formato fácil de compartilhar com cliente
