# Monitoramento de Aplicações Serverless na AWS — Lambda + DynamoDB

Guia de referência para configurar alarmes CloudWatch em projetos que usam AWS Lambda
e DynamoDB. Criado a partir da análise dos projetos `metads.app` e `ytbrowser` em
2026-04-20, após a implementação de monitoramento EC2 em `study-amigo.app`.

**Projetos cobertos por este documento:**
- `metads.app` — 8 funções Lambda (metaads-dev-*) + DynamoDB `metaads-dev-table`
- `ytbrowser` — 1 função Lambda (ytchannel-browser-dev-api) + 3 tabelas DynamoDB

**Pré-requisito:** SNS topic `study-amigo-alerts` já existe e está subscrito em
`ewerton.madruga@icloud.com`. Reutilizar o mesmo topic para todos os projetos.

---

## Por que Lambda falha de forma diferente de EC2

Em EC2, a infraestrutura pode falhar (host impaired, rede, disco). Em Lambda, a AWS
gerencia toda a infraestrutura — você nunca verá um "StatusCheckFailed". Porém Lambda
introduz falhas próprias, muitas delas **silenciosas**: a função é invocada, falha
internamente, e ninguém é notificado a menos que alarmes estejam configurados.

---

## Catálogo de eventos comuns em Lambda

### 1. Erros de execução (`Errors`)

**O que é:** A função lançou uma exceção não tratada, retornou um erro, ou foi
encerrada abruptamente (segfault em container, OOM interno).

**Por que é crítico:** Em invocações assíncronas (SQS, EventBridge, S3), o erro
**não chega ao chamador** — o job simplesmente falha em silêncio. Em invocações
síncronas (API Gateway), o usuário recebe um 502.

**Funções de alto risco aqui:**
- `metaads-dev-collect-worker` (timeout 900s) — job longo, erro no meio = trabalho perdido
- `metaads-dev-competitors-scraper` (container, timeout 300s) — sem runtime gerenciado
- `metaads-dev-collect-scheduler` — se falha, toda a pipeline de coleta para

**Alarme recomendado:**
```bash
# Exemplo para uma função (repetir para cada função crítica)
aws cloudwatch put-metric-alarm \
  --alarm-name "lambda-metaads-collect-worker-errors" \
  --alarm-description "Erros na função collect-worker — jobs de coleta falhando" \
  --metric-name Errors \
  --namespace AWS/Lambda \
  --statistic Sum \
  --dimensions Name=FunctionName,Value=metaads-dev-collect-worker \
  --period 60 \
  --evaluation-periods 1 \
  --threshold 1 \
  --comparison-operator GreaterThanOrEqualToThreshold \
  --treat-missing-data notBreaching \
  --alarm-actions <SNS_ARN> \
  --region us-east-1 --profile study-amigo
```

---

### 2. Throttling (`Throttles`)

**O que é:** A AWS limita o número de execuções simultâneas de Lambda. O limite padrão
por conta é **1.000 execuções concorrentes** (compartilhado entre todas as funções da
conta). Se esse limite for atingido, novas invocações são rejeitadas com erro 429.

**Por que é crítico para estes projetos:**
- `metaads-dev-collect-worker` tem timeout de **900 segundos**. Uma única invocação
  ocupa 1 slot de concorrência por 15 minutos. Se 10 workers rodarem em paralelo,
  consomem 10 slots por 15 min cada.
- `metaads-dev-competitors-scraper` (300s) tem o mesmo problema.
- Se throttling ocorrer em `metaads-dev-auth` ou `ytchannel-browser-dev-api`, o
  **usuário vê erro imediatamente**.

**Funções de alto risco:** todas, mas especialmente as de longa duração.

**Alarme recomendado:**
```bash
aws cloudwatch put-metric-alarm \
  --alarm-name "lambda-metaads-throttles" \
  --alarm-description "Throttling em funções metaads — limite de concorrência atingido" \
  --metric-name Throttles \
  --namespace AWS/Lambda \
  --statistic Sum \
  --dimensions Name=FunctionName,Value=metaads-dev-collect-worker \
  --period 60 \
  --evaluation-periods 1 \
  --threshold 1 \
  --comparison-operator GreaterThanOrEqualToThreshold \
  --treat-missing-data notBreaching \
  --alarm-actions <SNS_ARN> \
  --region us-east-1 --profile study-amigo
```

