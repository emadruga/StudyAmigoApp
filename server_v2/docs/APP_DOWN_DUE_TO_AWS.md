# App Down — Evento de Infraestrutura AWS (2026-04-20)

## O que aconteceu

Em 2026-04-20 às ~16:55 UTC, alunos reportaram Error 522 do Cloudflare ao acessar
`study-amigo.app`. O diagnóstico confirmou que **a instância EC2 perdeu conectividade
de rede por falha no host físico subjacente**, enquanto o sistema operacional e os
containers Docker continuavam rodando internamente.

---

## Linha do tempo

| Horário (UTC) | Evento |
|---|---|
| 16:37 | SSM Agent reporta `network is unreachable` ao tentar `169.254.169.254` (metadata service) — primeiro sinal de falha no hypervisor |
| 16:55 | Cloudflare registra Error 522 (connection timeout para `study-amigo.app`) |
| 17:06 | Comando `aws ec2 reboot-instances` enviado via AWS CLI |
| 17:06 | Shutdown limpo — containers parados ordenadamente |
| 17:07 | Instância reinicia em host físico saudável |
| 17:12 | SSH responde; todos os containers up; site acessível |

**Duração total do downtime:** ~17 minutos (16:55–17:12 UTC)

---

## Por que chegamos a esta conclusão

Evidências coletadas via `journalctl -b -1` (boot anterior):

1. **Sem OOM killer** — nenhuma linha `Out of memory: Kill process` nos logs de kernel.
2. **Sem kernel panic** — logs de kernel limpos durante todo o período.
3. **Disco OK** — 49% utilizado (`df -h /`).
4. **`network is unreachable` às 16:37** — o agente SSM não conseguiu alcançar o
   metadata service (`169.254.169.254`), que é local à instância e sempre disponível
   em condições normais. Falha aqui aponta para problema na camada de rede do
   hypervisor (abaixo do OS).
5. **`InstanceStatus: impaired` no AWS CLI** — `aws ec2 describe-instance-status`
   retornou `InstanceStatus: impaired` com `SystemStatus: ok`. O `SystemStatus` testa
   a infraestrutura AWS (rede, power, hardware do host) e estava ok; o `InstanceStatus`
   testa o OS/kernel da instância e estava impaired — consistente com a instância
   travada na camada de rede sem kernel panic.
6. **Containers rodando normalmente** — logs Docker sem erros relevantes no período.
   O shutdown às 17:06 foi limpo e ordenado.

A combinação de "rede inacessível externamente + OS aparentemente vivo + InstanceStatus
impaired" é a assinatura clássica de um **evento de infraestrutura no host físico AWS**
(falha de NIC virtual, migração de hipervisor, ou problema no switch ToR).

---

## Eventos comuns de infraestrutura na AWS

Instâncias EC2 rodam em servidores físicos compartilhados. Ao longo da vida de uma
instância, os seguintes eventos são normais e devem ser antecipados:

### 1. Falha de hardware no host físico
- **O que é:** NIC, memória ou disco do servidor físico falha.
- **Sintoma:** `InstanceStatus: impaired`, SSH inacessível, OS pode ou não travar.
- **Resolução:** Stop + Start (migra para novo host). Reboot simples às vezes resolve.
- **Frequência:** Rara, mas esperada em instâncias com meses/anos de uptime.

### 2. Manutenção programada (Scheduled Maintenance)
- **O que é:** AWS avisa com dias de antecedência que o host precisa de manutenção.
- **Sintoma:** Email/notificação na console AWS; instância pode ser reiniciada ou
  retired automaticamente.
- **Resolução:** Fazer o reboot no horário de menor impacto antes da janela programada.
- **Frequência:** Algumas vezes por ano.

### 3. Instance Retirement
- **O que é:** O host físico vai ser descomissionado. AWS exige que a instância seja
  migrada (Stop + Start) até uma data limite.
- **Sintoma:** Email de "Your instance is scheduled for retirement".
- **Resolução:** Stop + Start antes da data limite.
- **Frequência:** Rara, mas acontece com instâncias antigas.

### 4. Degradação de rede (Network Performance Degraded)
- **O que é:** Congestionamento ou falha parcial na rede do datacenter.
- **Sintoma:** Latência alta, pacotes perdidos, Cloudflare 524 (timeout) ou 522.
- **Resolução:** Geralmente auto-resolvido; se persistir, reboot ou mudança de AZ.
- **Frequência:** Ocasional.

### 5. OOM Killer (Out of Memory)
- **O que é:** O kernel mata processos para recuperar memória quando a RAM acaba e não
  há swap.
- **Sintoma:** Processo morre inesperadamente; `journalctl -k | grep -i oom` mostra
  o processo vitimado.
- **Resolução:** Adicionar swap, aumentar RAM, ou reduzir footprint de memória.
- **Frequência:** Comum em instâncias pequenas (t3.micro/small) com muitos containers.
- **Risco aqui:** Instância tem 906 MB RAM **sem swap**. Com 6 containers, este evento
  é questão de tempo.

### 6. CPU Credit Exhaustion (instâncias T-series)
- **O que é:** Instâncias `t3.*` acumulam créditos de CPU em idle e os gastam em
  bursts. Se os créditos acabam, a CPU throttla para a linha de base (ex.: 10%).
- **Sintoma:** App fica lento, timeouts ocasionais; CloudWatch mostra
  `CPUCreditBalance = 0`.
- **Resolução:** Aguardar recarga de créditos, ou mudar para modo `unlimited` (custo
  extra) ou instância `m-series`.
