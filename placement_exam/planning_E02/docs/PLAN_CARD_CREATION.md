# E02 — Plano de Criação de Flashcards

**Exercício**: E02 — Primeiro Exercício com Criação de Cartões
**Período previsto**: Abril 2026
**Turma**: ~54 alunos ativos (Biotecnologia, Metrologia, Segurança Cibernética)
**Elaborado em**: Março 2026

Este documento é um elemento de discussão para o planejamento pedagógico de E02. Consolida os dados do placement exam e de E01 para orientar duas decisões centrais: **qual texto usar** como base dos cartões (Component B) e **como os alunos devem criar cada cartão** para maximizar o aprendizado dentro do sistema StudyAmigo/SM-2.

> **Atualização — Março 2026**: O bug de crescimento linear de intervalos do SM-2 foi corrigido antes de E02. O peso da maturidade foi restaurado para 0.30 no componente Q. Ver `CARD_PROGRESSION_ANALYSIS.md` para detalhes. A seção 3 deste documento (pré-requisito técnico) é histórica.

---

## Sumário

1. [Ponto de partida: o que E01 nos disse](#1-ponto-de-partida-o-que-e01-nos-disse)
2. [Distribuição de tiers confirmada](#2-distribuição-de-tiers-confirmada)
3. [Pré-requisito técnico: correção do SM-2 antes de E02](#3-pré-requisito-técnico-correção-do-sm-2-antes-de-e02)
4. [Estrutura de E02: três componentes](#4-estrutura-de-e02-três-componentes)
5. [Seleção de texto — Component B](#5-seleção-de-texto--component-b)
6. [Metodologia de criação de cartões: análise e melhorias](#6-metodologia-de-criação-de-cartões-análise-e-melhorias)
   - [6.4.1 Problema (a): como o aluno chega à palavra](#641-problema-a-como-o-aluno-chega-à-palavra)
   - [6.4.2 Problema (b): como o Tier 1 escreve uma frase em inglês](#642-problema-b-como-o-tier-1-escreve-uma-frase-em-inglês)
7. [Método aprimorado por tier](#7-método-aprimorado-por-tier)
8. [Organização dos baralhos e nomenclatura](#8-organização-dos-baralhos-e-nomenclatura)
9. [Critérios de avaliação dos cartões criados](#9-critérios-de-avaliação-dos-cartões-criados)
10. [Component C — Material de livre escolha](#10-component-c--material-de-livre-escolha)
11. [Itens em aberto para discussão](#11-itens-em-aberto-para-discussão)

---

## 1. Ponto de partida: o que E01 nos disse

E01 foi um exercício diagnóstico. Nenhum aluno criou cartões — todos receberam o baralho **Verbal Tenses** pré-carregado e a tarefa era simplesmente revisar. Isso gerou os primeiros dados reais de interação com o SM-2.

### Resultados consolidados do placement exam + E01

| Sinal | Resultado | Implicação para E02 |
|-------|-----------|---------------------|
| **Distribuição de caminhos** | 17.5% Path A / 64.9% Path B / 17.5% Path C | Maioria esmagadora no nível intermediário-baixo |
| **Tier provisório (placement)** | ~56% Tier 1, ~33% Tier 2, ~0-2% Tier 3 | E02 deve ser acessível para Tier 1 sem frustrar os mais avançados |
| **60% dos Path A são "subestimadores"** | Alunos dizem "nunca estudei inglês" mas reconhecem cognatos | Tier 1 não é vazio total — exposição passiva existe |
| **0 estudantes Tier 3 identificados** | Threshold ajustado para 16/25; candidatos: 2-3 alunos com 16-14/25 | Tier 3 será muito pequeno (2-5 alunos) ou inexistente inicialmente |
| **10 alunos sem atividade em E01** | 18.5% da turma com nota 0 | E02 precisa de um gatilho de engajamento mais claro |
| **Bug de crescimento linear de intervalos** | Maturidade ≈ 0% para todos em E01 | Corrigir antes de E02 para que a métrica de maturidade funcione |

### O que E01 não mediu

E01 não avaliou a capacidade dos alunos de **criar** cartões — apenas de **revisar** cartões prontos. Criar um cartão é uma habilidade distinta:

- Requer identificar o que é digno de memorização num texto
- Requer formular uma pergunta/frente que active a memória
- Requer calibrar a dificuldade (cartão muito simples = não aprende nada; muito complexo = nunca passa para Review)

E02 é a primeira vez que os alunos vão exercitar essa habilidade no contexto do SM-2. O design das instruções e do texto-base deve minimizar a fricção dessa introdução.

---

## 2. Distribuição de tiers confirmada

Com base na combinação dos três sinais (Sinal 0: auto-avaliação, Sinal 1: placement exam, Sinal 2: E01), a distribuição provisória para E02 é:

| Tier | Perfil | Estimativa (turma de 54 ativos) |
|------|--------|--------------------------------|
| **Tier 1 — Foundation** | Inglês mínimo ou passivo. Reconhece cognatos, vocabulário básico. | ~30-33 alunos (55-60%) |
| **Tier 2 — Developing** | Inglês de escola pública. Consegue ler frases simples, identifica tempos verbais básicos. | ~18-20 alunos (33-37%) |
| **Tier 3 — Expanding** | Inglês de curso particular ou exposição significativa. Lê parágrafos curtos com fluência. | ~2-5 alunos (4-9%) |

> **Nota**: Esses números são provisórios. A alocação definitiva combina placement exam + E01 performance e deve ser finalizada pelo professor antes do início de E02.

### Alerta: alunos sem atividade em E01

Os 10 alunos que não participaram de E01 entram em E02 sem Signal 2. Para eles, o tier deve ser atribuído exclusivamente com base no placement exam. Se o placement indicar Tier 1, alocá-los em Tier 1 sem exceção — E02 servirá como seu diagnóstico tardio.

---

## 3. Pré-requisito técnico: correção do SM-2 antes de E02 ✅ RESOLVIDO

> **Status**: Bug corrigido em março de 2026, antes do início de E02.

O documento `CARD_PROGRESSION_ANALYSIS.md` identificou um bug crítico no cálculo de intervalos do `server/app.py` (linha 1702): os intervalos cresciam **linearmente** (+1 dia por revisão) em vez de **exponencialmente** (×fator de facilidade), como previsto no SM-2.

**Por que importava especificamente para E02:**

| Situação | E01 | E02 |
|----------|-----|-----|
| Alunos criam cartões? | Não | **Sim** |
| Duração do exercício | 3 semanas | ~3-4 semanas |
| Maturidade esperada ao final | 0% (aceitável — bug ativo + workaround B1) | >0% — bug corrigido, peso restaurado |
| Peso da maturidade na nota Q | 0% (workaround) | **30% (restaurado)** |

**Ações concluídas:**
- ✅ Linha 1702 do `server/app.py` corrigida: intervalos agora crescem multiplicativamente por `current_factor / 1000.0`
- ✅ Peso da maturidade restaurado para 0.30 no componente Q para E02+
- Ver `CARD_PROGRESSION_ANALYSIS.md` (seção "Resolution Log") para detalhes técnicos

---

## 4. Estrutura de E02: três componentes

Conforme a metodologia em `READING_MATERIAL_METHODOLOGY.md` (Seção 5), E02 é o primeiro exercício com os três componentes ativos:

| Componente | Descrição | Peso na nota |
|------------|-----------|--------------|
| **A — Shared Deck Review** | Revisão do batch 2 do baralho curado compartilhado (`SHARED_CURATED_v1`) | ~30% |
| **B — Tiered Passage + Card Creation** | Leitura de texto nivelado + criação de cartões do texto | ~40% |
| **C — Free Choice** | Material de livre escolha + criação de cartões mínima | ~30% |

Este documento foca nos Componentes B e C, que são novidades em E02.

---

## 5. Seleção de texto — Component B

### 5.1 Critérios de seleção

O texto-base de Component B deve satisfazer simultaneamente:

1. **Relevância cruzada**: Aplicável às três áreas técnicas (Metrologia, Biotecnologia, Segurança Cibernética)
2. **Alta densidade de cognatos no Tier 1**: Para manter os alunos Foundation engajados e confiantes na primeira experiência de criação de cartões
3. **Vocabulário alinhado com E01**: Continuidade temática com os tempos verbais estudados; o texto deve usar presente simples, passado simples e futuro de forma natural
4. **Gerabilidade de cartões**: O texto deve ter vocabulário-chave identificável, não apenas ideias abstratas — senão Tier 1 fica sem o que transformar em frente/verso
5. **Interesse estudantil**: Tópicos ligados a tecnologia e cotidiano têm melhor engajamento nesta faixa etária

### 5.2 Candidatos a tópico para E02

Quatro tópicos foram pré-selecionados considerando os critérios acima:

---

#### Opção 1 — Inteligência Artificial: o que é e como funciona ⭐ (RECOMENDADO)

**Justificativa:**
- Vocabulário com altíssima densidade de cognatos para Tier 1: *artificial* / *artificial*, *intelligence* / *inteligência*, *algorithm* / *algoritmo*, *data* / *dados*, *system* / *sistema*, *process* / *processo*, *digital* / *digital*, *technology* / *tecnologia*
- Relevante para as três áreas: automação em metrologia, bioinformática em biotecnologia, segurança em Ciber
- Tópico que os alunos já conhecem de nome (vivência com apps, YouTube, TikTok), o que reduz a carga cognitiva e mantém foco no idioma
- Permite progressão natural de tempos verbais: "AI **is** a system that **learns**..." (presente simples), "In 1956, researchers **created**..." (passado simples), "In the future, AI **will help**..." (futuro)
- Alto potencial de vocabulário técnico-acadêmico que aparece em múltiplas áreas

**Amostra de passagem Tier 1** (20-35 palavras, tempo presente, cognatos dominantes):
> *Artificial intelligence is a technology. A computer system learns from data. It processes information and finds patterns. AI helps doctors, engineers, and scientists every day.*

**Amostra de passagem Tier 2** (75-100 palavras, presente + passado):
> *Artificial intelligence, or AI, is a type of computer technology that allows machines to learn from experience. In the past, computers could only follow fixed instructions written by humans. Today, AI systems analyze large amounts of data to recognize patterns and make decisions. For example, an AI system can identify diseases in medical images with high accuracy. This technology is now used in many fields, including biotechnology, cybersecurity, and quality control in manufacturing.*

**Amostra de passagem Tier 3** (200-250 palavras, estruturas complexas, voz passiva, condicionais):
> *(Texto completo com: relative clauses — "AI systems, which were first theorized in the 1950s..."; passive voice — "algorithms are trained on massive datasets"; conditional — "If a model is exposed to biased data, its predictions will reflect that bias"; academic vocabulary — "methodology", "inference", "optimization")*

---

#### Opção 2 — O Sistema Imunológico: como o corpo combate doenças

**Justificativa:**
- Alta densidade de cognatos: *virus* / *vírus*, *immune* / *imune*, *bacteria* / *bactéria*, *protein* / *proteína*, *organism* / *organismo*, *infection* / *infecção*
- Especialmente relevante para Biotecnologia; moderadamente para Metrologia/Ciber
- Vocabulário muito gerável em cartões: palavras técnicas concretas com significados claros
- Risco: pode ser percebido como "só de biologia" pelos alunos de Segurança Cibernética

**Melhor uso**: Reservar para E03-E04 quando os alunos já tiverem fluência na criação de cartões. Em E02 (estreia), a familiaridade do tópico ajuda mais.

---

#### Opção 3 — A Internet: história e como funciona

**Justificativa:**
- Cognatos: *internet*, *network* / *rede*, *protocol* / *protocolo*, *digital*, *data* / *dados*, *server* / *servidor*, *connection* / *conexão*
- Relevante para Segurança Cibernética diretamente; aplicável às demais
- Tem progressão temporal natural (passado: criação; presente: funcionamento; futuro: evolução)
- Risco: vocabulário técnico de redes pode ser difícil para Tier 1 sem suporte de cognatos suficiente

**Melhor uso**: E04-E05, depois que Tier 1 tiver mais vocabulário acumulado.

---

#### Opção 4 — Medição e Precisão no Cotidiano

**Justificativa:**
- Cognatos: *meter* / *metro*, *precision* / *precisão*, *accuracy* / *acurácia*, *standard* / *padrão*, *instrument* / *instrumento*, *calibration* / *calibração*
- Diretamente relevante para Metrologia; conexão mais fraca com Biotecnologia e Ciber
- Q25 do placement exam era justamente sobre "precision vs. accuracy" — e 80.9% acertaram, indicando que os alunos têm algum domínio desse vocabulário em contexto

**Melhor uso**: E03, quando o foco específico em Metrologia for mais bem aproveitado e os alunos de outras áreas já tiverem vocabulário geral suficiente.

---

### 5.3 Recomendação para E02: Inteligência Artificial

A Opção 1 (IA) é a mais indicada para a estreia da criação de cartões porque:

1. **Máxima acessibilidade para Tier 1**: A densidade de cognatos é a maior entre as opções, o que protege a experiência dos alunos mais frágeis no primeiro exercício com carta criação
2. **Familiaridade prévia reduz carga cognitiva**: Os alunos já têm um modelo mental do tópico em português — podem concentrar o esforço no idioma, não na compreensão do conteúdo
3. **Tempos verbais diversificados**: Conecta organicamente com o que foi estudado em E01 (Verbal Tenses deck)
4. **Vocabulário técnico-acadêmico cruzado**: Termo como *algorithm*, *data*, *system*, *process* aparecem em TODAS as três áreas técnicas
5. **Engajamento elevado**: IA é um tópico que os alunos trazem para a aula espontaneamente — isso ajuda especialmente nos 10 alunos que não participaram de E01

---

## 6. Metodologia de criação de cartões: análise e melhorias

### 6.1 O método atual (baseline)

O método ensinado até agora aos alunos é composto de quatro etapas:

| Etapa | O que o aluno faz |
|-------|-------------------|
| **1. Seleção** | Identifica substantivos, adjetivos ou palavras importantes no texto lido |
| **2. Pesquisa** | Pesquisa em dicionários on-line 3 ou 4 exemplos de frases com a palavra escolhida |
| **3. Tradução** | Anota a tradução via Google Translator |
| **4. Criação** | Cria 1 ou 2 cartões com a palavra escolhida no StudyAmigo |

O resultado típico é um cartão do tipo:

```
Frente: process
Verso:  processo / processar
```

Este método funciona como ponto de partida. Ele garante que os alunos façam algo — e "fazer algo" já é melhor do que não fazer nada. No entanto, cada etapa tem uma limitação que o impede de maximizar o aprendizado.

---

### 6.2 Análise crítica: o que o método atual não captura

#### Problema 1 — Seleção incompleta: verbos e colocações ficam de fora

Focar em "substantivos e adjetivos" ignora os **verbos**, que são a parte mais gerativa da língua. Para produzir uma frase em inglês, o aluno precisa saber como usar o verbo — não apenas o substantivo isolado.

Além disso, palavras raramente funcionam isoladas. A língua inglesa é altamente **colocacional**: certas palavras aparecem juntas com frequência, e memorizá-las em pares é mais eficiente do que memorizá-las individualmente.

> **Exemplo**: No texto sobre IA, "analyze data" é uma colocação. Um cartão com apenas "analyze" ou apenas "data" é menos útil do que um cartão com a colocação completa.

**Outro problema de seleção**: o aluno pode escolher cognatos óbvios (como *technology* → *tecnologia*) que não precisam ser estudados — desperdício de "slots" de cartão.

#### Problema 2 — A pesquisa de 3–4 exemplos é trabalho passivo

Copiar exemplos de dicionário é **processamento passivo**. O aluno copia frases que já existem sem precisar produzir nada. O tempo gasto copiando 3–4 exemplos poderia ser melhor usado escrevendo **uma frase própria** — que aciona o *efeito de geração*.

> **Efeito de geração** (generation effect): informação que a pessoa **produz** por conta própria é retida significativamente melhor do que informação copiada ou lida passivamente. Está documentado desde os anos 1970 em psicologia cognitiva e é um dos princípios centrais do aprendizado ativo.

#### Problema 3 — O cartão palavra → tradução esgota-se rapidamente

Um cartão `process → processo` é fácil demais após 2 ou 3 revisões. O aluno clica **Easy** automaticamente, o SM-2 agenda o cartão para daqui a 30, 60 dias — e a palavra nunca foi realmente praticada em contexto de uso.

O problema é que **reconhecer** uma palavra (saber que *process* = *processo* quando você vê a palavra isolada) é muito mais fácil do que **usar** a palavra (produzir "The system *processes* the data before storing it"). Cartões de reconhecimento puro superestimam o quanto o aluno realmente aprendeu.

#### Problema 4 — Google Translate para o verso perde informação de uso

A tradução dada pelo Google Translate responde "o que essa palavra significa?", mas não responde "como eu uso essa palavra?". Para Tier 2 e 3, a ausência de informação sobre contexto de uso é uma perda real.

> **Exemplo**: *achieve* = *alcançar* é a tradução, mas o aluno precisa saber que se diz "achieve a goal" (não "achieve a dream"), que é verbo transitivo, que o substantivo é *achievement*. Nada disso aparece na tradução.

---

### 6.3 O método aprimorado: quatro upgrades

Os quatro upgrades abaixo são cumulativos e progressivos por tier. Não precisam ser todos introduzidos de uma vez — E02 é a primeira experiência, e adicionar complexidade excessiva na estreia pode desanimar.

**Sugestão de introdução gradual:**
- **E02**: Introduzir upgrades 1 e 3 (seleção melhorada + cloze)
- **E03**: Introduzir upgrade 4 (frase própria)
- **E04+**: Usar o método completo (todos os quatro upgrades)

---

#### Upgrade 1 — Ampliar a seleção: verbos, colocações, e o "teste de produção"

**Antes**: substantivos e adjetivos importantes
**Depois**: substantivos, adjetivos, **verbos** e **colocações** que passam no "teste de produção"

> **Teste de produção**: para cada palavra candidata, o aluno tenta mentalmente completar a frase: "Eu consigo usar essa palavra numa frase em inglês agora, sem olhar?" Se sim → pular (já sabe). Se não → criar cartão.

Isso evita cartões de cognatos desnecessários e garante que cada cartão represente um gap real de conhecimento.

Para colocações: ao identificar uma palavra interessante no texto, perguntar "com o que essa palavra normalmente aparece?". Se o texto tem "analyzes large amounts of data", a colocação candidata é "analyze + data" — mais valiosa do que apenas "analyze".

---

#### Upgrade 2 — Reduzir a pesquisa: 1 exemplo de qualidade, não 3–4

**Antes**: pesquisar 3 ou 4 exemplos de frases no dicionário
**Depois**: encontrar **1 exemplo claro e curto** de um dicionário confiável (Cambridge, Oxford)

O objetivo da pesquisa não é acumular exemplos — é encontrar um modelo de uso que mostre a palavra no contexto correto. Um bom exemplo é suficiente.

Para Tier 2 e 3: usar o **Cambridge Dictionary** (learner's version), que fornece exemplos de uso, nível de dificuldade, e collocations. É mais rico do que o Google Translate para compreensão de uso.

```
Cambridge: analyze (verb)
→ "Scientists are still analyzing the data from the experiment."
→ Noun form: analysis. Common collocations: analyze data, analyze results, analyze a problem.
```

---

#### Upgrade 3 — Mudar o formato: de palavra→tradução para cloze contextual

**Antes**: frente = palavra em inglês / verso = tradução em português
**Depois**: frente = frase do texto com a palavra removida / verso = a palavra + tradução + dica de uso

Isso é chamado de **cloze deletion** (deleção por lacuna) e é o formato de cartão mais recomendado para aquisição de vocabulário em L2 por uma razão simples: força o aluno a **lembrar** a palavra dentro de um contexto de uso, não isolada.

**Comparação direta:**

| Formato | Frente | Verso | O que treina |
|---------|--------|-------|--------------|
| **Atual** | `process` | `processo / processar` | Reconhecimento da palavra isolada |
| **Cloze** | `AI systems _____ large amounts of data.` | `analyze — analisar. Colocação: analyze data.` | Produção da palavra em contexto |

O cloze não é mais difícil — é diferente. Ele simula o que o aluno vai precisar fazer na vida real: ver uma frase incompleta (mentalmente, ao escrever ou falar) e recuperar a palavra correta.

---

#### Upgrade 4 — O verso inclui uma frase criada pelo próprio aluno

**Este é o upgrade mais impactante do ponto de vista cognitivo.**

**Antes**: o verso tem a tradução (copiada do Google Translate) + talvez um exemplo copiado do dicionário
**Depois**: o verso termina com uma frase **escrita pelo próprio aluno** usando a palavra

```
Verso do cartão (método aprimorado):
  analyze — analisar
  Exemplo (dicionário): "Scientists are still analyzing the data from the experiment."
  Minha frase: "I analyzed the errors in my last English exercise."
```

A frase própria do aluno:
1. Ativa o **efeito de geração** — a palavra foi produzida pelo aluno, não apenas copiada
2. Conecta a palavra a um **contexto pessoal** — memórias pessoais são mais fáceis de recuperar
3. Obriga o aluno a pensar na **forma correta** (tempo verbal, preposição, etc.) antes de criar o cartão
4. Funciona como **verificação de compreensão** — se o aluno não consegue escrever a frase, ele não entendeu a palavra bem o suficiente para criar um cartão

> **Instrução ao aluno**: "Se você não consegue escrever uma frase sua com essa palavra, você ainda não aprendeu a palavra — você apenas a reconheceu. Não crie o cartão ainda. Volte ao exemplo do dicionário, releia, e tente de novo."

---

### 6.4 Problemas práticos: o que o método aprimorado ainda não responde

As seções anteriores descrevem o **método ideal**. Dois problemas práticos ficaram em aberto, especialmente para Tier 1:

> **Problema (a)**: Como o aluno de Tier 1 chega à palavra? O "teste de produção" pressupõe que ele já sabe inglês suficiente para avaliar seu próprio gap — o que contradiz ser Tier 1.

> **Problema (b)**: Como o aluno de Tier 1 escreve uma frase em inglês, se ele mal lê o idioma?

Ambos os problemas têm solução — mas exigem **andaimes** (*scaffolding*) que o método ainda não fornece.

---

### 6.4.1 Problema (a): como o aluno chega à palavra

#### A armadilha do Tier 1

O "teste de produção" funciona para Tier 2/3: o aluno lê a palavra, percebe que não conseguiria usá-la sozinho, e cria o cartão. Mas um aluno Tier 1 não consegue aplicar esse teste porque **não tem parâmetro de comparação** — quase tudo é desconhecido para ele, e ele não sabe distinguir o que vale a pena aprender do que é raro ou irrelevante.

Deixar a seleção completamente livre para um Tier 1 leva a dois resultados ruins:
- **Paralisia**: o aluno não sabe por onde começar, cria zero ou um cartão e desiste
- **Seleção aleatória**: o aluno cria cartões de palavras pouco úteis (muito raras, ou ao contrário, tão básicas que não precisam ser estudadas)

#### Solução: seleção em dois modos por tier

| Tier | Modo de seleção | Quem escolhe |
|------|----------------|--------------|
| **Tier 1** | **Seleção guiada pelo professor**: o professor entrega uma lista de 8–12 palavras-alvo do texto. O aluno cria cartões a partir dessa lista — a decisão é *como* fazer o cartão, não *qual* palavra escolher. | Professor |
| **Tier 2** | **Seleção pelo critério "precisei consultar"**: o aluno lê o texto com Google Translate disponível; toda palavra que ele precisou traduzir para entender a frase *e* que ele não teria produzido sozinho entra na lista candidata (máximo 10 candidatas por texto). | Aluno, com critério definido |
| **Tier 3** | **Seleção pelo teste de produção + colocações**: conforme descrito no Upgrade 1. | Aluno, autônomo |

#### Por que entregar a lista para Tier 1 é pedagogicamente correto

Pode parecer que "dar a lista" pula o processo de seleção, mas o aprendizado mais importante em E02 para Tier 1 **não é aprender a selecionar palavras** — é aprender a **criar bons cartões** e a usar o sistema de revisão. A seleção pode ser introduzida gradualmente em E03/E04, quando o aluno já entendeu o ciclo de criação e revisão.

Analogia: não ensinamos uma criança a ler pedindo que ela escolha qual letra aprender primeiro. O professor sequencia o conteúdo; a autonomia vem depois.

---

### 6.4.2 Problema (b): como o Tier 1 escreve uma frase em inglês

#### O efeito de geração não exige fluência

O erro intuitivo é pensar que "escrever uma frase própria" requer fluência. Não requer. A pesquisa original de Slamecka & Graf (1978) mostrou que o efeito de geração ocorre mesmo em tarefas mínimas, como **completar uma lacuna** ou **trocar uma palavra** de uma frase existente. O que importa é que o cérebro execute uma operação **ativa** sobre o material — não que produza algo original do zero.

#### A escada de andaimes (*scaffolding ladder*)

Existem cinco níveis de produção, do mais simples ao mais complexo. Cada tier começa num nível diferente:

| Nível | Nome | O que o aluno faz | Tier inicial |
|-------|------|-------------------|--------------|
| **1** | **Substituição** | Pega o exemplo do dicionário e troca 1 palavra (sujeito, objeto ou tempo verbal) por algo da própria vida | Tier 1 |
| **2** | **Template** | Preenche uma moldura de frase fornecida pelo professor | Tier 1 (alternativo) |
| **3** | **Tradução reversa** | Escreve a frase em português → cola no Google Translate → edita deliberadamente 1 coisa no resultado | Tier 1/2 |
| **4** | **Frase guiada** | Escreve uma frase sobre seu próprio curso usando a palavra, com ajuda de dicionário | Tier 2 |
| **5** | **Produção livre** | Escreve uma frase original sem andaime | Tier 3 |

#### Nível 1 em prática (Tier 1 — Substituição)

Exemplo com a palavra *analyze*, texto sobre IA:

```
Exemplo do dicionário:
  "Scientists are still analyzing the data from the experiment."

Instrução ao aluno Tier 1:
  "Troque a palavra 'Scientists' por algo da sua área."

Frase do aluno (Biotecnologia):
  "Biologists are still analyzing the data from the experiment."

Frase do aluno (Metrologia):
  "Engineers are still analyzing the data from the sensors."
```

Por que funciona:
- O aluno não precisa saber inglês para trocar uma palavra
- A troca cria uma âncora pessoal ("engenheiros" é a profissão dele)
- A frase resultante é ligeiramente diferente do original — o suficiente para ativar o efeito de geração
- O esforço cognitivo é mínimo, mas a retenção é significativamente maior do que só copiar

#### Nível 2 em prática (Tier 1 — Template)

O professor prepara templates específicos para o texto do exercício:

```
Templates para o texto de IA (E02):
  "AI systems can _______ large amounts of _______."
  "In my course, I often _______ data to _______."
  "A _______ algorithm can solve _______ problems."
```

O aluno preenche os blanks com as palavras que está estudando. Isso é especialmente útil para os primeiros 2–3 exercícios enquanto o aluno ainda não tem referência de como construir frases em inglês.

#### Nível 3 em prática (Tier 1/2 — Tradução reversa editada)

Para alunos que já têm alguma familiaridade mas ainda não têm confiança para escrever:

```
Passo 1: escreva em português
  "Os engenheiros analisam os dados dos sensores em tempo real."

Passo 2: cole no Google Translate
  → "Engineers analyze sensor data in real time."

Passo 3: mude UMA coisa deliberadamente
  → "Metrologists analyze sensor data in real time." (trocou "Engineers" por sua área)
  → "Engineers analyze sensor data every day." (trocou "in real time" por algo mais pessoal)
```

O ato de editar deliberadamente — mesmo que seja uma troca de uma palavra — ativa o processamento ativo que o efeito de geração requer. O aluno está *tomando uma decisão* sobre a língua, não apenas copiando.

#### Resumo: o que cada tier deve colocar no verso do cartão

| Tier | Conteúdo do verso | Nível de produção |
|------|--------------------|-------------------|
| **Tier 1** | Tradução (PT) + exemplo do dicionário + frase com 1 substituição pessoal | Nível 1 ou 2 |
| **Tier 2** | Tradução (PT) + definição curta (EN) + frase guiada sobre o curso | Nível 3 ou 4 |
| **Tier 3** | Definição (EN) + frase original + colocação identificada | Nível 5 |

> **Nota pedagógica**: Não é preciso que a frase do aluno seja perfeita. Um erro gramatical na frase própria não invalida o cartão — na revisão, o aluno vai ver a própria frase, perceber o erro, e isso também é aprendizado. Se o professor quiser corrigir, pode ser feito numa rodada de revisão de cartões no final do exercício, não como bloqueio para criar o cartão.

---

### 6.5 Comparação resumida: método atual vs. método aprimorado

| Etapa | Método atual | Método aprimorado |
|-------|-------------|-------------------|
| **Seleção** | Substantivos e adjetivos | Substantivos, adjetivos, verbos e colocações; filtrado pelo teste de produção |
| **Pesquisa** | 3–4 exemplos copiados | 1 exemplo de qualidade (Cambridge/Oxford) |
| **Tradução** | Google Translate (somente) | Google Translate + definição em inglês (Tier 2/3) |
| **Formato do cartão** | Palavra → tradução | Cloze contextual → palavra + tradução + frase própria |
| **Processamento** | Passivo (copia e cola) | Ativo (produz uma frase própria) |
| **O que mede no SM-2** | Reconhecimento da palavra isolada | Produção da palavra em contexto |
| **Durabilidade do cartão** | Esgota-se rápido (Easy em 2–3 revisões) | Permanece útil por mais revisões |

### 6.5 Impacto esperado nas métricas de E02

| Métrica | Com método atual | Com método aprimorado |
|---------|-----------------|----------------------|
| **Retenção (retention_sub)** | Tende a ser alta artificialmente (cartões muito fáceis) | Mais calibrada — cartões cloze são levemente mais desafiadores |
| **Ease factor médio** | Tende a subir rápido (Easy pressionado frequentemente) | Mais distribuído entre Good e Easy |
| **Maturidade (maturity_sub)** | Alta após poucas revisões (cartões muito simples atingem ivl ≥ 21 rápido) | Maturidade mais significativa (baseada em uso real, não reconhecimento) |
| **Engajamento (time_sub)** | Revisão muito rápida (palavra → clica Easy em < 2 s) | Tempo de revisão mais realista (cloze exige leitura da frase) |

> **Nota sobre o time_sub**: O `time_sub` do componente E penaliza revisões com menos de 2 segundos. Cartões do tipo palavra→tradução são respondidos quase automaticamente após 2–3 revisões, caindo abaixo desse limiar. Cartões cloze exigem leitura da frase inteira, naturalmente mantendo o tempo de revisão dentro da janela válida (2–60 s).

---

## 7. Método aprimorado por tier

Esta é a seção central do documento. A qualidade do aprendizado pela repetição espaçada depende diretamente de **como** o cartão é construído. Um cartão mal formulado (muito simples, muito vago, ou sem contexto) pode ser revisado dezenas de vezes sem produzir aprendizado real.

### Princípios gerais (todos os tiers)

Antes das instruções específicas por tier, os seguintes princípios se aplicam a todos os alunos:

> **Regra do cartão atômico**: Cada cartão deve testar **exatamente uma** coisa. Um cartão com três perguntas na frente vai fazer o aluno clicar *Again* quando souber 2 das 3 — e o SM-2 vai tratar o cartão inteiro como não aprendido.

> **Regra do contexto mínimo**: A frente do cartão deve ter contexto suficiente para que haja apenas uma resposta correta. "What is 'data'?" é ambíguo. "In the sentence 'AI systems analyze large amounts of _____', what is the missing word?" é específico.

> **Regra da produtividade**: O verso do cartão deve conter **mais do que a resposta** — deve conter uma âncora de memória. Para Tier 1: a tradução + um exemplo. Para Tier 2: a definição em inglês + tradução. Para Tier 3: a definição acadêmica + uso em frase.

---

### 7.1 Tier 1 — Foundation

**Perfil do aluno**: Reconhece cognatos, vocabulário muito limitado. Nunca criou flashcards antes (provavelmente).

**Tipo de cartão recomendado: Palavra → Tradução com exemplo**

| Elemento | Instrução |
|----------|-----------|
| **Frente** | A palavra em inglês isolada, opcionalmente com a frase original como contexto: *"learn (in: 'A computer system learns from data')"* |
| **Verso** | Tradução em português + uma frase nova usando a palavra: *"aprender. Exemplo: 'I learn English every day.'"* |
| **Meta de cartões** | 5–8 cartões por exercício |
| **Vocabulário alvo** | Palavras do texto que o aluno **não reconheceu de imediato** — não criar cartão de cognatos óbvios como *technology* → *tecnologia* |

#### Texto recomendado para E02 Tier 1: Chapeuzinho Vermelho

Uma versão simplificada (~200 palavras) da Chapeuzinho Vermelho é a escolha ideal para a **estreia da criação de cartões** por quatro razões simultâneas:

1. **Carga cognitiva zero no enredo**: o aluno já conhece a história em português — toda a atenção vai para o vocabulário, não para entender o que está acontecendo
2. **Conecta com E01**: narrativa em passado (*walked, saw, said, brought, arrived*) usa exatamente os verbal tenses treinados em E01
3. **Substituição natural**: "Little Red Riding Hood walked through the forest" → "I walked through the campus" — o nível 1 de andaime funciona imediatamente
4. **Vocabulário concreto e fácil de exemplificar**: *gather, carry, warn, notice, arrive, dangerous* — palavras que os alunos podem usar em frases sobre a própria vida

> **Nota**: para E03/E04, evoluir para textos técnicos (IA, Metrologia, Biossegurança). E02 é sobre aprender o método — a Chapeuzinho é o andaime perfeito para isso.

---

#### Instrução ao aluno — o ponto crítico sobre o formato do cartão

Existe uma distinção importante que precisa ser ensinada explicitamente: **a frente do cartão deve testar exatamente uma coisa**. Uma frase completa sem marcação da palavra-alvo cria um cartão de *leitura* (o aluno revisa a frase inteira), não um cartão de *vocabulário* (o aluno recupera uma palavra específica).

A solução para Tier 1 é **marcar a palavra-alvo em maiúsculo ou entre colchetes** na frente do cartão:

```
❌ Frente ambígua:
   "Engineers analyze sensor data."
   (O que o cartão está testando? analyze? sensor? data?)

✅ Frente correta para E02:
   "Engineers [ANALYZE] sensor data."
   (Claro: o cartão está testando 'analyze')

✅ Frente cloze para E03+ (próxima evolução):
   "Engineers _______ sensor data."
   (O aluno precisa produzir a palavra — um degrau acima)
```

---

**Instruções passo a passo para o aluno Tier 1 (E02):**

1. Receba a lista de **10 palavras-alvo** fornecida pelo professor, retiradas do texto da Chapeuzinho.
2. Escolha **uma palavra** da lista que você quer aprender.
3. Encontre **1 exemplo de frase** com essa palavra num dicionário online (Cambridge ou apenas Google).
4. **Troque uma palavra de contexto** da frase por algo da sua própria vida (substitua "Little Red Riding Hood" por "I", ou "scientists" por "engineers", etc.).
5. Crie o cartão no StudyAmigo:
   - **Frente**: a frase modificada, com a palavra-alvo em **[MAIÚSCULO]**
   - **Verso**: a palavra em inglês (minúsculo) = tradução em português
6. Repita para mais 4–7 palavras da lista.
7. Revise imediatamente após criar (primeira sessão de aprendizado).

**Exemplo completo — palavra: *gather***

```
Dicionário:
  "Little Red Riding Hood gathered flowers in the forest."

Substituição (aluno de Metrologia):
  "I gathered data from the sensors in the lab."

Cartão criado:
  Frente: "I [GATHERED] data from the sensors in the lab."
  Verso:  gather / gathered = coletar, reunir
```

**Por que funciona:**
- O aluno modificou a frase → **efeito de geração** ativado na criação
- A frase é sobre a própria vida do aluno → **âncora de memória pessoal**
- A palavra-alvo está marcada → o SM-2 testa exatamente o que foi aprendido
- O verso é simples → fácil de lembrar, sem sobrecarga

**Exemplo de cartão mal-feito — Tier 1 (evitar):**
```
Frente: What is AI?
Verso:  Artificial intelligence is a type of computer technology that
        allows machines to learn from experience.
```
> ❌ Problema: A frente é uma pergunta de compreensão, não de vocabulário. O verso é longo e não será memorizado. Não tem palavra-alvo definida.

---

### 7.2 Tier 2 — Developing

**Perfil do aluno**: Entende frases simples, identifica tempos verbais básicos, vocabulário limitado mas funcional.

**Dois tipos de cartão recomendados:**

#### Tipo A — Vocabulário em contexto

| Elemento | Instrução |
|----------|-----------|
| **Frente** | Frase do texto com a palavra-alvo em branco: *"AI systems _______ large amounts of data to recognize patterns."* |
| **Verso** | A palavra + significado + exemplo novo: *"analyze — analisar. The scientists analyzed the experiment results."* |
| **Meta** | 6–10 cartões deste tipo |

#### Tipo B — Tempo verbal em contexto

| Elemento | Instrução |
|----------|-----------|
| **Frente** | Frase do texto + pergunta sobre o tempo verbal: *"'In the past, computers could only follow fixed instructions.' — What tense is 'could'? Why was it used here?"* |
| **Verso** | Resposta + regra: *"Modal past (could). Refers to an ability that existed in the past but no longer applies today."* |
| **Meta** | 3–5 cartões deste tipo |

**Instruções passo a passo para o aluno Tier 2:**

1. Leia o texto Tier 2 duas vezes: uma vez para entender, outra para identificar vocabulário-chave e estruturas gramaticais relevantes.
2. Selecione 6–10 palavras/expressões de vocabulário que você conhece pouco ou nunca usou na escrita → crie cartões Tipo A (cloze).
3. Selecione 2–4 frases com tempos verbais diferentes do presente simples → crie cartões Tipo B (análise de tempo verbal).
4. Crie os cartões no baralho `PASSAGE_E02_TIER2` no StudyAmigo.

**Exemplo de cartão bem-feito — Tier 2 Tipo A:**
```
Frente: AI systems _______ large amounts of data to recognize patterns.
Verso:  analyze
        analisar — to examine carefully to understand something.
        Exemplo novo: "We analyze data to improve our products."
```

**Exemplo de cartão bem-feito — Tier 2 Tipo B:**
```
Frente: "This technology IS NOW USED in many fields."
        → What tense? Why passive voice here?
Verso:  Present Simple Passive (is used).
        Passive voice because the subject (technology) receives the action.
        Focus is on the technology, not on who uses it.
```

---

### 7.3 Tier 3 — Expanding

**Perfil do aluno**: Lê textos curtos com razoável fluência. Reconhece estruturas gramaticais. Pode trabalhar com definições em inglês puro.

**Três tipos de cartão recomendados:**

#### Tipo A — Vocabulário acadêmico (inglês → definição em inglês)

| Elemento | Instrução |
|----------|-----------|
| **Frente** | Palavra do texto + frase de contexto: *"'algorithm' — 'algorithms are trained on massive datasets'"* |
| **Verso** | Definição em inglês + exemplo próprio (não do texto): *"A set of step-by-step rules a computer follows to solve a problem. Sorting a list of numbers from smallest to largest follows an algorithm."* |
| **Meta** | 8–12 cartões deste tipo |

#### Tipo B — Compreensão inferencial

| Elemento | Instrução |
|----------|-----------|
| **Frente** | Pergunta de compreensão que requer inferência: *"The author states that biased training data leads to biased predictions. What does this imply about the importance of data quality in AI systems?"* |
| **Verso** | Resposta sintetizada: *"Data quality determines the reliability and fairness of AI outputs. Poor or biased data creates systems that perpetuate or amplify existing inequalities."* |
| **Meta** | 4–6 cartões deste tipo |

#### Tipo C — Análise gramatical de estrutura complexa

| Elemento | Instrução |
|----------|-----------|
| **Frente** | Frase complexa do texto: *"AI systems, which were first theorized in the 1950s, have become integral to modern manufacturing quality control."* → Identify and explain the reduced relative clause. |
| **Verso** | Análise: *"'which were first theorized in the 1950s' is a non-restrictive relative clause modifying 'AI systems'. It adds non-essential information about when AI was theorized, parenthetically."* |
| **Meta** | 2–4 cartões deste tipo |

**Instruções passo a passo para o aluno Tier 3:**

1. Leia o texto Tier 3 uma vez para compreensão geral.
2. Releia com lápis na mão: marque (a) palavras acadêmicas desconhecidas ou parcialmente conhecidas, (b) frases que exigem inferência, (c) estruturas gramaticais complexas.
3. Crie 8–12 cartões Tipo A, 3–5 Tipo B, e 2–3 Tipo C.
4. Para os cartões Tipo A, **não use o dicionário bilíngue** — escreva a definição com suas próprias palavras em inglês. Isso força o processamento mais profundo.
5. Crie os cartões no baralho `PASSAGE_E02_TIER3` no StudyAmigo.

---

### 7.4 Resumo comparativo: criação de cartões por tier

| Critério | Tier 1 | Tier 2 | Tier 3 |
|----------|--------|--------|--------|
| **Tipo de cartão** | Palavra → tradução PT | Cloze + análise de tempo verbal | Vocabulário acadêmico + compreensão inferencial + gramática complexa |
| **Idioma do verso** | Português | Inglês + português | Inglês puro |
| **Meta de cartões** | 5–8 | 10–13 | 15–20 |
| **Nível de análise** | Reconhecimento léxico | Vocabulário em uso + gramática básica | Inferência + análise linguística |
| **Uso de dicionário** | Bilíngue (PT↔EN) | Bilíngue + definição em EN | Definição em EN apenas |

---

## 8. Organização dos baralhos e nomenclatura

Conforme a convenção estabelecida em `READING_MATERIAL_METHODOLOGY.md` (Seção 7.1), E02 terá os seguintes baralhos:

| Componente | Nome do baralho | Quem cria | Conteúdo |
|------------|-----------------|-----------|----------|
| **A** | `SHARED_CURATED_v1` | Instructor (pré-carregado) | Batch 2 do baralho curado compartilhado (~33 novos cartões) |
| **B — Tier 1** | `PASSAGE_E02_TIER1` | Alunos Tier 1 | 5–8 cartões do texto Tier 1 |
| **B — Tier 2** | `PASSAGE_E02_TIER2` | Alunos Tier 2 | 10–13 cartões do texto Tier 2 |
| **B — Tier 3** | `PASSAGE_E02_TIER3` | Alunos Tier 3 | 15–20 cartões do texto Tier 3 |
| **C** | Livre escolha | Todos os alunos | ≥5 cartões de material escolhido pelo aluno |

> **Atenção**: Os alunos precisam criar os baralhos com os nomes exatos acima. O script `grade_exercise.py` usa o nome do baralho para distinguir Component B de Component C. Um aluno que nomear o baralho errado terá seus cartões contabilizados como Component C em vez de B.

### Instrução prática para criação de baralho no StudyAmigo

*(A incluir no material do aluno)*

1. Acesse StudyAmigo e faça login.
2. Na tela de baralhos, clique em **"Novo Baralho"**.
3. Nomeie o baralho exatamente como indicado para o seu tier (ex: `PASSAGE_E02_TIER2`).
4. Use este baralho para todos os cartões criados a partir do texto de E02.
5. O baralho de livre escolha (Component C) pode ter qualquer nome.

---

## 9. Critérios de avaliação dos cartões criados

### 8.1 Métricas automáticas (geradas por `grade_exercise.py`)

| Métrica | O que mede | Peso em E02 |
|---------|------------|-------------|
| **Número de cartões criados** | Volume de Component B | Sub-score de Volume (V) |
| **Revisões dentro do exercício** | Aluno criou E revisou os cartões | Sub-score de Volume + Consistência |
| **Taxa de retenção dos cartões B** | Qualidade do aprendizado dos cartões próprios | Sub-score de Qualidade (Q) |
| **Maturidade dos cartões B** | Cartões B com `ivl ≥ 21` | Sub-score de Qualidade (Q) — só válido com bug corrigido |

### 8.2 Avaliação qualitativa pelo professor (opcional em E02, recomendado a partir de E03)

Dado que E02 é a estreia da criação de cartões, a avaliação qualitativa pode ser leve. Sugestão de rubrica simplificada:

| Critério | Nota máxima | Descrição |
|----------|-------------|-----------|
| **Adequação ao tier** | 3 pts | O cartão usa o formato correto para o tier? |
| **Atomicidade** | 2 pts | Cada cartão testa exatamente uma coisa? |
| **Qualidade do verso** | 3 pts | O verso tem informação suficiente para memorização? |
| **Derivação do texto** | 2 pts | O cartão claramente veio do texto (e não foi inventado sem relação)? |
| **Total** | 10 pts | |

Em E02, o professor pode avaliar apenas uma amostra aleatória (e.g., 5 alunos de cada tier) para calibrar os critérios antes de aplicar sistematicamente em E03.

---

## 10. Component C — Material de livre escolha

E02 introduz também a primeira entrega de Component C. Os guardrails conforme `READING_MATERIAL_METHODOLOGY.md` (Seção 5.3):

- **Mínimo de 5 cartões** do material escolhido
- O material deve ser **um texto em inglês legível** (não uma lista de palavras avulsas)
- O aluno deve **submeter a fonte** junto com os cartões (URL ou título do texto/música/vídeo)

### Orientação sobre tipos de material para Component C

| Material | Recomendação | Observação |
|----------|--------------|------------|
| **Letra de música** | ✅ Permitido, mas com ressalva | Linguagem coloquial, gírias e elisões são comuns — geram cartões interessantes mas de baixa transferência para inglês formal. Incentivar músicas com dicção clara. |
| **Transcrição de vídeo (YouTube, TED)** | ✅ Recomendado | Excelente para Tier 2–3. Para Tier 1, preferir vídeos com legendas em inglês simplificado. |
| **Artigo de notícias simplificado** | ✅ Recomendado | Sites como *BBC Learning English*, *VOA Learning English* têm conteúdo calibrado por nível. |
| **Trecho de livro/série** | ✅ Permitido | Verificar se o nível é adequado ao tier do aluno. |
| **Tradução direta de texto em português** | ❌ Não aceito | Não é um texto em inglês — é uma criação artificial sem input genuíno em L2. |

### Sugestão de fontes por tier para Component C

**Tier 1:**
- [VOA Learning English — Beginners](https://learningenglish.voanews.com/z/4488)
- Letras de músicas em inglês com vocabulário simples (pop, country, folk)
- Legendas de desenhos animados americanos

**Tier 2:**
- [BBC Learning English — News Report](https://www.bbc.co.uk/learningenglish/english/features/news-report)
- Transcrições de vídeos TED-Ed
- Artigos simples da Wikipedia em inglês (seções de introdução)

**Tier 3:**
- Artigos completos do *The Guardian*, *Scientific American*, ou *MIT Technology Review*
- Transcrições de podcasts (e.g., *Radiolab*, *Stuff You Should Know*)
- Trechos de livros de não-ficção populares

---

## 11. Itens em aberto para discussão

Os pontos abaixo requerem decisão do professor antes da instrução de E02 ser finalizada e distribuída aos alunos.

### 10.1 Finalização da alocação de tiers

- [ ] Combinar Signal 0 + Signal 1 + Signal 2 (E01) usando a matriz de três sinais do `PLAN_FOR_PLACEMENT_EXAM_v1.2.md`
- [ ] Decidir como alocar os 10 alunos sem atividade em E01 (Signal 2 ausente)
- [ ] Decidir se o Tier 3 terá alunos esta edição (threshold ajustado: 16/25 no placement) — candidatos são os 2-3 alunos com os scores mais altos no placement (Wallace Gabriel: 14/27, Matheus Dias: 12/27, Eduardo Fiuza: 12/27)

### 10.2 Correção do SM-2 antes de E02

- [ ] Aplicar a correção da linha 1702 do `server/app.py` conforme `CARD_PROGRESSION_ANALYSIS.md`
- [ ] Testar em ambiente de staging com usuário de teste
- [ ] Fazer deploy no servidor de produção antes do início de E02

### 10.3 Preparação dos textos nivelados

- [ ] Escrever (ou adaptar) os três textos sobre IA nos formatos Tier 1 / Tier 2 / Tier 3
- [ ] Validar readability: Tier 1 target Flesch-Kincaid grade 2–4; Tier 2 target grade 5–7; Tier 3 target grade 8–10
- [ ] Identificar 5–8 palavras-chave por texto para uso nas instruções de card creation

### 10.4 Engajamento dos alunos ausentes de E01

- [ ] Definir estratégia de contato com os 10 alunos sem atividade (mensagem direta, aviso em aula, etc.)
- [ ] Verificar se os 3 alunos sem conta cadastrada (Ana Beatriz, Luiz Henrique, Sophia) criaram conta antes de E02

### 10.5 Decisão sobre avaliação qualitativa

- [ ] Decidir se E02 terá avaliação qualitativa de cartões (opcional, recomendado para no mínimo amostra)
- [ ] Se sim, definir quem avalia e em que momento do ciclo (antes ou após o período de revisão)

### 10.6 Atualização da fórmula de avaliação para E02

A fórmula de E01 usava `--no-card-creation`, que colapsa o Volume para apenas revisões. Em E02, a fórmula completa deve incluir cartões criados. Verificar se o script `grade_exercise.py` precisa de ajustes para E02:

```bash
# E02 (com criação de cartões, bug SM-2 corrigido):
python grade_exercise.py \
    --interval custom --start 2026-04-07 --end 2026-04-28 \
    --label E02 \
    --roster placement_exam/docs/STUDENT_ROSTER_SPRING_2026.csv \
    --local-only \
    --admin-db ~/.cache/studyamigo/20260428/admin.db \
    --user-db-dir ~/.cache/studyamigo/20260428/user_dbs
```

*(Remover `--no-card-creation` para que o sub-score de cards_created entre no Volume V)*

---

## Referências

- `server/docs/READING_MATERIAL_METHODOLOGY.md` — Metodologia completa de seleção de textos e estrutura de exercícios
- `placement_exam/docs/PLACEMENT_EXAM_RESULTS_ANALYSIS.md` — Análise detalhada do placement exam (fevereiro 2026)
- `placement_exam/planning_E01/docs/E01_ANALISE.md` — Fórmula de avaliação e resultados de E01
- `placement_exam/planning_E01/docs/CARD_PROGRESSION_ANALYSIS.md` — Análise do bug de crescimento linear de intervalos
- `docs/SUPERMEMO-2.md` — Fundamentos do algoritmo SM-2 e sua implementação no StudyAmigo

---

*Documento de discussão — versão 1.0 — Março 2026*
