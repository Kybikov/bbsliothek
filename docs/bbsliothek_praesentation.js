const pptxgen = require("C:/Users/b.szovga/AppData/Roaming/npm/node_modules/pptxgenjs");

const pres = new pptxgen();
pres.layout = "LAYOUT_16x9";
pres.title = "BBSliothek – Lernmaterialverwaltung";

// ─── Palette ────────────────────────────────────────────────────────────────
const C = {
  black:   "111827",
  white:   "FFFFFF",
  blue:    "3B82F6",
  blueDk:  "1D4ED8",
  muted:   "6B7280",
  light:   "F9FAFB",
  card:    "F3F4F6",
  border:  "E5E7EB",
};

// ─── Helpers ────────────────────────────────────────────────────────────────
function darkSlide(slide) {
  slide.background = { color: C.black };
}
function lightSlide(slide) {
  slide.background = { color: C.white };
}

// Small blue accent bar before title (content slides)
function accentBar(slide, y = 0.52) {
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.55, y, w: 0.04, h: 0.35,
    fill: { color: C.blue }, line: { color: C.blue },
  });
}

// Section label top-left
function sectionLabel(slide, text) {
  slide.addText(text.toUpperCase(), {
    x: 0.55, y: 0.18, w: 9, h: 0.22,
    fontSize: 9, color: C.muted, charSpacing: 3,
    fontFace: "Calibri", margin: 0,
  });
}

// Slide title on content slides
function slideTitle(slide, text, y = 0.45) {
  accentBar(slide, y + 0.07);
  slide.addText(text, {
    x: 0.72, y, w: 8.8, h: 0.55,
    fontSize: 26, bold: true, color: C.black,
    fontFace: "Arial", margin: 0,
  });
}

// Speaker tag bottom-right
function speaker(slide, who) {
  slide.addText(who, {
    x: 7.5, y: 5.3, w: 2.2, h: 0.22,
    fontSize: 9, color: C.muted, align: "right",
    fontFace: "Calibri", margin: 0,
  });
}

// Pill / tag shape
function pill(slide, text, x, y, w = 1.6, h = 0.38) {
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x, y, w, h, rectRadius: 0.08,
    fill: { color: C.card }, line: { color: C.border, width: 0.5 },
  });
  slide.addText(text, {
    x, y, w, h,
    fontSize: 13, color: C.black, align: "center", valign: "middle",
    fontFace: "Calibri", margin: 0,
  });
}

// Flow arrow between boxes
function flowArrow(slide, x, y) {
  slide.addShape(pres.shapes.LINE, {
    x, y, w: 0, h: 0.3,
    line: { color: C.muted, width: 1.5 },
  });
  // arrowhead triangle (simple small shape)
  slide.addShape(pres.shapes.RECTANGLE, {
    x: x - 0.04, y: y + 0.28, w: 0.08, h: 0.06,
    fill: { color: C.muted }, line: { color: C.muted },
  });
}

// ─── SLIDE 1 — Titelfolie ──────────────────────────────────────────────────
{
  const s = pres.addSlide();
  darkSlide(s);

  s.addText("BBSliothek", {
    x: 0.7, y: 1.4, w: 8.6, h: 1.2,
    fontSize: 64, bold: true, color: C.white,
    fontFace: "Arial", margin: 0,
  });
  s.addText("Lernmaterialverwaltung für die BBS", {
    x: 0.7, y: 2.65, w: 8, h: 0.5,
    fontSize: 20, color: C.blue,
    fontFace: "Calibri", margin: 0,
  });
  s.addShape(pres.shapes.LINE, {
    x: 0.7, y: 3.28, w: 2.5, h: 0,
    line: { color: C.blue, width: 1.5 },
  });
  s.addText("Bogdan Szovga  ·  [Name Person 2]", {
    x: 0.7, y: 3.5, w: 8, h: 0.3,
    fontSize: 13, color: "9CA3AF",
    fontFace: "Calibri", margin: 0,
  });
  s.addText("bbsliothek.dev  ·  Juni 2025", {
    x: 0.7, y: 3.85, w: 8, h: 0.3,
    fontSize: 12, color: "6B7280",
    fontFace: "Calibri", margin: 0,
  });
}

