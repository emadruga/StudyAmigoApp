# Exam 01 Final — Geração do Formulário (Quickstart)

Guia rápido para gerar o formulário Google Forms da Prova de Final de 1º Bimestre.

---

## Sobre o banco de questões v2

O banco de questões padrão recomendado para este exame é o
`bases/exam_01_final_bank_v2.json`. Ele foi criado com os seguintes requisitos:

- **Sem 3ª pessoa do singular** — todas as frases usam sujeitos `I`, `you`,
  `we` ou `they`. Questões com `he`/`she`/`it` foram excluídas porque a
  conjugação de 3ª pessoa do singular (terminação `-s`, auxiliares `does` /
  `doesn't`, `Does...?`) não foi trabalhada com os alunos no baralho de SRS
  durante o 1º bimestre.

- **Frases originais sem sobreposição** — nenhuma `question_text` repete
  frases do banco do exame preparatório (`prep_exam_bank.json`) nem da v1
  (`exam_01_final_bank.json`), evitando vantagem por memória de exames anteriores.

- **Conteúdo alinhado ao baralho Verbal Tenses** — os tempos verbais cobertos
  foram confirmados consultando diretamente os flashcards revisados pelos alunos
  (Simple Present, Simple Past, Present Continuous, Present Perfect, Past
  Continuous, Simple Future com *will*). O futuro com *going to* foi
  **excluído** por ausência confirmada no baralho SRS do 1º bimestre — nenhum
  flashcard cobre essa estrutura.

- **Estrutura idêntica ao exame preparatório** — 10 questões Tier 1
  (afirmativo, negativo, pergunta e identificação de tempo) + 10 questões
  Tier 2-extra (Past Continuous, Present Perfect, Simple Future com *will*,
  contrastes e passagem mista), 1 ponto cada, 4 alternativas por questão,
  1 correta.

---

## Pré-requisito: credenciais da conta Google

