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

// ── SLIDE 21 — Voz Passiva com Modais: Estrutura ───────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: OFF_WHITE };
  addTopBar(s, "Modais na Voz Passiva");
  addLeftAccent(s);

  // Formula box
  s.addShape("rect", { x: 0.22, y: 1.28, w: 9.5, h: 0.75,
    fill: { color: NAVY }, line: { color: NAVY, width: 0 } });
  s.addText([
    { text: "Sujeito  +  ", options: { color: WHITE } },
    { text: "MODAL", options: { color: GOLD_LIGHT, bold: true } },
    { text: "  +  ", options: { color: WHITE } },
    { text: "BE", options: { color: GOLD_LIGHT, bold: true } },
    { text: "  +  ", options: { color: WHITE } },
    { text: "V₃", options: { color: GOLD_LIGHT, bold: true } },
    { text: "  (particípio passado)", options: { color: WHITE } },
  ], { x: 0.32, y: 1.28, w: 9.3, h: 0.75,
    fontSize: 20, fontFace: "Georgia", align: "center", valign: "middle" });

  const exs = [
    { src: "This form must be filled in before your appointment.", note: "must + be + V₃" },
    { src: "The match might be cancelled due to rain.", note: "might + be + V₃" },
    { src: "Fresh fruit should be kept in the refrigerator.", note: "should + be + V₃" },
    { src: "The medicine could have been taken incorrectly.", note: "could + have been + V₃ (passado passivo)" },
  ];

  exs.forEach(({ src, note }, i) => {
    const y = 2.18 + i * 0.8;
    s.addShape("rect", { x: 0.22, y, w: 7.5, h: 0.68,
      fill: { color: "e8f5e9" }, line: { color: "a0d8b0", width: 1 } });
    s.addText(src, { x: 0.32, y, w: 7.3, h: 0.68,
      fontSize: 13, fontFace: "Calibri", italic: true, color: DARK_TEXT, valign: "middle" });
    s.addShape("rect", { x: 7.77, y, w: 1.95, h: 0.68,
      fill: { color: GOLD_LIGHT }, line: { color: GOLD, width: 1 } });
    s.addText(note, { x: 7.82, y, w: 1.85, h: 0.68,
      fontSize: 10.5, fontFace: "Calibri", bold: true, color: DARK_TEXT, valign: "middle", align: "center" });
  });
}

// ── SLIDE 22 — Por que usar a Voz Passiva? ────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: OFF_WHITE };
  addTopBar(s, "Por que usar a Voz Passiva com Modais?");
  addLeftAccent(s);

  s.addText([
    { text: "Usamos a voz passiva para focar na ", options: {} },
    { text: "ação ou no objeto", options: { bold: true, color: NAVY } },
    { text: ", e não em quem a realiza.", options: {} },
  ], { x: 0.45, y: 1.28, w: 9.1, h: 0.42,
    fontSize: 15, fontFace: "Calibri", color: DARK_TEXT, valign: "middle" });

  s.addText("Muito comum em: instruções, regras, avisos, embalagens e etiquetas", {
    x: 0.45, y: 1.76, w: 9.1, h: 0.32,
    fontSize: 14, fontFace: "Calibri", bold: true, color: MID_GRAY });

  const signs = [
    { ctx: "🏥 Bula de remédio", ex: '"This medicine must be taken with food."' },
    { ctx: "🛒 Aviso no supermercado", ex: '"Trolleys should be returned after use."' },
    { ctx: "🐾 Placa na loja", ex: '"Pets cannot be brought into the store."' },
    { ctx: "⚽ Regulamento esportivo", ex: '"Shin guards must be worn during all matches."' },
  ];

  signs.forEach(({ ctx, ex }, i) => {
    const y = 2.18 + i * 0.78;
    s.addShape("rect", { x: 0.22, y, w: 2.5, h: 0.66,
      fill: { color: NAVY }, line: { color: NAVY, width: 0 } });
    s.addText(ctx, { x: 0.22, y, w: 2.5, h: 0.66,
      fontSize: 12, fontFace: "Calibri", bold: true, color: WHITE, align: "center", valign: "middle" });
    s.addShape("rect", { x: 2.77, y, w: 7.0, h: 0.66,
      fill: { color: "e8f5e9" }, line: { color: "a0d8b0", width: 1 } });
    s.addText(ex, { x: 2.87, y, w: 6.8, h: 0.66,
      fontSize: 13, fontFace: "Calibri", italic: true, color: DARK_TEXT, valign: "middle" });
  });

  s.addText("O agente (quem faz a ação) é desconhecido, óbvio ou irrelevante.", {
    x: 0.22, y: 5.28, w: 9.5, h: 0.28,
    fontSize: 11.5, fontFace: "Calibri", italic: true, color: MID_GRAY, align: "center" });
}

