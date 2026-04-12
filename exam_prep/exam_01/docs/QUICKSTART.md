# Exam 01 Final — Geração do Formulário (Quickstart)

Guia rápido para gerar o formulário Google Forms da Prova de Final de 1º Bimestre.

---

## Sobre o banco de questões v2

O banco de questões padrão recomendado para este exame é o
`bases/exam_01_final_bank_v2.json`. Ele foi criado com os seguintes requisitos,
definidos formalmente nas seções **3.4** (Regras de Construção) e **3.5**
(Revisão de Ambiguidade) do [PLAN_EXAM_01_FINAL.md](PLAN_EXAM_01_FINAL.md):

### Regras de construção (§3.4)

- **Regra 1 — Sem 3ª pessoa do singular** — todas as frases usam sujeitos
  `I`, `you`, `we` ou `they`. Questões com `he`/`she`/`it` foram excluídas
  porque a conjugação de 3ª pessoa do singular (terminação `-s`, auxiliares
  `does`/`doesn't`, `Does...?`) não foi trabalhada com os alunos no baralho
  de SRS durante o 1º bimestre.

- **Regra 2 — Marcador temporal ou âncora estrutural obrigatório** — toda
  questão de completar frase deve incluir um marcador de tempo ou elemento
  estrutural que torne exatamente uma opção gramaticalmente correta. Frases
  sem esse marcador (ex.: `"They _____ in New York."`) admitem múltiplas
  respostas corretas, o que invalida a questão para correção automática.
  Exemplos de marcadores por tempo verbal:
  - Simple Present: `every day`, `every summer`, `always`, `usually`
  - Simple Past: `yesterday`, `last night`, `last week`
  - Present Continuous: `right now`, `at the moment`, `currently`
  - Simple Future (will): `tomorrow`, `tomorrow morning`, `next week`, `by tomorrow`
  - Present Perfect: `already`, `yet`, `ever`, `so far`, `twice`
  - Past Continuous: `when + Simple Past` (ex.: `when the alarm went off`)

- **Regra 3 — Apenas estruturas presentes no baralho SRS** — não testar
  estruturas que os alunos não revisaram. Para o 1º bimestre, o futuro com
  *going to* foi **excluído** por ausência confirmada no baralho — nenhum
  flashcard cobre essa estrutura.

- **Regra 4 — Sem repetição de frases entre bancos** — nenhuma `question_text`
  repete frases do banco do exame de nivelamento (`question_bank.json`), do
  exame preparatório (`prep_exam_bank.json`) nem da v1 (`exam_01_final_bank.json`).

- **Estrutura idêntica ao exame preparatório** — 10 questões Tier 1
  (afirmativo, negativo, pergunta e identificação de tempo) + 10 questões
  Tier 2-extra (Past Continuous, Present Perfect, Simple Future com *will*,
  contrastes e passagem mista), 1 ponto cada, 4 alternativas por questão,
  1 correta.

### Revisão de ambiguidade obrigatória (§3.5)

