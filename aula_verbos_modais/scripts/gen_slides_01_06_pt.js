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

// ── SLIDE 1 — Capa ────────────────────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: NAVY };

  s.addShape("rect", { x: 5.5, y: 0, w: 4.5, h: 5.625,
    fill: { color: NAVY_MID }, line: { color: NAVY_MID, width: 0 } });
  s.addShape("rect", { x: 0, y: 2.55, w: 10, h: 0.08,
    fill: { color: GOLD }, line: { color: GOLD, width: 0 } });
  s.addShape("rect", { x: 0.55, y: 1.1, w: 0.18, h: 3.4,
    fill: { color: GOLD }, line: { color: GOLD, width: 0 } });
  s.addShape("ellipse", { x: 7.2, y: -1.0, w: 3.5, h: 3.5,
    fill: { color: GOLD, transparency: 88 }, line: { color: GOLD, width: 0 } });
  s.addShape("ellipse", { x: 7.8, y: -0.4, w: 2.2, h: 2.2,
    fill: { color: GOLD, transparency: 82 }, line: { color: GOLD, width: 0 } });
  s.addShape("ellipse", { x: 0.2, y: 4.5, w: 1.0, h: 1.0,
    fill: { color: GOLD, transparency: 85 }, line: { color: GOLD, width: 0 } });

  s.addText("Verbos Modais — Parte 1", {
    x: 0.9, y: 1.15, w: 8.5, h: 1.1,
    fontSize: 44, fontFace: "Georgia", bold: true,
    color: WHITE, align: "left",
  });
  s.addText("Habilidade, Permissão e Possibilidade", {
    x: 0.9, y: 2.7, w: 8.5, h: 0.7,
    fontSize: 24, fontFace: "Calibri", italic: true,
    color: GOLD_LIGHT, align: "left",
  });
  s.addText("Prof. Ewerton Madruga  |  Curso Técnico em Segurança Cibernética", {
    x: 0.9, y: 4.95, w: 9, h: 0.35,
    fontSize: 13, fontFace: "Calibri",
    color: "aabbcc", align: "left",
  });
}

// ── SLIDE 2 — Objetivos ───────────────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: OFF_WHITE };
  addTopBar(s, "O que vamos aprender hoje?");
  addLeftAccent(s);

  const items = [
    "Revisão: os 12 tempos verbais",
    "Revisão: verbos irregulares",
    "O que são verbos modais?",
    "Verbos modais: CAN, COULD, MAY, MIGHT",
    "Exercícios práticos",
  ];
  s.addText(
    items.map((t, i) => ({ text: t, options: { bullet: true, breakLine: i < items.length - 1 } })),
    { x: 0.55, y: 1.3, w: 9.0, h: 4.1,
      fontSize: 20, fontFace: "Calibri", color: DARK_TEXT, paraSpaceAfter: 8 }
  );
}