// ─── SLIDE 2 — Warum BBSliothek? ──────────────────────────────────────────
{
  const s = pres.addSlide();
  lightSlide(s);
  sectionLabel(s, "Das Problem");
  slideTitle(s, "Warum BBSliothek?");
  speaker(s, "Person 1");

  const problems = [
    ["USB / E-Mail / Laufwerk",   "Materialien liegen überall verteilt — keine zentrale Ablage."],
    ["Keine Versionskontrolle",   "Wer hat was geändert? Welche Version ist aktuell?"],
    ["Kein Feedback-System",      "Schüler und Lehrer haben keine Möglichkeit, Materialien zu kommentieren."],
  ];

  problems.forEach(([title, desc], i) => {
    const y = 1.35 + i * 1.2;
    slide_addDot(s, y + 0.12);
    s.addText(title, {
      x: 0.92, y, w: 8.5, h: 0.36,
      fontSize: 16, bold: true, color: C.black,
      fontFace: "Arial", margin: 0,
    });
    s.addText(desc, {
      x: 0.92, y: y + 0.38, w: 8.5, h: 0.36,
      fontSize: 14, color: C.muted,
      fontFace: "Calibri", margin: 0,
    });
  });

  function slide_addDot(sl, y) {
    sl.addShape(pres.shapes.OVAL, {
      x: 0.6, y, w: 0.15, h: 0.15,
      fill: { color: C.blue }, line: { color: C.blue },
    });
  }
}

// ─── SLIDE 3 — Technologie-Stack ──────────────────────────────────────────
{
  const s = pres.addSlide();
  lightSlide(s);
  sectionLabel(s, "Technologie");
  slideTitle(s, "Womit haben wir es gebaut?");
  speaker(s, "Person 1");

  const techs = [
    { label: "Python",  sub: "Programmiersprache",  num: "01" },
    { label: "Flet",    sub: "GUI-Framework",        num: "02" },
    { label: "MySQL",   sub: "Datenbank",            num: "03" },
  ];

  techs.forEach(({ label, sub, num }, i) => {
    const x = 0.55 + i * 3.15;
    const y = 1.5;
    const w = 2.8;
    const h = 2.8;

    s.addShape(pres.shapes.RECTANGLE, {
      x, y, w, h,
      fill: { color: C.light }, line: { color: C.border, width: 0.5 },
    });
    s.addText(num, {
      x, y: y + 0.22, w, h: 0.4,
      fontSize: 11, color: C.blue, align: "center",
      fontFace: "Calibri", bold: true, margin: 0, charSpacing: 2,
    });
    s.addText(label, {
      x, y: y + 0.9, w, h: 0.7,
      fontSize: 28, bold: true, color: C.black, align: "center",
      fontFace: "Arial", margin: 0,
    });
    s.addText(sub, {
      x, y: y + 1.7, w, h: 0.4,
      fontSize: 13, color: C.muted, align: "center",
      fontFace: "Calibri", margin: 0,
    });
  });
}

// ─── SLIDE 4 — Warum Flet? ────────────────────────────────────────────────
{
  const s = pres.addSlide();
  lightSlide(s);
  sectionLabel(s, "Framework");
  slideTitle(s, "Warum Flet?");
  speaker(s, "Person 1");

  // Big statement
  s.addText("1 Code  →  Desktop + Web + Mobile", {
    x: 0.55, y: 1.25, w: 9, h: 0.65,
    fontSize: 22, bold: true, color: C.blue,
    fontFace: "Arial", margin: 0,
  });

  const points = [
    "Windows / Mac / Linux Desktop-App",
    "Webbrowser – auch vom Handy erreichbar",
    "Alles in Python – keine neue Sprache lernen",
    "Material Design – modernes, sauberes Aussehen",
    "Universell: eine Plattform für jeden Anwendungsfall",
  ];

  points.forEach((pt, i) => {
    const y = 2.15 + i * 0.58;
    s.addShape(pres.shapes.RECTANGLE, {
      x: 0.55, y: y + 0.08, w: 0.22, h: 0.22,
      fill: { color: C.blue }, line: { color: C.blue },
    });
    s.addText(pt, {
      x: 0.9, y, w: 8.5, h: 0.4,
      fontSize: 14, color: C.black,
      fontFace: "Calibri", margin: 0,
    });
  });
}