// ── SLIDE 23 — Tabela: Voz Passiva com Modais ─────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: OFF_WHITE };
  addTopBar(s, "Voz Passiva com Modais — Exemplos");
  addLeftAccent(s);

  const H = { fill: { color: NAVY }, color: WHITE, bold: true, align: "center", valign: "middle", fontSize: 12.5 };

  const data = [
    { modal: "must", act: "You must refrigerate this product.", pass: "This product must be refrigerated." },
    { modal: "should", act: "They should wash the vegetables.", pass: "The vegetables should be washed." },
    { modal: "can", act: "Anyone can use this entrance.", pass: "This entrance can be used by anyone." },
    { modal: "could", act: "They could have cancelled the game.", pass: "The game could have been cancelled." },
    { modal: "may", act: "Someone may have taken the wrong bag.", pass: "The wrong bag may have been taken." },
    { modal: "might", act: "A customer might have left it here.", pass: "It might have been left by a customer." },
  ];

  const bgAct  = "d4e6f1";
  const bgPass = "e8f5e9";

  const rows = [
    [
      { text: "Modal", options: H },
      { text: "Voz Ativa", options: H },
      { text: "Voz Passiva", options: H },
    ],
    ...data.map(({ modal, act, pass }, i) => {
      const bg = i % 2 === 0 ? WHITE : LIGHT_GRAY;
      return [
        { text: modal.toUpperCase(), options: { fill: { color: bg }, bold: true, align: "center", valign: "middle", fontSize: 12, color: NAVY } },
        { text: act,  options: { fill: { color: bgAct  }, italic: true, align: "left", valign: "middle", fontSize: 11.5, color: DARK_TEXT } },
        { text: pass, options: { fill: { color: bgPass }, italic: true, align: "left", valign: "middle", fontSize: 11.5, color: DARK_TEXT } },
      ];
    }),
  ];

  s.addTable(rows, {
    x: 0.15, y: 1.28, w: 9.7, h: 4.08,
    border: { pt: 1, color: "ccccdd" },
    rowH: [0.4, 0.61, 0.61, 0.61, 0.61, 0.61, 0.61],
    colW: [1.2, 4.1, 4.4],
  });
}

// ── SLIDE 24 — Erros Comuns: Passiva com Modais ───────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: OFF_WHITE };
  addTopBar(s, "Erros Comuns — Passiva com Modais");
  addLeftAccent(s);

  const H = { fill: { color: NAVY }, color: WHITE, bold: true, align: "center", valign: "middle", fontSize: 13 };

  const rows = [
    [
      { text: "❌ Errado", options: { fill: { color: "fde8e8" }, color: RED_WRONG, bold: true, align: "center", valign: "middle", fontSize: 13 } },
      { text: "✅ Correto", options: { fill: { color: "e8f5e9" }, color: GREEN_OK, bold: true, align: "center", valign: "middle", fontSize: 13 } },
      { text: "Regra", options: H },
    ],
    ...[
      ["It must be refrigerate.", "It must be refrigerated.", "V₃ (particípio), não infinitivo"],
      ["It should been washed.", "It should be washed.", "modal + BE + V₃"],
      ["It could been taken.", "It could have been taken.", "Passado passivo: modal + have + been + V₃"],
    ].map(([wrong, right, rule]) => [
      { text: wrong, options: { fill: { color: "fde8e8" }, italic: true, color: RED_WRONG, align: "center", valign: "middle", fontSize: 13 } },
      { text: right, options: { fill: { color: "e8f5e9" }, italic: true, color: GREEN_OK, align: "center", valign: "middle", fontSize: 13 } },
      { text: rule, options: { fill: { color: LIGHT_GRAY }, color: DARK_TEXT, align: "center", valign: "middle", fontSize: 12.5 } },
    ]),
  ];

  s.addTable(rows, {
    x: 0.18, y: 1.3, w: 9.64, h: 3.1,
    border: { pt: 1, color: "ccccdd" },
    rowH: [0.46, 0.88, 0.88, 0.88],
    colW: [3.0, 3.2, 3.44],
  });

  // Quick reminder box
  s.addShape("rect", { x: 0.18, y: 4.55, w: 9.64, h: 0.85,
    fill: { color: GOLD_LIGHT }, line: { color: GOLD, width: 1 } });
  s.addText([
    { text: "Estruturas-chave:\n", options: { bold: true, color: NAVY } },
    { text: "  Presente passivo: modal + BE + V₃\n", options: {} },
    { text: "  Passado passivo: modal + HAVE BEEN + V₃", options: {} },
  ], { x: 0.28, y: 4.55, w: 9.44, h: 0.85, fontSize: 13, fontFace: "Calibri", color: DARK_TEXT, valign: "middle" });
}

