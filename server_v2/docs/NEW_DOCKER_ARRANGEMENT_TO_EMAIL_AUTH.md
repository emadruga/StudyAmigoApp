# Nova Arquitetura Docker — Migração SAv1.5 (Auth por Email)

## Visão Geral

Durante a migração para autenticação por email (SAv1.5), o EC2 passa a hospedar
**duas instâncias paralelas e completamente isoladas** da aplicação:

| Instância | Domínio | Diretório EC2 | Banco |
|-----------|---------|---------------|-------|
| SAv1.0 (legado) | `antigo.study-amigo.app` | `/opt/study-amigo` | `admin.db` sem email |
| SAv1.5 (novo) | `study-amigo.app` | `/opt/study-amigo-v15` | `admin.db` com email |

---

## Arquitetura de Rede

```
Browser
  │
  ▼ HTTPS
Cloudflare
  ├── study-amigo.app      ──► EC2:80 ──► Nginx host ──► v15_client:8082
  └── antigo.study-amigo.app ──► EC2:80 ──► Nginx host ──► v10_client:8081
                                                              │
                                              v10_client:8081 ──► v10_server:8000
                                              v15_client:8082 ──► v15_server:8001
```

**Cloudflare:** dois registros A, ambos `Proxied`, apontando para `54.152.109.26:80`.
O Cloudflare envia o header `Host` correto; o Nginx do host EC2 roteia por subdomínio.

---

## Mudança em relação à SAv1.0

### Antes (SAv1.0)
```
EC2 porta 80 ──► container flashcard_client (Nginx interno, porta 80)
                   └── proxy_pass ──► flashcard_server:8000
```
O Nginx vivia **dentro** do container `flashcard_client`. Não havia Nginx no host.

### Depois (SAv1.5)
```
EC2 porta 80 ──► Nginx HOST (instalado via apt no Ubuntu)
                   ├── Host: study-amigo.app      ──► v15_client:8082
                   └── Host: antigo.study-amigo.app ──► v10_client:8081
```
O Nginx do host recebe tudo na porta 80 e roteia por `server_name`.
Os containers client expõem apenas portas internas (8081, 8082).

---

## Estrutura de Diretórios no EC2

```
/opt/
├── study-amigo/            ← SAv1.0, intocado, branch main original
│   ├── server/
│   │   ├── admin.db        ← schema sem coluna email
│   │   ├── user_dbs/       ← DBs originais dos alunos
│   │   └── .env            ← SECRET_KEY, FLASK_ENV=production
│   ├── client/
│   └── docker-compose.yml  ← containers: v10_server, v10_client
│
└── study-amigo-v15/        ← SAv1.5, branch main pós-merge
    ├── server/
    │   ├── admin.db        ← schema com email + password_reset_tokens (migrado)
    │   ├── user_dbs/       ← cópia dos DBs dos alunos feita no dia do deploy
    │   └── .env            ← SECRET_KEY, SES_SENDER_EMAIL, APP_BASE_URL, etc.
    ├── client/
    └── docker-compose.yml  ← containers: v15_server, v15_client
```

---

## Containers Docker

### SAv1.0 — `/opt/study-amigo/docker-compose.yml`

```yaml
services:
  server:
    container_name: v10_server
    ports: []          # apenas expose interno
    expose: ["8000"]
    networks: [v10-net]

  client:
    container_name: v10_client
    ports:
      - "8081:80"      # expõe na 8081 do host (Nginx host aponta aqui)
    networks: [v10-net]

networks:
  v10-net:
    driver: bridge
```

### SAv1.5 — `/opt/study-amigo-v15/docker-compose.yml`

```yaml
services:
  server:
    container_name: v15_server
    ports: []          # apenas expose interno
    expose: ["8000"]
    networks: [v15-net]

  client:
    container_name: v15_client
    ports:
      - "8082:80"      # expõe na 8082 do host (Nginx host aponta aqui)
    networks: [v15-net]

networks:
  v15-net:
    driver: bridge
```

> **Nota:** Cada stack usa sua própria Docker network isolada. Os containers de
> v1.0 e v1.5 não se enxergam.

---

## Nginx do Host EC2

