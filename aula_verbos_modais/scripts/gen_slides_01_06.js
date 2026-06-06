const PptxGenJS = require("pptxgenjs");

// ── Palette: Navy + Gold ──────────────────────────────────────────────────────
const NAVY       = "1b2a4a";  // primary dark
const NAVY_MID   = "243560";  // slightly lighter navy for blending
const GOLD       = "c9a84c";  // accent gold
const GOLD_LIGHT = "f0dfa0";  // pale gold for table cells
const GOLD_DIM   = "a07828";  // darker gold for subtle accents
const WHITE      = "FFFFFF";
const OFF_WHITE  = "fafaf7";
const DARK_TEXT  = "1a1a2e";
const MID_GRAY   = "555566";
const LIGHT_GRAY = "eeeeee";

const pres = new PptxGenJS();
pres.layout = "LAYOUT_16x9"; // 10" × 5.625"

// ── helpers ───────────────────────────────────────────────────────────────────

// Top bar with title baked in. titleText is rendered white inside the bar.
function addTopBar(slide, titleText) {
  // Main navy bar — taller to fit the title
  slide.addShape("rect", { x: 0, y: 0, w: 10, h: 1.15,
    fill: { color: NAVY }, line: { color: NAVY, width: 0 } });
  // Gold accent stripe on the right edge
  slide.addShape("rect", { x: 9.65, y: 0, w: 0.35, h: 1.15,
    fill: { color: GOLD }, line: { color: GOLD, width: 0 } });
  // Gold bottom border line
  slide.addShape("rect", { x: 0, y: 1.11, w: 10, h: 0.05,
    fill: { color: GOLD }, line: { color: GOLD, width: 0 } });
  // Title text inside the bar
  if (titleText) {
    slide.addText(titleText, {
      x: 0.3, y: 0, w: 9.3, h: 1.11,
      fontSize: 28, fontFace: "Georgia", bold: true,
      color: GOLD_LIGHT, align: "left", valign: "middle", margin: 0,
    });
  }
}

// Gold left-side accent stripe for body slides (visual motif)
function addLeftAccent(slide) {
  slide.addShape("rect", { x: 0, y: 1.16, w: 0.12, h: 4.45,
    fill: { color: GOLD }, line: { color: GOLD, width: 0 } });
}

// ── SLIDE 1 — Cover ───────────────────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: NAVY };

  // Subtle lighter navy panel on right side (depth)
  s.addShape("rect", { x: 5.5, y: 0, w: 4.5, h: 5.625,
    fill: { color: NAVY_MID }, line: { color: NAVY_MID, width: 0 } });

  // Gold horizontal accent bar in the middle
  s.addShape("rect", { x: 0, y: 2.55, w: 10, h: 0.08,
    fill: { color: GOLD }, line: { color: GOLD, width: 0 } });

  // Decorative gold rectangle — left side vertical bar
  s.addShape("rect", { x: 0.55, y: 1.1, w: 0.18, h: 3.4,
    fill: { color: GOLD }, line: { color: GOLD, width: 0 } });

  // Subtle large circle ornament (top-right, dimmed)
  s.addShape("ellipse", { x: 7.2, y: -1.0, w: 3.5, h: 3.5,
    fill: { color: GOLD, transparency: 88 }, line: { color: GOLD, width: 0 } });
  s.addShape("ellipse", { x: 7.8, y: -0.4, w: 2.2, h: 2.2,
    fill: { color: GOLD, transparency: 82 }, line: { color: GOLD, width: 0 } });

  // Bottom-left small circle
  s.addShape("ellipse", { x: 0.2, y: 4.5, w: 1.0, h: 1.0,
    fill: { color: GOLD, transparency: 85 }, line: { color: GOLD, width: 0 } });

  // Title
  s.addText("Modal Verbs — Part 1", {
    x: 0.9, y: 1.15, w: 8.5, h: 1.1,
    fontSize: 44, fontFace: "Georgia", bold: true,
    color: WHITE, align: "left",
  });

  // Gold subtitle line
  s.addText("Ability, Permission & Possibility", {
    x: 0.9, y: 2.7, w: 8.5, h: 0.7,
    fontSize: 24, fontFace: "Calibri", italic: true,
    color: GOLD_LIGHT, align: "left",
  });

  // Footer
  s.addText("Prof. Ewerton Madruga  |  Curso Técnico em Segurança Cibernética", {
    x: 0.9, y: 4.95, w: 9, h: 0.35,
    fontSize: 13, fontFace: "Calibri",
    color: "aabbcc", align: "left",
  });
}

