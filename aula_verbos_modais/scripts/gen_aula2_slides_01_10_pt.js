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

  s.addText("Verbos Modais — Parte 2", {
    x: 0.9, y: 1.15, w: 8.5, h: 1.1,
    fontSize: 44, fontFace: "Georgia", bold: true,
    color: WHITE, align: "left",
  });
  s.addText("Obrigação, Conselho e Voz Passiva", {
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

// ── SLIDE 2 — Objetivos da Aula 2 ────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: OFF_WHITE };
  addTopBar(s, "O que vamos aprender hoje?");
  addLeftAccent(s);

  const items = [
    "Revisão rápida: CAN, COULD, MAY, MIGHT",
    "Verbos modais: SHALL, SHOULD, OUGHT TO",
    "MUST e HAVE TO — obrigação",
    "MUSTN'T vs. DON'T HAVE TO",
    "Modais na voz passiva",
    "Revisão geral e prática final",
  ];
  s.addText(
    items.map((t, i) => ({ text: t, options: { bullet: true, breakLine: i < items.length - 1 } })),
    { x: 0.55, y: 1.3, w: 9.0, h: 4.1,
      fontSize: 19, fontFace: "Calibri", color: DARK_TEXT, paraSpaceAfter: 7 }
  );
}

// ── SLIDE 3 — Quick Review: Aula 1 ───────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: OFF_WHITE };
  addTopBar(s, "Revisão Rápida — Parte 1");
  addLeftAccent(s);

  s.addText("Mini-quiz oral — responda sem olhar para as anotações!", {
    x: 0.45, y: 1.25, w: 9.1, h: 0.32,
    fontSize: 15, fontFace: "Calibri", italic: true, color: MID_GRAY,
  });

  const qs = [
    { q: "1. Qual modal expressa habilidade no presente?", a: "→ CAN" },
    { q: "2. Qual é mais formal/educado: CAN ou COULD?", a: "→ COULD" },
    { q: "3. Qual tem mais chance de acontecer: MAY ou MIGHT?", a: "→ MAY (~70%)" },
    { q: "4. Pode-se usar MIGHT para dar permissão?", a: "→ Não — só MAY" },
    { q: '5. Complete: "She _______ have left her bag at the supermarket."', a: "→ may / might" },
  ];

  const QBG  = "e8eef8";
  const ABG  = GOLD_LIGHT;
  const yStart = 1.65;
  const rowH   = 0.65;

  qs.forEach(({ q, a }, i) => {
    const y = yStart + i * rowH;
    s.addShape("rect", { x: 0.22, y, w: 6.5, h: 0.55,
      fill: { color: QBG }, line: { color: "c8d4e8", width: 1 } });
    s.addText(q, { x: 0.32, y: y + 0.02, w: 6.3, h: 0.51,
      fontSize: 13.5, fontFace: "Calibri", color: DARK_TEXT, valign: "middle" });
    s.addShape("rect", { x: 6.85, y, w: 2.9, h: 0.55,
      fill: { color: ABG }, line: { color: GOLD, width: 1 } });
    s.addText(a, { x: 6.9, y: y + 0.02, w: 2.75, h: 0.51,
      fontSize: 13, fontFace: "Calibri", bold: true, color: DARK_TEXT, valign: "middle" });
  });
}

// ── SLIDE 4 — SHALL / SHOULD / OUGHT TO: Introdução ──────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: OFF_WHITE };
  addTopBar(s, "SHALL, SHOULD e OUGHT TO");
  addLeftAccent(s);

  const cards = [
    { modal: "SHALL", bg: "d4e6f1", border: "2471a3",
      lines: ["Formal / pouco frequente", "Usado em ofertas e sugestões\n(especialmente em perguntas)"] },
    { modal: "SHOULD", bg: "d5f0e0", border: "1a7a3a",
      lines: ["Neutro / muito comum", "Conselho, recomendação,\nexpectativa, previsão"] },
    { modal: "OUGHT TO", bg: GOLD_LIGHT, border: GOLD_DIM,
      lines: ["Formal / menos frequente", "≈ SHOULD (mesmo significado)\nMais comum em textos escritos"] },
  ];

  cards.forEach(({ modal, bg, border, lines }, i) => {
    const x = 0.3 + i * 3.2;
    s.addShape("rect", { x, y: 1.3, w: 3.0, h: 3.8,
      fill: { color: bg }, line: { color: border, width: 2 } });
    s.addText(modal, { x, y: 1.3, w: 3.0, h: 0.65,
      fontSize: 22, fontFace: "Georgia", bold: true, color: NAVY,
      align: "center", valign: "middle" });
    s.addShape("rect", { x, y: 1.93, w: 3.0, h: 0.04,
      fill: { color: border }, line: { color: border, width: 0 } });
    lines.forEach((line, li) => {
      s.addText(line, { x: x + 0.12, y: 2.05 + li * 1.0, w: 2.76, h: 0.9,
        fontSize: 13.5, fontFace: "Calibri", color: DARK_TEXT, valign: "top", wrap: true });
    });
  });

  s.addText("Para uso cotidiano em ESL, o foco prático é SHOULD — SHALL e OUGHT TO aparecem mais em textos formais e contratos.", {
    x: 0.22, y: 5.2, w: 9.6, h: 0.28,
    fontSize: 11.5, fontFace: "Calibri", italic: true, color: MID_GRAY, align: "center",
  });
}