// ── SLIDE 25 — Prática: Voz Passiva com Modais ────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: OFF_WHITE };
  addTopBar(s, "Prática — Voz Passiva com Modais");
  addLeftAccent(s);

  s.addText("Reescreva na voz passiva:", {
    x: 0.45, y: 1.28, w: 9.1, h: 0.32,
    fontSize: 15, fontFace: "Calibri", italic: true, color: MID_GRAY });

  const items = [
    { q: "1. You must sign this form.", a: "This form must be signed." },
    { q: "2. Someone might have moved my bag.", a: "My bag might have been moved." },
    { q: "3. They should serve the soup hot.", a: "The soup should be served hot." },
    { q: "4. Customers can return the product within 30 days.", a: "The product can be returned within 30 days." },
    { q: "5. A player could have broken the record.", a: "The record could have been broken." },
  ];

  items.forEach(({ q, a }, i) => {
    const y = 1.72 + i * 0.72;
    s.addShape("rect", { x: 0.22, y, w: 5.5, h: 0.62,
      fill: { color: "e8eef8" }, line: { color: "c8d4e8", width: 1 } });
    s.addText(q, { x: 0.32, y, w: 5.3, h: 0.62,
      fontSize: 13, fontFace: "Calibri", color: DARK_TEXT, valign: "middle" });
    s.addText("→", { x: 5.78, y, w: 0.4, h: 0.62,
      fontSize: 16, fontFace: "Calibri", bold: true, color: GOLD_DIM, align: "center", valign: "middle" });
    s.addShape("rect", { x: 6.22, y, w: 3.5, h: 0.62,
      fill: { color: GOLD_LIGHT }, line: { color: GOLD, width: 1 } });
    s.addText(a, { x: 6.3, y, w: 3.35, h: 0.62,
      fontSize: 12.5, fontFace: "Calibri", bold: true, italic: true, color: DARK_TEXT, valign: "middle" });
  });
}

