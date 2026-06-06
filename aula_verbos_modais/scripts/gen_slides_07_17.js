const PptxGenJS = require("pptxgenjs");

// ── Palette: Navy + Gold ──────────────────────────────────────────────────────
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
pres.layout = "LAYOUT_16x9"; // 10" × 5.625"

// ── helpers ───────────────────────────────────────────────────────────────────

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

// Coloured card box used in Woodward-style slides
function addCard(slide, x, y, w, h, headerText, headerBg, bodyLines, bodyFontSize) {
  bodyFontSize = bodyFontSize || 15;
  // header
  slide.addShape("rect", { x, y, w, h: 0.42,
    fill: { color: headerBg }, line: { color: headerBg, width: 0 } });
  slide.addText(headerText, {
    x, y, w, h: 0.42,
    fontSize: 13, fontFace: "Calibri", bold: true,
    color: WHITE, align: "center", valign: "middle", margin: 0,
  });
  // body
  const bodyH = h - 0.42;
  slide.addShape("rect", { x, y: y + 0.42, w, h: bodyH,
    fill: { color: WHITE }, line: { color: "cccccc", width: 1 } });
  slide.addText(
    bodyLines.map((l, i) => ({ text: l, options: { breakLine: i < bodyLines.length - 1 } })),
    { x: x + 0.1, y: y + 0.42, w: w - 0.2, h: bodyH,
      fontSize: bodyFontSize, fontFace: "Calibri", color: DARK_TEXT,
      valign: "middle", align: "left" }
  );
}

// Domain tag chip
function domainTag(slide, x, y, label, bg) {
  slide.addShape("rect", { x, y, w: 1.6, h: 0.28,
    fill: { color: bg }, line: { color: bg, width: 0 }, rectRadius: 0.05 });
  slide.addText(label, {
    x, y, w: 1.6, h: 0.28,
    fontSize: 11, fontFace: "Calibri", bold: true,
    color: WHITE, align: "center", valign: "middle", margin: 0,
  });
}

// Four-domain example block (2×2 grid)
function addDomainGrid(slide, examples) {
  // examples = [{domain, color, lines[]}, ...]  — exactly 4 items
  const positions = [
    { x: 0.25, y: 1.35 },
    { x: 5.15, y: 1.35 },
    { x: 0.25, y: 3.45 },
    { x: 5.15, y: 3.45 },
  ];
  const W = 4.7, H = 1.9;
  examples.forEach((ex, i) => {
    const { x, y } = positions[i];
    // card bg
    slide.addShape("rect", { x, y, w: W, h: H,
      fill: { color: OFF_WHITE }, line: { color: "ddddcc", width: 1 } });
    // left accent stripe in domain colour
    slide.addShape("rect", { x, y, w: 0.1, h: H,
      fill: { color: ex.color }, line: { color: ex.color, width: 0 } });
    // domain label
    slide.addShape("rect", { x, y, w: W, h: 0.32,
      fill: { color: ex.color }, line: { color: ex.color, width: 0 } });
    slide.addText(ex.domain, {
      x, y, w: W, h: 0.32,
      fontSize: 12, fontFace: "Calibri", bold: true,
      color: WHITE, align: "center", valign: "middle", margin: 0,
    });
    // lines
    slide.addText(
      ex.lines.map((l, j) => ({ text: l, options: { breakLine: j < ex.lines.length - 1 } })),
      { x: x + 0.18, y: y + 0.36, w: W - 0.25, h: H - 0.4,
        fontSize: 13.5, fontFace: "Calibri", color: DARK_TEXT,
        valign: "top", align: "left" }
    );
  });
}

