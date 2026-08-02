# Plano de Encerramento da Infraestrutura AWS — Fim do Semestre 2026.1

> **Status**: plano de referência, **ainda não executado**. Nenhuma ação destrutiva
> foi tomada — este documento serve para orientar a decisão e a execução quando
> autorizadas.

## 1. Motivação

O semestre 2026.1 encerrou (E05 terminou oficialmente em 06/07/2026) e não há mais
necessidade de manter a aplicação rodando 24/7 na AWS, evitando custo mensal
recorrente de EC2 (instância `54.152.109.26`) enquanto não houver uso ativo.

---

## 2. Evidência de que é seguro proceder — atividade real pós-semestre

Antes de desligar, verificamos com o `server/tools/activity_monitor.py` se ainda
havia alunos usando o app depois do prazo final de E05, cobrindo 17/06 a 02/08/2026
(47 dias) direto da produção (SAv1.5, via SSH).

```bash
python server/tools/activity_monitor.py \
  --interval custom \
  --start 2026-06-17 \
  --end 2026-08-02 \
  --host 54.152.109.26 \
  --cache-dir ~/.cache/studyamigo/backup_final_20260802
```

### Resultado

| Período | Padrão observado |
|---|---|
| 17/06 – 03/07 | Atividade normal crescente, dentro do período letivo de E05 |
| **04–06/07** | **Pico de cramming coletivo** no prazo final: 492, 470 e 737 revisões/dia, 17–24 alunos ativos/dia |
| 07–28/07 | Atividade residual esparsa: no máximo 1 aluno ativo por dia, em poucos dias isolados (07, 08, 09, 10, 13, 16, 17, 22, 25, 27, 28/07) |
| **29/07 – 02/08 (hoje)** | **Zero atividade** — nenhuma revisão, nenhum aluno ativo por 5 dias corridos |

**Conclusão**: o uso da plataforma caiu a zero antes mesmo deste plano ser escrito.
Não há indício de alunos ainda dependendo do app para estudo ativo. O único uso
remanescente esperado é pontual — consulta a dados por reclamação de nota tardia —
que **não exige a aplicação no ar**, apenas acesso aos bancos de dados (via backup).

---

## 3. Onde está o backup final atual

Existem **duas cópias independentes** dos dados de produção (SAv1.5) neste momento,
além do backup automático rotativo em S3:

| Cópia | Local | Origem | Conteúdo |
|---|---|---|---|
| **Backup local (Mac)** | `~/.cache/studyamigo/backup_final_20260802/` | `scp` direto de `/opt/study-amigo-v15/server/` via `activity_monitor.py` em 02/08/2026 | `admin.db` (40 KB) + `user_dbs/` (96 bancos de usuário, ~12 MB no total) |
| **Backup automático em S3** | `s3://study-amigo-backups-<ACCOUNT_ID>/backups/v15/week-N/<dia>/` | Container sidecar `flashcard_backup`, diário às 06:00 UTC | `admin.db.gz` + `user_dbs.tar.gz`, janela rotativa de 4 semanas (28 slots) |

O backup local em `~/.cache/studyamigo/backup_final_20260802/` é o mais recente e
**é o mesmo snapshot usado na análise de atividade da seção 2** — já confirmado
íntegro e legível (foi usado para gerar o relatório acima). É a cópia recomendada
para consulta rápida de reclamações de nota tardias sem depender de rede/AWS.

Antes de rodar `terraform destroy`, gerar mais uma cópia local final (repetir o
Passo 0 do `SHUTDOWN_PROCEDURE.md`) para garantir que nada mudou entre a análise e
o desligamento efetivo:

```bash
ssh -i ~/.ssh/study-amigo-aws ubuntu@54.152.109.26 \
  "sudo tar czf /tmp/sav15-final-backup.tar.gz \
     -C /opt/study-amigo-v15/server admin.db user_dbs"
scp -i ~/.ssh/study-amigo-aws \
  ubuntu@54.152.109.26:/tmp/sav15-final-backup.tar.gz \
  ~/.cache/studyamigo/sav15-final-backup-$(date +%Y%m%d).tar.gz
```

Guardar essa cópia local em pelo menos dois lugares (ex.: Mac + Google Drive), já
que ela é a única fonte de dados depois que a instância EC2 for destruída e antes
de uma eventual restauração (seção 5).

