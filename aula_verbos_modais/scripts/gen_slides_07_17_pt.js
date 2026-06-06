const PptxGenJS = require("pptxgenjs");

const NAVY       = "1b2a4a";
const GOLD       = "c9a84c";
const GOLD_LIGHT = "f0dfa0";
const GOLD_DIM   = "a07828";
const WHITE      = "FFFFFF";
const OFF_WHITE  = "fafaf7";
const DARK_TEXT  = "1a1a2e";
const MID_GRAY   = "555566";
const LIGHT_GRAY = "eeeeee";
const RED_WRONG  = "c0392b";
const GREEN_OK   = "1a7a3a";

const pres = new PptxGenJS();
pres.layout = "LAYOUT_16x9";

function addTopBar(slide, titleText) {
  slide.addShape("rect", { x: 0, y: 0, w: 10, h: 1.15,
    fill: { color: NAVY }, line: { color: NAVY, width: 0 } });
  slide.addShape("rect", { x: 9.65, y: 0, w: 0.35, h: 1.15,
    fill: { color: GOLD }, line: { color: GOLD, width: 0 } });
  slide.addShape("rect", { x: 0, y: 1.11, w: 10, h: 0.05,
    fill: { color: GOLD }, line: { color: GOLD, width: 0 } });
  if (titleText) {
    slide.addText(titleText, {
      x: 0.3, y: 0, w: 9.3, h: 1.11,
      fontSize: 28, fontFace: "Georgia", bold: true,
      color: GOLD_LIGHT, align: "left", valign: "middle", margin: 0,
    });
  }
}

function addLeftAccent(slide) {
  slide.addShape("rect", { x: 0, y: 1.16, w: 0.12, h: 4.45,
    fill: { color: GOLD }, line: { color: GOLD, width: 0 } });
}

function addDomainGrid(slide, examples) {
  const positions = [
    { x: 0.25, y: 1.35 },
    { x: 5.15, y: 1.35 },
    { x: 0.25, y: 3.45 },
    { x: 5.15, y: 3.45 },
  ];
  const W = 4.7, H = 1.9;
  examples.forEach((ex, i) => {
    const { x, y } = positions[i];
    slide.addShape("rect", { x, y, w: W, h: H,
      fill: { color: OFF_WHITE }, line: { color: "ddddcc", width: 1 } });
    slide.addShape("rect", { x, y, w: 0.1, h: H,
      fill: { color: ex.color }, line: { color: ex.color, width: 0 } });
    slide.addShape("rect", { x, y, w: W, h: 0.32,
      fill: { color: ex.color }, line: { color: ex.color, width: 0 } });
    slide.addText(ex.domain, {
      x, y, w: W, h: 0.32,
      fontSize: 12, fontFace: "Calibri", bold: true,
      color: WHITE, align: "center", valign: "middle", margin: 0,
    });
    slide.addText(
      ex.lines.map((l, j) => ({ text: l, options: { breakLine: j < ex.lines.length - 1 } })),
      { x: x + 0.18, y: y + 0.36, w: W - 0.25, h: H - 0.4,
        fontSize: 13.5, fontFace: "Calibri", color: DARK_TEXT, valign: "top", align: "left" }
    );
  });
}