// ── SLIDE 3 — Os 12 Tempos Verbais ───────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: OFF_WHITE };
  addTopBar(s, "Os 12 Tempos Verbais");
  addLeftAccent(s);

  const H    = { fill: { color: NAVY     }, color: WHITE, bold: true, align: "center", valign: "middle", fontSize: 12 };
  const RL   = { fill: { color: "2d3f6a" }, color: WHITE, bold: true, align: "center", valign: "middle", fontSize: 11 };
  const PAST_BG = "d8cce8";
  const PRES_BG = "cce0f0";
  const FUT_BG  = GOLD_LIGHT;

  function cell(text, formula, bg) {
    return {
      text: [
        { text: text,    options: { italic: true, fontSize: 10, breakLine: true } },
        { text: formula, options: { fontSize: 9, color: "444455" } },
      ],
      options: { fill: { color: bg }, align: "center", valign: "middle" },
    };
  }

  const rows = [
    [ { text: "", options: H }, { text: "Passado", options: H }, { text: "Presente", options: H }, { text: "Futuro", options: H } ],
    [ { text: "Simples", options: RL },
      cell("I ate pizza yesterday.", "S + V₂", PAST_BG),
      cell("I eat pizza every day.", "S + V₁", PRES_BG),
      cell("I will eat pizza tomorrow.", "S + will + V", FUT_BG) ],
    [ { text: "Contínuo", options: RL },
      cell("I was eating pizza when you arrived.", "S + was/were + V-ing", PAST_BG),
      cell("I am eating pizza right now.", "S + am/is/are + V-ing", PRES_BG),
      cell("I will be eating when you arrive.", "S + will be + V-ing", FUT_BG) ],
    [ { text: "Perfeito", options: RL },
      cell("I had eaten all the pizza when you arrived.", "S + had + V₃", PAST_BG),
      cell("I have eaten all the pizza.", "S + have/has + V₃", PRES_BG),
      cell("I will have eaten all the pizza by then.", "S + will have + V₃", FUT_BG) ],
    [ { text: "Perfeito\nContínuo", options: Object.assign({}, RL, { fontSize: 10 }) },
      cell("I had been eating pizza for 2 hours.", "S + had been + V-ing", PAST_BG),
      cell("I have been eating pizza for 2 hours.", "S + have/has been + V-ing", PRES_BG),
      cell("I will have been eating for 2 hours by then.", "S + will have been + V-ing", FUT_BG) ],
  ];

  s.addTable(rows, {
    x: 0.18, y: 1.25, w: 9.64, h: 3.95,
    border: { pt: 1, color: "ccccdd" },
    rowH: [0.4, 0.85, 0.85, 0.85, 0.85],
    colW: [1.3, 2.77, 2.77, 2.77],
  });

  s.addText("S = Sujeito   V = Verbo   (V₁ = infinitivo / V₂ = passado simples / V₃ = particípio passado)", {
    x: 0.18, y: 5.32, w: 9.64, h: 0.22,
    fontSize: 10, fontFace: "Calibri", color: MID_GRAY, align: "center",
  });
}

// ── SLIDE 4 — Verbos Irregulares: O que são? ─────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: OFF_WHITE };
  addTopBar(s, "Verbos Irregulares");
  addLeftAccent(s);

  s.addText([
    { text: "Verbos regulares", options: { bold: true, breakLine: false } },
    { text: " formam o passado e o particípio adicionando ", options: {} },
    { text: "-ed / -d", options: { bold: true, breakLine: true } },
    { text: "    – play → played → played", options: { italic: true, color: MID_GRAY, breakLine: true } },
    { text: "    – live → lived → lived",  options: { italic: true, color: MID_GRAY, breakLine: true } },
    { text: "\n", options: { fontSize: 5, breakLine: true } },
    { text: "Verbos irregulares", options: { bold: true, breakLine: false } },
    { text: " têm formas próprias — precisam ser memorizados", options: { breakLine: true } },
    { text: "    – write → wrote → written", options: { italic: true, color: MID_GRAY, breakLine: true } },
    { text: "    – take → took → taken",    options: { italic: true, color: MID_GRAY, breakLine: true } },
    { text: "\n", options: { fontSize: 5, breakLine: true } },
    { text: "Três formas: ", options: { breakLine: false } },
    { text: "V₁", options: { bold: true, color: GOLD_DIM, breakLine: false } },
    { text: " (infinitivo)   |   ", options: { breakLine: false } },
    { text: "V₂", options: { bold: true, color: GOLD_DIM, breakLine: false } },
    { text: " (passado simples)   |   ", options: { breakLine: false } },
    { text: "V₃", options: { bold: true, color: GOLD_DIM, breakLine: false } },
    { text: " (particípio passado)", options: {} },
  ], {
    x: 0.45, y: 1.25, w: 9.1, h: 4.2,
    fontSize: 19, fontFace: "Calibri", color: DARK_TEXT, valign: "top",
  });
}