// ── SLIDE 5 — SHALL: Uses (Card estilo Woodward) ──────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: OFF_WHITE };
  addTopBar(s, "SHALL — Usos");
  addLeftAccent(s);

  const uses = [
    { label: "Sugestão", ex: "Shall I get a pizza for dinner tonight?" },
    { label: "Oferta / Voluntariar-se", ex: "That bag looks heavy. Shall I carry it for you?" },
    { label: "Instrução", ex: "What shall I do with your mail when it arrives?" },
    { label: "Promessa", ex: "You shall be the first person to know." },
    { label: "Confirmação", ex: "I shall meet you there at 7." },
  ];

  const bgColors = ["d4e6f1","dce8f0","e4eef8","d4e6f1","dce8f0"];
  const yStart = 1.28;
  const rowH   = 0.72;
  uses.forEach(({ label, ex }, i) => {
    const y = yStart + i * rowH;
    s.addShape("rect", { x: 0.22, y, w: 2.4, h: 0.62,
      fill: { color: NAVY }, line: { color: NAVY, width: 0 } });
    s.addText(label, { x: 0.22, y, w: 2.4, h: 0.62,
      fontSize: 13, fontFace: "Calibri", bold: true, color: WHITE,
      align: "center", valign: "middle" });
    s.addShape("rect", { x: 2.72, y, w: 7.0, h: 0.62,
      fill: { color: bgColors[i] }, line: { color: "c5d8e8", width: 1 } });
    s.addText(ex, { x: 2.85, y, w: 6.8, h: 0.62,
      fontSize: 13.5, fontFace: "Calibri", italic: true, color: DARK_TEXT, valign: "middle" });
  });

  s.addShape("rect", { x: 0.22, y: 4.95, w: 9.5, h: 0.5,
    fill: { color: GOLD_LIGHT }, line: { color: GOLD, width: 1 } });
  s.addText("💡 SHALL pode ser substituído: Sugestão → SHOULD  |  Oferta → CAN / COULD  |  Promessa → WILL", {
    x: 0.32, y: 4.95, w: 9.3, h: 0.5,
    fontSize: 12, fontFace: "Calibri", color: DARK_TEXT, valign: "middle",
  });
}

// ── SLIDE 6 — SHALL: Notas e Contexto ────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: OFF_WHITE };
  addTopBar(s, "SHALL — Notas e Exemplos");
  addLeftAccent(s);

  // Warning box
  s.addShape("rect", { x: 0.22, y: 1.28, w: 9.5, h: 0.9,
    fill: { color: "fff3cd" }, line: { color: "e09800", width: 2 } });
  s.addText([
    { text: "⚠  SHALL ", options: { bold: true, color: "9a6600" } },
    { text: "não é comum no inglês cotidiano moderno. ", options: { color: DARK_TEXT } },
    { text: "Em conversas, prefira SHOULD ou WILL.", options: { italic: true, color: DARK_TEXT } },
    { text: "\nAinda encontrado em: fala formal, documentos, contratos, cardápios e regulamentos.", options: { color: MID_GRAY, fontSize: 12 } },
  ], { x: 0.35, y: 1.3, w: 9.2, h: 0.84, fontSize: 13.5, fontFace: "Calibri", valign: "middle" });

  s.addText("Exemplos do cotidiano:", {
    x: 0.45, y: 2.3, w: 9.0, h: 0.35,
    fontSize: 16, fontFace: "Calibri", bold: true, color: NAVY,
  });

  const exs = [
    { ctx: "Sugestão entre amigos", en: '"Shall we go to the park after lunch?"' },
    { ctx: "Oferta no supermercado", en: '"Shall I carry your groceries?"' },
    { ctx: "Fazendo planos", en: '"Shall I book us a table for Saturday?"' },
  ];

  exs.forEach(({ ctx, en }, i) => {
    const y = 2.75 + i * 0.82;
    s.addShape("rect", { x: 0.22, y, w: 9.5, h: 0.72,
      fill: { color: "d4e6f1" }, line: { color: "2471a3", width: 1 } });
    s.addText([
      { text: ctx + "  ", options: { bold: true, color: NAVY } },
      { text: en, options: { italic: true, color: DARK_TEXT } },
    ], { x: 0.35, y, w: 9.2, h: 0.72, fontSize: 14, fontFace: "Calibri", valign: "middle" });
  });
}

