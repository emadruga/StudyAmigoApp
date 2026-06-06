const PptxGenJS = require("pptxgenjs");

const NAVY       = "1b2a4a";
const NAVY_MID   = "243560";
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
      fontSize: 26, fontFace: "Georgia", bold: true,
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
    { x: 0.25, y: 1.35 }, { x: 5.15, y: 1.35 },
    { x: 0.25, y: 3.45 }, { x: 5.15, y: 3.45 },
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

// ── SLIDE 18 — MAY e MIGHT: Introdução ───────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: OFF_WHITE };
  addTopBar(s, "MAY e MIGHT");
  addLeftAccent(s);

  // Two intro cards
  const cards = [
    {
      x: 0.25, color: "6e2f8a", word: "MAY",
      points: [
        "Possibilidade (~70% de chance)",
        "Permissão formal",
        "Expressar desejos",
        "Especular sobre o passado",
      ],
    },
    {
      x: 5.15, color: "1a5276", word: "MIGHT",
      points: [
        "Possibilidade (~40% de chance)",
        "Chance menor do que MAY",
        "NÃO usado para permissão ou desejos",
        "Especular sobre o passado",
      ],
    },
  ];

  cards.forEach(c => {
    const W = 4.6, H = 3.0;
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
        fontSize: 15, fontFace: "Calibri", color: DARK_TEXT, valign: "top", paraSpaceAfter: 6 }
    );
  });

  // Probability bar
  s.addShape("rect", { x: 0.25, y: 4.42, w: 9.5, h: 0.28,
    fill: { color: LIGHT_GRAY }, line: { color: "cccccc", width: 1 } });
  // MAY marker ~70%
  s.addShape("rect", { x: 0.25, y: 4.42, w: 6.65, h: 0.28,
    fill: { color: "6e2f8a", transparency: 40 }, line: { color: "6e2f8a", width: 0 } });
  // MIGHT marker ~40%
  s.addShape("rect", { x: 0.25, y: 4.42, w: 3.8, h: 0.28,
    fill: { color: "1a5276", transparency: 40 }, line: { color: "1a5276", width: 0 } });

  s.addText("0%                  MIGHT (~40%)                  MAY (~70%)                  100%", {
    x: 0.25, y: 4.74, w: 9.5, h: 0.25,
    fontSize: 11, fontFace: "Calibri", color: MID_GRAY, align: "center",
  });

  s.addShape("rect", { x: 0.25, y: 5.03, w: 9.5, h: 0.4,
    fill: { color: GOLD_LIGHT }, line: { color: GOLD, width: 1 } });
  s.addText("Atenção: na prática cotidiana MAY e MIGHT são frequentemente intercambiáveis para possibilidade.", {
    x: 0.35, y: 5.03, w: 9.3, h: 0.4,
    fontSize: 12, fontFace: "Calibri", italic: true, color: NAVY, valign: "middle",
  });
}

// ── SLIDE 19 — MAY: Usos ─────────────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: OFF_WHITE };
  addTopBar(s, "MAY — Usos");
  addLeftAccent(s);

  const uses = [
    { label: "Possibilidade",                       example: "It may rain later, so take an umbrella." },
    { label: "Dar permissão",                       example: "You may have another cookie if you like." },
    { label: "Pedir permissão",                     example: "May I borrow your pen, please?" },
    { label: "Expressar desejos",                   example: "May the New Year bring you happiness." },
    { label: "Especular sobre o passado",           example: "She may have missed her plane." },
    { label: "Permissão formal (escrita/oficial)",  example: "Visitors may not enter after 10 p.m." },
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

// ── SLIDE 20 — MAY: Exemplos do Cotidiano ────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: OFF_WHITE };
  addTopBar(s, "MAY — Exemplos do Cotidiano");
  addLeftAccent(s);

  addDomainGrid(s, [
    { domain: "Rotina Diária", color: "6e2f8a", lines: [
      'I may be late tonight — traffic is bad.',
      'May I use your phone for a moment?',
    ]},
    { domain: "Saúde & Farmácia", color: "1a7a3a", lines: [
      'The doctor said I may have an allergy.',
      'You may feel a little dizzy after this medication.',
    ]},
    { domain: "Compras & Supermercado", color: "7d6608", lines: [
      'This product may be out of stock by the weekend.',
      'May I try this on?',
    ]},
    { domain: "Esportes & Lazer", color: "7d3c00", lines: [
      'It may rain during the match.',
      "She may not play today — she twisted her ankle.",
    ]},
  ]);
}

