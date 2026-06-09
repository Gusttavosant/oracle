# Seu Agente na OCI com OpenClaw ou Hermes

Crie um agente próprio rodando dentro da sua OCI, com uma URL para conversar pelo navegador. A ideia é simples: a infraestrutura fica na sua tenancy, a VM roda o OpenClaw ou o Hermes, e as chamadas ao modelo passam pelo OCI Generative AI usando autenticação da própria instância.

Você não precisa colar API key de modelo, token de Telegram ou chat id. A stack sobe tudo, testa tudo e só termina com `Succeeded` quando o agente estiver pronto de verdade.

## Em Uma Frase

Você sobe uma stack, escolhe `openclaw` ou `hermes`, espera alguns minutos e recebe uma URL pronta para abrir o seu agente.

## Arquivo

Use este pacote:

```text
openclaw-hermes-oci-principal-v14.zip
```

Ele cria uma VM com `2 OCPU` e `16 GB` de RAM. A stack tenta usar `VM.Standard.E5.Flex` primeiro e, se precisar, tenta `VM.Standard.E6.Flex`.

O app é leve. Para uma versão mais econômica, ele também pode rodar em A1 Always Free, mas este pacote prioriza E5/E6 porque costuma ter uma experiência de subida mais previsível.

## O Que Fica Na OCI

Quase tudo que importa fica dentro da sua OCI:

- a VM onde o agente roda;
- a rede da VM;
- as regras de acesso;
- o app escolhido, OpenClaw ou Hermes.
- o acesso ao modelo enterprise via OCI Generative AI.

A pessoa conversa por fora, usando a interface web. Se você quiser, depois também pode conectar canais como Telegram no app. O agente e o modelo ficam do lado da OCI.

```mermaid
flowchart LR
    Web["Interface Web"]
    Telegram["Telegram"]

    subgraph OCI["OCI - sua tenancy"]
        subgraph VM["VM instance E5"]
            App["Hermes ou OpenClaw"]
        end
        Model["Enterprise AI Model OpenAI-compatible"]

        VM --> Model
    end

    Web --> VM
    Telegram -.-> VM

    class Web,Telegram purpleBox
    classDef purpleBox fill:#e1d5e7,stroke:#9673a6,stroke-width:2px,color:#4527a0

    style Telegram stroke-dasharray: 5 5,color:#4527a0

    style OCI fill:#f3f4f6,stroke:#111111,stroke-width:2px,stroke-dasharray: 5 5,color:#000000
    style VM fill:#f3f4f6,stroke:#111111,stroke-width:2px,color:#000000
    style App fill:#f3f4f6,stroke:#111111,stroke-width:1px,color:#000000
    style Model fill:#f3f4f6,stroke:#111111,stroke-width:2px,color:#000000
```

Em termos práticos:

- Fora da OCI fica a forma de interação: navegador e, se configurado depois, Telegram.
- Dentro da OCI fica a VM com Hermes ou OpenClaw.
- A VM conversa com o OCI Generative AI em formato OpenAI-compatible.
- O modelo é enterprise, consumido sob demanda e com proposta de zero retenção para inferência.

Para explicar de forma simples: a infraestrutura fica na sua OCI, e o modelo é consumido pelo OCI Generative AI com uma proposta de zero retenção para inferência. Segundo a documentação de tratamento de dados do serviço, prompts e respostas usados em inferência não são armazenados dentro do OCI Generative AI, e também não são compartilhados com provedores terceiros. Referência oficial: <https://docs.oracle.com/pt-br/iaas/Content/generative-ai/data-handling.htm>

## Custo, Sem Complicar

Pense no custo em três partes:

| Parte | Como pensar |
| --- | --- |
| Rede | VCN, subnet, route table e security list não cobram por existir. Para esse teste, pense na rede base como grátis; tráfego de saída pode seguir regras de cobrança da OCI. |
| VM | A VM paga por hora enquanto estiver ligada. Se desligar, para de consumir computação. O boot volume pode continuar existindo. |
| LLM | O modelo paga por consumo, normalmente por tokens de entrada e saída. Usou mais, paga mais; usou menos, paga menos. |

Resumo bem direto:

- para testar pouco, o maior cuidado é a VM ligada;
- para conversar bastante, o custo do LLM passa a importar;
- para economia máxima, uma variação com A1 Always Free pode ser usada;
- para uma subida mais tranquila, E5/E6 tende a ser mais confortável.

## Variáveis Que Você Preenche

Você precisa preencher só o essencial:

```text
tenancy_ocid   = ocid1.tenancy.oc1....
compartment_id = ocid1.compartment.oc1....
region         = sa-saopaulo-1
app            = openclaw
```

Para subir Hermes:

```text
app = hermes
```

Campos opcionais:

- `ssh_public_key`: pode deixar vazio para a stack gerar uma chave.
- `system_prompt`: o comportamento inicial do agente.
- `boot_volume_size_in_gbs`: tamanho do disco.
- `create_iam_policy`: deixe `true` para a stack criar as permissões necessárias.

## Encontrar o Compartment

Escolha onde os recursos vão morar dentro da sua OCI e copie o OCID do compartment.

<img width="1892" height="865" alt="Buscar compartment_id no ambiente OCI" src="https://github.com/user-attachments/assets/56b3f258-3ed2-4550-8161-92340f22c04a" />

## Criar a Stack

1. Abra o OCI Console.
2. Vá em `Developer Services`.
3. Entre em `Resource Manager`.
4. Clique em `Stacks`.
5. Clique em `Create Stack`.
6. Escolha upload de `.zip`.
7. Envie `openclaw-hermes-oci-principal-v14.zip`.
8. Escolha o compartment.
9. Dê um nome para a stack.

<img width="1906" height="1020" alt="Criar stack no Resource Manager" src="https://github.com/user-attachments/assets/ed8177d6-112e-470f-8662-229fdd768845" />

## Rodar o Apply

Marque `Run apply` na criação da stack ou rode um Apply depois.

<img width="1910" height="1035" alt="Rodar apply na stack" src="https://github.com/user-attachments/assets/7580d4a1-d47d-4916-b4a6-6dd3945f4b4e" />

Agora é só esperar. Normalmente leva em torno de 4 a 5 minutos.

Esse tempo não é só a VM nascendo. A stack também espera:

- o app terminar de instalar;
- a URL local responder;
- o modelo responder `OK`;
- a página temporária sair;
- o serviço final ficar ativo.

<img width="1050" height="311" alt="Apply em andamento" src="https://github.com/user-attachments/assets/8454a2be-821f-4ec0-a482-982e91f6c0f1" />

<img width="1125" height="415" alt="Apply concluido" src="https://github.com/user-attachments/assets/1897ecb2-2a81-4032-a879-b9132c77837b" />

Quando aparecer `Succeeded`, a experiência esperada é: abrir o output e usar.

## Abrir o Agente

Na stack, vá em outputs e procure `chat_url`.

<img width="1898" height="1020" alt="Outputs da stack com URL final" src="https://github.com/user-attachments/assets/b4f4576a-2971-47b7-81c5-72617aa67cac" />

Se você escolheu OpenClaw, a URL vem assim:

```text
http://IP_PUBLICO:18789/#token=TOKEN_GERADO
```

O token no final é só para abrir o gateway do OpenClaw. Ele não é uma chave da OCI.

Se você escolheu Hermes, a URL vem assim:

```text
http://IP_PUBLICO:9119
```

Abra no navegador e comece a conversar.

## E Agora Que O Agente Está Pronto?

Comece simples. Trate o agente como alguém que acabou de chegar no seu ambiente e pode te ajudar a organizar, investigar e construir coisas.

Algumas ideias de primeiros pedidos:

- "Pesquise concorrentes da minha empresa..."
- "Me manda todos os dias as 8h as noticias de AI do dia"
- "Leia os arquivos deste projeto e me diga como melhorar a documentação."
- "Me ajude a conectar este agente ao Telegram usando token."
- "Ative a conversa por voz, eu quero te mandar audio."
- "Crie uma página publica com as suas métricas da VM, que tenha consumo de CPU, RAM"

Você também pode pedir coisas mais abertas, como:

```text
Quero transformar este agente em um assistente pessoal de operações.
Sempre me responda desse jeito.
```

Ou:

```text
Quero que você trabalhe comigo pelo WhatsApp.
Você consegue configurar isso sozinho?
```

### Opcional: Conectar Com Telegram

O Telegram não é obrigatório para subir a stack. A interface web já funciona logo depois do `Succeeded`.

Mas, se você quiser conversar pelo celular, uma boa próxima etapa é criar um bot no Telegram e pedir para o próprio agente te ajudar a conectar esse canal.

Para gerar o token:

1. Abra o Telegram.
2. Procure por `@BotFather`.
3. Envie `/start`.
4. Envie `/newbot`.
5. Escolha o nome do bot.
6. Escolha o username do bot.
7. Copie o token retornado.
8. Volte para o agente e peça para configurar o Telegram com esse token.

<img width="1838" height="813" alt="Criar bot no Telegram com BotFather" src="https://github.com/user-attachments/assets/d9ec5059-155a-426b-8bc3-234d11618a4f" />

Um exemplo de pedido para fazer ao agente:

```text
Configure um canal Telegram para este agente.
Meu bot token é: COLE_AQUI_O_TOKEN
Me diga também como testar se está respondendo corretamente.
```

Guarde esse token com cuidado. Ele dá acesso ao seu bot.