Toda nova versão do banco deve passar por uma revisão de ambiguidade **antes**
de ser usada para gerar um formulário. O script `validate_question_bank.py`
automatiza essa verificação — veja a seção [Validando o banco antes de gerar](#validando-o-banco-antes-de-gerar).

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
| `scripts/create_exam_01_final_form.py` | Script gerador do formulário Google Forms |
| `scripts/create_exam_01_final_docx.py` | Script gerador da prova impressa (DOCX) |
| `scripts/validate_question_bank.py` | Validador do banco (§3.4 e §3.5) — chamado automaticamente pelo gerador |
| `bases/exam_01_final_bank_v2.json` | Banco de questões v2 (sem 3ª pessoa singular) |
| `bases/exam_01_final_bank.json` | Banco de questões v1 (referência, não usar) |
| `bases/curated_student_roster_v2.csv` | Lista de alunos com tier atribuído |
| `../../../placement_exam/credentials.json` | Credenciais OAuth do Google Cloud |
| `../../../placement_exam/token.json` | Token de acesso (gerado automaticamente) |

---

## Validando o banco antes de gerar

O script `validate_question_bank.py` verifica as regras das seções §3.4 e §3.5
do plano do exame. Ele é chamado **automaticamente** pelo gerador (Step 2.5)
antes de qualquer chamada à API do Google. Se forem detectados problemas, o
script lista as ocorrências e pergunta se a geração deve prosseguir.

Também pode ser executado de forma independente para verificar um banco sem
gerar o formulário:

```bash
cd exam_prep/exam_01/scripts

# Validar o banco v2 contra os bancos anteriores
../venv/bin/python3 validate_question_bank.py \
    ../bases/exam_01_final_bank_v2.json \
    ../../../placement_exam/bases/question_bank.json \
    ../../bases/prep_exam_bank.json
```

### O que é verificado

| Regra | Severidade | O que detecta |
|-------|-----------|---------------|
| Rule 1 | aviso | Sujeito `he/she/it` em questão de completar frase |
| Rule 2 / §3.5 | aviso | Ausência de marcador temporal ou âncora estrutural (`-ing` no stem) |
| Rule 3 | **erro** | Estrutura ausente do baralho SRS (`going to`) em qualquer campo |
| Rule 4 | **erro** | `question_text` duplicado dentro do banco ou em bancos anteriores |
| Rule 5 | **erro** | Número de opções diferente de 4, ou número de respostas corretas diferente de 1 |

### Comportamento ao detectar problemas

- **Erros**: a mensagem de prompt usa padrão **N** — é necessário digitar `y`
  explicitamente para prosseguir. Erros indicam questões estruturalmente
  inválidas para correção automática.
- **Apenas avisos**: padrão é **Y** — pressione Enter para prosseguir ou `n`
  para cancelar. Avisos indicam possível ambiguidade que deve ser revisada
  manualmente.
- **Sem problemas**: prossegue automaticamente sem interação.

### Saída esperada (banco válido)

```
Validating question bank against rules in §3.4 and §3.5...
✓ Question bank passed all validation checks.
```

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

## Gerando a prova impressa (DOCX)

Para alunos que não têm smartphone ou não podem usar o formulário online durante
a prova, use o script `create_exam_01_final_docx.py` para gerar um documento
Word imprimível (.docx).

Execute a partir do diretório `exam_prep/exam_01/scripts/`:

```bash
cd exam_prep/exam_01/scripts

# Cópia do aluno (sem gabarito)
../venv/bin/python3 create_exam_01_final_docx.py \
    --bank ../bases/exam_01_final_bank_v2.json \
    --out  ../output/prova_final_1bim.docx

# Cópia do professor (com gabarito ao final)
../venv/bin/python3 create_exam_01_final_docx.py \
    --bank ../bases/exam_01_final_bank_v2.json \
    --out  ../output/prova_final_1bim_gabarito.docx \
    --answer-key
```

### Argumentos disponíveis

| Argumento | Padrão | Descrição |
|-----------|--------|-----------|
| `--bank` | `../bases/exam_01_final_bank_v2.json` | Caminho para o banco de questões JSON |
| `--out` | `../output/prova_final_1bim.docx` | Caminho do arquivo `.docx` de saída |
| `--answer-key` | (desativado) | Acrescenta página de gabarito ao final (cópia do professor) |
| `--skip-validation` | (desativado) | Pula a validação do banco (não recomendado) |

### Estrutura do documento gerado

- **Cabeçalho** — campos para Nome Completo, Curso, E-mail e Tier de Preferência
- **Parte 1** — Questões 1–10 (Tier 1 — todos os alunos)
- **Parte 2** — Questões 11–20 (Tier 2 — apenas se indicado pelo professor)
- **Gabarito** *(opcional, `--answer-key`)* — tabela compacta com letra e texto da resposta correta em verde

### Saída esperada

```
============================================================
EXAM 01 FINAL — DOCX GENERATOR
============================================================

Question bank: .../bases/exam_01_final_bank_v2.json
Output file:   .../output/prova_final_1bim.docx
Answer key:    no

Validating question bank against rules in §3.4 and §3.5...
✓ Question bank passed all validation checks.
Building document...
✓ Document saved: .../output/prova_final_1bim.docx

Done.
```

> **Nota:** O ambiente virtual já inclui `python-docx`. Se precisar reinstalar:
> ```bash
> cd exam_prep/exam_01
> venv/bin/pip install python-docx
> ```

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
| `exam_01_final_bank_v2.json` | v2.4 | **Recomendado.** Questões com sujeitos I/you/we/they; sem `going to`; marcadores temporais em todas as questões de completar frase; aprovado pelo `validate_question_bank.py`. |
| `exam_01_final_bank.json` | v1 | Primeira versão. Contém questões com 3ª pessoa singular e `going to`. Não distribuir. |

---

## Referências

- [PLAN_EXAM_01_FINAL.md](PLAN_EXAM_01_FINAL.md) — plano completo do exame (inclui §3.4 Regras de Construção e §3.5 Revisão de Ambiguidade)
- [validate_question_bank.py](../scripts/validate_question_bank.py) — script de validação do banco
- [create_exam_01_final_docx.py](../scripts/create_exam_01_final_docx.py) — gerador da prova impressa (DOCX)
- [Google Cloud Console](https://console.cloud.google.com/) — gerenciamento de credenciais
- [Google Forms API](https://developers.google.com/forms/api/reference/rest) — documentação da API
