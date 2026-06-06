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

// ── SLIDE 11 — SHOULD: Erros Comuns ──────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: OFF_WHITE };
  addTopBar(s, "Erros Comuns — SHOULD");
  addLeftAccent(s);

  const H = { fill: { color: NAVY }, color: WHITE, bold: true, align: "center", valign: "middle", fontSize: 13 };

  const rows = [
    [
      { text: "❌ Errado", options: { fill: { color: "fde8e8" }, color: RED_WRONG, bold: true, align: "center", valign: "middle", fontSize: 13 } },
      { text: "✅ Correto", options: { fill: { color: "e8f5e9" }, color: GREEN_OK, bold: true, align: "center", valign: "middle", fontSize: 13 } },
      { text: "Regra", options: H },
    ],
    ...[
      ["You should to eat less sugar.", "You should eat less sugar.", "Sem 'to' após modal"],
      ["She shoulds rest.", "She should rest.", "Sem -s na 3ª pessoa"],
      ["I should went to the gym.", "I should have gone to the gym.", "Passado = should + have + V₃"],
      ["You should have go.", "You should have gone.", "V₃ (particípio), não infinitivo"],
    ].map(([wrong, right, rule]) => [
      { text: wrong, options: { fill: { color: "fde8e8" }, italic: true, color: RED_WRONG, align: "center", valign: "middle", fontSize: 12.5 } },
      { text: right, options: { fill: { color: "e8f5e9" }, italic: true, color: GREEN_OK, align: "center", valign: "middle", fontSize: 12.5 } },
      { text: rule, options: { fill: { color: LIGHT_GRAY }, color: DARK_TEXT, align: "center", valign: "middle", fontSize: 12 } },
    ]),
  ];

  s.addTable(rows, {
    x: 0.18, y: 1.3, w: 9.64, h: 3.85,
    border: { pt: 1, color: "ccccdd" },
    rowH: [0.46, 0.84, 0.84, 0.84, 0.84],
    colW: [3.1, 3.1, 3.44],
  });
}

// ── SLIDE 12 — Prática: SHALL / SHOULD / OUGHT TO ────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: OFF_WHITE };
  addTopBar(s, "Prática — SHALL / SHOULD / OUGHT TO");
  addLeftAccent(s);

  s.addText("Complete as frases com o modal mais adequado:", {
    x: 0.45, y: 1.28, w: 9.1, h: 0.32,
    fontSize: 15, fontFace: "Calibri", italic: true, color: MID_GRAY,
  });

  const items = [
    { q: '1. You _______ drink more water — it\'s really hot today.', a: 'should / ought to' },
    { q: '2. _______ I carry those grocery bags for you?', a: 'Shall' },
    { q: '3. The bus _______ arrive at 3:15 — it\'s usually on time.', a: 'should' },
    { q: '4. She _______ have gone to the doctor sooner.', a: 'should have / ought to have' },
    { q: '5. You _______ eat junk food every day — it\'s bad for your health.', a: "shouldn't" },
    { q: '6. Players _______ arrive at the stadium one hour before the game.', a: 'should / ought to' },
  ];

  items.forEach(({ q, a }, i) => {
    const y = 1.72 + i * 0.62;
    s.addShape("rect", { x: 0.22, y, w: 6.6, h: 0.52,
      fill: { color: "e8eef8" }, line: { color: "c8d4e8", width: 1 } });
    s.addText(q, { x: 0.32, y, w: 6.4, h: 0.52,
      fontSize: 13, fontFace: "Calibri", color: DARK_TEXT, valign: "middle" });
    s.addShape("rect", { x: 6.95, y, w: 2.8, h: 0.52,
      fill: { color: GOLD_LIGHT }, line: { color: GOLD, width: 1 } });
    s.addText(a, { x: 7.0, y, w: 2.7, h: 0.52,
      fontSize: 12.5, fontFace: "Calibri", bold: true, color: DARK_TEXT, valign: "middle" });
  });
}

