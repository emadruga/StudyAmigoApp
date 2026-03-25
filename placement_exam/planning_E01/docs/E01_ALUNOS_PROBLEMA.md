# E01 — Alunos com Comportamento Suspeito

**Exercício**: E01 — Verbal Tenses
**Período**: 01/03/2026 – 23/03/2026

Este documento lista os alunos sinalizados automaticamente pelo `grade_exercise.py` com
flags de comportamento suspeito, analisa cada caso e propõe encaminhamento.

Os flags **não são prova de desonestidade** — são sinais de alerta que justificam uma
análise mais atenta antes de confirmar a nota. A fórmula já penaliza automaticamente
esses comportamentos (LOW_TIME reduz `time_sub`; RET100 com `ease_sub` alto se
concentra no componente E). A questão é se há necessidade de intervenção **além** do
que a fórmula já capturou.

---

## Alunos com flags RET100 e LOW_TIME

### RET100 — 100% de retenção com ≥ 30 revisões agendadas

O flag dispara quando o aluno acertou **todas** as revisões de tipo 1/2 (revisões
agendadas e re-aprendizado) com Good ou Easy, tendo pelo menos 30 revisões desse tipo.
Dois cenários possíveis:

1. **Aluno genuinamente bom**: domina o conteúdo; Verbal Tenses era trivial para ele.
2. **Aluno clicando Good/Easy sem ler**: o cruzamento com `time_sub` e `ease_sub`
   separa os dois casos — tempo baixo + ease alto = padrão de botão automático.

| ID | Nome | Revisões | Dias | time_sub | ease_sub | Nota | Leitura |
|----|------|----------|------|----------|----------|------|---------|
| 5011 | Arthur do Nascimento Paiva | 93 | 3 | 100% | 56.2 | D | Tempo OK mas 93 rev. em apenas 3 dias — **suspeito** |
| 5066 | Madson ferreira de souza | 329 | 5 | 63.2% | 61.7 | C | Volume muito alto concentrado em 5 dias |
| 4041 | Isabella | 373 | 7 | 48.5% | 64.4 | B | time_sub baixo + ease alto = padrão de botão automático — **mais suspeito** |
| — | Ana Luiza (user 62) | 324 | 9 | 73.6% | 54.5 | C | Sem ID de cadastro no roster; identidade a confirmar |
| 3056 | Wallace Gabriel Ferreira Dos Santos | 81 | 5 | 84.8% | 59.8 | D | Volume baixo; pode simplesmente saber o conteúdo |
| 3026 | Gabriel Bernardo Do Nascimento | 200 | 4 | 42.0% | 58.0 | D | time_sub médio-baixo + apenas 4 dias |

**Isabella (4041)** é o caso mais preocupante: 373 revisões, 100% retenção,
time_sub = 48.5% e ease_sub elevado. É o padrão clássico de quem respondeu
boa parte dos cartões automaticamente sem ler.

**Wallace (3056)** e **Madson (5066)** são menos preocupantes — volume não é
absurdo e tempo não é extremamente baixo.

---

### LOW_TIME — maioria das respostas abaixo de 2 segundos

O flag dispara quando `time_sub` < 30% com ≥ 20 revisões. Um tempo de resposta
inferior a 2 s é insuficiente para ler e processar um cartão. A fórmula já
penaliza via `time_sub`, mas os casos extremos merecem atenção.

| ID | Nome | Revisões | Dias | time_sub | Nota | Leitura |
|----|------|----------|------|----------|------|---------|
| 5086 | Samêa Soares Pacheco | 141 | 5 | 11.3% | D | Quase tudo < 2 s |
| 4081 | Lucas Pandini Pinheiro | 132 | 4 | 3.0% | F | time_sub praticamente zero com retenção de 95.7% — **mais suspeito** |
| — | Cauã Jorge (sem roster) | 52 | 1 | 29.4% | F | 1 dia, respostas muito rápidas |
| 5081 | Mateus Ferreira Patrício | 522 | 10 | 7.3% | C | Maior volume da turma + tempo quase zero — **par mais atípico** |
| 5021 | Bruno dos Santos Lima | 50 | 2 | 18.0% | F | 2 dias, tempo muito baixo |

**Lucas Pandini (4081)** é o caso mais extremo: 132 revisões, time_sub = 3%,
mas retenção de 95.7%. É quase impossível acertar com essa frequência lendo cada
cartão em menos de 2 s — sugere clique automático com Good/Easy.

**Mateus Patrício (5081)** tem o maior volume absoluto da turma (522 revisões),
10 dias de uso, mas time_sub = 7.3%. O par volume muito alto + tempo quase zero
é o mais atípico de toda a turma.

---

## Recomendação de encaminhamento

Três opções possíveis, em ordem crescente de intervenção:

### Opção 1 — Manter nota como está (padrão)

A fórmula já descontou os comportamentos suspeitos. É a opção mais simples e
defensável: o algoritmo funciona exatamente para isso.

### Opção 2 — Intervenção seletiva nos casos extremos

Conversa individual com os três casos mais atípicos antes de confirmar a nota:

- **Isabella (4041)** — RET100 + time_sub baixo + ease alto
- **Lucas Pandini (4081)** — LOW_TIME extremo (3%) com volume razoável
- **Mateus Patrício (5081)** — volume altíssimo + tempo quase zero

Se confirmado comportamento automático, o componente Q (ou E) pode ser ajustado
manualmente para zero.

### Opção 3 — Documentar e arquivar sem alterar nota

Mesmo que a nota não mude, registrar que esses alunos foram sinalizados
automaticamente serve como evidência caso haja contestação posterior. Esta opção
complementa qualquer uma das anteriores.

---

*Última atualização: 25/03/2026*