// ── SLIDE 21 — MIGHT: Usos ───────────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: OFF_WHITE };
  addTopBar(s, "MIGHT — Usos");
  addLeftAccent(s);

  const uses = [
    { label: "Possibilidade (menos certa)",          example: "It might rain tomorrow. (~40% de chance)" },
    { label: "Chance menor do que MAY",              example: "I might go to the gym later — not sure yet." },
    { label: "Especular sobre o passado",            example: "She might have missed her plane." },
    { label: "Sugestão educada (informal)",          example: "You might want to try the other size." },
    { label: "NÃO para desejos ou permissão",        example: '✗  "Might I come in?"  →  Use: "May I come in?"' },
    { label: "Might + have + V₃  (passado)",        example: "He might have taken the wrong bus." },
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
      fontSize: 13, fontFace: "Calibri", italic: true, color: DARK_TEXT, valign: "middle",
    });
  });
}

// ── SLIDE 22 — MIGHT: Exemplos do Cotidiano ──────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: OFF_WHITE };
  addTopBar(s, "MIGHT — Exemplos do Cotidiano");
  addLeftAccent(s);

  addDomainGrid(s, [
    { domain: "Rotina Diária", color: "1a5276", lines: [
      'I might go to the gym after class — I\'m not sure yet.',
      'He might have forgotten to set his alarm.',
    ]},
    { domain: "Saúde & Farmácia", color: "1a7a3a", lines: [
      'You might need to see a specialist.',
      'She might have caught a cold at the game.',
    ]},
    { domain: "Compras & Supermercado", color: "7d6608", lines: [
      'The price might go up next week.',
      'I might buy that jacket if it goes on sale.',
    ]},
    { domain: "Esportes & Lazer", color: "7d3c00", lines: [
      'They might win the championship this year.',
      'He might not be fit enough to play on Saturday.',
    ]},
  ]);
}

// ── SLIDE 23 — MAY vs. MIGHT: Comparação ─────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: OFF_WHITE };
  addTopBar(s, "MAY vs. MIGHT — Principais Diferenças");
  addLeftAccent(s);

  const H  = { fill: { color: NAVY     }, color: WHITE, bold: true, align: "center", valign: "middle", fontSize: 13 };
  const HM = { fill: { color: "6e2f8a" }, color: WHITE, bold: true, align: "center", valign: "middle", fontSize: 13 };
  const HT = { fill: { color: "1a5276" }, color: WHITE, bold: true, align: "center", valign: "middle", fontSize: 13 };
  const DASH = { text: "✗ não usado", options: { fill: { color: LIGHT_GRAY }, color: RED_WRONG, align: "center", valign: "middle", fontSize: 12, bold: true } };

  function rc(text, bg, opts) {
    return { text, options: Object.assign({ fill: { color: bg || WHITE }, valign: "middle", fontSize: 13, color: DARK_TEXT, align: "center" }, opts || {}) };
  }

  const rows = [
    [ { text: "Situação", options: H }, { text: "MAY", options: HM }, { text: "MIGHT", options: HT } ],
    [ rc("Possibilidade (maior)", "e8edf5", { align: "left" }),
      rc('It may rain. (~70%)', GOLD_LIGHT, { italic: true }), DASH ],
    [ rc("Possibilidade (menor)", "e8edf5", { align: "left" }),
      DASH, rc('It might rain. (~40%)', GOLD_LIGHT, { italic: true }) ],
    [ rc("Dar permissão", "e8edf5", { align: "left" }),
      rc('You may sit down.', GOLD_LIGHT, { italic: true }), DASH ],
    [ rc("Pedir permissão", "e8edf5", { align: "left" }),
      rc('May I come in?', GOLD_LIGHT, { italic: true }), DASH ],
    [ rc("Expressar desejos", "e8edf5", { align: "left" }),
      rc('May you be happy!', GOLD_LIGHT, { italic: true }), DASH ],
    [ rc("Especulação no passado", "e8edf5", { align: "left" }),
      rc('She may have left early.', GOLD_LIGHT, { italic: true }),
      rc('She might have left early.', GOLD_LIGHT, { italic: true }) ],
  ];

  s.addTable(rows, {
    x: 0.2, y: 1.28, w: 9.6, h: 4.15,
    border: { pt: 1, color: "cccccc" },
    rowH: [0.42, 0.57, 0.57, 0.57, 0.57, 0.57, 0.57],
    colW: [2.6, 3.5, 3.5],
  });
}