// ── SLIDE 13 — MUST / HAVE TO: Introdução ────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: OFF_WHITE };
  addTopBar(s, "MUST e HAVE TO");
  addLeftAccent(s);

  // Two speech-bubble style boxes
  const cards = [
    { speaker: "Médico → MUST", bg: "fff3cd", border: "e09800", icon: "👨‍⚕️",
      desc: "Obrigação imposta pelo próprio FALANTE\n(interna / pessoal)",
      ex: '"You must rest for three days."' },
    { speaker: "Paciente → HAVE TO", bg: "d4e6f1", border: "2471a3", icon: "🛌",
      desc: "Obrigação vinda de uma FONTE EXTERNA\n(regras, leis, terceiros)",
      ex: '"I have to rest for three days."' },
  ];

  cards.forEach(({ speaker, bg, border, icon, desc, ex }, i) => {
    const x = 0.22 + i * 4.9;
    s.addShape("rect", { x, y: 1.28, w: 4.6, h: 3.9,
      fill: { color: bg }, line: { color: border, width: 2 } });
    s.addText(icon + "  " + speaker, { x: x + 0.12, y: 1.35, w: 4.36, h: 0.55,
      fontSize: 15, fontFace: "Georgia", bold: true, color: NAVY, valign: "middle" });
    s.addShape("rect", { x: x + 0.1, y: 1.95, w: 4.4, h: 0.04,
      fill: { color: border }, line: { color: border, width: 0 } });
    s.addText(desc, { x: x + 0.12, y: 2.05, w: 4.36, h: 1.1,
      fontSize: 13, fontFace: "Calibri", color: DARK_TEXT, valign: "top", wrap: true });
    s.addShape("rect", { x: x + 0.1, y: 3.2, w: 4.4, h: 0.75,
      fill: { color: WHITE }, line: { color: border, width: 1 } });
    s.addText(ex, { x: x + 0.2, y: 3.22, w: 4.2, h: 0.7,
      fontSize: 13, fontFace: "Calibri", italic: true, color: DARK_TEXT, valign: "middle" });
  });

  s.addText("💡 Na prática, a distinção é sutil — em contextos informais, MUST e HAVE TO são frequentemente intercambiáveis.", {
    x: 0.22, y: 5.28, w: 9.5, h: 0.28,
    fontSize: 11, fontFace: "Calibri", italic: true, color: MID_GRAY, align: "center",
  });
}

// ── SLIDE 14 — MUST: Uses (Card estilo Woodward) ──────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: OFF_WHITE };
  addTopBar(s, "MUST — Usos");
  addLeftAccent(s);

  const uses = [
    { label: "Obrigação", ex: "You must wear a seatbelt when you drive." },
    { label: "Dedução (certeza)", ex: "Look at that snow. It must be cold outside." },
    { label: "Necessidade enfatizada", ex: "Plants must have light and water to grow." },
    { label: "Recomendação forte", ex: "We must get together for dinner soon." },
    { label: "MUSTN'T = Proibição", ex: "You mustn't use your phone while driving." },
  ];

  const bgColors = ["fff3cd","fff8dc","fff3cd","fff8dc","fde8e8"];
  const borderColors = ["e09800","e09800","e09800","e09800","c0392b"];
  const yStart = 1.28;
  const rowH   = 0.72;
  uses.forEach(({ label, ex }, i) => {
    const y = yStart + i * rowH;
    const isLast = i === uses.length - 1;
    s.addShape("rect", { x: 0.22, y, w: 2.7, h: 0.62,
      fill: { color: isLast ? "c0392b" : NAVY }, line: { color: NAVY, width: 0 } });
    s.addText(label, { x: 0.22, y, w: 2.7, h: 0.62,
      fontSize: 12.5, fontFace: "Calibri", bold: true, color: WHITE,
      align: "center", valign: "middle" });
    s.addShape("rect", { x: 3.02, y, w: 6.7, h: 0.62,
      fill: { color: bgColors[i] }, line: { color: borderColors[i], width: 1 } });
    s.addText(ex, { x: 3.12, y, w: 6.5, h: 0.62,
      fontSize: 13, fontFace: "Calibri", italic: true, color: DARK_TEXT, valign: "middle" });
  });

  s.addShape("rect", { x: 0.22, y: 4.95, w: 9.5, h: 0.5,
    fill: { color: GOLD_LIGHT }, line: { color: GOLD, width: 1 } });
  s.addText('💡 HAD TO substitui MUST no passado: "I had to pay the speeding ticket."', {
    x: 0.32, y: 4.95, w: 9.3, h: 0.5,
    fontSize: 12, fontFace: "Calibri", color: DARK_TEXT, valign: "middle",
  });
}