// ── SLIDE 26 — Resumo: Todos os 8 Modais ──────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: OFF_WHITE };
  addTopBar(s, "Verbos Modais — Resumo Completo");
  addLeftAccent(s);

  const H = { fill: { color: NAVY }, color: WHITE, bold: true, align: "center", valign: "middle", fontSize: 12 };

  const data = [
    { modal: "CAN",      fn: "Habilidade (presente) / Permissão",     cert: "Neutro",        ex: "I can swim." },
    { modal: "COULD",    fn: "Habilidade (passado) / Educado / Cond.", cert: "Baixo–Médio",   ex: "I could cook as a child." },
    { modal: "MAY",      fn: "Possibilidade / Permissão (formal)",     cert: "~70%",           ex: "It may rain later." },
    { modal: "MIGHT",    fn: "Possibilidade (menos certa)",            cert: "~40%",           ex: "I might go to the gym." },
    { modal: "SHALL",    fn: "Oferta / Sugestão (formal)",             cert: "Neutro",        ex: "Shall we go?" },
    { modal: "SHOULD",   fn: "Conselho / Expectativa",                 cert: "Médio",          ex: "You should see a doctor." },
    { modal: "OUGHT TO", fn: "Obrigação moral / Conselho (formal)",    cert: "Médio",          ex: "You ought to call her." },
    { modal: "MUST",     fn: "Obrigação forte / Dedução",              cert: "Alto",           ex: "You must rest today." },
  ];

  const bgColors = ["d4e6f1","dce8f0","e0f0d8","e8f5e0","fff3cd","fff8e1",GOLD_LIGHT,"fde8e8"];

  const rows = [
    [
      { text: "Modal", options: H },
      { text: "Função Principal", options: H },
      { text: "Certeza / Força", options: H },
      { text: "Exemplo", options: H },
    ],
    ...data.map(({ modal, fn, cert, ex }, i) => {
      const bg = bgColors[i];
      const c = (t, opts={}) => ({ text: t, options: Object.assign({ fill: { color: bg }, align: "center", valign: "middle", fontSize: 11, color: DARK_TEXT }, opts) });
      return [
        c(modal, { bold: true, color: NAVY }),
        c(fn, { align: "left" }),
        c(cert),
        c(ex, { italic: true, align: "left" }),
      ];
    }),
  ];

  s.addTable(rows, {
    x: 0.15, y: 1.28, w: 9.7, h: 4.08,
    border: { pt: 1, color: "ccccdd" },
    rowH: [0.4, 0.46, 0.46, 0.46, 0.46, 0.46, 0.46, 0.46, 0.46],
    colW: [1.45, 3.2, 1.7, 3.35],
  });
}

// ── SLIDE 27 — Pares Críticos: Não Confunda! ──────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: OFF_WHITE };
  addTopBar(s, "Não Confunda Estes Pares!");
  addLeftAccent(s);

  const pairs = [
    {
      a: "MUSTN'T", adesc: "= PROIBIDO",         aex: '"You mustn\'t smoke here."',
      b: "DON'T HAVE TO", bdesc: "= NÃO OBRIGATÓRIO", bex: '"You don\'t have to buy anything."',
      abg: "fde8e8", bbg: "e8f5e9", aborder: "c0392b", bborder: "2e7d32",
    },
    {
      a: "MUST", adesc: "Obrigação do falante",  aex: '"You must try this cake!"',
      b: "HAVE TO", bdesc: "Obrigação externa",  bex: '"I have to be at work at 8."',
      abg: "fff3cd", bbg: "d4e6f1", aborder: "e09800", bborder: "2471a3",
    },
    {
      a: "MAY", adesc: "~70% de chance",          aex: '"It may rain."',
      b: "MIGHT", bdesc: "~40% de chance",         bex: '"It might rain."',
      abg: "e0f0d8", bbg: "d4e6f1", aborder: "2e7d32", bborder: "2471a3",
    },
    {
      a: "CAN", adesc: "Habilidade presente",     aex: '"I can run 5 km."',
      b: "COULD", bdesc: "Habilidade passada / educado", bex: '"I could run faster last year."',
      abg: "e0f0d8", bbg: "dce8f0", aborder: "2e7d32", bborder: "2471a3",
    },
  ];

  const positions = [
    { x: 0.18, y: 1.28 }, { x: 5.12, y: 1.28 },
    { x: 0.18, y: 3.4  }, { x: 5.12, y: 3.4  },
  ];

  pairs.forEach(({ a, adesc, aex, b, bdesc, bex, abg, bbg, aborder, bborder }, i) => {
    const { x, y } = positions[i];
    const W = 4.7, H2 = 1.88;
    // left half
    s.addShape("rect", { x, y, w: W / 2 - 0.05, h: H2,
      fill: { color: abg }, line: { color: aborder, width: 2 } });
    s.addText(a, { x: x + 0.08, y, w: W / 2 - 0.2, h: 0.42,
      fontSize: 13, fontFace: "Georgia", bold: true, color: NAVY, valign: "middle" });
    s.addText(adesc, { x: x + 0.08, y: y + 0.44, w: W / 2 - 0.2, h: 0.38,
      fontSize: 11, fontFace: "Calibri", color: DARK_TEXT });
    s.addText(aex, { x: x + 0.08, y: y + 0.86, w: W / 2 - 0.2, h: 0.9,
      fontSize: 11, fontFace: "Calibri", italic: true, color: DARK_TEXT });
    // ≠ divider
    s.addText("≠", { x: x + W / 2 - 0.1, y, w: 0.42, h: H2,
      fontSize: 18, fontFace: "Georgia", bold: true, color: GOLD_DIM,
      align: "center", valign: "middle" });
    // right half
    const x2 = x + W / 2 + 0.1;
    s.addShape("rect", { x: x2, y, w: W / 2 - 0.05, h: H2,
      fill: { color: bbg }, line: { color: bborder, width: 2 } });
    s.addText(b, { x: x2 + 0.08, y, w: W / 2 - 0.2, h: 0.42,
      fontSize: 13, fontFace: "Georgia", bold: true, color: NAVY, valign: "middle" });
    s.addText(bdesc, { x: x2 + 0.08, y: y + 0.44, w: W / 2 - 0.2, h: 0.38,
      fontSize: 11, fontFace: "Calibri", color: DARK_TEXT });
    s.addText(bex, { x: x2 + 0.08, y: y + 0.86, w: W / 2 - 0.2, h: 0.9,
      fontSize: 11, fontFace: "Calibri", italic: true, color: DARK_TEXT });
  });
}