// ─── SLIDE 5 — Datenbankstruktur ──────────────────────────────────────────
{
  const s = pres.addSlide();
  lightSlide(s);
  sectionLabel(s, "Datenbank");
  slideTitle(s, "Datenbankstruktur – 6 Tabellen");
  speaker(s, "Person 2");

  // 6 pills in 2 rows
  const tables = [
    "benutzer", "rollen", "materialien",
    "material_versionen", "themengebiete", "kommentare",
  ];
  tables.forEach((t, i) => {
    const col = i % 3;
    const row = Math.floor(i / 3);
    pill(s, t, 0.55 + col * 3.1, 1.55 + row * 0.7, 2.7, 0.48);
  });

  // Key facts
  const facts = [
    "Dateien < 1 MB → BLOB direkt in der Datenbank",
    "Dateien ≥ 1 MB → Dateisystem, nur Pfad in DB gespeichert",
    "Versionierung: jede neue Datei = neuer Versionseintrag",
  ];
  facts.forEach((f, i) => {
    s.addShape(pres.shapes.LINE, {
      x: 0.55, y: 3.1 + i * 0.55, w: 8.9, h: 0,
      line: { color: C.border, width: 0.5 },
    });
    s.addText(f, {
      x: 0.55, y: 3.18 + i * 0.55, w: 8.9, h: 0.38,
      fontSize: 13, color: C.muted,
      fontFace: "Calibri", margin: 0,
    });
  });
}

// ─── SLIDE 6 — Systemarchitektur ──────────────────────────────────────────
{
  const s = pres.addSlide();
  lightSlide(s);
  sectionLabel(s, "Architektur");
  slideTitle(s, "Systemarchitektur");
  speaker(s, "Person 2");

  // Left column: flow
  const boxes = [
    { label: "Benutzer",      x: 1.4, y: 1.3,  w: 2.2, h: 0.5, dark: false },
    { label: "Flet GUI",      x: 0.55, y: 2.1, w: 1.8, h: 0.5, dark: true  },
    { label: "Konsole",       x: 2.6, y: 2.1,  w: 1.8, h: 0.5, dark: false },
    { label: "datenbank.py",  x: 1.2, y: 3.0,  w: 2.6, h: 0.5, dark: false },
    { label: "MySQL Server",  x: 1.4, y: 3.9,  w: 2.2, h: 0.5, dark: false },
  ];

  boxes.forEach(({ label, x, y, w, h, dark }) => {
    s.addShape(pres.shapes.RECTANGLE, {
      x, y, w, h,
      fill: { color: dark ? C.blue : C.card },
      line: { color: dark ? C.blue : C.border, width: 0.8 },
    });
    s.addText(label, {
      x, y, w, h,
      fontSize: 13, bold: dark, color: dark ? C.white : C.black,
      align: "center", valign: "middle",
      fontFace: dark ? "Arial" : "Calibri", margin: 0,
    });
  });

  // Arrows
  const arrows = [
    { x: 2.4, y: 1.82 },
    { x: 1.35, y: 2.63 },
    { x: 3.4, y: 2.63 },
    { x: 2.4, y: 3.52 },
  ];
  arrows.forEach(({ x, y }) => {
    s.addShape(pres.shapes.LINE, {
      x, y, w: 0, h: 0.25,
      line: { color: C.muted, width: 1.2 },
    });
  });

  // Horizontal arrow between GUI and Konsole
  s.addShape(pres.shapes.LINE, {
    x: 2.35, y: 2.35, w: 0.25, h: 0,
    line: { color: C.muted, width: 1.2 },
  });

  // Right column: description
  const desc = [
    ["main.py", "Grafische Oberfläche mit Flet"],
    ["konsole.py", "Konsolen-Interface (Terminal)"],
    ["datenbank.py", "Datenbanklogik – von beiden genutzt"],
    ["MySQL", "Daten werden auf dem Linux-Server gespeichert"],
  ];
  desc.forEach(([title, text], i) => {
    const y = 1.55 + i * 0.92;
    s.addText(title, {
      x: 5.3, y, w: 4.2, h: 0.32,
      fontSize: 13, bold: true, color: C.black,
      fontFace: "Calibri", margin: 0,
    });
    s.addText(text, {
      x: 5.3, y: y + 0.32, w: 4.2, h: 0.32,
      fontSize: 12, color: C.muted,
      fontFace: "Calibri", margin: 0,
    });
  });

  // Divider
  s.addShape(pres.shapes.LINE, {
    x: 5.1, y: 1.3, w: 0, h: 3.5,
    line: { color: C.border, width: 0.5 },
  });
}