// ── SLIDE 7 — SHOULD: Uses (Card estilo Woodward) ────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: OFF_WHITE };
  addTopBar(s, "SHOULD — Usos");
  addLeftAccent(s);

  const uses = [
    { label: "Conselho / Sugestão", ex: "You should get a haircut." },
    { label: "Situação provável (presente)", ex: "Mary should be at home right now." },
    { label: "Previsão (futuro)", ex: "They should win tonight." },
    { label: "SHOULD + have + V₃ (passado)", ex: "You should have given your boss the report yesterday." },
    { label: "SHOULD + be + V-ing", ex: "You should be wearing your seatbelt." },
    { label: "SHOULDN'T = aconselhar NÃO fazer", ex: "You shouldn't skip breakfast every day." },
  ];

  const bgColors = ["d5f0e0","daf2e5","d5f0e0","daf2e5","d5f0e0","daf2e5"];
  const yStart = 1.28;
  const rowH   = 0.66;
  uses.forEach(({ label, ex }, i) => {
    const y = yStart + i * rowH;
    s.addShape("rect", { x: 0.22, y, w: 2.8, h: 0.56,
      fill: { color: NAVY }, line: { color: NAVY, width: 0 } });
    s.addText(label, { x: 0.22, y, w: 2.8, h: 0.56,
      fontSize: 11.5, fontFace: "Calibri", bold: true, color: WHITE,
      align: "center", valign: "middle" });
    s.addShape("rect", { x: 3.12, y, w: 6.6, h: 0.56,
      fill: { color: bgColors[i] }, line: { color: "a0d8b0", width: 1 } });
    s.addText(ex, { x: 3.22, y, w: 6.4, h: 0.56,
      fontSize: 13, fontFace: "Calibri", italic: true, color: DARK_TEXT, valign: "middle" });
  });
}

// ── SLIDE 8 — SHOULD: Contexto do Cotidiano ───────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: OFF_WHITE };
  addTopBar(s, "SHOULD — Exemplos do Cotidiano");
  addLeftAccent(s);

  const domains = [
    { icon: "☀️", label: "Rotina Diária", bg: "fff8e1", border: "f9a825",
      lines: ['"You should sleep at least 8 hours a night."', '"You shouldn\'t skip breakfast."'] },
    { icon: "🏥", label: "Saúde & Farmácia", bg: "fce4ec", border: "c62828",
      lines: ['"You should see a doctor if the pain continues."', '"She should have taken the medicine before eating."'] },
    { icon: "🛒", label: "Compras & Supermercado", bg: "e8f5e9", border: "2e7d32",
      lines: ['"You should compare prices before buying."', '"They should have more staff at the checkout."'] },
    { icon: "⚽", label: "Esportes & Lazer", bg: "e3f2fd", border: "1565c0",
      lines: ['"He should train harder if he wants to make the team."', '"You shouldn\'t run without warming up first."'] },
  ];

  const positions = [
    { x: 0.22, y: 1.3 }, { x: 5.15, y: 1.3 },
    { x: 0.22, y: 3.4 }, { x: 5.15, y: 3.4 },
  ];

  domains.forEach(({ icon, label, bg, border, lines }, i) => {
    const { x, y } = positions[i];
    s.addShape("rect", { x, y, w: 4.7, h: 1.95,
      fill: { color: bg }, line: { color: border, width: 2 } });
    s.addText(icon + "  " + label, { x: x + 0.12, y: y + 0.08, w: 4.46, h: 0.38,
      fontSize: 13, fontFace: "Calibri", bold: true, color: NAVY });
    lines.forEach((line, li) => {
      s.addText(line, { x: x + 0.12, y: y + 0.52 + li * 0.68, w: 4.46, h: 0.62,
        fontSize: 12, fontFace: "Calibri", italic: true, color: DARK_TEXT });
    });
  });
}