// ── SLIDE 7 — O que são Verbos Modais? ───────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: OFF_WHITE };
  addTopBar(s, "O que são Verbos Modais?");
  addLeftAccent(s);

  s.addText("Verbos modais dão um significado especial ao verbo principal.", {
    x: 0.35, y: 1.28, w: 9.3, h: 0.45,
    fontSize: 18, fontFace: "Calibri", bold: true, color: NAVY,
  });
  s.addText("Eles expressam:", {
    x: 0.35, y: 1.72, w: 9.3, h: 0.32,
    fontSize: 16, fontFace: "Calibri", color: DARK_TEXT,
  });

  const functions = [
    { label: "Habilidade",  bg: "1a5276" },
    { label: "Permissão",   bg: "1a5276" },
    { label: "Possibilidade", bg: "6e2f8a" },
    { label: "Obrigação",   bg: "7d6608" },
    { label: "Conselho",    bg: "1a7a3a" },
    { label: "Dedução",     bg: "7d3c00" },
  ];
  const chipW = 2.6, chipH = 0.52;
  const cols = [0.35, 3.7, 7.05];
  const rows2 = [2.1, 2.75];
  functions.forEach((f, i) => {
    const x = cols[i % 3], y = rows2[Math.floor(i / 3)];
    s.addShape("rect", { x, y, w: chipW, h: chipH,
      fill: { color: f.bg }, line: { color: f.bg, width: 0 } });
    s.addText(f.label, {
      x, y, w: chipW, h: chipH,
      fontSize: 16, fontFace: "Calibri", bold: true,
      color: WHITE, align: "center", valign: "middle", margin: 0,
    });
  });

  s.addText("Os principais verbos modais:", {
    x: 0.35, y: 3.4, w: 9.3, h: 0.3,
    fontSize: 15, fontFace: "Calibri", color: DARK_TEXT, italic: true,
  });

  const families = [
    { text: "CAN / COULD",               bg: "1a5276" },
    { text: "MAY / MIGHT",               bg: "6e2f8a" },
    { text: "SHALL / SHOULD / OUGHT TO", bg: "1a7a3a" },
    { text: "MUST",                      bg: "7d6608" },
  ];
  const fX = [0.35, 2.65, 4.95, 7.7];
  families.forEach((f, i) => {
    const w = i === 2 ? 2.45 : 2.2;
    s.addShape("rect", { x: fX[i], y: 3.78, w, h: 0.7,
      fill: { color: f.bg }, line: { color: f.bg, width: 0 } });
    s.addText(f.text, {
      x: fX[i], y: 3.78, w, h: 0.7,
      fontSize: 14, fontFace: "Calibri", bold: true,
      color: WHITE, align: "center", valign: "middle", margin: 0,
    });
  });
}

// ── SLIDE 8 — Regras Gramaticais ─────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: OFF_WHITE };
  addTopBar(s, "Verbos Modais — Regras Gramaticais");
  addLeftAccent(s);

  const rules = [
    {
      num: "1", bg: "1a5276",
      title: 'Sempre seguidos do INFINITIVO SEM "to"',
      ok:    'She can go.   ✓',
      wrong: 'She can to go. / She can goes.   ✗',
    },
    {
      num: "2", bg: "1a7a3a",
      title: "Sem -s na 3ª pessoa do singular",
      ok:    'He must leave.   ✓',
      wrong: 'He musts leave.   ✗',
    },
    {
      num: "3", bg: "7d6608",
      title: "Sem auxiliar para perguntas e negativas",
      ok:    'Can you help?  /  You must not enter.   ✓',
      wrong: 'Do you can help?   ✗',
    },
  ];

  const boxH = 1.2;
  rules.forEach((r, i) => {
    const y = 1.28 + i * (boxH + 0.18);
    s.addShape("rect", { x: 0.25, y, w: 0.55, h: boxH,
      fill: { color: r.bg }, line: { color: r.bg, width: 0 } });
    s.addText(r.num, {
      x: 0.25, y, w: 0.55, h: boxH,
      fontSize: 26, fontFace: "Georgia", bold: true,
      color: WHITE, align: "center", valign: "middle", margin: 0,
    });
    s.addShape("rect", { x: 0.85, y, w: 9.0, h: boxH,
      fill: { color: WHITE }, line: { color: r.bg, width: 2 } });
    s.addText(r.title, {
      x: 1.0, y, w: 8.7, h: 0.42,
      fontSize: 15, fontFace: "Calibri", bold: true, color: r.bg, valign: "middle",
    });
    s.addText([
      { text: r.ok,    options: { color: GREEN_OK,  bold: true, breakLine: true } },
      { text: r.wrong, options: { color: RED_WRONG, bold: true } },
    ], {
      x: 1.0, y: y + 0.42, w: 8.7, h: boxH - 0.42,
      fontSize: 14, fontFace: "Calibri", valign: "middle",
    });
  });
}

