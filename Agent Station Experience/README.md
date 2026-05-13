# OpenClaw Standalone on OCI via Terraform

## Arquivo para usar

- `novo-v6.zip`

## Variáveis

- `compartment_id`
- `api_key`
- `telegram_bot_token`
- `telegram_chat_id`

## 1. Criar o bot no Telegram

1. Abra o Telegram.
2. Procure por `@BotFather`.
3. Envie `/start`.
4. Envie `/newbot`.
5. Escolha o nome do bot.
6. Escolha o username do bot.
7. Copie o token retornado.
8. Use esse valor em `telegram_bot_token`.

```md
<!-- SCREENSHOT: telegram-botfather-create-bot -->
<!-- Cole aqui a imagem do BotFather criando o bot -->
```

## 2. Descobrir o `chat_id`

1. Abra uma conversa com o bot.
2. Envie `/start`.
3. Envie `oi`.
4. Abra:

```text
https://api.telegram.org/botSEU_TOKEN/getUpdates
```

5. Procure por:

```json
message.chat.id
```

6. Use esse valor em `telegram_chat_id`.

```md
<!-- SCREENSHOT: telegram-chat-id -->
<!-- Cole aqui a imagem mostrando como localizar o chat_id -->
```

## 3. Separar os 4 valores

```text
compartment_id     = ocid1.compartment.oc1....
api_key            = sk-...
telegram_bot_token = 123456789:ABC...
telegram_chat_id   = 123456789
```

## 4. Criar a Stack na OCI

1. Abra o OCI Console.
2. Vá em `Developer Services`.
3. Entre em `Resource Manager`.
4. Clique em `Stacks`.
5. Clique em `Create Stack`.
6. Escolha upload de `.zip`.
7. Envie `novo-v6.zip`.
8. Escolha o compartment.
9. Dê um nome para a stack.

```md
<!-- SCREENSHOT: oci-stack-create-start -->
<!-- Cole aqui o print da tela inicial de criação da Stack -->
```

```md
<!-- SCREENSHOT: oci-stack-upload-zip -->
<!-- Cole aqui o print do upload do arquivo ZIP -->
```

## 5. Preencher as variáveis

Preencha:

- `compartment_id`
- `api_key`
- `telegram_bot_token`
- `telegram_chat_id`

```md
<!-- SCREENSHOT: oci-stack-variables -->
<!-- Cole aqui o print da tela de variáveis da Stack -->
```

## 6. Rodar o Plan

1. Abra a Stack.
2. Clique em `Plan`.
3. Aguarde terminar.

Recursos principais:

- `openclaw-standalone`
- `openclaw-standalone-vcn`
- `openclaw-standalone-public-subnet`
- `openclaw-standalone-public-sl`
- `openclaw-standalone-public-rt`
- `openclaw-standalone-igw`
- `tls_private_key.ssh`

```md
<!-- SCREENSHOT: oci-stack-plan -->
<!-- Cole aqui o print do resultado do Plan -->
```

## 7. Rodar o Apply

1. Clique em `Apply`.
2. Aguarde terminar.

```md
<!-- SCREENSHOT: oci-stack-apply -->
<!-- Cole aqui o print da execução do Apply -->
```

## 8. Abrir os Outputs

Depois do `Apply`, abra `Outputs`.

Os mais importantes:

- `public_ip`
- `ssh_command`
- `ssh_private_key_pem`
- `dashboard_host`
- `dashboard_url_file`
- `dashboard_token_file`
- `bootstrap_progress_file`
- `bootstrap_status_file`
- `bootstrap_error_file`
- `bootstrap_log_file`
- `cloud_init_output_file`
- `postchecks_log_file`

```md
<!-- SCREENSHOT: oci-stack-outputs -->
<!-- Cole aqui o print da tela de Outputs -->
```

## 9. Salvar a chave SSH

Copie o valor de `ssh_private_key_pem` e salve como:

```text
generated_ssh_key.pem
```

Depois:

```bash
chmod 600 generated_ssh_key.pem
```

## 10. Acessar a VM

Use o output `ssh_command`.

Ou:

```bash
ssh -i generated_ssh_key.pem opc@SEU_IP_PUBLICO
```

## 11. Acompanhar o bootstrap

```bash
cat /home/opc/openclaw-bootstrap-progress.txt
```

```bash
cat /home/opc/openclaw-bootstrap-status.txt
```

```bash
cat /home/opc/openclaw-bootstrap-error.txt
```

```bash
sudo tail -n 200 /var/log/openclaw-bootstrap.log
```

```bash
sudo tail -n 200 /var/log/openclaw-postchecks.log
```

```bash
sudo tail -n 200 /var/log/cloud-init-output.log
```

## 12. Ver se o OpenClaw está saudável

```bash
source /home/opc/.openclaw/openclaw.env
"$OPENCLAW_BIN" health --json
```

Esperado:

- `"ok": true`
- Telegram com `running: true`
- Telegram com `connected: true`

## 13. Abrir a interface

URL base:

```text
http://IP_PUBLICO:18789
```

Token:

```text
/home/opc/openclaw-dashboard-token.txt
```

URL pronta com token:

```text
/home/opc/openclaw-dashboard-url.txt
```

```md
<!-- SCREENSHOT: openclaw-dashboard-login -->
<!-- Cole aqui o print da primeira tela do OpenClaw -->
```

## 14. Testar no Telegram

1. Abra a conversa com o bot.
2. Envie `oi`.
3. Aguarde a resposta.

## 15. Se não responder

```bash
cat /home/opc/openclaw-bootstrap-error.txt
```

```bash
sudo tail -n 200 /var/log/openclaw-bootstrap.log
```

```bash
source /home/opc/.openclaw/openclaw.env
"$OPENCLAW_BIN" health --json
```

Veja principalmente:

- `telegram.running`
- `telegram.connected`
- `telegram.lastError`

## Arquivos úteis na VM

- `/var/log/openclaw-bootstrap.log`
- `/var/log/openclaw-postchecks.log`
- `/var/log/cloud-init-output.log`
- `/home/opc/openclaw-bootstrap-progress.txt`
- `/home/opc/openclaw-bootstrap-error.txt`
- `/home/opc/openclaw-bootstrap-status.txt`
- `/home/opc/openclaw-dashboard-url.txt`
- `/home/opc/openclaw-dashboard-token.txt`
- `/home/opc/openclaw-direct-smoke.json`
- `/home/opc/openclaw-gateway-health.json`
- `/home/opc/openclaw-model-smoke.json`
- `/home/opc/openclaw-telegram-smoke.json`