Instalado via `sudo apt install nginx`. Arquivo de configuração:
`/etc/nginx/sites-available/study-amigo`

```nginx
# SAv1.5 — domínio principal
server {
    listen 80;
    server_name study-amigo.app www.study-amigo.app;

    location / {
        proxy_pass         http://127.0.0.1:8082;
        proxy_set_header   Host $host;
        proxy_set_header   X-Real-IP $remote_addr;
        proxy_set_header   X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Proto $scheme;
    }
}

# SAv1.0 — domínio legado (read-only de emergência)
server {
    listen 80;
    server_name antigo.study-amigo.app;

    location / {
        proxy_pass         http://127.0.0.1:8081;
        proxy_set_header   Host $host;
        proxy_set_header   X-Real-IP $remote_addr;
        proxy_set_header   X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Proto $scheme;
    }
}
```

Ativar e recarregar:
```bash
sudo ln -s /etc/nginx/sites-available/study-amigo /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## Cloudflare DNS

Adicionar registro para o subdomínio legado (o registro raiz já existe):

| Type | Name | Content | Proxy status |
|------|------|---------|-------------|
| A | `@` | `54.152.109.26` | Proxied ← já existe |
| A | `antigo` | `54.152.109.26` | Proxied ← **adicionar** |

> Ambos apontam para o mesmo IP. O roteamento é feito pelo Nginx do host
> via header `Host`.

---

## Variáveis de Ambiente

### `/opt/study-amigo/server/.env` (SAv1.0 — não alterar)
```
SECRET_KEY=<valor atual>
FLASK_ENV=production
```

### `/opt/study-amigo-v15/server/.env` (SAv1.5 — configurar no deploy)
```
SECRET_KEY=<mesmo valor ou novo>
FLASK_ENV=production
SES_SENDER_EMAIL=noreply@metads.app
SES_AWS_REGION=us-east-1
APP_BASE_URL=https://study-amigo.app
```

O container v15_server usa credenciais AWS via **IAM Instance Profile** já anexado
à EC2 (`study-amigo-ec2-instance-profile`). boto3 resolve automaticamente via
metadata service — sem credenciais em arquivo.

A permissão `ses:SendEmail` para `noreply@metads.app` foi adicionada ao role
existente `study-amigo-ec2-backup-role` em `server/aws_terraform/backup.tf`
(resource `aws_iam_role_policy.ec2_ses_send`). Aplicar com:
```bash
cd server/aws_terraform
terraform apply
```

---

## Backup

O container `flashcard_backup` roda apenas no stack SAv1.5.
O SAv1.0 não tem backup ativo — seus dados são os do backup de 15/04/2026.

---

## Rollback

Se houver problema com SAv1.5:

```bash
# Parar SAv1.5
cd /opt/study-amigo-v15
sudo docker compose down

# Reconfigurar Nginx host para mandar tudo para SAv1.0 temporariamente
# (editar /etc/nginx/sites-available/study-amigo, apontar study-amigo.app → 8081)
sudo nginx -t && sudo systemctl reload nginx
```

SAv1.0 continua rodando em paralelo o tempo todo — o rollback é apenas
uma mudança de roteamento no Nginx, sem restart de containers.

---

## Sequência de Deploy

1. Merge `feat/email-auth` → `main` no GitHub
2. Instalar Nginx no host EC2: `sudo apt install nginx`
3. Parar container atual (libera porta 80 para o Nginx host):
   ```bash
   cd /opt/study-amigo
   sudo docker compose down
   ```
4. Alterar `docker-compose.yml` do SAv1.0: porta `80:80` → `8081:80`
5. Subir SAv1.0 na nova porta: `sudo docker compose up -d`
6. Configurar Nginx host (arquivo acima) e recarregar
7. Verificar que `antigo.study-amigo.app` funciona
8. Clonar repo SAv1.5: `sudo git clone ... /opt/study-amigo-v15`
9. Copiar `admin.db` migrado e `user_dbs/` para `/opt/study-amigo-v15/server/`
10. Configurar `.env` do SAv1.5
11. Build e subir SAv1.5: `sudo docker compose up -d --build`
12. Verificar que `study-amigo.app` funciona com login por email
13. Adicionar registro DNS `antigo` no Cloudflare