---

## 4. Procedimento técnico de encerramento

O procedimento técnico detalhado (backup final, opções de parar vs. destruir,
limpeza de DNS/S3, checklist e reativação futura) já está documentado em:

**→ [`server/docs/SHUTDOWN_PROCEDURE.md`](../server/docs/SHUTDOWN_PROCEDURE.md)**

Este plano não duplica esse conteúdo — ele existe para registrar a *decisão* e a
*evidência* que a sustentam. Seguir o checklist do documento técnico acima na hora
de executar.

Resumo das opções lá descritas, da menos à mais destrutiva:

1. **Parar containers** (`docker compose down`) — não reduz custo de EC2, só CPU/RAM.
2. **Parar a instância EC2** (`aws ec2 stop-instances`) — reduz a maior parte do
   custo (compute), reversível, mantém dados no EBS.
3. **`terraform destroy`** — encerramento definitivo e irreversível da EC2, Elastic
   IP, VPC e recursos associados. O bucket S3 de backups é protegido
   (`force_destroy = false`) e sobrevive por padrão.

> **O backup automático não continua rodando durante a pausa.** O container
> `flashcard_backup` vive dentro da instância EC2 — nas opções 1 e 2, ele para
> junto (containers desligados ou instância parada), então nenhum backup novo é
> enviado ao S3 enquanto durar a pausa. Isso não é perda de dados: `admin.db` e
> `user_dbs/` continuam intactos no volume EBS da instância parada, e o backup
> retoma sozinho ao reiniciar. Mas o snapshot mais recente em S3 (janela rotativa
> de 4 semanas) fica "congelado" na data da parada — ver seção 3 para onde está o
> backup manual mais atual, que não depende da instância estar ligada.

### 4.1 Decisão tomada (02/08/2026)

Decidido proceder em duas etapas, deixando o `terraform destroy` para o mês
seguinte:

1. **Desligar os containers** dos dois ambientes (`docker compose down` em
   `/opt/study-amigo-v15` e `/opt/study-amigo`).
2. **Parar a instância EC2** (`aws ec2 stop-instances --instance-ids
   i-09d0d2b6bb8ae8ad7 --region us-east-1`).

**O que permanece ativo/preservado durante essa pausa:**
- Volume **EBS** da instância (dados intactos, `admin.db` + `user_dbs/` dos dois
  ambientes).
- **Elastic IP** `54.152.109.26` (permanece associado à instância parada — atenção:
  a AWS cobra por Elastic IP associado a instância **parada**, ao contrário de uma
  instância em execução, onde é gratuito; ver nota de custo abaixo).
- Bucket **S3** de backups (`study-amigo-backups-645069181643`), com todo o
  histórico já acumulado até a data da parada.

**O que fica suspenso durante essa pausa:**
- **O backup automático diário para de rodar** (ver aviso acima) — nenhum backup
  novo é gravado no S3 enquanto a instância estiver parada. O último snapshot em
  S3 antes da parada permanece como o mais recente disponível até a reativação ou
  até o `terraform destroy` do mês seguinte. O backup manual local da seção 3
  (`~/.cache/studyamigo/backup_final_20260802/`) cobre essa lacuna.

**Nota de custo — Elastic IP ocioso**: como o IP elástico fica associado a uma
instância parada (não terminada), a AWS passa a cobrar por ele enquanto durar a
pausa (diferente de quando associado a uma instância em execução, que é gratuito).
O valor é baixo (centavos/hora), mas soma ao longo do mês até o `terraform destroy`.

---

## 5. Landing page no domínio enquanto a aplicação estiver fora do ar

O domínio `study-amigo.app` é gerenciado na Cloudflare. Em vez de deixar o DNS
apontando para um Elastic IP morto (erro de conexão para quem acessar) ou remover
os registros por completo (domínio "cai" sem explicação), a recomendação é publicar
uma página estática simples via **Cloudflare Pages** — gratuito, não depende do EC2
nem de nenhuma infraestrutura de compute, e fica no ar até a reativação no próximo
semestre.

### 5.1 Por que Cloudflare Pages (e não deixar o DNS quebrado)