// ── SLIDE 24 — Prática: MAY / MIGHT ──────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: OFF_WHITE };
  addTopBar(s, "Prática — MAY / MIGHT");
  addLeftAccent(s);

  s.addText("Complete as frases com MAY ou MIGHT:", {
    x: 0.35, y: 1.3, w: 9.3, h: 0.35,
    fontSize: 16, fontFace: "Calibri", italic: true, color: MID_GRAY,
  });

  const items = [
    { q: "_______ I try on these shoes in a size 40?",                               a: "May" },
    { q: "It _______ snow tonight — the forecast shows only 30% chance.",            a: "might" },
    { q: "She _______ have already bought all the vegetables on the list.",          a: "may / might" },
    { q: "_______ your team win the tournament!",                                    a: "May" },
    { q: "He _______ be at the gym right now — I'm not sure.",                       a: "might" },
    { q: "The pharmacy _______ be closed on Sundays.",                               a: "may / might" },
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

// ── SLIDE 25 — Resumo: Modais da Aula 1 ──────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: OFF_WHITE };
  addTopBar(s, "O que Aprendemos — Parte 1");
  addLeftAccent(s);

  const H = { fill: { color: NAVY }, color: WHITE, bold: true, align: "center", valign: "middle", fontSize: 13 };

  function row(modal, uses, strength, bg) {
    const cell = (t, opts) => ({ text: t, options: Object.assign({ fill: { color: bg }, valign: "middle", fontSize: 13, color: DARK_TEXT }, opts || {}) });
    return [
      cell(modal,    { bold: true, align: "center" }),
      cell(uses,     { align: "left" }),
      cell(strength, { align: "center", italic: true }),
    ];
  }

  const rows = [
    [ { text: "Modal", options: H }, { text: "Usos principais", options: H }, { text: "Certeza / Força", options: H } ],
    row("CAN",   "Habilidade (presente), permissão informal, possibilidade", "Neutro",        GOLD_LIGHT),
    row("COULD", "Habilidade (passado), pedido educado, condicional",        "Baixa–Média",   GOLD_LIGHT),
    row("MAY",   "Possibilidade (~70%), permissão formal, desejos",          "Média–Alta",    GOLD_LIGHT),
    row("MIGHT", "Possibilidade (~40%), especulação no passado",             "Baixa–Média",   GOLD_LIGHT),
  ];

  s.addTable(rows, {
    x: 0.2, y: 1.28, w: 9.6, h: 3.6,
    border: { pt: 1, color: "cccccc" },
    rowH: [0.45, 0.72, 0.72, 0.72, 0.72],
    colW: [1.5, 5.1, 3.0],
  });

  s.addShape("rect", { x: 0.2, y: 5.0, w: 9.6, h: 0.42,
    fill: { color: NAVY }, line: { color: NAVY, width: 0 } });
  s.addText("Próxima aula: SHALL, SHOULD, OUGHT TO, MUST — e verbos modais na voz passiva.", {
    x: 0.3, y: 5.0, w: 9.4, h: 0.42,
    fontSize: 13, fontFace: "Calibri", italic: true,
    color: GOLD_LIGHT, valign: "middle",
  });
}