// ── SLIDE 7 — Modal Verbs: Introduction ──────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: OFF_WHITE };
  addTopBar(s, "What Are Modal Verbs?");
  addLeftAccent(s);

  // intro sentence
  s.addText("Modal verbs give special meaning to the main verb.", {
    x: 0.35, y: 1.28, w: 9.3, h: 0.45,
    fontSize: 18, fontFace: "Calibri", bold: true, color: NAVY,
  });

  s.addText("They express:", {
    x: 0.35, y: 1.72, w: 9.3, h: 0.32,
    fontSize: 16, fontFace: "Calibri", color: DARK_TEXT,
  });

  // Six function chips in 3×2 grid
  const functions = [
    { label: "Ability",     bg: "1a5276" },
    { label: "Permission",  bg: "1a5276" },
    { label: "Possibility", bg: "6e2f8a" },
    { label: "Obligation",  bg: "7d6608" },
    { label: "Advice",      bg: "1a7a3a" },
    { label: "Deduction",   bg: "7d3c00" },
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

  // The four modal families
  s.addText("The main modal verbs:", {
    x: 0.35, y: 3.4, w: 9.3, h: 0.3,
    fontSize: 15, fontFace: "Calibri", color: DARK_TEXT, italic: true,
  });

  const families = [
    { text: "CAN / COULD",          bg: "1a5276" },
    { text: "MAY / MIGHT",          bg: "6e2f8a" },
    { text: "SHALL / SHOULD / OUGHT TO", bg: "1a7a3a" },
    { text: "MUST",                 bg: "7d6608" },
  ];
  const fW = 2.2, fH = 0.7;
  const fX = [0.35, 2.65, 4.95, 7.7];
  families.forEach((f, i) => {
    s.addShape("rect", { x: fX[i], y: 3.78, w: fW + (i === 2 ? 0.25 : 0), h: fH,
      fill: { color: f.bg }, line: { color: f.bg, width: 0 } });
    s.addText(f.text, {
      x: fX[i], y: 3.78, w: fW + (i === 2 ? 0.25 : 0), h: fH,
      fontSize: 14, fontFace: "Calibri", bold: true,
      color: WHITE, align: "center", valign: "middle", margin: 0,
    });
  });
}