// ── SLIDE 9 — Estrutura da Frase ─────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: OFF_WHITE };
  addTopBar(s, "Como Construir Frases com Verbos Modais");
  addLeftAccent(s);

  const structures = [
    { label: "Afirmativa",                 formula: "Sujeito  +  modal  +  verbo base  +  (complemento)", example: 'She should drink more water.', bg: "1a5276" },
    { label: "Negativa",                   formula: "Sujeito  +  modal  +  NOT  +  verbo base",           example: 'You must not eat before the blood test.', bg: "c0392b" },
    { label: "Pergunta",                   formula: "Modal  +  sujeito  +  verbo base  +  ?",             example: 'Can you carry these bags for me?', bg: "1a7a3a" },
    { label: "Modal Perfeito (passado)",   formula: "modal  +  HAVE  +  particípio passado (V₃)",         example: 'He could have taken the wrong medicine.', bg: "7d6608" },
  ];

  const bW = 4.6, bH = 1.75;
  const positions = [
    { x: 0.2, y: 1.28 }, { x: 5.05, y: 1.28 },
    { x: 0.2, y: 3.2  }, { x: 5.05, y: 3.2  },
  ];

  structures.forEach((st, i) => {
    const { x, y } = positions[i];
    s.addShape("rect", { x, y, w: bW, h: 0.38,
      fill: { color: st.bg }, line: { color: st.bg, width: 0 } });
    s.addText(st.label, {
      x, y, w: bW, h: 0.38,
      fontSize: 13, fontFace: "Calibri", bold: true,
      color: WHITE, align: "center", valign: "middle", margin: 0,
    });
    s.addShape("rect", { x, y: y + 0.38, w: bW, h: bH - 0.38,
      fill: { color: WHITE }, line: { color: "cccccc", width: 1 } });
    s.addText(st.formula, {
      x: x + 0.12, y: y + 0.42, w: bW - 0.22, h: 0.52,
      fontSize: 12, fontFace: "Consolas", bold: true, color: st.bg, valign: "middle",
    });
    s.addText(`"${st.example}"`, {
      x: x + 0.12, y: y + 0.95, w: bW - 0.22, h: 0.72,
      fontSize: 14, fontFace: "Calibri", italic: true, color: DARK_TEXT, valign: "top",
    });
  });
}

// ── SLIDE 10 — Tabela Resumo ──────────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: OFF_WHITE };
  addTopBar(s, "Verbos Modais — Visão Geral");
  addLeftAccent(s);

  const H  = { fill: { color: NAVY }, color: WHITE, bold: true, align: "center", valign: "middle", fontSize: 13 };
  const A1 = GOLD_LIGHT;
  const A2 = "e8edf5";

  function row(modal, fn, example, bg) {
    const cell = (t, b, opts) => ({
      text: t,
      options: Object.assign({ fill: { color: b }, valign: "middle", fontSize: 13, color: DARK_TEXT }, opts || {}),
    });
    return [
      cell(modal,   bg, { bold: true, align: "center" }),
      cell(fn,      bg, { align: "left" }),
      cell(example, bg, { italic: true, align: "left" }),
    ];
  }

  const rows = [
    [ { text: "Modal", options: H }, { text: "Função Principal", options: H }, { text: "Exemplo", options: H } ],
    row("CAN",      "Habilidade (presente) / Permissão",        'I can swim very well.',           A1),
    row("COULD",    "Habilidade (passado) / Pedido educado",    'I could ride a bike as a child.',  A1),
    row("MAY",      "Possibilidade / Permissão (formal)",       'It may rain this afternoon.',      A1),
    row("MIGHT",    "Possibilidade (menos certa)",              'I might go to the gym later.',     A1),
    row("SHALL",    "Sugestão / Oferta (formal)",               'Shall I open the window?',         A2),
    row("SHOULD",   "Conselho / Recomendação",                  'You should see a doctor.',         A2),
    row("OUGHT TO", "Obrigação moral (formal)",                 'You ought to call your parents.',  A2),
    row("MUST",     "Obrigação forte / Dedução",                'You must take this medicine.',     A2),
  ];

  s.addTable(rows, {
    x: 0.2, y: 1.25, w: 9.6, h: 4.15,
    border: { pt: 1, color: "cccccc" },
    rowH: [0.42, 0.46, 0.46, 0.46, 0.46, 0.46, 0.46, 0.46, 0.46],
    colW: [1.5, 3.5, 4.6],
  });

  s.addText("★  Foco da Aula 1 (linhas douradas)   |   Conteúdo da Aula 2 (linhas claras)", {
    x: 0.2, y: 5.32, w: 9.6, h: 0.22,
    fontSize: 10, fontFace: "Calibri", italic: true, color: MID_GRAY, align: "center",
  });
}