// ── SLIDE 28 — Prática Final: Todos os Modais ─────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: OFF_WHITE };
  addTopBar(s, "Prática Final — Todos os Modais");
  addLeftAccent(s);

  s.addText("Escolha o modal correto:", {
    x: 0.45, y: 1.28, w: 9.1, h: 0.3,
    fontSize: 15, fontFace: "Calibri", italic: true, color: MID_GRAY });

  const items = [
    { q: "1. You _______ eat in the changing room. It's not allowed.", a: "mustn't" },
    { q: "2. She _______ play the guitar when she was ten.", a: "could" },
    { q: "3. _______ I try this jacket on, please?", a: "May / Can / Could" },
    { q: "4. The supermarket _______ be closed — it's a holiday today.", a: "may / might / could" },
    { q: "5. You _______ bring your gym bag; they provide towels there.", a: "don't have to" },
    { q: "6. All visitors _______ sign in at the reception desk.", a: "must / have to" },
    { q: "7. He _______ have eaten something bad — he feels terrible.", a: "must / may / might" },
    { q: "8. Medicines _______ be kept out of reach of children.", a: "must be / should be" },
  ];

  items.forEach(({ q, a }, i) => {
    const y = 1.68 + i * 0.49;
    s.addShape("rect", { x: 0.22, y, w: 6.5, h: 0.4,
      fill: { color: "e8eef8" }, line: { color: "c8d4e8", width: 1 } });
    s.addText(q, { x: 0.32, y, w: 6.3, h: 0.4,
      fontSize: 12, fontFace: "Calibri", color: DARK_TEXT, valign: "middle" });
    s.addShape("rect", { x: 6.82, y, w: 2.9, h: 0.4,
      fill: { color: GOLD_LIGHT }, line: { color: GOLD, width: 1 } });
    s.addText(a, { x: 6.87, y, w: 2.8, h: 0.4,
      fontSize: 11.5, fontFace: "Calibri", bold: true, color: DARK_TEXT, valign: "middle" });
  });
}