- **Custo zero** — Cloudflare Pages tem tier gratuito generoso para sites estáticos, sem relação com o EC2 que está sendo desligado.
- **Não depende da AWS** — a página continua no ar mesmo depois do `terraform destroy`, sem exigir nenhuma instância rodando.
- **Boa experiência para quem tentar acessar** — alunos, ou qualquer pessoa com o link salvo, veem uma mensagem clara em vez de "esse site não pode ser acessado".
- **Fácil de desativar depois** — quando a aplicação real voltar ao ar no próximo semestre, basta trocar o registro DNS de volta (Pages → Elastic IP), sem precisar apagar o projeto Pages (pode ficar arquivado para reuso em uma futura pausa).

### 5.2 Página já criada no repositório

A landing page estática já foi criada e validada visualmente (desktop + mobile) em:

**→ [`server_v2/shutdown_landing_page/index.html`](../server_v2/shutdown_landing_page/index.html)**

Arquivo único, autocontido (HTML + CSS inline, sem build, sem dependências
externas), pronto para upload direto no Cloudflare Pages. Conteúdo: agradecimento
aos alunos pela edição do semestre, aviso de que a aplicação está pausada com os
dados seguros em backup, aviso de retorno na próxima edição (2027.1), e contato
por e-mail para dúvidas de nota — layout com menção explícita ao `StudyAmigo.app`.

> O e-mail de contato usado no rascunho (`contato@study-amigo.app`) é um
> placeholder — confirmar/trocar pelo endereço real antes de publicar.

### 5.3 Passo a passo — publicar

**Opção simples (upload direto, sem Git) — via dashboard da Cloudflare:**

1. No dashboard da Cloudflare, ir em **Workers & Pages → Create → Pages → Upload assets**.
2. Dar um nome ao projeto (ex.: `study-amigo-offline`) e fazer upload do conteúdo de `server_v2/shutdown_landing_page/` (o `index.html`).
3. A Cloudflare publica automaticamente em uma URL tipo `study-amigo-offline.pages.dev` — testar antes de apontar o domínio.

**Opção via Git (mais fácil de atualizar depois):**

1. No dashboard da Cloudflare: **Workers & Pages → Create → Pages → Connect to Git**, selecionar o repositório `StudyAmigoApp` e o diretório de build `server_v2/shutdown_landing_page/` (sem comando de build — é HTML puro).
2. Cada push nesse diretório republica a página automaticamente.

### 5.4 Apontar o domínio para a landing page

Depois que o projeto Pages estiver publicado e testado na URL `.pages.dev`:

1. Na Cloudflare, ir em **DNS → Records** do domínio `study-amigo.app`.
2. **Remover ou editar** o registro A que hoje aponta `@` (e `www`, se existir) para `54.152.109.26`.
3. Adicionar um registro **CNAME** apontando `study-amigo.app` para o domínio do projeto Pages (`study-amigo-offline.pages.dev`), mantendo o proxy da Cloudflare ativado (nuvem laranja).
   - Se o domínio raiz (`@`) não aceitar CNAME diretamente, a Cloudflare oferece **CNAME flattening** automático para o registro raiz — funciona nativamente, sem necessidade de registro A.
4. Se `antigo.study-amigo.app` (SAv1.0) também for encerrado, repetir o mesmo processo para esse subdomínio ou apenas remover o registro, conforme a decisão para o legado.

### 5.5 Checklist da landing page

- [x] Página HTML estática criada e revisada (`server_v2/shutdown_landing_page/index.html`) — mensagem clara, contato de suporte, sem dados sensíveis
- [ ] Confirmar/trocar o e-mail de contato placeholder (`contato@study-amigo.app`) pelo endereço real
- [ ] Projeto Cloudflare Pages criado e testado na URL `.pages.dev`
- [ ] Registro DNS de `study-amigo.app` trocado de A (`54.152.109.26`) para CNAME (projeto Pages)
- [ ] Acesso testado em `https://study-amigo.app` depois da propagação DNS (minutos, tipicamente)
- [ ] Decisão tomada sobre `antigo.study-amigo.app` (landing page própria, redirect, ou remoção do registro)

---

## 6. Como restaurar na próxima edição da disciplina (após `terraform destroy`)