// ── SLIDE 11 — CAN e COULD: Introdução ───────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: OFF_WHITE };
  addTopBar(s, "CAN e COULD");
  addLeftAccent(s);

  const cards = [
    {
      x: 0.25, color: "1a5276", word: "CAN",
      points: [
        "Habilidade ou possibilidade NO PRESENTE",
        "Permissão informal",
        "Pedidos e ofertas",
      ],
    },
    {
      x: 5.15, color: "6e2f8a", word: "COULD",
      points: [
        "Habilidade NO PASSADO",
        "Forma mais educada de CAN",
        "Possibilidade (menos certa)",
        "Condicional de CAN",
      ],
    },
  ];

  cards.forEach(c => {
    const W = 4.6, H = 3.5;
    s.addShape("rect", { x: c.x, y: 1.28, w: W, h: 0.65,
      fill: { color: c.color }, line: { color: c.color, width: 0 } });
    s.addText(c.word, {
      x: c.x, y: 1.28, w: W, h: 0.65,
      fontSize: 30, fontFace: "Georgia", bold: true,
      color: WHITE, align: "center", valign: "middle", margin: 0,
    });
    s.addShape("rect", { x: c.x, y: 1.93, w: W, h: H - 0.65,
      fill: { color: WHITE }, line: { color: c.color, width: 2 } });
    s.addText(
      c.points.map((p, i) => ({ text: p, options: { bullet: true, breakLine: i < c.points.length - 1 } })),
      { x: c.x + 0.15, y: 1.98, w: W - 0.25, h: H - 0.75,
        fontSize: 16, fontFace: "Calibri", color: DARK_TEXT, valign: "top", paraSpaceAfter: 8 }
    );
  });

  s.addShape("rect", { x: 0.25, y: 4.88, w: 9.5, h: 0.5,
    fill: { color: GOLD_LIGHT }, line: { color: GOLD, width: 1 } });
  s.addText('COULD é também o condicional de CAN:  "If we had oranges, I could make juice."', {
    x: 0.35, y: 4.88, w: 9.3, h: 0.5,
    fontSize: 14, fontFace: "Calibri", italic: true, color: NAVY, valign: "middle",
  });
}

// ── SLIDE 12 — CAN: Usos ──────────────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: OFF_WHITE };
  addTopBar(s, "CAN — Usos");
  addLeftAccent(s);

  const uses = [
    { label: "Habilidade geral (presente)",         example: "I can speak English." },
    { label: "Pedir permissão (informal)",          example: "Can I borrow your pen, please?" },
    { label: "Fazer um pedido",                     example: "Can you help me, please?" },
    { label: "Possibilidade",                       example: "It can get very cold there at night." },
    { label: "Oferecer ajuda",                      example: "Can I carry your bags for you?" },
    { label: "Cannot (can't) = proibido",           example: "You cannot smoke in this room." },
  ];

  uses.forEach((u, i) => {
    const col = i % 2, row = Math.floor(i / 2);
    const x = col === 0 ? 0.22 : 5.12;
    const y = 1.3 + row * 1.38;
    const W = 4.7, H = 1.25;
    s.addShape("rect", { x, y, w: W, h: H,
      fill: { color: WHITE }, line: { color: "1a5276", width: 1 } });
    s.addShape("rect", { x, y, w: W, h: 0.36,
      fill: { color: "1a5276" }, line: { color: "1a5276", width: 0 } });
    s.addText(u.label, {
      x: x + 0.1, y, w: W - 0.15, h: 0.36,
      fontSize: 12, fontFace: "Calibri", bold: true, color: WHITE, valign: "middle",
    });
    s.addText(`"${u.example}"`, {
      x: x + 0.12, y: y + 0.4, w: W - 0.2, h: H - 0.42,
      fontSize: 14, fontFace: "Calibri", italic: true, color: DARK_TEXT, valign: "middle",
    });
  });
}