// ── SLIDE 2 — Objectives ──────────────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: OFF_WHITE };
  addTopBar(s, "What will we learn today?");
  addLeftAccent(s);

  const items = [
    "Review: the 12 verb tenses",
    "Review: irregular verbs",
    "What are modal verbs?",
    "Modal verbs: CAN, COULD, MAY, MIGHT",
    "Practice exercises",
  ];
  s.addText(
    items.map((t, i) => ({ text: t, options: { bullet: true, breakLine: i < items.length - 1 } })),
    { x: 0.55, y: 1.3, w: 9.0, h: 4.1,
      fontSize: 20, fontFace: "Calibri", color: DARK_TEXT,
      paraSpaceAfter: 8 }
  );
}

// ── SLIDE 3 — The 12 Verb Tenses ─────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: OFF_WHITE };
  addTopBar(s, "The 12 Verb Tenses");
  addLeftAccent(s);

  // Column header colors (navy for col labels, tinted for time cols)
  const H   = { fill: { color: NAVY     }, color: WHITE,    bold: true, align: "center", valign: "middle", fontSize: 12 };
  const RL  = { fill: { color: "2d3f6a" }, color: WHITE,    bold: true, align: "center", valign: "middle", fontSize: 11 };
  const PAST_BG = "d8cce8";   // muted lavender — past
  const PRES_BG = "cce0f0";   // muted sky blue — present
  const FUT_BG  = GOLD_LIGHT; // pale gold — future

  function cell(text, formula, bg) {
    return {
      text: [
        { text: text,    options: { italic: true, fontSize: 10, breakLine: true } },
        { text: formula, options: { fontSize: 9,  color: "444455" } },
      ],
      options: { fill: { color: bg }, align: "center", valign: "middle" },
    };
  }

  const rows = [
    [ { text: "", options: H }, { text: "Past", options: H }, { text: "Present", options: H }, { text: "Future", options: H } ],
    [ { text: "Simple", options: RL },
      cell("I ate pizza yesterday.", "S + V₂", PAST_BG),
      cell("I eat pizza every day.", "S + V₁", PRES_BG),
      cell("I will eat pizza tomorrow.", "S + will + V", FUT_BG) ],
    [ { text: "Continuous", options: RL },
      cell("I was eating pizza when you arrived.", "S + was/were + V-ing", PAST_BG),
      cell("I am eating pizza right now.", "S + am/is/are + V-ing", PRES_BG),
      cell("I will be eating when you arrive.", "S + will be + V-ing", FUT_BG) ],
    [ { text: "Perfect", options: RL },
      cell("I had eaten all the pizza when you arrived.", "S + had + V₃", PAST_BG),
      cell("I have eaten all the pizza.", "S + have/has + V₃", PRES_BG),
      cell("I will have eaten all the pizza by then.", "S + will have + V₃", FUT_BG) ],
    [ { text: "Perfect\nContinuous", options: Object.assign({}, RL, { fontSize: 10 }) },
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

  s.addText("S = Subject   V = Verb   (V₁ = infinitive / V₂ = simple past / V₃ = past participle)", {
    x: 0.18, y: 5.32, w: 9.64, h: 0.22,
    fontSize: 10, fontFace: "Calibri", color: MID_GRAY, align: "center",
  });
}

// ── SLIDE 4 — Irregular Verbs: What Are They? ────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: OFF_WHITE };
  addTopBar(s, "Irregular Verbs");
  addLeftAccent(s);

  s.addText([
    { text: "Regular verbs", options: { bold: true, breakLine: false } },
    { text: " form the past and past participle by adding ", options: {} },
    { text: "-ed / -d", options: { bold: true, breakLine: true } },
    { text: "    – play → played → played", options: { italic: true, color: MID_GRAY, breakLine: true } },
    { text: "    – live → lived → lived",  options: { italic: true, color: MID_GRAY, breakLine: true } },
    { text: "\n", options: { fontSize: 5, breakLine: true } },
    { text: "Irregular verbs", options: { bold: true, breakLine: false } },
    { text: " have their own unique forms — must be memorized", options: { breakLine: true } },
    { text: "    – write → wrote → written", options: { italic: true, color: MID_GRAY, breakLine: true } },
    { text: "    – take → took → taken",    options: { italic: true, color: MID_GRAY, breakLine: true } },
    { text: "\n", options: { fontSize: 5, breakLine: true } },
    { text: "Three forms: ", options: { breakLine: false } },
    { text: "V₁", options: { bold: true, color: GOLD_DIM, breakLine: false } },
    { text: " (infinitive)   |   ", options: { breakLine: false } },
    { text: "V₂", options: { bold: true, color: GOLD_DIM, breakLine: false } },
    { text: " (simple past)   |   ", options: { breakLine: false } },
    { text: "V₃", options: { bold: true, color: GOLD_DIM, breakLine: false } },
    { text: " (past participle)", options: {} },
  ], {
    x: 0.45, y: 1.25, w: 9.1, h: 4.2,
    fontSize: 19, fontFace: "Calibri", color: DARK_TEXT,
    valign: "top",
  });
}