// ── SLIDE 26 — Modal Perfeito ─────────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: OFF_WHITE };
  addTopBar(s, "Modal + HAVE + Particípio Passado");
  addLeftAccent(s);

  // Formula box
  s.addShape("rect", { x: 0.3, y: 1.28, w: 9.4, h: 0.72,
    fill: { color: NAVY }, line: { color: NAVY, width: 0 } });
  s.addText([
    { text: "modal  +  ", options: { color: WHITE } },
    { text: "HAVE", options: { color: GOLD_LIGHT, bold: true } },
    { text: "  +  particípio passado (", options: { color: WHITE } },
    { text: "V₃", options: { color: GOLD_LIGHT, bold: true } },
    { text: ")", options: { color: WHITE } },
  ], {
    x: 0.3, y: 1.28, w: 9.4, h: 0.72,
    fontSize: 22, fontFace: "Calibri", align: "center", valign: "middle",
  });

  s.addText("Usado para especular ou comentar sobre eventos NO PASSADO.", {
    x: 0.35, y: 2.1, w: 9.3, h: 0.35,
    fontSize: 16, fontFace: "Calibri", color: NAVY, bold: true,
  });

  const examples = [
    { modal: "could have", rest: "taken", tail: "the wrong bus.",    color: "1a5276" },
    { modal: "may have",   rest: "forgotten", tail: "his wallet at the supermarket.", color: "6e2f8a" },
    { modal: "might have", rest: "left",   tail: "her medicine at home.", color: "1a7a3a" },
  ];

  examples.forEach((ex, i) => {
    const y = 2.58 + i * 0.88;
    s.addShape("rect", { x: 0.3, y, w: 9.4, h: 0.72,
      fill: { color: WHITE }, line: { color: "cccccc", width: 1 } });
    s.addShape("rect", { x: 0.3, y, w: 0.18, h: 0.72,
      fill: { color: ex.color }, line: { color: ex.color, width: 0 } });
    s.addText([
      { text: "She ", options: { italic: true } },
      { text: ex.modal + " ", options: { bold: true, color: ex.color, italic: true } },
      { text: ex.rest,        options: { bold: true, color: GOLD_DIM, italic: true } },
      { text: " " + ex.tail,  options: { italic: true } },
    ], {
      x: 0.6, y, w: 9.0, h: 0.72,
      fontSize: 17, fontFace: "Calibri", valign: "middle",
    });
  });

  s.addText("O verbo principal é sempre o PARTICÍPIO PASSADO (V₃).", {
    x: 0.35, y: 5.27, w: 9.3, h: 0.25,
    fontSize: 12, fontFace: "Calibri", italic: true, color: MID_GRAY,
  });
}

// ── SLIDE 27 — Erros Comuns ───────────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: OFF_WHITE };
  addTopBar(s, "Erros Comuns — Parte 1");
  addLeftAccent(s);

  const H = { fill: { color: NAVY }, color: WHITE, bold: true, align: "center", valign: "middle", fontSize: 13 };

  function row(wrong, correct, rule) {
    return [
      { text: wrong,   options: { fill: { color: "fde8e8" }, color: RED_WRONG,  bold: true,  align: "left", valign: "middle", fontSize: 13 } },
      { text: correct, options: { fill: { color: "e8f5e9" }, color: GREEN_OK,   bold: true,  align: "left", valign: "middle", fontSize: 13 } },
      { text: rule,    options: { fill: { color: GOLD_LIGHT }, color: DARK_TEXT, align: "left", valign: "middle", fontSize: 12 } },
    ];
  }

  const rows = [
    [ { text: "❌ Errado", options: H }, { text: "✅ Correto", options: H }, { text: "Regra", options: H } ],
    row('She cans swim.',          'She can swim.',             'Sem -s na 3ª pessoa'),
    row('I can to drive.',         'I can drive.',              'Sem "to" após modal'),
    row('Can she swims?',          'Can she swim?',             'Infinitivo em perguntas'),
    row('He could go yesterday.',  'He could have gone yesterday.', 'Passado = modal + have + V₃'),
    row('May I to try this on?',   'May I try this on?',        'Sem "to" após modal'),
  ];

  s.addTable(rows, {
    x: 0.2, y: 1.28, w: 9.6, h: 4.15,
    border: { pt: 1, color: "cccccc" },
    rowH: [0.44, 0.72, 0.72, 0.72, 0.72, 0.72],
    colW: [2.9, 2.9, 3.8],
  });
}