// ── SLIDE 15 — MUST: Contexto do Cotidiano ────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: OFF_WHITE };
  addTopBar(s, "MUST — Exemplos do Cotidiano");
  addLeftAccent(s);

  const domains = [
    { icon: "☀️", label: "Rotina Diária", bg: "fff8e1", border: "f9a825",
      lines: ['"I must wake up at 6 a.m. tomorrow — I have an early class."', '"You must try this recipe!"'] },
    { icon: "🏥", label: "Saúde & Farmácia", bg: "fce4ec", border: "c62828",
      lines: ['"You must take this medicine twice a day."', '"She must be exhausted — she worked all night."'] },
    { icon: "🛒", label: "Compras & Supermercado", bg: "e8f5e9", border: "2e7d32",
      lines: ['"You must keep your receipt to get a refund."', '"This bread must be fresh — it smells amazing."'] },
    { icon: "⚽", label: "Esportes & Lazer", bg: "e3f2fd", border: "1565c0",
      lines: ['"Players must wear shin guards during the match."', '"He trains every day — he must really love football."'] },
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

// ── SLIDE 16 — MUST vs. HAVE TO ───────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: OFF_WHITE };
  addTopBar(s, "MUST vs. HAVE TO — Diferença Principal");
  addLeftAccent(s);

  // MUST card
  s.addShape("rect", { x: 0.22, y: 1.28, w: 4.4, h: 2.8,
    fill: { color: "fff3cd" }, line: { color: "e09800", width: 2 } });
  s.addText("MUST", { x: 0.22, y: 1.28, w: 4.4, h: 0.55,
    fontSize: 20, fontFace: "Georgia", bold: true, color: NAVY, align: "center", valign: "middle" });
  s.addText("Obrigação sentida ou imposta\npelo FALANTE (interna)", {
    x: 0.32, y: 1.9, w: 4.2, h: 0.65,
    fontSize: 12.5, fontFace: "Calibri", color: DARK_TEXT, wrap: true });
  s.addText('"I must call my mother."\n(sinto que devo)', {
    x: 0.32, y: 2.6, w: 4.2, h: 0.55,
    fontSize: 12, fontFace: "Calibri", italic: true, color: DARK_TEXT });
  s.addText('"You must try this dish!"\n(recomendação forte minha)', {
    x: 0.32, y: 3.2, w: 4.2, h: 0.55,
    fontSize: 12, fontFace: "Calibri", italic: true, color: DARK_TEXT });

  // HAVE TO card
  s.addShape("rect", { x: 5.0, y: 1.28, w: 4.7, h: 2.8,
    fill: { color: "d4e6f1" }, line: { color: "2471a3", width: 2 } });
  s.addText("HAVE TO", { x: 5.0, y: 1.28, w: 4.7, h: 0.55,
    fontSize: 20, fontFace: "Georgia", bold: true, color: NAVY, align: "center", valign: "middle" });
  s.addText("Obrigação vinda de uma fonte\nEXTERNA (regras, leis, terceiros)", {
    x: 5.1, y: 1.9, w: 4.5, h: 0.65,
    fontSize: 12.5, fontFace: "Calibri", color: DARK_TEXT, wrap: true });
  s.addText('"I have to be at work by 8 a.m."\n(regra da empresa)', {
    x: 5.1, y: 2.6, w: 4.5, h: 0.55,
    fontSize: 12, fontFace: "Calibri", italic: true, color: DARK_TEXT });
  s.addText('"We have to show ID to enter."\n(exigência externa)', {
    x: 5.1, y: 3.2, w: 4.5, h: 0.55,
    fontSize: 12, fontFace: "Calibri", italic: true, color: DARK_TEXT });

  s.addShape("rect", { x: 0.22, y: 4.22, w: 9.5, h: 0.75,
    fill: { color: GOLD_LIGHT }, line: { color: GOLD, width: 1 } });
  s.addText([
    { text: "Em perguntas, ", options: {} },
    { text: "have to", options: { bold: true } },
    { text: ' é mais natural: "Do you ', options: {} },
    { text: "have to", options: { bold: true } },
    { text: ' work on Saturdays?" (NÃO: "Must you work on Saturdays?")', options: {} },
  ], { x: 0.32, y: 4.22, w: 9.3, h: 0.75, fontSize: 13, fontFace: "Calibri", color: DARK_TEXT, valign: "middle" });
}