// ─── SLIDE 7 — Login ──────────────────────────────────────────────────────
{
  const s = pres.addSlide();
  lightSlide(s);
  sectionLabel(s, "Funktionen");
  slideTitle(s, "Login & Benutzerverwaltung");
  speaker(s, "Person 2");

  const items = [
    ["Anmeldung",         "Benutzername + Passwort, Enter-Taste löst Login aus"],
    ["Fehlermeldung",     "Bei falschen Daten erscheint eine klare Rückmeldung"],
    ["Zwei Rollen",       "Lehrkraft und Auszubildende – unterschiedliche Rechte"],
    ["Username-Schema",   "Automatisch generiert: m.hoffmann für Mia Hoffmann"],
  ];

  items.forEach(([title, desc], i) => {
    const y = 1.4 + i * 0.98;
    s.addShape(pres.shapes.RECTANGLE, {
      x: 0.55, y, w: 8.9, h: 0.76,
      fill: { color: C.light }, line: { color: C.border, width: 0.5 },
    });
    s.addText(title, {
      x: 0.8, y: y + 0.1, w: 2.5, h: 0.28,
      fontSize: 13, bold: true, color: C.blue,
      fontFace: "Calibri", margin: 0,
    });
    s.addText(desc, {
      x: 0.8, y: y + 0.38, w: 8.3, h: 0.28,
      fontSize: 13, color: C.black,
      fontFace: "Calibri", margin: 0,
    });
  });
}

// ─── SLIDE 8 — Materialien & Suche ────────────────────────────────────────
{
  const s = pres.addSlide();
  lightSlide(s);
  sectionLabel(s, "Funktionen");
  slideTitle(s, "Materialien & Suche");
  speaker(s, "Person 1");

  // Table header mockup
  const cols = ["ID", "Titel", "Typ", "Thema", "Autor", "Ver.", "Größe", "Aktionen"];
  const colW = [0.4, 1.8, 0.6, 1.4, 1.2, 0.4, 0.7, 1.2];
  let cx = 0.55;
  cols.forEach((col, i) => {
    s.addShape(pres.shapes.RECTANGLE, {
      x: cx, y: 1.3, w: colW[i], h: 0.35,
      fill: { color: C.card }, line: { color: C.border, width: 0.5 },
    });
    s.addText(col, {
      x: cx, y: 1.3, w: colW[i], h: 0.35,
      fontSize: 10, bold: true, color: C.muted,
      align: "center", valign: "middle",
      fontFace: "Calibri", margin: 0,
    });
    cx += colW[i];
  });

  // 2 sample rows
  const rows = [
    ["1", "Python Grundlagen", ".pdf", "Informatik", "M. Hoffmann", "2", "342 KB", "↓  ↑  ✕"],
    ["2", "SQL Übungen",       ".docx","Informatik", "J. Becker",   "1", "85 KB",  "↓  ↑  ✕"],
  ];
  rows.forEach((row, ri) => {
    cx = 0.55;
    row.forEach((cell, ci) => {
      s.addShape(pres.shapes.RECTANGLE, {
        x: cx, y: 1.65 + ri * 0.38, w: colW[ci], h: 0.38,
        fill: { color: ri % 2 === 0 ? C.white : C.light },
        line: { color: C.border, width: 0.5 },
      });
      s.addText(cell, {
        x: cx, y: 1.65 + ri * 0.38, w: colW[ci], h: 0.38,
        fontSize: 10, color: C.black,
        align: "center", valign: "middle",
        fontFace: "Calibri", margin: 0,
      });
      cx += colW[ci];
    });
  });

  // Features below
  const features = [
    "Filter nach Titel, Dateityp und Autor",
    "Aktionen pro Material: Herunterladen · Neue Version · Löschen",
    "Zeigt Versionsnummer und Dateigröße direkt in der Tabelle",
  ];
  features.forEach((f, i) => {
    s.addShape(pres.shapes.OVAL, {
      x: 0.6, y: 2.7 + i * 0.65 + 0.1, w: 0.14, h: 0.14,
      fill: { color: C.blue }, line: { color: C.blue },
    });
    s.addText(f, {
      x: 0.88, y: 2.7 + i * 0.65, w: 8.6, h: 0.42,
      fontSize: 13, color: C.black,
      fontFace: "Calibri", margin: 0,
    });
  });
}