// ── SLIDE 8 — Grammar Rules ───────────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: OFF_WHITE };
  addTopBar(s, "Modal Verbs — Grammar Rules");
  addLeftAccent(s);

  const rules = [
    {
      num: "1",
      bg: "1a5276",
      title: "Always followed by the BASE FORM (no \"to\")",
      ok:    'She can go.   ✓',
      wrong: 'She can to go. / She can goes.   ✗',
    },
    {
      num: "2",
      bg: "1a7a3a",
      title: "No -s in the 3rd person singular",
      ok:    'He must leave.   ✓',
      wrong: 'He musts leave.   ✗',
    },
    {
      num: "3",
      bg: "7d6608",
      title: "No auxiliary for questions and negatives",
      ok:    'Can you help?  /  You must not enter.   ✓',
      wrong: 'Do you can help?   ✗',
    },
  ];

  const boxH = 1.2;
  rules.forEach((r, i) => {
    const y = 1.28 + i * (boxH + 0.18);
    // number badge
    s.addShape("rect", { x: 0.25, y, w: 0.55, h: boxH,
      fill: { color: r.bg }, line: { color: r.bg, width: 0 } });
    s.addText(r.num, {
      x: 0.25, y, w: 0.55, h: boxH,
      fontSize: 26, fontFace: "Georgia", bold: true,
      color: WHITE, align: "center", valign: "middle", margin: 0,
    });
    // rule box
    s.addShape("rect", { x: 0.85, y, w: 9.0, h: boxH,
      fill: { color: WHITE }, line: { color: r.bg, width: 2 } });
    s.addText(r.title, {
      x: 1.0, y, w: 8.7, h: 0.42,
      fontSize: 15, fontFace: "Calibri", bold: true, color: r.bg,
      valign: "middle",
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

// ── SLIDE 9 — Sentence Structure ──────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: OFF_WHITE };
  addTopBar(s, "How to Build Sentences with Modals");
  addLeftAccent(s);

  const structures = [
    { label: "Affirmative", formula: "Subject  +  modal  +  base verb  +  (complement)", example: 'She should drink more water.', bg: "1a5276" },
    { label: "Negative",    formula: "Subject  +  modal  +  NOT  +  base verb",          example: 'You must not eat before the blood test.', bg: "c0392b" },
    { label: "Question",    formula: "Modal  +  subject  +  base verb  +  ?",            example: 'Can you carry these bags for me?', bg: "1a7a3a" },
    { label: "Perfect modal (past)", formula: "modal  +  HAVE  +  past participle (V₃)", example: 'He could have taken the wrong medicine.', bg: "7d6608" },
  ];

  const bW = 4.6, bH = 1.75;
  const positions = [
    { x: 0.2,  y: 1.28 },
    { x: 5.05, y: 1.28 },
    { x: 0.2,  y: 3.2  },
    { x: 5.05, y: 3.2  },
  ];

  structures.forEach((st, i) => {
    const { x, y } = positions[i];
    // header
    s.addShape("rect", { x, y, w: bW, h: 0.38,
      fill: { color: st.bg }, line: { color: st.bg, width: 0 } });
    s.addText(st.label, {
      x, y, w: bW, h: 0.38,
      fontSize: 13, fontFace: "Calibri", bold: true,
      color: WHITE, align: "center", valign: "middle", margin: 0,
    });
    // body
    s.addShape("rect", { x, y: y + 0.38, w: bW, h: bH - 0.38,
      fill: { color: WHITE }, line: { color: "cccccc", width: 1 } });
    s.addText(st.formula, {
      x: x + 0.12, y: y + 0.42, w: bW - 0.22, h: 0.52,
      fontSize: 13, fontFace: "Consolas", bold: true, color: st.bg,
      valign: "middle",
    });
    s.addText(`"${st.example}"`, {
      x: x + 0.12, y: y + 0.95, w: bW - 0.22, h: 0.72,
      fontSize: 14, fontFace: "Calibri", italic: true, color: DARK_TEXT,
      valign: "top",
    });
  });
}

// ── SLIDE 10 — Modal Verbs Overview Table ─────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: OFF_WHITE };
  addTopBar(s, "Modal Verbs at a Glance");
  addLeftAccent(s);

  const H = { fill: { color: NAVY }, color: WHITE, bold: true, align: "center", valign: "middle", fontSize: 13 };

  // highlight colours — Aula 1 modals get a gold-tinted bg
  const A1 = GOLD_LIGHT;  // CAN/COULD/MAY/MIGHT  (Aula 1)
  const A2 = "e8edf5";    // rest                  (Aula 2)

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
    [ { text: "Modal", options: H }, { text: "Main Function", options: H }, { text: "Example", options: H } ],
    row("CAN",      "Ability (present) / Permission",       'I can swim very well.',           A1),
    row("COULD",    "Ability (past) / Polite request",      'I could ride a bike as a child.',  A1),
    row("MAY",      "Possibility / Permission (formal)",    'It may rain this afternoon.',      A1),
    row("MIGHT",    "Possibility (less certain)",           'I might go to the gym later.',     A1),
    row("SHALL",    "Suggestion / Offer (formal)",          'Shall I open the window?',         A2),
    row("SHOULD",   "Advice / Recommendation",              'You should see a doctor.',         A2),
    row("OUGHT TO", "Moral obligation (formal)",            'You ought to call your parents.',  A2),
    row("MUST",     "Strong obligation / Deduction",        'You must take this medicine.',     A2),
  ];

  s.addTable(rows, {
    x: 0.2, y: 1.25, w: 9.6, h: 4.15,
    border: { pt: 1, color: "cccccc" },
    rowH: [0.42, 0.46, 0.46, 0.46, 0.46, 0.46, 0.46, 0.46, 0.46],
    colW: [1.5, 3.5, 4.6],
  });

  s.addText("★  Aula 1 focus (gold rows)   |   Aula 2 content (light rows)", {
    x: 0.2, y: 5.32, w: 9.6, h: 0.22,
    fontSize: 10, fontFace: "Calibri", italic: true, color: MID_GRAY, align: "center",
  });
}

// ── SLIDE 11 — CAN and COULD: Introduction ───────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: OFF_WHITE };
  addTopBar(s, "CAN and COULD");
  addLeftAccent(s);

  // Two side-by-side intro cards
  const cards = [
    {
      x: 0.25, color: "1a5276",
      word: "CAN",
      points: [
        "Ability or possibility in the PRESENT",
        "Informal permission",
        "Requests and offers",
      ],
    },
    {
      x: 5.15, color: "6e2f8a",
      word: "COULD",
      points: [
        "Ability in the PAST",
        "More polite form of CAN",
        "Possibility (less certain)",
        "Conditional of CAN",
      ],
    },
  ];

  cards.forEach(c => {
    const W = 4.6, H = 3.5;
    // header
    s.addShape("rect", { x: c.x, y: 1.28, w: W, h: 0.65,
      fill: { color: c.color }, line: { color: c.color, width: 0 } });
    s.addText(c.word, {
      x: c.x, y: 1.28, w: W, h: 0.65,
      fontSize: 30, fontFace: "Georgia", bold: true,
      color: WHITE, align: "center", valign: "middle", margin: 0,
    });
    // body
    s.addShape("rect", { x: c.x, y: 1.93, w: W, h: H - 0.65,
      fill: { color: WHITE }, line: { color: c.color, width: 2 } });
    s.addText(
      c.points.map((p, i) => ({ text: p, options: { bullet: true, breakLine: i < c.points.length - 1 } })),
      { x: c.x + 0.15, y: 1.98, w: W - 0.25, h: H - 0.75,
        fontSize: 16, fontFace: "Calibri", color: DARK_TEXT, valign: "top", paraSpaceAfter: 8 }
    );
  });

  // bottom note
  s.addShape("rect", { x: 0.25, y: 4.88, w: 9.5, h: 0.5,
    fill: { color: GOLD_LIGHT }, line: { color: GOLD, width: 1 } });
  s.addText('COULD is also the conditional of CAN:  "If we had oranges, I could make juice."', {
    x: 0.35, y: 4.88, w: 9.3, h: 0.5,
    fontSize: 14, fontFace: "Calibri", italic: true, color: NAVY,
    valign: "middle",
  });
}