// ── SLIDE 9 — OUGHT TO: Usos ──────────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: OFF_WHITE };
  addTopBar(s, "OUGHT TO — Usos");
  addLeftAccent(s);

  // Header explanation
  s.addShape("rect", { x: 0.22, y: 1.28, w: 9.5, h: 0.75,
    fill: { color: GOLD_LIGHT }, line: { color: GOLD, width: 2 } });
  s.addText([
    { text: "OUGHT TO", options: { bold: true, color: NAVY } },
    { text: " pode substituir ", options: {} },
    { text: "SHOULD", options: { bold: true, color: NAVY } },
    { text: " sem alterar o significado — soa mais ", options: {} },
    { text: "formal", options: { bold: true } },
    { text: " e é menos frequente na fala.", options: {} },
  ], { x: 0.35, y: 1.3, w: 9.2, h: 0.7, fontSize: 14, fontFace: "Calibri", color: DARK_TEXT, valign: "middle" });

  // Comparison rows
  const rows = [
    { should: "You should drink more water.", ought: "You ought to drink more water." },
    { should: "You should visit your grandparents more often.", ought: "You ought to visit your grandparents more often." },
    { should: "They should have called the doctor sooner.", ought: "They ought to have called the doctor sooner." },
  ];

  s.addText("SHOULD", { x: 2.5, y: 2.15, w: 3.5, h: 0.32, fontSize: 14, fontFace: "Georgia",
    bold: true, color: NAVY, align: "center" });
  s.addText("OUGHT TO", { x: 6.1, y: 2.15, w: 3.5, h: 0.32, fontSize: 14, fontFace: "Georgia",
    bold: true, color: GOLD_DIM, align: "center" });

  rows.forEach(({ should, ought }, i) => {
    const y = 2.55 + i * 0.82;
    s.addShape("rect", { x: 0.22, y, w: 3.75, h: 0.7,
      fill: { color: "d5f0e0" }, line: { color: "a0d8b0", width: 1 } });
    s.addText(should, { x: 0.32, y, w: 3.55, h: 0.7,
      fontSize: 12.5, fontFace: "Calibri", italic: true, color: DARK_TEXT, valign: "middle" });
    s.addText("=", { x: 4.05, y, w: 0.6, h: 0.7,
      fontSize: 18, fontFace: "Calibri", bold: true, color: GOLD_DIM, align: "center", valign: "middle" });
    s.addShape("rect", { x: 4.72, y, w: 5.0, h: 0.7,
      fill: { color: GOLD_LIGHT }, line: { color: GOLD, width: 1 } });
    s.addText(ought, { x: 4.82, y, w: 4.8, h: 0.7,
      fontSize: 12.5, fontFace: "Calibri", italic: true, color: DARK_TEXT, valign: "middle" });
  });

  s.addText('Negativa: "ought not to" (raro) — na prática, prefira SHOULDN\'T.', {
    x: 0.22, y: 5.2, w: 9.5, h: 0.28,
    fontSize: 11.5, fontFace: "Calibri", italic: true, color: MID_GRAY, align: "center",
  });
}

// ── SLIDE 10 — SHALL / SHOULD / OUGHT TO: Comparação ─────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: OFF_WHITE };
  addTopBar(s, "SHALL / SHOULD / OUGHT TO — Comparação");
  addLeftAccent(s);

  const H   = { fill: { color: NAVY }, color: WHITE, bold: true, align: "center", valign: "middle", fontSize: 13 };
  const sub = { fill: { color: NAVY_MID }, color: WHITE, bold: true, align: "center", valign: "middle", fontSize: 12 };

  function makeRow(modal, register, use, example, bgColor) {
    const cell = (t, opts) => ({ text: t, options: Object.assign({ fill: { color: bgColor }, align: "center", valign: "middle", fontSize: 12.5, color: DARK_TEXT }, opts) });
    return [
      { text: modal, options: Object.assign({}, sub, { fill: { color: NAVY } }) },
      cell(register, {}),
      cell(use, {}),
      cell(example, { italic: true }),
    ];
  }

  const rows = [
    [
      { text: "Modal", options: H },
      { text: "Registro", options: H },
      { text: "Uso Principal", options: H },
      { text: "Exemplo", options: H },
    ],
    makeRow("SHALL", "Formal / datado", "Ofertas e sugestões\n(especialmente perguntas)", "Shall I carry your bags?", "d4e6f1"),
    makeRow("SHOULD", "Neutro / comum", "Conselho, expectativa,\nprevisão", "You should eat more fruit.", "d5f0e0"),
    makeRow("OUGHT TO", "Formal", "Obrigação moral,\nconselho", "You ought to call your doctor.", GOLD_LIGHT),
  ];

  s.addTable(rows, {
    x: 0.18, y: 1.28, w: 9.64, h: 3.7,
    border: { pt: 1, color: "ccccdd" },
    rowH: [0.46, 1.05, 1.05, 1.05],
    colW: [1.6, 2.0, 2.8, 3.24],
  });

  s.addText("💡 Para o ESL cotidiano, o foco prático é SHOULD. SHALL e OUGHT TO aparecem mais em leitura de textos formais.", {
    x: 0.22, y: 5.1, w: 9.5, h: 0.38,
    fontSize: 12, fontFace: "Calibri", italic: true, color: MID_GRAY, align: "center",
  });
}

pres.writeFile({ fileName: "/Users/emadruga/proj/StudyAmigoApp/aula_verbos_modais/Aula2_PT_Slides_01-10.pptx" })
  .then(() => console.log("✅ Saved: Aula2_PT_Slides_01-10.pptx"))
  .catch(e => { console.error("❌", e); process.exit(1); });