// ── SLIDE 29 — Atividade de Produção Oral ─────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: OFF_WHITE };
  addTopBar(s, "Vamos Falar! — Atividade Final");
  addLeftAccent(s);

  s.addText("Em duplas ou pequenos grupos — use verbos modais nas respostas:", {
    x: 0.45, y: 1.25, w: 9.1, h: 0.35,
    fontSize: 14.5, fontFace: "Calibri", italic: true, color: MID_GRAY });

  const qs = [
    { n: "1", q: "O que toda pessoa MUST fazer para ter saúde?\nO que ela DON'T HAVE TO fazer?", bg: "fde8e8", border: "c0392b" },
    { n: "2", q: "O que um bom colega de equipe SHOULD fazer?\nO que ele SHOULDN'T fazer?", bg: "e8f5e9", border: "2e7d32" },
    { n: "3", q: "Você chega ao supermercado e seu produto favorito sumiu.\nO que COULD HAVE happened?", bg: "d4e6f1", border: "2471a3" },
    { n: "4", q: "SHALL we make a list of rules for our classroom?\nWhat SHOULD be on it?", bg: GOLD_LIGHT, border: GOLD_DIM },
  ];

  const positions = [
    { x: 0.22, y: 1.7 }, { x: 5.12, y: 1.7 },
    { x: 0.22, y: 3.6 }, { x: 5.12, y: 3.6 },
  ];

  qs.forEach(({ n, q, bg, border }, i) => {
    const { x, y } = positions[i];
    s.addShape("rect", { x, y, w: 4.68, h: 1.73,
      fill: { color: bg }, line: { color: border, width: 2 } });
    s.addShape("rect", { x, y, w: 0.45, h: 1.73,
      fill: { color: border }, line: { color: border, width: 0 } });
    s.addText(n, { x, y, w: 0.45, h: 1.73,
      fontSize: 18, fontFace: "Georgia", bold: true, color: WHITE,
      align: "center", valign: "middle" });
    s.addText(q, { x: x + 0.52, y: y + 0.12, w: 4.08, h: 1.5,
      fontSize: 13, fontFace: "Calibri", color: DARK_TEXT, valign: "top", wrap: true });
  });
}

// ── SLIDE 30 — Encerramento: Pontos-Chave ─────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: OFF_WHITE };
  addTopBar(s, "Pontos-Chave — Verbos Modais");
  addLeftAccent(s);

  const takeaways = [
    { icon: "🔒", text: "Modais NUNCA mudam de forma — sem -s, sem -ed, sem 'to' depois deles" },
    { icon: "⏩", text: "modal + verbo base → significado presente / futuro" },
    { icon: "⏪", text: "modal + HAVE + V₃ → referência ao passado" },
    { icon: "🔄", text: "modal + BE + V₃ → voz passiva" },
    { icon: "⏮️", text: "modal + HAVE BEEN + V₃ → passado passivo" },
    { icon: "🎯", text: "MUST/HAVE TO | MUSTN'T/DON'T HAVE TO | MAY/MIGHT | CAN/COULD" },
  ];

  const cols = [0.22, 3.45, 6.68];
  const rows2 = [1.28, 2.72];
  const W = 3.05, H2 = 1.28;

  takeaways.forEach(({ icon, text }, i) => {
    const col = i % 3;
    const row = Math.floor(i / 3);
    const x = cols[col];
    const y = rows2[row];
    s.addShape("rect", { x, y, w: W, h: H2,
      fill: { color: WHITE }, line: { color: GOLD, width: 2 } });
    s.addShape("rect", { x, y, w: W, h: 0.32,
      fill: { color: NAVY }, line: { color: NAVY, width: 0 } });
    s.addText(icon, { x, y, w: W, h: 0.32,
      fontSize: 14, align: "center", valign: "middle" });
    s.addText(text, { x: x + 0.1, y: y + 0.36, w: W - 0.2, h: H2 - 0.42,
      fontSize: 11.5, fontFace: "Calibri", color: DARK_TEXT, valign: "top", wrap: true });
  });

  // Bottom navy banner
  s.addShape("rect", { x: 0, y: 4.1, w: 10, h: 0.75,
    fill: { color: NAVY }, line: { color: NAVY, width: 0 } });
  s.addText([
    { text: "Obrigado! ", options: { color: GOLD_LIGHT, bold: true, fontSize: 17 } },
    { text: "  |  ", options: { color: GOLD, fontSize: 17 } },
    { text: "Dúvidas?", options: { color: WHITE, fontSize: 17 } },
    { text: "  |  ", options: { color: GOLD, fontSize: 17 } },
    { text: "Próxima aula: Review + Speaking Practice", options: { color: "aabbcc", fontSize: 14, italic: true } },
  ], { x: 0, y: 4.1, w: 10, h: 0.75, align: "center", valign: "middle" });
}

pres.writeFile({ fileName: "/Users/emadruga/proj/StudyAmigoApp/aula_verbos_modais/Aula2_PT_Slides_21-30.pptx" })
  .then(() => console.log("✅ Saved: Aula2_PT_Slides_21-30.pptx"))
  .catch(e => { console.error("❌", e); process.exit(1); });