// ── SLIDE 12 — CAN: Uses (Woodward-style card) ───────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: OFF_WHITE };
  addTopBar(s, "CAN — Uses");
  addLeftAccent(s);

  const uses = [
    { label: "General ability (present)", example: "I can speak English." },
    { label: "Ask for permission (informal)", example: "Can I borrow your pen, please?" },
    { label: "To request something", example: "Can you help me, please?" },
    { label: "Possibility", example: "It can get very cold there at night." },
    { label: "Offer to help someone", example: "Can I carry your bags for you?" },
    { label: "Cannot (can't) = not allowed", example: "You cannot smoke in this room." },
  ];

  uses.forEach((u, i) => {
    const col = i % 2;
    const row = Math.floor(i / 2);
    const x = col === 0 ? 0.22 : 5.12;
    const y = 1.3 + row * 1.38;
    const W = 4.7, H = 1.25;

    s.addShape("rect", { x, y, w: W, h: H,
      fill: { color: WHITE }, line: { color: "1a5276", width: 1 } });
    s.addShape("rect", { x, y, w: W, h: 0.36,
      fill: { color: "1a5276" }, line: { color: "1a5276", width: 0 } });
    s.addText(u.label, {
      x: x + 0.1, y, w: W - 0.15, h: 0.36,
      fontSize: 12, fontFace: "Calibri", bold: true,
      color: WHITE, valign: "middle",
    });
    s.addText(`"${u.example}"`, {
      x: x + 0.12, y: y + 0.4, w: W - 0.2, h: H - 0.42,
      fontSize: 14, fontFace: "Calibri", italic: true, color: DARK_TEXT,
      valign: "middle",
    });
  });
}

// ── SLIDE 13 — CAN: Everyday Context ─────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: OFF_WHITE };
  addTopBar(s, "CAN — Everyday Examples");
  addLeftAccent(s);

  addDomainGrid(s, [
    { domain: "Daily Routine", color: "1a5276", lines: [
      'I can wake up early on weekdays.',
      'Can I borrow your charger?',
    ]},
    { domain: "Health & Pharmacy", color: "1a7a3a", lines: [
      'Can I get this medicine without a prescription?',
      "She can't eat gluten.",
    ]},
    { domain: "Shopping & Supermarket", color: "7d6608", lines: [
      'Can I pay by card?',
      'You can get two for the price of one today.',
    ]},
    { domain: "Sports & Leisure", color: "7d3c00", lines: [
      'He can run 10 km without stopping.',
      "You can't use your hands in football.",
    ]},
  ]);
}