// ── SLIDE 13 — CAN: Exemplos do Cotidiano ────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: OFF_WHITE };
  addTopBar(s, "CAN — Exemplos do Cotidiano");
  addLeftAccent(s);

  addDomainGrid(s, [
    { domain: "Rotina Diária", color: "1a5276", lines: [
      'I can wake up early on weekdays.',
      'Can I borrow your charger?',
    ]},
    { domain: "Saúde & Farmácia", color: "1a7a3a", lines: [
      'Can I get this medicine without a prescription?',
      "She can't eat gluten.",
    ]},
    { domain: "Compras & Supermercado", color: "7d6608", lines: [
      'Can I pay by card?',
      'You can get two for the price of one today.',
    ]},
    { domain: "Esportes & Lazer", color: "7d3c00", lines: [
      'He can run 10 km without stopping.',
      "You can't use your hands in football.",
    ]},
  ]);
}

// ── SLIDE 14 — COULD: Usos ───────────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: OFF_WHITE };
  addTopBar(s, "COULD — Usos");
  addLeftAccent(s);

  const uses = [
    { label: "Habilidade geral no passado",            example: "I could play the piano when I was younger." },
    { label: "Pedir permissão (mais educado)",         example: "Could I use your bathroom, please?" },
    { label: "Fazer um pedido (mais educado)",         example: "Could you pass me the salt, please?" },
    { label: "Possibilidade no passado",               example: "You could have broken your leg." },
    { label: "Sugestão",                               example: "We could go to the movies if you like." },
    { label: "Condicional de CAN",                     example: "If we had oranges, I could make you juice." },
  ];

  uses.forEach((u, i) => {
    const col = i % 2, row = Math.floor(i / 2);
    const x = col === 0 ? 0.22 : 5.12;
    const y = 1.3 + row * 1.38;
    const W = 4.7, H = 1.25;
    s.addShape("rect", { x, y, w: W, h: H,
      fill: { color: WHITE }, line: { color: "6e2f8a", width: 1 } });
    s.addShape("rect", { x, y, w: W, h: 0.36,
      fill: { color: "6e2f8a" }, line: { color: "6e2f8a", width: 0 } });
    s.addText(u.label, {
      x: x + 0.1, y, w: W - 0.15, h: 0.36,
      fontSize: 12, fontFace: "Calibri", bold: true, color: WHITE, valign: "middle",
    });
    s.addText(`"${u.example}"`, {
      x: x + 0.12, y: y + 0.4, w: W - 0.2, h: H - 0.42,
      fontSize: 14, fontFace: "Calibri", italic: true, color: DARK_TEXT, valign: "middle",
    });
  });
}

// ── SLIDE 15 — COULD: Exemplos do Cotidiano ──────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: OFF_WHITE };
  addTopBar(s, "COULD — Exemplos do Cotidiano");
  addLeftAccent(s);

  addDomainGrid(s, [
    { domain: "Rotina Diária", color: "1a5276", lines: [
      'I could ride a bike when I was five.',
      'Could you turn off the lights, please?',
    ]},
    { domain: "Saúde & Farmácia", color: "1a7a3a", lines: [
      "He could have taken the wrong pill — he wasn't paying attention.",
      'Could I schedule an appointment for tomorrow?',
    ]},
    { domain: "Compras & Supermercado", color: "7d6608", lines: [
      'Could you show me a smaller size?',
      'If they had it in stock, I could buy it today.',
    ]},
    { domain: "Esportes & Lazer", color: "7d3c00", lines: [
      'She could swim faster when she trained every day.',
      'We could win if everyone plays their best.',
    ]},
  ]);
}

