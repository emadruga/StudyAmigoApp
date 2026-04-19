# Configurar `noreply@study-amigo.app` como remetente de email via AWS SES

Este documento descreve o passo-a-passo completo para habilitar o endereço
`noreply@study-amigo.app` como remetente de email transacional (ex.: redefinição
de senha) usando AWS SES, com DNS gerenciado pelo Cloudflare.

**Referência:** este processo foi executado com sucesso para `metads.app` em
2026-04-19 e serve de modelo para `study-amigo.app`.

### Por que cada mecanismo é necessário

O envio confiável de email exige que os principais provedores (Gmail, Outlook,
iCloud) possam verificar que a mensagem é legítima. Cada mecanismo cumpre um
papel distinto nessa cadeia:

- **SPF** (*Sender Policy Framework*): registro TXT na raiz do domínio que
  declara quais servidores estão autorizados a enviar email em seu nome. O
  servidor receptor consulta esse registro e rejeita (ou penaliza) mensagens
  originadas de IPs não listados.

- **DKIM** (*DomainKeys Identified Mail*): assina criptograficamente cada
  mensagem enviada. Os 3 registros CNAME apontam para as chaves públicas do
  SES; o servidor receptor usa essas chaves para verificar que o conteúdo não
  foi alterado em trânsito e que o remetente controla o domínio declarado.

- **DMARC** (*Domain-based Message Authentication, Reporting and Conformance*):
  política que combina SPF e DKIM, instruindo o servidor receptor sobre o que
  fazer com mensagens que falham nas verificações (`none` → monitorar,
  `quarantine` → spam, `reject` → descartar). Também habilita relatórios de
  entrega e é pré-requisito para recursos como BIMI (logotipo do remetente).

- **Custom MAIL FROM / bounce** (`bounce.study-amigo.app`): por padrão o SES
  usa `@amazonses.com` como endereço de envelope (`Return-Path`), o que causa
  desalinhamento entre o domínio visível (`study-amigo.app`) e o domínio
  verificado pelo SPF (`amazonses.com`). Configurar um subdomínio próprio
  (`bounce.study-amigo.app`) como MAIL FROM — com seus próprios registros MX
  e SPF — elimina esse desalinhamento, faz o DMARC passar por SPF além de
  DKIM, e melhora significativamente a reputação junto a provedores restritivos
  como o iCloud.

---

## Sumário