// ── SLIDE 5 — Verbos Irregulares: Tabela ─────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: OFF_WHITE };
  addTopBar(s, "Verbos Irregulares — Exemplos");
  addLeftAccent(s);

  const H = { fill: { color: NAVY }, color: WHITE, bold: true, align: "center", valign: "middle", fontSize: 13 };
  function dr(inf, sp, sps, pp, even) {
    const base = even ? LIGHT_GRAY : WHITE;
    const cell = (t, bg) => ({ text: t, options: { fill: { color: bg }, align: "center", valign: "middle", fontSize: 13, color: DARK_TEXT } });
    return [cell(inf, base), cell(sp, base), cell(sps, base), cell(pp, GOLD_LIGHT)];
  }

  const rows = [
    [
      { text: "Infinitivo",         options: H },
      { text: "Presente Simples",   options: H },
      { text: "Passado Simples",    options: H },
      { text: "Particípio Passado", options: Object.assign({}, H, { fill: { color: GOLD_DIM } }) },
    ],
    dr("to drive", "drive(s)", "drove",  "driven", false),
    dr("to eat",   "eat(s)",   "ate",    "eaten",  true),
    dr("to buy",   "buy(s)",   "bought", "bought", false),
    dr("to run",   "run(s)",   "ran",    "run",    true),
    dr("to swim",  "swim(s)",  "swam",   "swum",   false),
    dr("to feel",  "feel(s)",  "felt",   "felt",   true),
    dr("to take",  "take(s)",  "took",   "taken",  false),
    dr("to go",    "go(es)",   "went",   "gone",   true),
  ];

  s.addTable(rows, {
    x: 0.15, y: 1.25, w: 9.7, h: 4.2,
    border: { pt: 1, color: "cccccc" },
    rowH: [0.46, 0.46, 0.46, 0.46, 0.46, 0.46, 0.46, 0.46, 0.46],
    colW: [1.9, 2.1, 2.1, 2.1],
  });
}

// ── SLIDE 6 — Verificação Rápida ─────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: OFF_WHITE };
  addTopBar(s, "Verbos Irregulares — Verificação Rápida");
  addLeftAccent(s);

  s.addText("Complete a tabela com as formas corretas do verbo:", {
    x: 0.45, y: 1.28, w: 9.1, h: 0.35,
    fontSize: 17, fontFace: "Calibri", italic: true, color: MID_GRAY,
  });

  const H = { fill: { color: NAVY }, color: WHITE, bold: true, align: "center", valign: "middle", fontSize: 16 };
  const blankCell = { text: "___________", options: { fill: { color: GOLD_LIGHT }, align: "center", valign: "middle", fontSize: 16, color: "999977" } };
  const verb = (v) => ({ text: v, options: { fill: { color: WHITE }, align: "center", valign: "middle", fontSize: 16, color: DARK_TEXT } });

  const rows = [
    [
      { text: "Infinitivo", options: H },
      { text: "Passado Simples", options: Object.assign({}, H, { fill: { color: GOLD_DIM } }) },
      { text: "Particípio Passado", options: Object.assign({}, H, { fill: { color: GOLD_DIM } }) },
    ],
    [ verb("to go"),   blankCell, blankCell ],
    [ verb("to eat"),  blankCell, blankCell ],
    [ verb("to run"),  blankCell, blankCell ],
    [ verb("to buy"),  blankCell, blankCell ],
    [ verb("to feel"), blankCell, blankCell ],
  ];

  s.addTable(rows, {
    x: 0.75, y: 1.72, w: 8.5, h: 3.2,
    border: { pt: 1, color: "cccccc" },
    rowH: [0.48, 0.54, 0.54, 0.54, 0.54, 0.54],
    colW: [2.3, 3.1, 3.1],
  });

  s.addText("Respostas: went / gone   |   ate / eaten   |   ran / run   |   bought / bought   |   felt / felt", {
    x: 0.5, y: 5.15, w: 9, h: 0.3,
    fontSize: 13, fontFace: "Calibri", italic: true, color: "999999", align: "center",
  });
}

pres.writeFile({ fileName: "/Users/emadruga/proj/StudyAmigoApp/aula_verbos_modais/Aula1_PT_Slides_01-06.pptx" })
  .then(() => console.log("✅ Saved: Aula1_PT_Slides_01-06.pptx"))
  .catch(e => { console.error("❌", e); process.exit(1); });