// ── SLIDE 28 — Prática Mista ──────────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: OFF_WHITE };
  addTopBar(s, "Prática Mista — CAN / COULD / MAY / MIGHT");
  addLeftAccent(s);

  s.addText("Escolha o melhor verbo modal para cada frase:", {
    x: 0.35, y: 1.3, w: 9.3, h: 0.33,
    fontSize: 15, fontFace: "Calibri", italic: true, color: MID_GRAY,
  });

  const items = [
    { q: "_______ you pass me the salt, please?",                                              a: "Could / Can" },
    { q: "I _______ go to the match on Saturday — it depends on work.",                        a: "may / might" },
    { q: "She _______ run 5 km when she was training every day.",                              a: "could" },
    { q: "He _______ have eaten something bad at the restaurant.",                             a: "may / might" },
    { q: "You _______ park here — it's a no-parking zone.",                                    a: "cannot / can't" },
    { q: "_______ I try a sample before buying?",                                              a: "May / Can / Could" },
    { q: "If I had a car, I _______ drive you to the pharmacy.",                               a: "could" },
    { q: "The supermarket _______ be open until midnight on Fridays.",                         a: "may / might / could" },
  ];

  items.forEach((item, i) => {
    const col = i % 2, row = Math.floor(i / 2);
    const x = col === 0 ? 0.22 : 5.12;
    const y = 1.72 + row * 0.88;
    const W = 4.72;
    s.addShape("rect", { x, y, w: 0.36, h: 0.72,
      fill: { color: NAVY }, line: { color: NAVY, width: 0 } });
    s.addText(String(i + 1), {
      x, y, w: 0.36, h: 0.72,
      fontSize: 13, fontFace: "Georgia", bold: true,
      color: WHITE, align: "center", valign: "middle", margin: 0,
    });
    s.addShape("rect", { x: x + 0.36, y, w: W - 0.36, h: 0.72,
      fill: { color: WHITE }, line: { color: "cccccc", width: 1 } });
    s.addText(item.q, {
      x: x + 0.46, y: y + 0.02, w: W - 0.55, h: 0.46,
      fontSize: 12.5, fontFace: "Calibri", color: DARK_TEXT, valign: "middle",
    });
    s.addShape("rect", { x: x + 0.36, y: y + 0.48, w: W - 0.36, h: 0.24,
      fill: { color: GOLD_LIGHT }, line: { color: GOLD, width: 0 } });
    s.addText(item.a, {
      x: x + 0.46, y: y + 0.48, w: W - 0.46, h: 0.24,
      fontSize: 11, fontFace: "Calibri", bold: true, color: NAVY, valign: "middle",
    });
  });
}

// ── SLIDE 29 — Atividade de Conversação ──────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: OFF_WHITE };
  addTopBar(s, "Vamos Conversar — Atividade em Duplas");
  addLeftAccent(s);

  s.addText("Discuta com um colega. Use verbos modais nas respostas!", {
    x: 0.35, y: 1.28, w: 9.3, h: 0.35,
    fontSize: 15, fontFace: "Calibri", italic: true, color: MID_GRAY,
  });

  const questions = [
    { num: "1", color: "1a5276", q: "What CAN you do now that you COULDN'T do when you were a child?" },
    { num: "2", color: "6e2f8a", q: "Where MIGHT you go this weekend? Are you sure?" },
    { num: "3", color: "1a7a3a", q: "MAY students use their phones during class at your school?" },
    { num: "4", color: "7d6608", q: "You feel a little sick after lunch. What COULD you have eaten?" },
  ];

  questions.forEach((q, i) => {
    const y = 1.75 + i * 0.88;
    s.addShape("rect", { x: 0.22, y, w: 0.5, h: 0.72,
      fill: { color: q.color }, line: { color: q.color, width: 0 } });
    s.addText(q.num, {
      x: 0.22, y, w: 0.5, h: 0.72,
      fontSize: 20, fontFace: "Georgia", bold: true,
      color: WHITE, align: "center", valign: "middle", margin: 0,
    });
    s.addShape("rect", { x: 0.77, y, w: 9.0, h: 0.72,
      fill: { color: WHITE }, line: { color: q.color, width: 2 } });
    s.addText(q.q, {
      x: 0.92, y, w: 8.7, h: 0.72,
      fontSize: 15, fontFace: "Calibri", color: DARK_TEXT, valign: "middle",
    });
  });

  s.addShape("rect", { x: 0.22, y: 5.27, w: 9.55, h: 0.22,
    fill: { color: GOLD_LIGHT }, line: { color: GOLD, width: 0 } });
  s.addText("Dica do professor: a última pergunta é um gancho para SHOULD/MUST na Aula 2!", {
    x: 0.32, y: 5.27, w: 9.35, h: 0.22,
    fontSize: 11, fontFace: "Calibri", italic: true, color: NAVY, valign: "middle",
  });
}

