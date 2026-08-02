# Procedimento de Encerramento da Aplicação (Fim de Semestre)

> **Status deste documento**: guia de referência, ainda **não executado**. Nenhum
> passo abaixo foi rodado — serve para quando a decisão de desligar for tomada.

## 1. Objetivo

Encerrar a infraestrutura AWS do StudyAmigo (EC2 `54.152.109.26` + recursos associados)
para parar de gerar custo mensal, preservando os dados dos alunos para possível consulta
futura (ex.: reclamações de nota tardias, auditorias, ou reativação em semestre seguinte).

**Isto NÃO é o mesmo que apenas parar os containers.** Ver seção 6 para alternativas
menos drásticas caso o objetivo seja pausar temporariamente em vez de desmontar tudo.

---

## 2. O que existe hoje (inventário)

| Recurso | Detalhe |
|---|---|
| Instância EC2 | `t4g.micro`, Elastic IP `54.152.109.26`, provisionada via Terraform (`server/aws_terraform/`) |
| SAv1.0 (legado) | Containers `flashcard_server`/`flashcard_client` (ou `v10_server`/`v10_client`), diretório `/opt/study-amigo/`, porta 8081, domínio `antigo.study-amigo.app` |
| SAv1.5 (produção atual) | Containers `v15_server`/`v15_client`, diretório `/opt/study-amigo-v15/`, porta 8082, domínio `study-amigo.app` |
| Nginx do host | Roteia por `server_name` para 8081/8082 (ver `server_v2/docs/NEW_DOCKER_ARRANGEMENT_TO_EMAIL_AUTH.md`) |
| Backup automático | Container sidecar `flashcard_backup`, roda diariamente às 06:00 UTC, sobe `admin.db` + `user_dbs/` para S3 (`study-amigo-backups-<ACCOUNT_ID>`), janela rotativa de 4 semanas |
| Bucket S3 de backup | Recurso Terraform (`backup.tf`), com `force_destroy = false` — **protegido contra `terraform destroy` acidental** |
| DNS | Cloudflare, domínio `study-amigo.app` — dois registros A (`@` e `antigo`), proxied |
| VPC/Subnet/IGW/Security Group | Criados pelo mesmo `main.tf`, sem custo relevante isolado, mas destruídos junto com a instância |

Custo mensal recorrente vem essencialmente de: **EC2 rodando 24/7** (principal), Elastic IP
associado a instância parada (cobrado se não liberado), e armazenamento S3 dos backups
(baixo custo, cresce lentamente por ser rotativo).

---

## 3. Passo 0 — Backup final antes de qualquer ação destrutiva

Mesmo com o backup automático diário já em S3, fazer um backup manual final é
recomendado antes de desligar algo, para ter uma cópia local recente e confirmada.

```bash
# 1. Baixar o backup mais recente do S3 (ajustar bucket conforme account ID real)
aws s3 sync s3://study-amigo-backups-<ACCOUNT_ID>/backups/ \
  ~/studyamigo-final-backup-$(date +%Y%m%d)/ \
  --profile <seu-profile-aws>

# 2. Alternativa: copiar direto da instância via SSH (mais garantido, pega o estado atual)
ssh -i ~/.ssh/study-amigo-aws ubuntu@54.152.109.26 \
  "sudo tar czf /tmp/sav15-final-backup.tar.gz \
     -C /opt/study-amigo-v15/server admin.db user_dbs"
scp -i ~/.ssh/study-amigo-aws \
  ubuntu@54.152.109.26:/tmp/sav15-final-backup.tar.gz \
  ~/studyamigo-final-backup-$(date +%Y%m%d)/sav15.tar.gz

# repetir para SAv1.0 se ainda houver dados relevantes não migrados
ssh -i ~/.ssh/study-amigo-aws ubuntu@54.152.109.26 \
  "sudo tar czf /tmp/sav10-final-backup.tar.gz \
     -C /opt/study-amigo/server admin.db user_dbs"
scp -i ~/.ssh/study-amigo-aws \
  ubuntu@54.152.109.26:/tmp/sav10-final-backup.tar.gz \
  ~/studyamigo-final-backup-$(date +%Y%m%d)/sav10.tar.gz
```

Guardar essa pasta localmente (e idealmente em um segundo local, ex. Google Drive) —
é a fonte para gerar timelines de reclamações de nota que cheguem depois do desligamento
(ver `placement_exam/planning_E05/docs/E05_Licoes_Aprendidas_e_Sugestoes.md`, seção 12).

---

## 4. Opções de encerramento (da menos à mais destrutiva)

### 4.1 Parar containers, manter a instância rodando
Reduz uso de CPU/RAM mas **não reduz custo de EC2** (a fatura é por instância ligada,
não por container). Útil só como pausa curta e reversível em segundos.

```bash
ssh -i ~/.ssh/study-amigo-aws ubuntu@54.152.109.26 \
  "cd /opt/study-amigo-v15 && sudo docker compose down && \
   cd /opt/study-amigo && sudo docker compose down"
```

### 4.2 Parar (stop) a instância EC2
Interrompe a cobrança de **compute** (a maior parte do custo), mas mantém o volume EBS
(cobrado à parte, valor baixo) e a Elastic IP pode passar a ser cobrada quando associada
a uma instância parada (AWS cobra IP elástico ocioso). Totalmente reversível — a instância
pode ser reiniciada depois com os dados intactos.