// ── SLIDE 17 — MUSTN'T vs. DON'T HAVE TO (Card Woodward) ─────────────────────
{
  const s = pres.addSlide();
  s.background = { color: OFF_WHITE };
  addTopBar(s, "MUSTN'T vs. DON'T HAVE TO");
  addLeftAccent(s);

  // MUSTN'T
  s.addShape("rect", { x: 0.22, y: 1.28, w: 4.45, h: 3.75,
    fill: { color: "fde8e8" }, line: { color: "c0392b", width: 2 } });
  s.addText("MUSTN'T", { x: 0.22, y: 1.28, w: 4.45, h: 0.6,
    fontSize: 18, fontFace: "Georgia", bold: true, color: "c0392b",
    align: "center", valign: "middle" });
  s.addText("= PROIBIDO — não é permitido", {
    x: 0.32, y: 1.95, w: 4.25, h: 0.42,
    fontSize: 13, fontFace: "Calibri", bold: true, color: DARK_TEXT });
  s.addText('"You must not drink that."\n= É proibido.\n\n"You mustn\'t tell John."\n= Você não tem permissão.', {
    x: 0.32, y: 2.42, w: 4.25, h: 2.3,
    fontSize: 13, fontFace: "Calibri", italic: true, color: DARK_TEXT });

  // DON'T HAVE TO
  s.addShape("rect", { x: 5.1, y: 1.28, w: 4.6, h: 3.75,
    fill: { color: "e8f5e9" }, line: { color: "2e7d32", width: 2 } });
  s.addText("DON'T HAVE TO", { x: 5.1, y: 1.28, w: 4.6, h: 0.6,
    fontSize: 18, fontFace: "Georgia", bold: true, color: "2e7d32",
    align: "center", valign: "middle" });
  s.addText("= SEM OBRIGAÇÃO — opcional", {
    x: 5.2, y: 1.95, w: 4.4, h: 0.42,
    fontSize: 13, fontFace: "Calibri", bold: true, color: DARK_TEXT });
  s.addText('"You don\'t have to drink that."\n= Pode beber se quiser, mas não é obrigatório.\n\n"You don\'t have to tell John."\n= É opcional.', {
    x: 5.2, y: 2.42, w: 4.4, h: 2.3,
    fontSize: 13, fontFace: "Calibri", italic: true, color: DARK_TEXT });

  s.addShape("rect", { x: 0.22, y: 5.13, w: 9.5, h: 0.38,
    fill: { color: "fff3cd" }, line: { color: "e09800", width: 1 } });
  s.addText("⚠  Este é um dos erros mais comuns de alunos de ESL — MUSTN'T ≠ DON'T HAVE TO!", {
    x: 0.32, y: 5.13, w: 9.3, h: 0.38,
    fontSize: 12.5, fontFace: "Calibri", bold: true, color: "9a6600", valign: "middle" });
}