// ─── SLIDE 9 — Upload & Versionierung ────────────────────────────────────
{
  const s = pres.addSlide();
  lightSlide(s);
  sectionLabel(s, "Funktionen");
  slideTitle(s, "Upload & Versionierung");
  speaker(s, "Person 1");

  // Versioning flow
  const versions = ["V 1", "V 2", "V 3"];
  versions.forEach((v, i) => {
    const x = 1.0 + i * 2.8;
    s.addShape(pres.shapes.RECTANGLE, {
      x, y: 1.55, w: 1.8, h: 0.9,
      fill: { color: i === 2 ? C.blue : C.card },
      line: { color: i === 2 ? C.blue : C.border, width: 0.8 },
    });
    s.addText(v, {
      x, y: 1.55, w: 1.8, h: 0.9,
      fontSize: 22, bold: true,
      color: i === 2 ? C.white : C.black,
      align: "center", valign: "middle",
      fontFace: "Arial", margin: 0,
    });
    if (i < 2) {
      s.addShape(pres.shapes.LINE, {
        x: x + 1.8, y: 2.0, w: 1.0, h: 0,
        line: { color: C.muted, width: 1.5 },
      });
    }
  });

  s.addText("gleiche Material-ID · neue Versionsnummer · alte Version bleibt erhalten", {
    x: 0.55, y: 2.6, w: 9, h: 0.4,
    fontSize: 12, color: C.muted, align: "center",
    fontFace: "Calibri", margin: 0,
  });

  // Speicherstrategie
  s.addShape(pres.shapes.LINE, {
    x: 0.55, y: 3.2, w: 8.9, h: 0,
    line: { color: C.border, width: 0.5 },
  });

  const strategy = [
    ["< 1 MB",  "Als BLOB direkt in der Datenbank gespeichert"],
    ["≥ 1 MB",  "Im Dateisystem gespeichert, nur Pfad in der DB"],
  ];
  strategy.forEach(([size, desc], i) => {
    const x = 0.55 + i * 4.6;
    s.addShape(pres.shapes.RECTANGLE, {
      x, y: 3.45, w: 4.2, h: 1.6,
      fill: { color: C.light }, line: { color: C.border, width: 0.5 },
    });
    s.addText(size, {
      x, y: 3.6, w: 4.2, h: 0.45,
      fontSize: 20, bold: true, color: C.blue, align: "center",
      fontFace: "Arial", margin: 0,
    });
    s.addText(desc, {
      x, y: 4.1, w: 4.2, h: 0.5,
      fontSize: 12, color: C.muted, align: "center",
      fontFace: "Calibri", margin: 0,
    });
  });
}