```bash
# Via AWS CLI (usar a região correta, us-east-1 conforme terraform)
aws ec2 stop-instances --instance-ids <INSTANCE_ID> --region us-east-1

# Obter o instance ID, se necessário:
cd server/aws_terraform && terraform output
```

**Recomendado se ainda houver incerteza sobre precisar reativar no curto prazo** (ex.:
recurso de nota pendente, alunos que ainda vão reclamar).

> **Atenção — o backup automático para junto com a instância.** O container
> `flashcard_backup` (sidecar do `docker-compose.yml`) só roda enquanto a instância
> está ligada. Com a instância parada, **nenhum backup novo é feito** — não porque os
> dados sumam (o `admin.db` e `user_dbs/` continuam intactos no volume EBS, parado
> junto com a instância), mas porque não há processo rodando para gerar novos
> snapshots no S3. O backup retoma sozinho (sem passo manual) assim que a instância
> for reiniciada (`aws ec2 start-instances`) e o `docker-compose` subir de novo.
> Ou seja: dados existentes ficam seguros no EBS durante a pausa, mas a janela
> rotativa de 4 semanas no S3 (seção 2.3 de `APP_BACKUP_RESTORE.md`) para de avançar
> — o último snapshot em S3 antes da parada é o mais recente disponível até a
> reativação.

### 4.3 Terminar/destruir tudo via Terraform (encerramento definitivo)
Ação **irreversível**: apaga a instância EC2, Elastic IP, VPC, Security Group e demais
recursos gerenciados pelo Terraform. O bucket S3 de backups **não** será destruído
automaticamente (protegido por `force_destroy = false`) — o `terraform destroy` vai
falhar nesse recurso especificamente se o bucket não estiver vazio, o que é o
comportamento esperado/desejado.

```bash
cd server/aws_terraform
terraform plan -destroy   # revisar o que será destruído antes de confirmar
terraform destroy
```

Digitar `yes` quando solicitado. Esperado: tudo destruído exceto o bucket S3 (que ficará
com um erro de "BucketNotEmpty" se `force_destroy=false` e houver objetos — isso é
proposital, não um bug).

**Somente executar esta etapa depois de confirmar o Passo 0 (backup) concluído.**

---

## 5. Limpeza fora do Terraform (não gerenciado por IaC)

Estes recursos não são destruídos pelo `terraform destroy` e precisam de ação manual:

1. **DNS na Cloudflare** — remover os registros A de `study-amigo.app` (`@`) e
   `antigo.study-amigo.app` (`antigo`), ou ao menos desativar o proxy, para evitar
   confusão de usuários batendo em um domínio que não resolve mais para nada útil.
2. **Bucket S3 de backups** — decidir o destino final dos dados:
   - **Manter o bucket** (recomendado no curto prazo): custo de armazenamento é baixo
     (poucos MB/GB de SQLite comprimido) e preserva histórico para consultas tardias.
   - **Esvaziar e destruir o bucket**, apenas depois de ter certeza de que o backup
     manual do Passo 0 está seguro em outro lugar:
     ```bash
     aws s3 rm s3://study-amigo-backups-<ACCOUNT_ID>/ --recursive
     cd server/aws_terraform && terraform destroy   # agora o bucket também é removido
     ```
3. **Chave SSH / par de chaves na AWS** (`study-amigo-aws`) — pode ser mantida sem custo,
   não precisa de ação.
4. **Domínio `study-amigo.app` em si** (registro do domínio, se pago separadamente da
   Cloudflare) — verificar se há renovação anual pendente independente do EC2.

---

## 6. Checklist resumido

- [ ] Backup manual final feito e verificado localmente (Passo 0)
- [ ] Decisão tomada: pausa temporária (4.1/4.2) ou encerramento definitivo (4.3)?
- [ ] Se definitivo: `terraform plan -destroy` revisado antes do `destroy`
- [ ] Registros DNS removidos/desativados na Cloudflare
- [ ] Decisão sobre o bucket S3 de backups tomada e documentada
- [ ] Confirmar na fatura AWS (Billing Dashboard) que não há mais cobrança de EC2/Elastic IP no ciclo seguinte

---

## 7. Reativação futura

Como a infraestrutura é 100% Terraform (`server/aws_terraform/main.tf`), reativar em um
semestre futuro é essencialmente `terraform apply` novamente + restaurar o backup mais
recente do S3 (ou do backup manual local) para `server/admin.db` e `server/user_dbs/`,
seguindo `server/docs/APP_BACKUP_RESTORE.md`. O domínio precisa ser reapontado na
Cloudflare para o novo Elastic IP gerado (o IP muda a cada `apply`, a menos que se
reserve o mesmo IP elástico separadamente).

---

*Criado em: 02/08/2026. Referências: `server/docs/AWS_DOCKER_DEPLOY.md` (seção 15,
Tear Down genérico), `server/docs/APP_BACKUP_RESTORE.md`,
`server_v2/docs/NEW_DOCKER_ARRANGEMENT_TO_EMAIL_AUTH.md`.*