1. [Pré-condições](#pré-condições)
2. [Passo 1 — Registrar o domínio no SES](#passo-1--registrar-o-domínio-no-ses)
3. [Passo 2 — Adicionar registros DNS no Cloudflare](#passo-2--adicionar-registros-dns-no-cloudflare)
   - 2.1 SPF
   - 2.2 DKIM (3 registros CNAME)
   - 2.3 DMARC
   - 2.4 Custom MAIL FROM (MX + SPF do bounce)
4. [Passo 3 — Configurar Custom MAIL FROM no SES](#passo-3--configurar-custom-mail-from-no-ses)
5. [Passo 4 — Verificar propagação e status](#passo-4--verificar-propagação-e-status)
6. [Passo 5 — Atualizar o backend para usar o novo remetente](#passo-5--atualizar-o-backend-apppy-para-usar-o-novo-remetente)
7. [Estado atual](#estado-atual-2026-04-19)
8. [Referências](#referências)

---

## Pré-condições

- Acesso ao painel DNS do Cloudflare para `study-amigo.app`
- AWS CLI configurado com o perfil `study-amigo`:
  ```bash
  aws configure --profile study-amigo
  # ou verificar: aws sts get-caller-identity --profile study-amigo
  ```
- Conta AWS fora do SES sandbox (já confirmado em 2026-04-19)

---

## Passo 1 — Registrar o domínio no SES

```bash
aws sesv2 create-email-identity \
  --email-identity study-amigo.app \
  --dkim-signing-attributes SigningAttributesOrigin=AWS_SES,NextSigningKeyLength=RSA_2048_BIT \
  --region us-east-1 --profile study-amigo
```

O comando retorna 3 tokens DKIM. Anote-os — serão usados no Passo 2.

Para recuperar os tokens a qualquer momento:

```bash
aws sesv2 get-email-identity \
  --email-identity study-amigo.app \
  --region us-east-1 --profile study-amigo \
  --query 'DkimAttributes'
```

---

## Passo 2 — Adicionar registros DNS no Cloudflare

Acesse **Cloudflare → study-amigo.app → DNS → Records** e adicione os
registros abaixo. Todos devem ter **Proxy desativado** (nuvem cinza — "DNS only").

### 2.1 SPF (autoriza o SES a enviar pelo domínio)

| Campo | Valor |
|---|---|
| Tipo | `TXT` |
| Nome | `@` (raiz do domínio) |
| Conteúdo | `v=spf1 include:amazonses.com ~all` |

> Se já existir um registro TXT SPF para `@`, **edite-o** para incluir
> `include:amazonses.com` em vez de criar um segundo registro.

### 2.2 DKIM — 3 registros CNAME

Para cada token retornado no Passo 1 (substitua `TOKEN` pelo valor real):

| Campo | Valor |
|---|---|
| Tipo | `CNAME` |
| Nome | `TOKEN._domainkey` |
| Destino | `TOKEN.dkim.amazonses.com` |

Exemplo com token fictício:
```
Nome:    abc123xyz._domainkey.study-amigo.app
Destino: abc123xyz.dkim.amazonses.com
```

### 2.3 DMARC

| Campo | Valor |
|---|---|
| Tipo | `TXT` |
| Nome | `_dmarc` |
| Conteúdo | `v=DMARC1; p=quarantine; rua=mailto:noreply@study-amigo.app` |

> `p=quarantine` (em vez de `p=none`) melhora a reputação com provedores como
> iCloud e Outlook.

### 2.4 Custom MAIL FROM — MX e SPF para `bounce.study-amigo.app`

Estes dois registros fazem o `Return-Path` dos emails usar o domínio próprio
em vez de `@amazonses.com`, alinhando SPF e DMARC corretamente.

**Registro MX:**

| Campo | Valor |
|---|---|
| Tipo | `MX` |
| Nome | `bounce` |
| Servidor de email | `feedback-smtp.us-east-1.amazonses.com` |
| Prioridade | `10` |

**Registro TXT (SPF do bounce):**

| Campo | Valor |
|---|---|
| Tipo | `TXT` |
| Nome | `bounce` |
| Conteúdo | `v=spf1 include:amazonses.com ~all` |

---

## Passo 3 — Configurar Custom MAIL FROM no SES

Após adicionar os registros DNS do Passo 2.4:

```bash
aws sesv2 put-email-identity-mail-from-attributes \
  --email-identity study-amigo.app \
  --mail-from-domain bounce.study-amigo.app \
  --behavior-on-mx-failure USE_DEFAULT_VALUE \
  --region us-east-1 --profile study-amigo
```

---

## Passo 4 — Verificar propagação e status

```bash
# SPF raiz
dig TXT study-amigo.app +short

# DMARC
dig TXT _dmarc.study-amigo.app +short

# DKIM (substitua TOKEN pelo valor real)
dig CNAME TOKEN._domainkey.study-amigo.app +short

# MX e SPF do bounce
dig MX bounce.study-amigo.app +short
dig TXT bounce.study-amigo.app +short

# Status geral no SES (DKIM deve mostrar "SUCCESS")
aws sesv2 get-email-identity \
  --email-identity study-amigo.app \
  --region us-east-1 --profile study-amigo
```

O campo `DkimAttributes.Status` deve ser `SUCCESS` e
`MailFromAttributes.MailFromDomainStatus` deve ser `SUCCESS`.
A propagação DNS via Cloudflare costuma ser imediata, mas pode levar até 5 minutos.

---

## Passo 5 — Atualizar o backend (`app.py`) para usar o novo remetente

Localizar no `server_v2/app.py` (ou `server/app.py`) a configuração do
remetente SES e substituir `noreply@metads.app` por `noreply@study-amigo.app`:

```python
# Antes
SENDER_EMAIL = "noreply@metads.app"

# Depois
SENDER_EMAIL = "noreply@study-amigo.app"
```

Após a alteração, como o diretório `server` é bind-mounted no container
`v15_server`, basta reiniciar o container (sem rebuild de imagem):

```bash
ssh -i ~/.ssh/study-amigo-aws ubuntu@54.152.109.26 \
  "cd /opt/study-amigo-v15 && sudo git pull origin main && \
   sudo docker compose restart server"
```

---

## Estado atual (2026-04-19)

| Item | `metads.app` | `study-amigo.app` |
|---|---|---|
| Registrado no SES | ✅ | ❌ pendente |
| DKIM | ✅ SUCCESS | ❌ pendente |
| SPF raiz | ✅ | ❌ pendente |
| DMARC | ✅ `p=quarantine` | ❌ pendente |
| Custom MAIL FROM | ✅ `bounce.metads.app` | ❌ pendente |
| Remetente em uso no app | ✅ `noreply@metads.app` | — |

O domínio `metads.app` está operacional e em uso. A migração para
`study-amigo.app` é opcional e pode ser feita quando conveniente — os passos
acima são autossuficientes para executá-la do zero.

---

## Referências

- `server_v2/docs/PLAN_MIGRATE_TO_EMAIL_AUTH.md` — plano técnico da migração
- `server_v2/docs/TODO-20260419.md` — pendências SAv1.5
- [AWS SES — Custom MAIL FROM domain](https://docs.aws.amazon.com/ses/latest/dg/mail-from.html)
- [Apple iCloud postmaster](https://support.apple.com/en-us/102322)