- **Frequência:** Comum em ambientes com picos de uso (ex.: alunos acessando ao mesmo
  tempo durante aula).

---

## Medidas necessárias

### 🔴 Alta prioridade

#### 1. Adicionar swap (1–2 GB)
Sem swap, um pico de memória mata containers silenciosamente. Com 906 MB RAM e 6
containers (nginx × 2, gunicorn × 2, backup × 2), a margem é pequena.

```bash
ssh -i ~/.ssh/study-amigo-aws ubuntu@54.152.109.26 "
  sudo fallocate -l 2G /swapfile &&
  sudo chmod 600 /swapfile &&
  sudo mkswap /swapfile &&
  sudo swapon /swapfile &&
  echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab &&
  free -h
"
```

#### 2. CloudWatch Alarms — monitoramento completo ✅ IMPLEMENTADO (2026-04-20)

**Infraestrutura criada:**
- SNS topic: `arn:aws:sns:us-east-1:645069181643:study-amigo-alerts`
- Subscrito: `ewerton.madruga@icloud.com` (confirmado)
- CloudWatch Agent instalado no EC2 (arm64) — coleta mem e disco a cada 60s
- IAM policy `CloudWatchAgentServerPolicy` adicionada ao role `study-amigo-ec2-backup-role`

**4 alarmes ativos (todos em estado OK):**

| Alarme | Métrica | Limiar | Ação |
|---|---|---|---|
| `study-amigo-StatusCheckFailed` | `StatusCheckFailed` (AWS/EC2) | ≥ 1 por 2 períodos de 60s | Email |
| `study-amigo-CPUHigh` | `CPUUtilization` (AWS/EC2) | ≥ 95% por 2 períodos de 5min | Email |
| `study-amigo-DiskHigh` | `disk_used_percent` (StudyAmigo/EC2) | ≥ 85% por 2 períodos de 5min | Email |
| `study-amigo-MemHigh` | `mem_used_percent` (StudyAmigo/EC2) | ≥ 90% por 3 períodos de 60s | Email |

Todos os alarmes enviam email também ao recuperar (transição ALARM → OK).

**Para recriar em nova instância:**
```bash
# 1. Instalar CloudWatch Agent (arm64)
wget -q https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/arm64/latest/amazon-cloudwatch-agent.deb -O /tmp/cwa.deb
sudo dpkg -i /tmp/cwa.deb

# 2. Configurar métricas de mem e disco
sudo bash -c 'cat > /opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json << EOF
{
  "metrics": {
    "namespace": "StudyAmigo/EC2",
    "append_dimensions": { "InstanceId": "\${aws:InstanceId}" },
    "metrics_collected": {
      "mem":  { "measurement": ["mem_used_percent"],  "metrics_collection_interval": 60 },
      "disk": { "measurement": ["disk_used_percent"], "resources": ["/"], "metrics_collection_interval": 60 }
    }
  }
}
EOF'
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
  -a fetch-config -m ec2 \
  -c file:/opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json -s
sudo systemctl enable amazon-cloudwatch-agent

# 3. Criar SNS topic e subscrever email
aws sns create-topic --name study-amigo-alerts --region us-east-1 --profile study-amigo
aws sns subscribe --topic-arn <ARN> --protocol email \
  --notification-endpoint ewerton.madruga@icloud.com \
  --region us-east-1 --profile study-amigo
# *** Confirmar a subscrição no email antes de continuar ***

# 4. Criar alarmes (ajustar INSTANCE_ID e SNS_ARN)
INSTANCE="i-09d0d2b6bb8ae8ad7"
SNS_ARN="arn:aws:sns:us-east-1:645069181643:study-amigo-alerts"
# Ver comandos completos no histórico git (commit que adicionou esta seção)
```

### 🟡 Média prioridade

#### 3. Verificar `restart: unless-stopped` nos containers
Garante que os containers sobem automaticamente após um reboot não planejado.

```bash
ssh -i ~/.ssh/study-amigo-aws ubuntu@54.152.109.26 \
  "grep -A2 'restart' /opt/study-amigo-v15/docker-compose.yml"
```

#### 4. Habilitar notificações de manutenção programada
No console AWS → EC2 → Scheduled Events, ou via EventBridge rule para capturar
`AWS_EC2_INSTANCE_REBOOT_MAINTENANCE_SCHEDULED` e enviar email.

#### 5. Monitorar CPUCreditBalance (se instância for T-series)
```bash
aws ec2 describe-instances \
  --instance-ids i-09d0d2b6bb8ae8ad7 \
  --query 'Reservations[0].Instances[0].InstanceType' \
  --profile study-amigo
```
Se for `t3.*`, criar alarm para `CPUCreditBalance < 20`.

### 🟢 Longo prazo

#### 6. Runbook de recuperação
Documentar o procedimento de reboot/stop+start para que qualquer pessoa com acesso
AWS CLI possa executar sem depender do desenvolvedor principal.

#### 7. Health check externo (UptimeRobot ou similar)
Serviço gratuito que pinga `study-amigo.app` a cada 5 minutos e envia SMS/email se
cair. Detecta o problema antes dos alunos reportarem.

---

## Referências

- [AWS EC2 — Instance Status Checks](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/monitoring-system-instance-status-check.html)
- [Cloudflare — Error 522](https://developers.cloudflare.com/support/troubleshooting/cloudflare-errors/troubleshooting-cloudflare-5xx-errors/#error-522-connection-timed-out)
- [AWS EC2 — Scheduled Events](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/monitoring-instances-status-check_sched.html)