---

### 3. Timeout (`Duration` próximo do limite)

**O que é:** A função é encerrada à força quando atinge o timeout configurado. Não
lança exceção — simplesmente para no meio da execução. Dados parcialmente processados
podem ficar inconsistentes.

**Por que é crítico:**
- `collect-worker` tem timeout de 900s (15 min). Se a duração média se aproximar de
  900s, significa que jobs estão quase sempre no limite — qualquer variação corta o
  processamento.
- Lambda **não avisa** quando uma função é encerrada por timeout a menos que você
  monitore.

**Alarme recomendado (alerta quando média > 80% do timeout):**
```bash
# collect-worker: timeout=900s → alertar se média > 720s
aws cloudwatch put-metric-alarm \
  --alarm-name "lambda-metaads-collect-worker-duration" \
  --alarm-description "collect-worker durando > 720s (80% do timeout de 900s)" \
  --metric-name Duration \
  --namespace AWS/Lambda \
  --statistic Average \
  --dimensions Name=FunctionName,Value=metaads-dev-collect-worker \
  --period 300 \
  --evaluation-periods 2 \
  --threshold 720000 \
  --comparison-operator GreaterThanOrEqualToThreshold \
  --treat-missing-data notBreaching \
  --alarm-actions <SNS_ARN> \
  --region us-east-1 --profile study-amigo
```

> **Nota:** `Duration` é reportado em **milissegundos** — 720s = 720.000ms.

---

### 4. Falha em Dead Letter Queue / destino de erro (`DeadLetterErrors`)

**O que é:** Funções assíncronas (acionadas por EventBridge, SQS, S3) que falham
são automaticamente reprocessadas pela AWS (até 2 tentativas, com backoff). Se todas
as tentativas falharem, a invocação deveria ir para uma Dead Letter Queue (DLQ) ou
destino de falha. Se a DLQ também falhar (permissão errada, fila cheia), o evento é
descartado completamente.

**Por que é crítico:** Jobs de coleta perdidos = dados faltando. Sem DLQ configurada,
nem há onde o evento ir.

**Ação recomendada antes do alarme:**
1. Verificar se `collect-scheduler` e `collect-trigger` têm DLQ configurada:
   ```bash
   aws lambda get-function-event-invoke-config \
     --function-name metaads-dev-collect-scheduler \
     --region us-east-1 --profile study-amigo
   ```
2. Se não tiver, configurar uma SQS queue como DLQ.

**Alarme:**
```bash
aws cloudwatch put-metric-alarm \
  --alarm-name "lambda-metaads-dead-letter-errors" \
  --alarm-description "Falha ao entregar evento à DLQ — invocações sendo descartadas" \
  --metric-name DeadLetterErrors \
  --namespace AWS/Lambda \
  --statistic Sum \
  --dimensions Name=FunctionName,Value=metaads-dev-collect-scheduler \
  --period 60 \
  --evaluation-periods 1 \
  --threshold 1 \
  --comparison-operator GreaterThanOrEqualToThreshold \
  --treat-missing-data notBreaching \
  --alarm-actions <SNS_ARN> \
  --region us-east-1 --profile study-amigo
```

---

### 5. Erros no API Gateway (`5XXError`)

**O que é:** O API Gateway retorna HTTP 5xx quando a Lambda falha, tem timeout, ou
é throttled. Este é o único alarme que monitora o **ponto de vista do usuário** —
os outros monitoram a função internamente.

**Funções expostas via API Gateway:**
- `ytchannel-browser-dev-api` — interface pública do ytbrowser
- `metaads-dev-auth`, `metaads-dev-ads`, `metaads-dev-niches`, `metaads-dev-saved`,
  `metaads-dev-competitors` — endpoints da metads.app