// ── SLIDE 14 — COULD: Uses (Woodward-style card) ─────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: OFF_WHITE };
  addTopBar(s, "COULD — Uses");
  addLeftAccent(s);

  const uses = [
    { label: "General ability in the past",     example: "I could play the piano when I was younger." },
    { label: "Ask for permission (more polite)", example: "Could I use your bathroom, please?" },
    { label: "To request something (polite)",    example: "Could you pass me the salt, please?" },
    { label: "Possibility in the past",          example: "You could have broken your leg." },
    { label: "Suggestion",                       example: "We could go to the movies if you like." },
    { label: "Conditional of CAN",               example: "If we had oranges, I could make you juice." },
  ];

  uses.forEach((u, i) => {
    const col = i % 2;
    const row = Math.floor(i / 2);
    const x = col === 0 ? 0.22 : 5.12;
    const y = 1.3 + row * 1.38;
    const W = 4.7, H = 1.25;

    s.addShape("rect", { x, y, w: W, h: H,
      fill: { color: WHITE }, line: { color: "6e2f8a", width: 1 } });
    s.addShape("rect", { x, y, w: W, h: 0.36,
      fill: { color: "6e2f8a" }, line: { color: "6e2f8a", width: 0 } });
    s.addText(u.label, {
      x: x + 0.1, y, w: W - 0.15, h: 0.36,
      fontSize: 12, fontFace: "Calibri", bold: true,
      color: WHITE, valign: "middle",
    });
    s.addText(`"${u.example}"`, {
      x: x + 0.12, y: y + 0.4, w: W - 0.2, h: H - 0.42,
      fontSize: 14, fontFace: "Calibri", italic: true, color: DARK_TEXT,
      valign: "middle",
    });
  });
}

// ── SLIDE 15 — COULD: Everyday Context ───────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: OFF_WHITE };
  addTopBar(s, "COULD — Everyday Examples");
  addLeftAccent(s);

  addDomainGrid(s, [
    { domain: "Daily Routine", color: "1a5276", lines: [
      'I could ride a bike when I was five.',
      'Could you turn off the lights, please?',
    ]},
    { domain: "Health & Pharmacy", color: "1a7a3a", lines: [
      "He could have taken the wrong pill — he wasn't paying attention.",
      'Could I schedule an appointment for tomorrow?',
    ]},
    { domain: "Shopping & Supermarket", color: "7d6608", lines: [
      'Could you show me a smaller size?',
      'If they had it in stock, I could buy it today.',
    ]},
    { domain: "Sports & Leisure", color: "7d3c00", lines: [
      'She could swim faster when she trained every day.',
      'We could win if everyone plays their best.',
    ]},
  ]);
}