// ── SLIDE 18 — MUSTN'T vs. DON'T HAVE TO: Contexto ───────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: OFF_WHITE };
  addTopBar(s, "MUSTN'T vs. DON'T HAVE TO — Cotidiano");
  addLeftAccent(s);

  const rows = [
    { ctx: "☀️ Rotina",
      must: "You mustn't be late for the exam.",
      dont: "You don't have to wear a uniform on weekends." },
    { ctx: "🏥 Saúde",
      must: "You mustn't drink alcohol while taking this medication.",
      dont: "You don't have to fast before this test — only before blood work." },
    { ctx: "🛒 Compras",
      must: "You mustn't open the package before paying.",
      dont: "You don't have to bring a bag — we have free ones here." },
    { ctx: "⚽ Esportes",
      must: "Players mustn't argue with the referee.",
      dont: "You don't have to join the extra practice — it's optional." },
  ];

  // Header
  s.addText("Domínio", { x: 0.18, y: 1.28, w: 1.55, h: 0.42,
    fontSize: 12, fontFace: "Calibri", bold: true, color: WHITE,
    fill: NAVY, align: "center", valign: "middle" });
  // Draw headers manually since addTable with merged-ish look
  s.addShape("rect", { x: 0.18, y: 1.28, w: 1.55, h: 0.42,
    fill: { color: NAVY }, line: { color: NAVY, width: 0 } });
  s.addText("Domínio", { x: 0.18, y: 1.28, w: 1.55, h: 0.42,
    fontSize: 12, fontFace: "Calibri", bold: true, color: WHITE, align: "center", valign: "middle" });
  s.addShape("rect", { x: 1.78, y: 1.28, w: 3.9, h: 0.42,
    fill: { color: "c0392b" }, line: { color: "c0392b", width: 0 } });
  s.addText("MUSTN'T (proibição)", { x: 1.78, y: 1.28, w: 3.9, h: 0.42,
    fontSize: 12, fontFace: "Calibri", bold: true, color: WHITE, align: "center", valign: "middle" });
  s.addShape("rect", { x: 5.73, y: 1.28, w: 4.0, h: 0.42,
    fill: { color: "2e7d32" }, line: { color: "2e7d32", width: 0 } });
  s.addText("DON'T HAVE TO (opcional)", { x: 5.73, y: 1.28, w: 4.0, h: 0.42,
    fontSize: 12, fontFace: "Calibri", bold: true, color: WHITE, align: "center", valign: "middle" });

  rows.forEach(({ ctx, must, dont }, i) => {
    const y = 1.78 + i * 0.87;
    const bg = i % 2 === 0 ? WHITE : LIGHT_GRAY;
    s.addShape("rect", { x: 0.18, y, w: 1.55, h: 0.77,
      fill: { color: bg }, line: { color: "ccccdd", width: 1 } });
    s.addText(ctx, { x: 0.22, y, w: 1.47, h: 0.77,
      fontSize: 12, fontFace: "Calibri", bold: true, color: NAVY, align: "center", valign: "middle" });
    s.addShape("rect", { x: 1.78, y, w: 3.9, h: 0.77,
      fill: { color: "fde8e8" }, line: { color: "e8c0bb", width: 1 } });
    s.addText(must, { x: 1.88, y, w: 3.7, h: 0.77,
      fontSize: 11.5, fontFace: "Calibri", italic: true, color: DARK_TEXT, valign: "middle" });
    s.addShape("rect", { x: 5.73, y, w: 4.0, h: 0.77,
      fill: { color: "e8f5e9" }, line: { color: "b0d8b5", width: 1 } });
    s.addText(dont, { x: 5.83, y, w: 3.8, h: 0.77,
      fontSize: 11.5, fontFace: "Calibri", italic: true, color: DARK_TEXT, valign: "middle" });
  });
}