// ─── SLIDE 10 — Kommentare ────────────────────────────────────────────────
{
  const s = pres.addSlide();
  lightSlide(s);
  sectionLabel(s, "Funktionen");
  slideTitle(s, "Kommentare");
  speaker(s, "Person 2");

  const features = [
    ["Material auswählen",    "Dropdown mit allen verfügbaren Materialien"],
    ["Kommentare anzeigen",   "Mit Autor, Datum und vollständigem Text"],
    ["Neuen Kommentar",       "Freitextfeld, mehrzeilig, direkt abschicken"],
    ["Bearbeiten & Löschen",  "Kommentare können nachträglich geändert werden"],
  ];

  features.forEach(([title, desc], i) => {
    const col = i % 2;
    const row = Math.floor(i / 2);
    const x = 0.55 + col * 4.7;
    const y = 1.4 + row * 1.75;
    s.addShape(pres.shapes.RECTANGLE, {
      x, y, w: 4.3, h: 1.5,
      fill: { color: C.light }, line: { color: C.border, width: 0.5 },
    });
    s.addShape(pres.shapes.RECTANGLE, {
      x, y, w: 0.06, h: 1.5,
      fill: { color: C.blue }, line: { color: C.blue },
    });
    s.addText(title, {
      x: x + 0.22, y: y + 0.22, w: 3.9, h: 0.38,
      fontSize: 14, bold: true, color: C.black,
      fontFace: "Arial", margin: 0,
    });
    s.addText(desc, {
      x: x + 0.22, y: y + 0.65, w: 3.9, h: 0.55,
      fontSize: 12, color: C.muted,
      fontFace: "Calibri", margin: 0,
    });
  });
}

// ─── SLIDE 11 — Standardabfragen ─────────────────────────────────────────
{
  const s = pres.addSlide();
  lightSlide(s);
  sectionLabel(s, "SQL / Datenbank");
  slideTitle(s, "Standardabfragen");
  speaker(s, "Person 2");

  const queries = [
    "Anzahl Materialien pro Themengebiet",
    "Durchschnittliche Dateigröße je Thema",
    "Materialien mit Autoren (Inner Join)",
    "Kommentare mit Material und Autor",
    "Materialien pro Autor mit Rolle",
    "Materialien mit Thema und Version (2× Join)",
    "Vollständige Übersicht (mehrere Joins)",
  ];

  queries.forEach((q, i) => {
    const y = 1.35 + i * 0.54;
    s.addText(String(i + 1).padStart(2, "0"), {
      x: 0.55, y, w: 0.5, h: 0.38,
      fontSize: 13, bold: true, color: C.blue,
      fontFace: "Calibri", margin: 0,
    });
    s.addText(q, {
      x: 1.1, y, w: 8.3, h: 0.38,
      fontSize: 13, color: C.black,
      fontFace: "Calibri", margin: 0,
    });
    if (i < queries.length - 1) {
      s.addShape(pres.shapes.LINE, {
        x: 0.55, y: y + 0.4, w: 8.9, h: 0,
        line: { color: C.border, width: 0.5 },
      });
    }
  });
}