**Alarme recomendado:**
```bash
# Buscar o nome da API primeiro:
aws apigateway get-rest-apis --region us-east-1 --profile study-amigo \
  --query 'items[*].{Nome:name,Id:id}' --output table

# Depois criar o alarme por API (substituir API_NAME pelo nome real):
aws cloudwatch put-metric-alarm \
  --alarm-name "apigw-ytbrowser-5xx" \
  --alarm-description "API Gateway ytbrowser retornando 5XX — usuários impactados" \
  --metric-name 5XXError \
  --namespace AWS/ApiGateway \
  --statistic Sum \
  --dimensions Name=ApiName,Value=<API_NAME> \
  --period 60 \
  --evaluation-periods 2 \
  --threshold 5 \
  --comparison-operator GreaterThanOrEqualToThreshold \
  --treat-missing-data notBreaching \
  --alarm-actions <SNS_ARN> \
  --region us-east-1 --profile study-amigo
```

---

## Catálogo de eventos comuns em DynamoDB

### 6. Throttling de leitura/escrita (`ReadThrottleEvents`, `WriteThrottleEvents`)

**O que é:** Mesmo em modo **PAY_PER_REQUEST** (on-demand), o DynamoDB tem um limite
de burst interno. Se a taxa de requisições aumentar muito rápido (mais que o dobro em
30 minutos), o DynamoDB throttla temporariamente até escalar.

**Por que é relevante aqui:** Ambas as tabelas são on-demand:
- `metaads-dev-table` — PAY_PER_REQUEST
- `ytchannel-browser-dev-*` — PAY_PER_REQUEST

Em on-demand, throttling é raro mas pode ocorrer em picos abruptos (ex.: scraper
disparando muitas escritas simultâneas).

**Alarme recomendado:**
```bash
aws cloudwatch put-metric-alarm \
  --alarm-name "dynamo-metaads-write-throttle" \
  --alarm-description "DynamoDB metaads-dev-table com WriteThrottleEvents" \
  --metric-name WriteThrottleEvents \
  --namespace AWS/DynamoDB \
  --statistic Sum \
  --dimensions Name=TableName,Value=metaads-dev-table \
  --period 60 \
  --evaluation-periods 2 \
  --threshold 10 \
  --comparison-operator GreaterThanOrEqualToThreshold \
  --treat-missing-data notBreaching \
  --alarm-actions <SNS_ARN> \
  --region us-east-1 --profile study-amigo
```

---

### 7. Erros do sistema DynamoDB (`SystemErrors`)

**O que é:** Erros internos da AWS no DynamoDB (HTTP 5xx). Raros, mas acontecem
durante eventos de infraestrutura AWS. Diferente dos erros de throttling — aqui
a falha é da AWS, não do seu código ou da sua capacidade.

**Alarme recomendado:**
```bash
aws cloudwatch put-metric-alarm \
  --alarm-name "dynamo-metaads-system-errors" \
  --alarm-description "Erros internos AWS no DynamoDB metaads — evento de infraestrutura" \
  --metric-name SystemErrors \
  --namespace AWS/DynamoDB \
  --statistic Sum \
  --dimensions Name=TableName,Value=metaads-dev-table \
  --period 60 \
  --evaluation-periods 1 \
  --threshold 1 \
  --comparison-operator GreaterThanOrEqualToThreshold \
  --treat-missing-data notBreaching \
  --alarm-actions <SNS_ARN> \
  --region us-east-1 --profile study-amigo
```

---

### 8. Latência alta (`SuccessfulRequestLatency`)

**O que é:** Tempo médio de resposta do DynamoDB acima do esperado. Em condições
normais, operações de chave primária levam < 10ms. Latência alta indica:
- Hot partition (muitas requisições na mesma chave)
- Tabela crescendo sem GSI adequado (full scan)
- Problema de infraestrutura AWS

**Alarme recomendado:**
```bash
aws cloudwatch put-metric-alarm \
  --alarm-name "dynamo-ytbrowser-latency" \
  --alarm-description "DynamoDB ytbrowser-data com latência > 50ms" \
  --metric-name SuccessfulRequestLatency \
  --namespace AWS/DynamoDB \
  --statistic Average \
  --dimensions Name=TableName,Value=ytchannel-browser-dev-data Name=Operation,Value=GetItem \
  --period 300 \
  --evaluation-periods 2 \
  --threshold 50 \
  --comparison-operator GreaterThanOrEqualToThreshold \
  --treat-missing-data notBreaching \
  --alarm-actions <SNS_ARN> \
  --region us-east-1 --profile study-amigo
```