// ── SLIDE 19 — MUST: Erros Comuns ─────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: OFF_WHITE };
  addTopBar(s, "Erros Comuns — MUST");
  addLeftAccent(s);

  const H = { fill: { color: NAVY }, color: WHITE, bold: true, align: "center", valign: "middle", fontSize: 13 };

  const rows = [
    [
      { text: "❌ Errado", options: { fill: { color: "fde8e8" }, color: RED_WRONG, bold: true, align: "center", valign: "middle", fontSize: 13 } },
      { text: "✅ Correto", options: { fill: { color: "e8f5e9" }, color: GREEN_OK, bold: true, align: "center", valign: "middle", fontSize: 13 } },
      { text: "Regra", options: H },
    ],
    ...[
      ["She musts rest.", "She must rest.", "Sem -s na 3ª pessoa"],
      ["I must to leave.", "I must leave.", "Sem 'to' após modal"],
      ["He must go yesterday.", "He had to go yesterday.", "Passado de MUST = HAD TO"],
      ['You mustn\'t bring ID. (sentido: "opcional")', "You don't have to bring ID.", "MUSTN'T ≠ DON'T HAVE TO"],
    ].map(([wrong, right, rule]) => [
      { text: wrong, options: { fill: { color: "fde8e8" }, italic: true, color: RED_WRONG, align: "center", valign: "middle", fontSize: 12.5 } },
      { text: right, options: { fill: { color: "e8f5e9" }, italic: true, color: GREEN_OK, align: "center", valign: "middle", fontSize: 12.5 } },
      { text: rule, options: { fill: { color: LIGHT_GRAY }, color: DARK_TEXT, align: "center", valign: "middle", fontSize: 12 } },
    ]),
  ];

  s.addTable(rows, {
    x: 0.18, y: 1.3, w: 9.64, h: 3.85,
    border: { pt: 1, color: "ccccdd" },
    rowH: [0.46, 0.84, 0.84, 0.84, 0.84],
    colW: [3.0, 3.2, 3.44],
  });
}

// ── SLIDE 20 — Prática: MUST / HAVE TO / MUSTN'T / DON'T HAVE TO ─────────────
{
  const s = pres.addSlide();
  s.background = { color: OFF_WHITE };
  addTopBar(s, "Prática — MUST / HAVE TO / MUSTN'T / DON'T HAVE TO");
  addLeftAccent(s);

  s.addText("Complete as frases com o modal mais adequado:", {
    x: 0.45, y: 1.28, w: 9.1, h: 0.32,
    fontSize: 15, fontFace: "Calibri", italic: true, color: MID_GRAY,
  });

  const items = [
    { q: "1. You _______ run on the pool deck — it's slippery and dangerous.", a: "mustn't" },
    { q: "2. You _______ bring a gift to the party — it's not expected.", a: "don't have to" },
    { q: "3. All passengers _______ show their ticket before boarding.", a: "have to / must" },
    { q: "4. Look at that dark sky. It _______ be about to rain.", a: "must" },
    { q: "5. She _______ take an extra class last semester — it wasn't required.", a: "didn't have to" },
    { q: "6. I _______ leave early yesterday because my daughter was sick.", a: "had to" },
  ];

  items.forEach(({ q, a }, i) => {
    const y = 1.72 + i * 0.62;
    s.addShape("rect", { x: 0.22, y, w: 6.6, h: 0.52,
      fill: { color: "e8eef8" }, line: { color: "c8d4e8", width: 1 } });
    s.addText(q, { x: 0.32, y, w: 6.4, h: 0.52,
      fontSize: 13, fontFace: "Calibri", color: DARK_TEXT, valign: "middle" });
    s.addShape("rect", { x: 6.95, y, w: 2.8, h: 0.52,
      fill: { color: GOLD_LIGHT }, line: { color: GOLD, width: 1 } });
    s.addText(a, { x: 7.0, y, w: 2.7, h: 0.52,
      fontSize: 12.5, fontFace: "Calibri", bold: true, color: DARK_TEXT, valign: "middle" });
  });
}

pres.writeFile({ fileName: "/Users/emadruga/proj/StudyAmigoApp/aula_verbos_modais/Aula2_PT_Slides_11-20.pptx" })
  .then(() => console.log("✅ Saved: Aula2_PT_Slides_11-20.pptx"))
  .catch(e => { console.error("❌", e); process.exit(1); });