// ─── SLIDE 12 — Konsolen-Interface ───────────────────────────────────────
{
  const s = pres.addSlide();
  lightSlide(s);
  sectionLabel(s, "Interface");
  slideTitle(s, "Konsolen-Interface");
  speaker(s, "Person 1");

  // Terminal mockup
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.55, y: 1.3, w: 5.5, h: 3.9,
    fill: { color: "1E1E1E" }, line: { color: "333333", width: 0.5 },
  });
  // Terminal title bar
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.55, y: 1.3, w: 5.5, h: 0.35,
    fill: { color: "2D2D2D" }, line: { color: "333333", width: 0.5 },
  });
  s.addText("BBSliothek – Terminal", {
    x: 0.55, y: 1.3, w: 5.5, h: 0.35,
    fontSize: 10, color: "9CA3AF", align: "center", valign: "middle",
    fontFace: "Consolas", margin: 0,
  });

  const lines = [
    "  BBSliothek - Lernmaterialverwaltung",
    "--------------------------------------------------",
    "BBSliothek - Anmelden",
    "Benutzername: m.hoffmann",
    "Passwort: ********",
    "Angemeldet als: Mia Hoffmann (Lehrkraft)",
    "--------------------------------------------------",
    "BBSliothek - Hauptmenü",
    "Moin Chef Mia!",
    "1. Materialien",
    "2. Themengebiete",
    "3. Benutzer",
    "4. Kommentare",
    "5. Beenden",
  ];

  lines.forEach((line, i) => {
    s.addText(line, {
      x: 0.65, y: 1.72 + i * 0.22, w: 5.3, h: 0.22,
      fontSize: 9, color: i < 2 ? "6EE7B7" : "D1D5DB",
      fontFace: "Consolas", margin: 0,
    });
  });

  // Right side: explanation
  const points = [
    "Vollständige Alternative zur GUI",
    "Login mit 3 Versuchen",
    "Materialien: Upload, Download, Löschen",
    "Themen, Benutzer, Kommentare",
    "Nutzt exakt dieselbe datenbank.py",
  ];
  points.forEach((p, i) => {
    s.addShape(pres.shapes.RECTANGLE, {
      x: 6.4, y: 1.55 + i * 0.7 + 0.1, w: 0.2, h: 0.2,
      fill: { color: C.blue }, line: { color: C.blue },
    });
    s.addText(p, {
      x: 6.75, y: 1.55 + i * 0.7, w: 3.0, h: 0.42,
      fontSize: 13, color: C.black,
      fontFace: "Calibri", margin: 0,
    });
  });
}

// ─── SLIDE 13 — Deployment ───────────────────────────────────────────────
{
  const s = pres.addSlide();
  lightSlide(s);
  sectionLabel(s, "Deployment");
  slideTitle(s, "Linux-Server & .dev-Domain");
  speaker(s, "Person 2");

  // Flow diagram
  const flow = [
    { label: "Internet",         sub: "Öffentlich erreichbar" },
    { label: "bbsliothek.dev",   sub: ".dev-Domain (HTTPS)" },
    { label: "Linux-Server",     sub: "Port 3000" },
    { label: "Flet Web-App",     sub: "python main.py --web" },
    { label: "MySQL Datenbank",  sub: "Lokal auf dem Server" },
  ];

  flow.forEach(({ label, sub }, i) => {
    const y = 1.25 + i * 0.8;
    const isAccent = i === 1;
    s.addShape(pres.shapes.RECTANGLE, {
      x: 0.8, y, w: 4.2, h: 0.58,
      fill: { color: isAccent ? C.blue : C.card },
      line: { color: isAccent ? C.blue : C.border, width: 0.8 },
    });
    s.addText(label, {
      x: 0.8, y, w: 4.2, h: 0.58,
      fontSize: 15, bold: true,
      color: isAccent ? C.white : C.black,
      align: "center", valign: "middle",
      fontFace: "Arial", margin: 0,
    });
    s.addText(sub, {
      x: 5.2, y: y + 0.12, w: 4.3, h: 0.35,
      fontSize: 12, color: C.muted,
      fontFace: "Calibri", margin: 0,
    });
    if (i < flow.length - 1) {
      s.addShape(pres.shapes.LINE, {
        x: 1.8, y: y + 0.58, w: 0, h: 0.22,
        line: { color: C.muted, width: 1.2 },
      });
    }
  });
}