// ── SLIDE 16 — CAN vs. COULD: Side by Side ───────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: OFF_WHITE };
  addTopBar(s, "CAN vs. COULD — What's the Difference?");
  addLeftAccent(s);

  const H  = { fill: { color: NAVY    }, color: WHITE,    bold: true, align: "center", valign: "middle", fontSize: 13 };
  const HC = { fill: { color: "1a5276"}, color: WHITE,    bold: true, align: "center", valign: "middle", fontSize: 13 };
  const HD = { fill: { color: "6e2f8a"}, color: WHITE,    bold: true, align: "center", valign: "middle", fontSize: 13 };

  function rc(text, bg, opts) {
    return { text, options: Object.assign({ fill: { color: bg || WHITE }, valign: "middle", fontSize: 13, color: DARK_TEXT, align: "center" }, opts || {}) };
  }
  const DASH = { text: "—", options: { fill: { color: LIGHT_GRAY }, color: MID_GRAY, align: "center", valign: "middle", fontSize: 13 } };

  const rows = [
    [ { text: "Situation", options: H }, { text: "CAN", options: HC }, { text: "COULD", options: HD } ],
    [ rc("Ability (present)", "e8edf5", { align: "left" }),
      rc('I can cook pasta.', GOLD_LIGHT, { italic: true }),
      DASH ],
    [ rc("Ability (past)", "e8edf5", { align: "left" }),
      DASH,
      rc('I could cook pasta as a kid.', GOLD_LIGHT, { italic: true }) ],
    [ rc("Permission (informal)", "e8edf5", { align: "left" }),
      rc('Can I leave early today?', GOLD_LIGHT, { italic: true }),
      DASH ],
    [ rc("Permission (polite)", "e8edf5", { align: "left" }),
      DASH,
      rc('Could I leave early today?', GOLD_LIGHT, { italic: true }) ],
    [ rc("Possibility", "e8edf5", { align: "left" }),
      rc('It can happen anytime.', GOLD_LIGHT, { italic: true }),
      rc('It could happen. (less certain)', GOLD_LIGHT, { italic: true }) ],
    [ rc("Conditional", "e8edf5", { align: "left" }),
      DASH,
      rc('If I had flour, I could make bread.', GOLD_LIGHT, { italic: true }) ],
  ];

  s.addTable(rows, {
    x: 0.2, y: 1.28, w: 9.6, h: 4.2,
    border: { pt: 1, color: "cccccc" },
    rowH: [0.42, 0.58, 0.58, 0.58, 0.58, 0.58, 0.58],
    colW: [2.5, 3.55, 3.55],
  });
}

// ── SLIDE 17 — CAN / COULD: Practice ─────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: OFF_WHITE };
  addTopBar(s, "Practice — CAN / COULD");
  addLeftAccent(s);

  s.addText("Fill in the blanks with CAN, CAN'T, COULD or COULD HAVE:", {
    x: 0.35, y: 1.3, w: 9.3, h: 0.35,
    fontSize: 16, fontFace: "Calibri", italic: true, color: MID_GRAY,
  });

  const items = [
    { q: '_______ you carry this box for me? It\'s too heavy.', a: 'Can / Could' },
    { q: 'She _______ run very fast when she was in high school.', a: 'could' },
    { q: 'You _______ smoke inside the pharmacy.', a: "can't / cannot" },
    { q: '_______ you have left your wallet at the supermarket?', a: 'Could' },
    { q: 'If we had more time, we _______ visit the whole market.', a: 'could' },
    { q: 'He _______ eat spicy food — it makes him feel sick.', a: "can't" },
  ];

  items.forEach((item, i) => {
    const y = 1.75 + i * 0.63;
    // number
    s.addShape("rect", { x: 0.22, y: y + 0.04, w: 0.38, h: 0.44,
      fill: { color: NAVY }, line: { color: NAVY, width: 0 } });
    s.addText(String(i + 1), {
      x: 0.22, y: y + 0.04, w: 0.38, h: 0.44,
      fontSize: 14, fontFace: "Georgia", bold: true,
      color: WHITE, align: "center", valign: "middle", margin: 0,
    });
    // question
    s.addText(item.q, {
      x: 0.7, y, w: 6.9, h: 0.52,
      fontSize: 15, fontFace: "Calibri", color: DARK_TEXT, valign: "middle",
    });
    // answer chip
    s.addShape("rect", { x: 7.7, y: y + 0.06, w: 2.0, h: 0.4,
      fill: { color: GOLD_LIGHT }, line: { color: GOLD, width: 1 } });
    s.addText(item.a, {
      x: 7.7, y: y + 0.06, w: 2.0, h: 0.4,
      fontSize: 13, fontFace: "Calibri", bold: true, color: NAVY,
      align: "center", valign: "middle", margin: 0,
    });
  });

  s.addText("(answers shown — cover before class)", {
    x: 0.35, y: 5.3, w: 9.3, h: 0.22,
    fontSize: 10, fontFace: "Calibri", italic: true, color: "aaaaaa", align: "right",
  });
}

// ── write file ────────────────────────────────────────────────────────────────
pres.writeFile({ fileName: "/Users/emadruga/proj/StudyAmigoApp/aula_verbos_modais/Aula1_Slides_07-17.pptx" })
  .then(() => console.log("✅ Saved: Aula1_Slides_07-17.pptx"))
  .catch(e => { console.error("❌ Error:", e); process.exit(1); });