// ── SLIDE 5 — Irregular Verbs Table ──────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: OFF_WHITE };
  addTopBar(s, "Irregular Verbs — Examples");
  addLeftAccent(s);

  const H = { fill: { color: NAVY }, color: WHITE, bold: true, align: "center", valign: "middle", fontSize: 13 };
  function dr(inf, sp, sps, pp, even) {
    const base = even ? LIGHT_GRAY : WHITE;
    const cell = (t, bg) => ({ text: t, options: { fill: { color: bg }, align: "center", valign: "middle", fontSize: 13, color: DARK_TEXT } });
    return [cell(inf, base), cell(sp, base), cell(sps, base), cell(pp, GOLD_LIGHT)];
  }

  const rows = [
    [
      { text: "Infinitive",      options: H },
      { text: "Simple Present",  options: H },
      { text: "Simple Past",     options: H },
      { text: "Past Participle", options: Object.assign({}, H, { fill: { color: GOLD_DIM } }) },
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

// ── SLIDE 6 — Irregular Verbs Quick Practice ─────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: OFF_WHITE };
  addTopBar(s, "Irregular Verbs — Quick Check");
  addLeftAccent(s);

  s.addText("Complete the table with the correct verb forms:", {
    x: 0.45, y: 1.28, w: 9.1, h: 0.35,
    fontSize: 17, fontFace: "Calibri", italic: true, color: MID_GRAY,
  });

  const H = { fill: { color: NAVY }, color: WHITE, bold: true, align: "center", valign: "middle", fontSize: 16 };
  const blank = { text: "___________", options: { align: "center", valign: "middle", fontSize: 16, color: "aaaaaa" } };
  const verb  = (v) => ({ text: v, options: { fill: { color: WHITE }, align: "center", valign: "middle", fontSize: 16, color: DARK_TEXT } });
  const blankCell = { text: "___________", options: { fill: { color: GOLD_LIGHT }, align: "center", valign: "middle", fontSize: 16, color: "999977" } };

  const rows = [
    [ { text: "Infinitive", options: H }, { text: "Simple Past", options: Object.assign({}, H, { fill: { color: GOLD_DIM } }) }, { text: "Past Participle", options: Object.assign({}, H, { fill: { color: GOLD_DIM } }) } ],
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

  s.addText("Answers: went / gone   |   ate / eaten   |   ran / run   |   bought / bought   |   felt / felt", {
    x: 0.5, y: 5.15, w: 9, h: 0.3,
    fontSize: 13, fontFace: "Calibri", italic: true, color: "999999", align: "center",
  });
}

// ── write file ────────────────────────────────────────────────────────────────
pres.writeFile({ fileName: "/Users/emadruga/proj/StudyAmigoApp/aula_verbos_modais/Aula1_Slides_01-06.pptx" })
  .then(() => console.log("✅ Saved: Aula1_Slides_01-06.pptx"))
  .catch(e => { console.error("❌ Error:", e); process.exit(1); });