Se o encerramento for feito via `terraform destroy` (opção definitiva), a EC2, o
Elastic IP e a VPC são apagados — mas o **bucket S3 de backups sobrevive**
(`force_destroy = false` em `backup.tf`), e o **backup local** da seção 3 também
sobrevive independente da AWS. A reativação no próximo semestre parte de qualquer
uma dessas duas fontes.

### 6.1 Recriar a infraestrutura

```bash
cd server/aws_terraform
terraform apply
```

Isso recria a instância EC2, um **novo** Elastic IP (o IP muda — `54.152.109.26`
não é garantido permanecer o mesmo, a menos que reservado separadamente), o bucket
S3 de backups é reaproveitado se ainda existir (Terraform detecta e não recria), e
o `user_data.sh` deixa a aplicação já clonada e os containers subindo do zero
(bancos vazios/de exemplo nesse ponto — os dados reais vêm no passo seguinte).

### 6.2 Restaurar os dados dos alunos

**Opção A — a partir do S3** (se ainda dentro da janela de 4 semanas do backup
rotativo, improvável para o início do semestre seguinte, mas possível logo após o
encerramento):

```bash
ssh -i ~/.ssh/study-amigo-aws ubuntu@<novo_elastic_ip>

python3 /opt/study-amigo-v15/server/tools/restore_backup.py \
    --bucket study-amigo-backups-<ACCOUNT_ID> \
    --latest
```

Ver `server/docs/APP_BACKUP_RESTORE.md` (seção 7) para listar slots específicos
(`--week`/`--day`) e o modo `--dry-run` de simulação.

**Opção B — a partir do backup local do Mac** (recomendada — é a fonte mais
provável de ainda estar válida meses depois, já que o S3 rotaciona em 4 semanas):

```bash
# Copiar o backup local mais recente (seção 3) de volta para a nova instância
scp -i ~/.ssh/study-amigo-aws \
  ~/.cache/studyamigo/sav15-final-backup-20260802.tar.gz \
  ubuntu@<novo_elastic_ip>:/tmp/

ssh -i ~/.ssh/study-amigo-aws ubuntu@<novo_elastic_ip>

# Na instância: parar o server, extrair, corrigir dono, reiniciar
sudo docker compose -f /opt/study-amigo-v15/docker-compose.yml stop server
sudo tar xzf /tmp/sav15-final-backup-20260802.tar.gz -C /opt/study-amigo-v15/server/
sudo chown -R ubuntu:ubuntu /opt/study-amigo-v15/server/admin.db /opt/study-amigo-v15/server/user_dbs/
sudo docker compose -f /opt/study-amigo-v15/docker-compose.yml start server
```

### 6.3 Reverter o DNS da landing page para a aplicação real

Se a landing page da seção 5 estiver no ar, este é o passo que a desativa (sem
precisar apagar o projeto Pages — pode ficar arquivado na Cloudflare para reuso em
uma futura pausa entre semestres):

1. Na Cloudflare, ir em **DNS → Records** do domínio `study-amigo.app`.
2. Remover o registro **CNAME** que aponta para `study-amigo-offline.pages.dev`.
3. Recriar o registro **A** apontando `@` (e `www`, se aplicável) para o **novo**
   Elastic IP gerado no passo 6.1 — o IP muda a cada `terraform apply`, então não é
   apenas "reativar" o registro antigo, é preciso atualizá-lo com o IP atual:
   ```bash
   cd server/aws_terraform && terraform output elastic_ip
   ```
4. Repetir para `antigo.study-amigo.app`, se a SAv1.0 também for reativada.

Como o Elastic IP muda a cada `terraform apply` (a menos que reservado à parte),
sempre confirmar o IP atual com `terraform output` antes de configurar o DNS —
não reutilizar o IP antigo documentado neste plano (`54.152.109.26`) sem checar.

### 6.4 Reativar o backup automático

Confirmar que o container `flashcard_backup` subiu junto (ver `docker compose ps`)
e que consegue falar com o bucket S3 — ver `server/docs/APP_BACKUP_RESTORE.md`
seção 9 (Diagnostics) se houver erro de IAM/instance profile.

### 6.5 Checklist de reativação