// ── SLIDE 30 — Encerramento ───────────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: OFF_WHITE };

  // Navy top bar — taller para comportar título
  addTopBar(s, "Pontos-Chave — Parte 1");
  addLeftAccent(s);

  // Six takeaway cards in 2×3 grid
  const takeaways = [
    { icon: "🔵", text: 'Verbos modais nunca mudam de forma\nsem -s, sem -ed, sem "to" após eles', color: NAVY },
    { icon: "➡️",  text: "modal + verbo base\nsentido presente / futuro",                         color: "1a5276" },
    { icon: "⏪",  text: "modal + HAVE + V₃\nreferência ao passado",                              color: "6e2f8a" },
    { icon: "💡",  text: "CAN = habilidade presente\nCOULD = passado / educado / condicional",    color: "1a7a3a" },
    { icon: "❓",  text: "MAY (~70%) vs. MIGHT (~40%)\nambos expressam possibilidade",            color: "7d6608" },
    { icon: "⚠️", text: "Somente MAY\npara permissão e desejos",                                 color: "7d3c00" },
  ];

  const W = 3.05, H = 1.3;
  const cols = [0.22, 3.57, 6.72];
  const rows2 = [1.28, 2.73];

  takeaways.forEach((t, i) => {
    const x = cols[i % 3];
    const y = rows2[Math.floor(i / 3)];
    // card bg
    s.addShape("rect", { x, y, w: W, h: H,
      fill: { color: WHITE }, line: { color: t.color, width: 2 } });
    // colour top strip
    s.addShape("rect", { x, y, w: W, h: 0.3,
      fill: { color: t.color }, line: { color: t.color, width: 0 } });
    // text
    s.addText(t.text, {
      x: x + 0.12, y: y + 0.34, w: W - 0.2, h: H - 0.38,
      fontSize: 13, fontFace: "Calibri", bold: false, color: DARK_TEXT,
      valign: "middle", align: "left",
    });
  });

  // Bottom banner
  s.addShape("rect", { x: 0, y: 4.18, w: 10, h: 0.65,
    fill: { color: NAVY }, line: { color: NAVY, width: 0 } });
  s.addText("Próxima aula: SHALL / SHOULD / OUGHT TO / MUST + Voz Passiva", {
    x: 0.3, y: 4.18, w: 7.5, h: 0.65,
    fontSize: 15, fontFace: "Calibri", bold: true,
    color: GOLD_LIGHT, valign: "middle",
  });
  s.addText("Dúvidas? / Obrigado!", {
    x: 7.6, y: 4.18, w: 2.3, h: 0.65,
    fontSize: 15, fontFace: "Georgia", italic: true,
    color: WHITE, align: "right", valign: "middle",
  });
}

pres.writeFile({ fileName: "/Users/emadruga/proj/StudyAmigoApp/aula_verbos_modais/Aula1_PT_Slides_18-30.pptx" })
  .then(() => console.log("✅ Saved: Aula1_PT_Slides_18-30.pptx"))
  .catch(e => { console.error("❌", e); process.exit(1); });
