# E03 → E04 — Sugestões: Como Associar Cartões do Componente C ao Vídeo-Fonte

## Contexto

Em E03, o Componente C pedia que o aluno criasse cartões a partir de "material de livre escolha". A fonte (URL, título, nome da música) era solicitada informalmente nas instruções, mas **não havia mecanismo para registrá-la junto ao cartão**. Isso impossibilitou a verificação programática de adesão ao tema sugerido (letras de música, por exemplo).

Para E04, o plano é usar **transcrições de vídeos educacionais do YouTube** como inspiração para criação de cartões no Componente C. Precisamos de uma forma de associar cada cartão (ou grupo de cartões) ao vídeo utilizado, de modo que:

1. O professor possa verificar a fonte programaticamente
2. O impacto no fluxo de criação do aluno seja mínimo

---

## Restrição principal

A UI do StudyAmigo expõe apenas **dois campos** na tela de criação de cartão: **frente** e **verso**. Não há campo de tags, campo de fonte, nem descrição de baralho acessível ao aluno. Qualquer solução "zero código" precisa usar esses dois campos.

---

## Opções analisadas

### Opção 1 — Última linha do verso

O aluno adiciona um separador + URL do YouTube na última linha do verso de cada cartão.

**Formato:**
```
determined (adj.) = determinado
☞ determined to succeed / a determined effort
Ele estava determinado a vencer o campeonato.
---
📺 https://youtube.com/watch?v=abc123
```

| Aspecto | Avaliação |
|---------|-----------|
| Impacto no aluno | Baixo — 1 linha extra por cartão (pode copiar/colar) |
| Parseável programaticamente | Sim — regex na última linha do verso |
| Aparece na revisão | Sim — pode ser positivo (lembra o contexto do vídeo) |
| Risco de esquecimento | Médio — precisa lembrar em cada cartão |

---

### Opção 2 — Cartão-metadado (1º cartão do baralho)

O aluno cria um cartão especial como primeiro cartão do baralho:
- **Frente**: `📺 FONTE`
- **Verso**: URL completa do vídeo

Os demais cartões do baralho são normais.

| Aspecto | Avaliação |
|---------|-----------|
| Impacto no aluno | Mínimo — 1 cartão extra por baralho |
| Parseável programaticamente | Sim — buscar cartão com frente contendo "FONTE" |
| Aparece na revisão | Sim — mas como é 1 só, é irrelevante |
| Risco de esquecimento | Baixo — instrução clara no enunciado |
| Limitação | Assume 1 vídeo por baralho. Se usar múltiplos vídeos, precisa de múltiplos cartões-fonte |

---

### Opção 3 — Mudança mínima no código (campo "fonte" na UI)

Adicionar um campo opcional "Fonte" na tela de criação de cartão (`AddCardPage.jsx`). O campo seria salvo como 3º campo do note type (`flds` separados por `\x1f` no SQLite) ou como tag automática.

| Aspecto | Avaliação |
|---------|-----------|
| Impacto no aluno | Zero — campo opcional nativo na UI |
| Parseável programaticamente | Sim — leitura direta do campo no DB |
| Aparece na revisão | Não (controlável pelo template) |
| Risco de esquecimento | Baixo — campo visível na tela |
| Custo de desenvolvimento | Pequeno — 1 campo no form + ajuste no endpoint de criação |

---

## Como o Anki resolve este problema

O Anki utiliza **note types com campos personalizáveis**. Um tipo de nota "Vocabulário + Fonte" teria:

- Campo 1: Front
- Campo 2: Back
- Campo 3: Source

O campo "Source" pode ser excluído do template de revisão (não aparece ao estudar) mas fica pesquisável e exportável. Também suporta **tags por nota** (`source::yt::VIDEO_ID`) que são filtráveis pelo browser.

Nenhuma dessas soluções está disponível na UI atual do StudyAmigo sem alteração de código.

---

## Comparação final

| # | Opção | Impacto aluno | Parseável? | Código necessário |
|---|-------|---------------|------------|-------------------|
| 1 | Última linha do verso | Baixo (1 linha/cartão) | Sim (regex) | Zero |
| 2 | Cartão-metadado | Mínimo (1 cartão/baralho) | Sim (heurística) | Zero |
| 3 | Campo "fonte" na UI | Zero | Sim (DB direto) | Pequeno |

---

## Decisão

**Pendente** — professor avaliando as opções.

---

*Elaborado em: 17/05/2026*
*Referência: discussão sobre rastreabilidade de fontes para E04 Component C*