- [ ] `terraform apply` executado, novo Elastic IP anotado
- [ ] Dados restaurados (S3 ou backup local) e validados (`admin.db` + `user_dbs/` com contagem de usuários condizente)
- [ ] DNS revertido da landing page (CNAME → Pages) para o registro A do novo Elastic IP
- [ ] Container `flashcard_backup` confirmado ativo e falando com o S3
- [ ] Login de teste feito com um usuário real para confirmar dados restaurados corretamente

---

## 7. Justificativa da decisão

Dado que:
- a atividade está zerada há 5+ dias corridos (seção 2);
- o semestre encerrou oficialmente em 06/07/2026;
- o backup automático diário em S3 já preserva os dados até a data da parada (`server/docs/APP_BACKUP_RESTORE.md`), complementado pelo backup manual local (seção 3);
- reclamações de nota tardias podem ser resolvidas com os dados já em cache local
  ou no S3, sem precisar da aplicação no ar (ver
  `placement_exam/planning_E05/docs/E05_Licoes_Aprendidas_e_Sugestoes.md`, seção 12);

optou-se por **parar containers + parar a instância EC2** (opções 1+2 da seção 4)
agora, mantendo EBS/Elastic IP/S3 intactos, e adiar o **`terraform destroy`**
definitivo para o mês seguinte — dando uma janela de segurança para reclamações de
nota tardias antes do encerramento irreversível.

---

## 8. Checklist de execução

- [x] Rodar Passo 0 do `SHUTDOWN_PROCEDURE.md` (backup manual final) antes de qualquer ação
- [x] Criar a landing page estática (`server_v2/shutdown_landing_page/index.html`, seção 5.2)
- [ ] Publicar a landing page no Cloudflare Pages e testar na URL `.pages.dev` (seção 5.3)
- [x] Desligar os containers dos dois ambientes (`docker compose down` em `/opt/study-amigo-v15` e `/opt/study-amigo`)
- [x] Parar a instância EC2 (`aws ec2 stop-instances --instance-ids i-09d0d2b6bb8ae8ad7 --region us-east-1`)
- [ ] Trocar o DNS de `study-amigo.app` (e `antigo.study-amigo.app`, se aplicável) do registro A do EC2 para o CNAME da landing page
- [ ] Confirmar na fatura AWS que a cobrança de EC2 (compute) não aparece no ciclo seguinte, e observar a cobrança residual do Elastic IP ocioso
- [x] Registrar a data efetiva da pausa neste documento (seção 9)
- [ ] Agendar o `terraform destroy` para o mês seguinte (ver seção 4.1)

---

## 9. Registro de execução

- Data de execução (containers + stop EC2): **02/08/2026, ~16:00 UTC (13:00 BRT)**
- Passos executados:
  - Backup manual final gerado na instância e baixado para o Mac:
    `~/.cache/studyamigo/sav15-final-backup-20260802.tar.gz` (2.7 MB) e
    `~/.cache/studyamigo/sav10-final-backup-20260802.tar.gz` (1.9 MB)
  - `docker compose down` em `/opt/study-amigo-v15` — containers `v15_client`,
    `v15_server`, `v15_backup` parados e removidos
  - `docker compose down` em `/opt/study-amigo` — containers `flashcard_client`,
    `flashcard_server`, `flashcard_backup` parados e removidos
  - Instância `i-09d0d2b6bb8ae8ad7` parada via AWS CLI (profile `study-amigo`),
    confirmada em estado `stopped`. Elastic IP `54.152.109.26` permanece associado.
- Responsável: Ewerton Madruga (via Claude Code)
- Data planejada para `terraform destroy`: — (mês seguinte, conforme decisão de 02/08/2026)
- Observações: Landing page no Cloudflare Pages e troca de DNS **ainda pendentes**
  — o domínio `study-amigo.app` continua apontando para o Elastic IP, que agora
  não responde (aplicação fora do ar sem página explicativa até esse passo ser
  feito). Backup automático em S3 parado a partir desta data (ver aviso na seção
  4) — os backups manuais acima cobrem essa lacuna.

---

*Criado em: 02/08/2026. Baseado em análise de atividade via `activity_monitor.py`
(17/06–02/08/2026) e no procedimento técnico em `server/docs/SHUTDOWN_PROCEDURE.md`.*