O script usa a **Google Forms API** via OAuth 2.0. Você precisa de um arquivo
`credentials.json` gerado no Google Cloud Console. **Isso só precisa ser feito
uma vez.** Se o arquivo já existe em `placement_exam/credentials.json` (reutilizado
do exame de nivelamento), pule direto para a seção [Configuração do ambiente](#configuração-do-ambiente).

### Como obter o credentials.json

**1. Acesse o Google Cloud Console**

Vá para [https://console.cloud.google.com/](https://console.cloud.google.com/)
e faça login com a conta Google que será proprietária dos formulários gerados.

**2. Habilite a Google Forms API**

- No menu lateral: **APIs e Serviços → Biblioteca**
- Pesquise por `Google Forms API` → clique em **Ativar**

**3. Configure a tela de consentimento OAuth**

- Menu lateral: **APIs e Serviços → Tela de permissão OAuth**
- Tipo de usuário: **Externo** → Criar
- Preencha:
  - Nome do app: `StudyAmigo Forms` (ou qualquer nome)
  - E-mail de suporte: seu e-mail
  - E-mail do desenvolvedor: seu e-mail
- Escopos: clique em **Adicionar ou remover escopos** → adicione
  `.../auth/forms.body` → Salvar e continuar
- Usuários de teste: adicione seu próprio e-mail do Google → Salvar e continuar
- Clique em **Voltar ao painel**

**4. Crie as credenciais OAuth**

- Menu lateral: **APIs e Serviços → Credenciais**
- Clique em **+ Criar credenciais → ID do cliente OAuth**
- Tipo de aplicativo: **App para computador** (Desktop app)
- Nome: `StudyAmigo CLI` (ou qualquer nome)
- Clique em **Criar** → **Fazer download do JSON**
- Renomeie o arquivo baixado para `credentials.json` e mova para:

```
placement_exam/credentials.json
```

**5. Primeiro login (token)**

Na primeira execução do script, um navegador abrirá automaticamente pedindo
autorização. Após conceder, o arquivo `placement_exam/token.json` é criado e
reutilizado em todas as execuções seguintes — você não precisará fazer login
novamente.

---

## Configuração do ambiente

O script requer as bibliotecas da Google API. Um ambiente virtual já está
configurado em `exam_prep/exam_01/venv/`. Se precisar recriá-lo:

```bash
cd exam_prep/exam_01
python3 -m venv venv
venv/bin/pip install google-auth google-auth-oauthlib google-api-python-client
```

---

## Arquivos envolvidos

| Arquivo | Descrição |
|---------|-----------|
| `scripts/create_exam_01_final_form.py` | Script gerador do formulário |
| `bases/exam_01_final_bank_v2.json` | Banco de questões v2 (sem 3ª pessoa singular) |
| `bases/exam_01_final_bank.json` | Banco de questões v1 (referência, não usar) |
| `bases/curated_student_roster_v2.csv` | Lista de alunos com tier atribuído |
| `../../../placement_exam/credentials.json` | Credenciais OAuth do Google Cloud |
| `../../../placement_exam/token.json` | Token de acesso (gerado automaticamente) |

---

## Gerando o formulário

Execute a partir do diretório `exam_prep/exam_01/scripts/`:

```bash
cd exam_prep/exam_01/scripts

# Usando o banco v2 (recomendado — sem questões de 3ª pessoa singular)
../venv/bin/python3 create_exam_01_final_form.py \
    --bank ../bases/exam_01_final_bank_v2.json \
    --roster ../bases/curated_student_roster_v2.csv \
    --title "Prova Final 1º Bimestre — Tempos Verbais / Exam 01 Final — Verbal Tenses"
```

Se as credenciais estiverem nos caminhos padrão
(`placement_exam/credentials.json` e `placement_exam/token.json`), os
argumentos `--credentials` e `--token` podem ser omitidos.

### Argumentos disponíveis

| Argumento | Padrão | Descrição |
|-----------|--------|-----------|
| `--bank` | `../bases/exam_01_final_bank.json` | Caminho para o banco de questões JSON |
| `--roster` | `../bases/curated_student_roster_v2.csv` | Caminho para a lista de alunos CSV |
| `--credentials` | `../../../placement_exam/credentials.json` | Arquivo de credenciais OAuth |
| `--token` | `../../../placement_exam/token.json` | Arquivo de token OAuth |
| `--title` | Título bilíngue padrão | Título do formulário no Google Forms |

### Saída esperada

```
✓ Authentication successful
✓ Loaded 20 questions (Tier 1: 10, Tier 2-extra: 10, Tier 3-extra: 0)
✓ Loaded 63 students
✓ Blank form created: <FORM_ID>
✓ Quiz mode enabled
✓ Form structure built (36 items)
✓ Name selector branching configured for 63 names
✓ Self-selection branching configured

📝 Edit form (instructor):
   https://docs.google.com/forms/d/<FORM_ID>/edit

👥 Share with students:
   https://docs.google.com/forms/d/<FORM_ID>/viewform
```

---

## Passos manuais após a geração

O Google Forms API cria o formulário em modo inativo. Antes de distribuir
aos alunos, faça os seguintes ajustes manualmente na **Edit URL**:

1. **Ativar respostas** — No topo do formulário, o toggle estará em
   "Não aceitando respostas". Clique para mudar para "Aceitando respostas".

2. **Vincular ao Google Sheets** — Aba "Respostas" → ícone de planilha →
   Criar nova planilha. Isso facilita a correção e o acompanhamento.

3. **Coletar e-mails** — Configurações (⚙️) → Respostas →
   Coletar endereços de e-mail: **Ativado**.

4. **Limitar a 1 resposta por pessoa** — Configurações (⚙️) → Respostas →
   Limitar a 1 resposta: **Ativado**.

5. **Testar o roteamento** — Antes de distribuir, submeta respostas de teste
   com um nome Tier 1, um Tier 2 e um aluno sem tier (auto-seleção). Verifique
   se cada um cai na seção correta. Apague as respostas de teste da planilha
   em seguida.

6. **Distribuir** — Envie a **View URL** aos alunos. Informe o tier de cada
   um na mensagem para que possam verificar se foram direcionados corretamente.

---

## Notas sobre os bancos de questões

| Banco | Versão | Uso |
|-------|--------|-----|
| `exam_01_final_bank_v2.json` | v2 | **Recomendado.** Questões com sujeitos I/you/we/they; evita 3ª pessoa singular (-s, does/doesn't) que não foi revisada com os alunos. |
| `exam_01_final_bank.json` | v1 | Primeira versão. Contém questões com 3ª pessoa singular. Não distribuir. |

---

## Referências

- [PLAN_EXAM_01_FINAL.md](PLAN_EXAM_01_FINAL.md) — plano completo do exame
- [Google Cloud Console](https://console.cloud.google.com/) — gerenciamento de credenciais
- [Google Forms API](https://developers.google.com/forms/api/reference/rest) — documentação da API