---

## Evento transversal: Billing spike

### 9. Custo inesperado (`EstimatedCharges`)

**O que é:** Uma função em loop infinito, scraper disparando sem parar, ou bug de
recursão pode gerar milhares de invocações em minutos e custo inesperado. Lambda cobra
por GB-segundo de execução — `collect-worker` com 512MB rodando 900s = 450 GB-s por
invocação.

**Alarme de billing (região us-east-1, namespace especial):**
```bash
aws cloudwatch put-metric-alarm \
  --alarm-name "billing-monthly-spike" \
  --alarm-description "Custo estimado AWS acima de USD 50 no mês" \
  --metric-name EstimatedCharges \
  --namespace AWS/Billing \
  --statistic Maximum \
  --dimensions Name=Currency,Value=USD \
  --period 86400 \
  --evaluation-periods 1 \
  --threshold 50 \
  --comparison-operator GreaterThanOrEqualToThreshold \
  --treat-missing-data notBreaching \
  --alarm-actions <SNS_ARN> \
  --region us-east-1 --profile study-amigo
```

> **Nota:** Métricas de billing só estão disponíveis em `us-east-1` e precisam ser
> ativadas em **AWS Console → Billing → Billing preferences → Receive Billing Alerts**.

---

## Resumo — Grupo de alarmes recomendado por projeto

### metads.app

| Alarme | Métrica | Prioridade |
|---|---|---|
| Erros em `collect-worker` | `Errors` Lambda | 🔴 Alta |
| Erros em `collect-scheduler` | `Errors` Lambda | 🔴 Alta |
| Erros em `auth` | `Errors` Lambda | 🔴 Alta |
| Throttling em `collect-worker` | `Throttles` Lambda | 🔴 Alta |
| Duração > 80% do timeout em `collect-worker` | `Duration` Lambda | 🟡 Média |
| Dead Letter Errors em `collect-scheduler` | `DeadLetterErrors` Lambda | 🟡 Média |
| 5XX no API Gateway metaads | `5XXError` API GW | 🔴 Alta |
| WriteThrottle DynamoDB | `WriteThrottleEvents` | 🟡 Média |
| SystemErrors DynamoDB | `SystemErrors` | 🟡 Média |
| Billing spike | `EstimatedCharges` | 🟡 Média |

### ytbrowser

| Alarme | Métrica | Prioridade |
|---|---|---|
| Erros em `ytchannel-browser-dev-api` | `Errors` Lambda | 🔴 Alta |
| Throttling em `ytchannel-browser-dev-api` | `Throttles` Lambda | 🔴 Alta |
| 5XX no API Gateway ytbrowser | `5XXError` API GW | 🔴 Alta |
| Latência DynamoDB `ytchannel-browser-dev-data` | `SuccessfulRequestLatency` | 🟢 Baixa |
| WriteThrottle DynamoDB | `WriteThrottleEvents` | 🟡 Média |

---

## Custo estimado dos alarmes

Cada alarme CloudWatch custa **$0,10/mês** para métricas padrão AWS (Lambda, DynamoDB,
API GW) — não requerem CloudWatch Agent.

Para o conjunto completo acima (~15 alarmes):
- metads.app: 10 alarmes × $0,10 = **$1,00/mês**
- ytbrowser: 5 alarmes × $0,10 = **$0,50/mês**
- **Total adicional: ~$1,50/mês**

Emails SNS: gratuito até 1.000/mês (free tier permanente).

---

## Referências

- [AWS Lambda — Métricas CloudWatch](https://docs.aws.amazon.com/lambda/latest/dg/monitoring-metrics.html)
- [DynamoDB — Métricas CloudWatch](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/metrics-dimensions.html)
- [API Gateway — Métricas CloudWatch](https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-metrics-and-dimensions.html)
- `server_v2/docs/APP_DOWN_DUE_TO_AWS.md` — equivalente para EC2 (study-amigo.app)