// ── SLIDE 16 — CAN vs. COULD: Comparação ─────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: OFF_WHITE };
  addTopBar(s, "CAN vs. COULD — Qual a Diferença?");
  addLeftAccent(s);

  const H  = { fill: { color: NAVY     }, color: WHITE, bold: true, align: "center", valign: "middle", fontSize: 13 };
  const HC = { fill: { color: "1a5276" }, color: WHITE, bold: true, align: "center", valign: "middle", fontSize: 13 };
  const HD = { fill: { color: "6e2f8a" }, color: WHITE, bold: true, align: "center", valign: "middle", fontSize: 13 };
  const DASH = { text: "—", options: { fill: { color: LIGHT_GRAY }, color: MID_GRAY, align: "center", valign: "middle", fontSize: 13 } };

  function rc(text, bg, opts) {
    return { text, options: Object.assign({ fill: { color: bg || WHITE }, valign: "middle", fontSize: 13, color: DARK_TEXT, align: "center" }, opts || {}) };
  }

  const rows = [
    [ { text: "Situação", options: H }, { text: "CAN", options: HC }, { text: "COULD", options: HD } ],
    [ rc("Habilidade (presente)", "e8edf5", { align: "left" }), rc('I can cook pasta.', GOLD_LIGHT, { italic: true }), DASH ],
    [ rc("Habilidade (passado)",  "e8edf5", { align: "left" }), DASH, rc('I could cook pasta as a kid.', GOLD_LIGHT, { italic: true }) ],
    [ rc("Permissão (informal)",  "e8edf5", { align: "left" }), rc('Can I leave early today?', GOLD_LIGHT, { italic: true }), DASH ],
    [ rc("Permissão (educado)",   "e8edf5", { align: "left" }), DASH, rc('Could I leave early today?', GOLD_LIGHT, { italic: true }) ],
    [ rc("Possibilidade",         "e8edf5", { align: "left" }), rc('It can happen anytime.', GOLD_LIGHT, { italic: true }), rc('It could happen. (menos certo)', GOLD_LIGHT, { italic: true }) ],
    [ rc("Condicional",           "e8edf5", { align: "left" }), DASH, rc('If I had flour, I could make bread.', GOLD_LIGHT, { italic: true }) ],
  ];

  s.addTable(rows, {
    x: 0.2, y: 1.28, w: 9.6, h: 4.2,
    border: { pt: 1, color: "cccccc" },
    rowH: [0.42, 0.58, 0.58, 0.58, 0.58, 0.58, 0.58],
    colW: [2.5, 3.55, 3.55],
  });
}

// ── SLIDE 17 — Prática: CAN / COULD ──────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: OFF_WHITE };
  addTopBar(s, "Prática — CAN / COULD");
  addLeftAccent(s);

  s.addText("Complete as frases com CAN, CAN'T, COULD ou COULD HAVE:", {
    x: 0.35, y: 1.3, w: 9.3, h: 0.35,
    fontSize: 16, fontFace: "Calibri", italic: true, color: MID_GRAY,
  });

  const items = [
    { q: "_______ you carry this box for me? It's too heavy.",       a: "Can / Could" },
    { q: "She _______ run very fast when she was in high school.",    a: "could" },
    { q: "You _______ smoke inside the pharmacy.",                    a: "can't / cannot" },
    { q: "_______ you have left your wallet at the supermarket?",    a: "Could" },
    { q: "If we had more time, we _______ visit the whole market.",   a: "could" },
    { q: "He _______ eat spicy food — it makes him feel sick.",       a: "can't" },
  ];

  items.forEach((item, i) => {
    const y = 1.75 + i * 0.63;
    s.addShape("rect", { x: 0.22, y: y + 0.04, w: 0.38, h: 0.44,
      fill: { color: NAVY }, line: { color: NAVY, width: 0 } });
    s.addText(String(i + 1), {
      x: 0.22, y: y + 0.04, w: 0.38, h: 0.44,
      fontSize: 14, fontFace: "Georgia", bold: true,
      color: WHITE, align: "center", valign: "middle", margin: 0,
    });
    s.addText(item.q, {
      x: 0.7, y, w: 6.9, h: 0.52,
      fontSize: 15, fontFace: "Calibri", color: DARK_TEXT, valign: "middle",
    });
    s.addShape("rect", { x: 7.7, y: y + 0.06, w: 2.0, h: 0.4,
      fill: { color: GOLD_LIGHT }, line: { color: GOLD, width: 1 } });
    s.addText(item.a, {
      x: 7.7, y: y + 0.06, w: 2.0, h: 0.4,
      fontSize: 13, fontFace: "Calibri", bold: true, color: NAVY,
      align: "center", valign: "middle", margin: 0,
    });
  });

  s.addText("(respostas visíveis — cobrir antes da aula)", {
    x: 0.35, y: 5.3, w: 9.3, h: 0.22,
    fontSize: 10, fontFace: "Calibri", italic: true, color: "aaaaaa", align: "right",
  });
}

pres.writeFile({ fileName: "/Users/emadruga/proj/StudyAmigoApp/aula_verbos_modais/Aula1_PT_Slides_07-17.pptx" })
  .then(() => console.log("✅ Saved: Aula1_PT_Slides_07-17.pptx"))
  .catch(e => { console.error("❌", e); process.exit(1); });