// ─── SLIDE 14 — Live-Demo ────────────────────────────────────────────────
{
  const s = pres.addSlide();
  darkSlide(s);

  s.addText("Live-Demo", {
    x: 0.7, y: 0.9, w: 8.6, h: 0.55,
    fontSize: 14, color: C.blue, charSpacing: 4,
    fontFace: "Calibri", margin: 0,
  });
  s.addText("bbsliothek.dev", {
    x: 0.7, y: 1.55, w: 8.6, h: 1.4,
    fontSize: 58, bold: true, color: C.white,
    fontFace: "Arial", margin: 0,
  });
  s.addShape(pres.shapes.LINE, {
    x: 0.7, y: 3.1, w: 3.0, h: 0,
    line: { color: C.blue, width: 1.5 },
  });
  s.addText("Login:  m.hoffmann  /  lehrer123", {
    x: 0.7, y: 3.3, w: 8.6, h: 0.4,
    fontSize: 14, color: "9CA3AF",
    fontFace: "Calibri", margin: 0,
  });
  s.addText("Jetzt im Browser öffnen →", {
    x: 0.7, y: 3.85, w: 8.6, h: 0.38,
    fontSize: 13, color: C.blue,
    fontFace: "Calibri", margin: 0,
  });
}

// ─── SLIDE 15 — Was haben wir gelernt? ───────────────────────────────────
{
  const s = pres.addSlide();
  lightSlide(s);
  sectionLabel(s, "Fazit");
  slideTitle(s, "Was haben wir gelernt?");
  speaker(s, "Beide");

  const learned = [
    ["Python + MySQL",      "Datenbankanbindung, Abfragen, Transaktionen"],
    ["Flet GUI",            "Ereignisgesteuerte Desktop- und Web-Entwicklung"],
    ["Datenbankdesign",     "ERD, Normalisierung, Views, Indizes"],
    ["SQL",                 "JOINs, Aggregationen, parametrisierte Abfragen"],
    ["Linux & Deployment",  "Server-Setup, Domain, Web-Modus"],
    ["Git",                 "Versionsverwaltung im Team"],
  ];

  const cols = 2;
  learned.forEach(([title, desc], i) => {
    const col = i % cols;
    const row = Math.floor(i / cols);
    const x = 0.55 + col * 4.7;
    const y = 1.4 + row * 1.2;
    s.addText(title, {
      x: x + 0.2, y, w: 4.2, h: 0.38,
      fontSize: 14, bold: true, color: C.black,
      fontFace: "Arial", margin: 0,
    });
    s.addText(desc, {
      x: x + 0.2, y: y + 0.38, w: 4.2, h: 0.4,
      fontSize: 12, color: C.muted,
      fontFace: "Calibri", margin: 0,
    });
    s.addShape(pres.shapes.RECTANGLE, {
      x, y, w: 0.06, h: 0.78,
      fill: { color: C.blue }, line: { color: C.blue },
    });
  });
}

// ─── SLIDE 16 — Danke ────────────────────────────────────────────────────
{
  const s = pres.addSlide();
  darkSlide(s);

  s.addText("Danke für Ihre Aufmerksamkeit.", {
    x: 0.7, y: 1.3, w: 8.6, h: 1.1,
    fontSize: 40, bold: true, color: C.white,
    fontFace: "Arial", margin: 0,
  });
  s.addShape(pres.shapes.LINE, {
    x: 0.7, y: 2.55, w: 3.0, h: 0,
    line: { color: C.blue, width: 1.5 },
  });
  s.addText("Haben Sie Fragen?", {
    x: 0.7, y: 2.75, w: 8.6, h: 0.5,
    fontSize: 18, color: "9CA3AF",
    fontFace: "Calibri", margin: 0,
  });
  s.addText("bbsliothek.dev", {
    x: 0.7, y: 3.5, w: 8.6, h: 0.45,
    fontSize: 16, color: C.blue,
    fontFace: "Calibri", margin: 0,
  });
  s.addText("Bogdan Szovga  ·  [Name Person 2]", {
    x: 0.7, y: 4.1, w: 8.6, h: 0.35,
    fontSize: 12, color: "6B7280",
    fontFace: "Calibri", margin: 0,
  });
}

// ─── Export ──────────────────────────────────────────────────────────────
pres.writeFile({ fileName: "C:\\Users\\b.szovga\\PycharmProjects\\bbsliothek\\docs\\bbsliothek.pptx" })
  .then(() => console.log("bbsliothek.pptx created"))
  .catch(e => console.error(e));
