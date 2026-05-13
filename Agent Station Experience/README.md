# OpenClaw on OCI via Terraform
Criando seu próprio agente e habilitando ele para conversar com você na palma da sua mão, em minutos.

## Arquivo para usar

- `openclaw-terraform-E5.zip` (Preferência, sobe uma VM E5)
- `openclaw-terraform.zip` (Sobe uma VM A1, as vezes sem disponibilidade, mas é Always-free)

## Variáveis

- `compartment_id`
- `api_key`
- `telegram_bot_token`
- `telegram_chat_id`

## 1. Criar o bot no Telegram

Intale o Telegram no seu celular e crie uma conta com seu numero. Uma vez que tiver a conta criada, siga os passos:

1. Abra o Telegram.
2. Procure por `@BotFather`.
3. Envie `/start`.
4. Envie `/newbot`.
5. Escolha o nome do bot.
6. Escolha o username do bot.
7. Copie o token retornado.
8. Use esse valor em `telegram_bot_token`.

<img width="1838" height="813" alt="image" src="https://github.com/user-attachments/assets/d9ec5059-155a-426b-8bc3-234d11618a4f" />


## 2. Descobrir o `chat_id`

1. Abra uma conversa com o bot.
2. Envie `/start`.
3. Envie `oi`.
4. Abra:

```text
https://api.telegram.org/botSEU_TOKEN/getUpdates
```
<img width="1657" height="1020" alt="image" src="https://github.com/user-attachments/assets/3a9f454c-8a11-4d1f-9d1b-8d0e3b501b4e" />

5. Procure por:

```json
message.chat.id
```
<img width="1258" height="158" alt="image" src="https://github.com/user-attachments/assets/85cef3de-c841-4886-b9dd-ff22d4cd0926" />


6. Use esse valor em `telegram_chat_id`.

## 3. Separar os 4 valores

```text
compartment_id     = ocid1.compartment.oc1....
api_key            = sk-...
telegram_bot_token = 123456789:ABC...
telegram_chat_id   = 123456789
```
Buscar compartment_id no seu ambiente trial:
<img width="1892" height="865" alt="image" src="https://github.com/user-attachments/assets/56b3f258-3ed2-4550-8161-92340f22c04a" />

Criar uma API key no seu ambiente:
<img width="2642" height="1021" alt="image" src="https://github.com/user-attachments/assets/0050854a-75e0-41b8-8c33-4e659ebc6e37" />

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

<img width="1906" height="1020" alt="image" src="https://github.com/user-attachments/assets/ed8177d6-112e-470f-8662-229fdd768845" />

## 5. Preencher as variáveis

Preencha:

- `compartment_id`
- `api_key`
- `telegram_bot_token`
- `telegram_chat_id`

<img width="1897" height="1027" alt="image" src="https://github.com/user-attachments/assets/d3388305-0153-4d8e-8a48-4737982d5e4b" />

## 6. Rodar o Apply

1. Ainda na Stack.
2. Marque `Run apply`.
3. E clique para criar.

<img width="1910" height="1035" alt="image" src="https://github.com/user-attachments/assets/7580d4a1-d47d-4916-b4a6-6dd3945f4b4e" />

Aguarde até a configuração completar, esse processo pode demorar em torno de 5 minutos para concluir:
<img width="1050" height="311" alt="image" src="https://github.com/user-attachments/assets/8454a2be-821f-4ec0-a482-982e91f6c0f1" />
<img width="1125" height="415" alt="image" src="https://github.com/user-attachments/assets/1897ecb2-2a81-4032-a879-b9132c77837b" />

Recursos criados:

- `openclaw-standalone`
- `openclaw-standalone-vcn`
- `openclaw-standalone-public-subnet`
- `openclaw-standalone-public-sl`
- `openclaw-standalone-public-rt`
- `openclaw-standalone-igw`
- `tls_private_key.ssh`

## 7. Abrir a interface

URL base:

```text
http://IP_PUBLICO:18789
```

Você encontra essas informações em output, assim que seu job estiver com status `Succeeded`:
<img width="1898" height="1020" alt="image" src="https://github.com/user-attachments/assets/b4f4576a-2971-47b7-81c5-72617aa67cac" />

## 8. Testar no Telegram

1. Nesse momento o OpenClaw já deve enviar uma primeira mensagem para o seu chat no Telegram.
2. Envie `oi`.
3. Aguarde a resposta.

Agora você já pode utilizar seu agente 24/7 para trabalhar por você, criar rotinas e buscar na web diretamente do seu celular. Ele é capaz de desenvolver código e rodar no próprio ambiente em que foi configurado, então aproveite essa capacidade para criar o que você precisa com mais liberdade e `inteligência`.
