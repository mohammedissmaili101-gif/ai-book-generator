#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════╗
║   📚 PROFESSIONAL BOOK GENERATOR  v7.0                  ║
║   ✅ Crystal typography — zero eye strain                ║
║   ✅ Luxury spacious layout — pages breathe              ║
║   ✅ Colorful themed pages per topic                     ║
║   ✅ Pull quotes · dividers · visual delight             ║
║   ✅ Anti-repetition AI prompting                        ║
║   ✅ COLORING BOOK mode (any language, KDP-ready)        ║
║   ✅ Amazon KDP 6×9 + Gumroad Mobile PDF                 ║
╚══════════════════════════════════════════════════════════╝
"""

import os, json, sys, requests, time, re
from datetime import datetime

# ────────────────────────────────────────────────────────────
#  CONFIGURATION
# ────────────────────────────────────────────────────────────
GROQ_API_KEY  = os.environ.get("GROQ_API_KEY", "")
GROQ_API_URL  = "https://api.groq.com/openai/v1/chat/completions"
MODEL         = "llama-3.1-8b-instant"
MIN_WORDS     = int(os.environ.get("MIN_WORDS_PER_CHAPTER", "1500"))
MAX_RETRIES   = 7
INITIAL_DELAY = 15

# Book type: "standard" or "coloring"
BOOK_TYPE     = os.environ.get("BOOK_TYPE", "standard")   # set "coloring" for coloring books

# ────────────────────────────────────────────────────────────
#  THEMES  ── each has a unique color accent per chapter
# ────────────────────────────────────────────────────────────
CHAPTER_COLORS = [
    "#E8634A",  # 1 – coral
    "#9B8EF0",  # 2 – lavender
    "#F4A22D",  # 3 – amber
    "#3ECFB2",  # 4 – teal
    "#E85A8A",  # 5 – rose
    "#5BADE8",  # 6 – sky
    "#7DC96E",  # 7 – sage
    "#C87DD4",  # 8 – violet
]

BOOK_THEMES = {
    "business": {
        "primary": "#09090D", "secondary": "#111118", "accent": "#F4A22D",
        "text": "#F2EDE4", "muted": "#8A8680", "highlight": "#F4C46D",
        "font_title": "Cormorant+Garamond:ital,wght@0,400;0,600;0,700;1,400",
        "font_body":  "Crimson+Pro:ital,wght@0,300;0,400;0,500;1,300;1,400",
        "font_title_css": "'Cormorant Garamond', Georgia, serif",
        "font_body_css":  "'Crimson Pro', Georgia, serif",
        "emoji": "💼",
        "cover_gradient": "linear-gradient(145deg,#09090D 0%,#18140A 55%,#261E0C 100%)",
        "divider": "◆",
    },
    "self_help": {
        "primary": "#07070F", "secondary": "#0D0C1C", "accent": "#9B8EF0",
        "text": "#EDEBFC", "muted": "#7570A0", "highlight": "#C4B8FF",
        "font_title": "DM+Serif+Display:ital@0;1",
        "font_body":  "Lora:ital,wght@0,400;0,500;1,400",
        "font_title_css": "'DM Serif Display', Georgia, serif",
        "font_body_css":  "'Lora', Georgia, serif",
        "emoji": "✨",
        "cover_gradient": "linear-gradient(145deg,#050410 0%,#12103A 55%,#1C1850 100%)",
        "divider": "✦",
    },
    "technology": {
        "primary": "#03060E", "secondary": "#070C18", "accent": "#00D4E8",
        "text": "#E2EEF8", "muted": "#507090", "highlight": "#5CE8F4",
        "font_title": "Space+Grotesk:wght@400;600;700",
        "font_body":  "IBM+Plex+Serif:ital,wght@0,300;0,400;1,300",
        "font_title_css": "'Space Grotesk', sans-serif",
        "font_body_css":  "'IBM Plex Serif', Georgia, serif",
        "emoji": "🤖",
        "cover_gradient": "linear-gradient(145deg,#020508 0%,#060C1E 55%,#0A1030 100%)",
        "divider": "◈",
    },
    "coloring": {
        # White background — for printing & coloring
        "primary": "#FFFFFF", "secondary": "#F8F8F8", "accent": "#333333",
        "text": "#1A1A1A", "muted": "#666666", "highlight": "#444444",
        "font_title": "Fredoka+One",
        "font_body":  "Nunito:wght@300;400;600",
        "font_title_css": "'Fredoka One', cursive",
        "font_body_css":  "'Nunito', sans-serif",
        "emoji": "🎨",
        "cover_gradient": "linear-gradient(145deg,#FFFFFF 0%,#F0F0F0 100%)",
        "divider": "❋",
    },
    "default": {
        "primary": "#07090C", "secondary": "#0F1118", "accent": "#E8634A",
        "text": "#F2EEE8", "muted": "#7A7570", "highlight": "#F08C76",
        "font_title": "Cormorant+Garamond:ital,wght@0,400;0,600;0,700;1,400",
        "font_body":  "Crimson+Pro:ital,wght@0,300;0,400;0,500;1,300;1,400",
        "font_title_css": "'Cormorant Garamond', Georgia, serif",
        "font_body_css":  "'Crimson Pro', Georgia, serif",
        "emoji": "📖",
        "cover_gradient": "linear-gradient(145deg,#07090C 0%,#121520 55%,#1A1E28 100%)",
        "divider": "❧",
    },
}

def detect_theme(title: str) -> str:
    if BOOK_TYPE == "coloring":
        return "coloring"
    t = title.lower()
    if any(w in t for w in ["business","startup","sales","marketing","entrepreneur","affaires"]):
        return "business"
    if any(w in t for w in ["confidence","mindset","habit","success","ombre","shadow",
                             "discipline","confiance","résilience","stoic","mental"]):
        return "self_help"
    if any(w in t for w in ["ai","tech","code","digital","technologie","software","data"]):
        return "technology"
    return "default"

# ────────────────────────────────────────────────────────────
#  GROQ  API
# ────────────────────────────────────────────────────────────
def call_groq(messages, max_tokens=3500, temperature=0.75):
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    payload = {"model": MODEL, "messages": messages,
               "max_tokens": max_tokens, "temperature": temperature, "top_p": 0.9}
    delay = INITIAL_DELAY
    for attempt in range(MAX_RETRIES):
        r = requests.post(GROQ_API_URL, headers=headers, json=payload)
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"]
        elif r.status_code == 429:
            print(f"⚠️  Rate-limit (attempt {attempt+1}/{MAX_RETRIES}). Waiting {delay}s…")
            time.sleep(delay); delay += 15
        else:
            raise Exception(f"Groq error {r.status_code}: {r.text}")
    raise Exception("Max retries exceeded.")

def clean_json(text):
    text = text.strip()
    for fence in ["```json", "```"]:
        if fence in text:
            text = text.split(fence)[1].split("```")[0]; break
    s, e = text.find('{'), text.rfind('}')+1
    return text[s:e] if s != -1 else text

# ────────────────────────────────────────────────────────────
#  STEP 1 — OUTLINE
# ────────────────────────────────────────────────────────────
def generate_outline(title, language):
    sys_msg = {
        "en": "You are a bestselling author creating unforgettable, joyful books.",
        "fr": "Vous êtes un auteur bestseller créant des livres inoubliables et joyeux.",
        "ar": "أنت كاتب مشهور تبدع كتباً لا تُنسى ومبهجة.",
    }.get(language, "You are a bestselling author.")

    if BOOK_TYPE == "coloring":
        coloring_extra = """
COLORING BOOK RULES:
- Each chapter = 1 coloring theme (animals, nature, mandalas, fantasy, etc.)
- Provide 5 coloring page descriptions per chapter (detailed SVG-ready scene descriptions)
- Titles must be fun, age-appropriate, inviting
- key_technique = "Scene description for illustrator"
- exercises = ["Color with X palette", "Add your own details to Y"]
"""
    else:
        coloring_extra = ""

    prompt = f"""
Create a rich, emotionally engaging book outline for: "{title}"
{coloring_extra}

CRITICAL: Each chapter MUST cover a COMPLETELY DISTINCT topic — NO idea repeated across chapters.
Return ONLY valid JSON (no markdown, no backticks):

{{
  "title": "...",
  "subtitle": "Benefit-driven subtitle",
  "author": "Maria Talks",
  "tagline": "One unforgettable sentence under 15 words",
  "description": "Compelling 200-word description: problem + transformation",
  "target_audience": "Specific reader profile",
  "keywords": ["kw1","kw2","kw3","kw4","kw5"],
  "categories": ["Primary","Secondary"],
  "key_benefits": ["Specific benefit 1","Benefit 2","Benefit 3","Benefit 4","Benefit 5"],
  "chapters": [
    {{
      "number": 1,
      "title": "...",
      "subtitle": "...",
      "hook": "Provocative opening question or shocking fact (1 sentence)",
      "pull_quote": "A powerful 12-20 word quote capturing this chapter's soul",
      "key_points": ["Unique point A","Unique point B","Unique point C"],
      "key_technique": "Named, memorable technique",
      "exercises": ["Concrete exercise 1","Concrete exercise 2"],
      "unique_angle": "What makes this chapter irreplaceable",
      "scene_color": "dominant color mood for this chapter (e.g. deep purple, warm amber)"
    }}
  ],
  "introduction": "300-word hook introduction",
  "conclusion": "300-word emotionally resonant conclusion",
  "about_author": "150-word first-person warm author bio",
  "back_cover_description": "120-word back cover sales copy"
}}

Write exactly 8 chapters. Each MUST have a unique angle not found in any other chapter.
Language: {language}.
"""
    msgs = [{"role":"system","content":sys_msg},{"role":"user","content":prompt}]
    raw  = call_groq(msgs, max_tokens=4000, temperature=0.85)
    return json.loads(clean_json(raw))

# ────────────────────────────────────────────────────────────
#  STEP 2 — CHAPTER CONTENT
# ────────────────────────────────────────────────────────────
def generate_chapter(ch, book_title, num, language, previous_topics):
    prev_str = "\n".join(f"- {t}" for t in previous_topics) or "None yet"

    if BOOK_TYPE == "coloring":
        prompt = f"""
Create content for a COLORING BOOK chapter.
Book: "{book_title}"
Chapter {num}: {ch['title']} — {ch['subtitle']}
Theme: {ch.get('unique_angle','')}

Write {MIN_WORDS} words total with this structure:

[WELCOME TO THIS CHAPTER]
Warm, joyful 2-paragraph welcome (100 words). Invite the reader to relax and be creative.

[COLORING TIPS FOR THIS THEME]
5 specific tips for coloring this chapter's theme. Each tip = 2-3 sentences. (200 words)

[SCENE DESCRIPTIONS] — Write 5 detailed coloring page scenes:
Scene 1: [Title] — Describe in 80 words every element of the illustration to be drawn.
Scene 2: [Title] — Same format.
Scene 3: [Title] — Same format.
Scene 4: [Title] — Same format.
Scene 5: [Title] — Same format.

[COLOR PALETTE SUGGESTIONS]
3 named palette suggestions for this theme, each with 4-5 colors and a mood description. (150 words)

[AFFIRMATION]
3 positive affirmations related to this chapter's theme (1 sentence each).

Language: {language}. Plain text only. No markdown symbols.
"""
    else:
        prompt = f"""
Write a premium, deeply engaging book chapter.
Book: "{book_title}"
Chapter {num}: {ch['title']} — {ch['subtitle']}
Unique angle: {ch.get('unique_angle','Something no other chapter covers')}
Key technique: {ch['key_technique']}
Exercises: {', '.join(ch['exercises'])}

IDEAS ALREADY COVERED — DO NOT REPEAT:
{prev_str}

Write at least {MIN_WORDS} words with this EXACT 8-part structure:

[OPENING SCENE]
A vivid, sensory story or surprising real-world scenario. Make the reader feel present.
(180–220 words)

[THE PROBLEM REFRAMED]
Expose the deeper root cause most people miss. Use a counterintuitive angle.
Cite 1 neuroscience or psychology study (Author, year).
(280–350 words)

[THE HIDDEN TRUTH]
A paradigm shift — something the reader has never heard before.
Use a metaphor or analogy that makes it unforgettable.
(280–350 words)

[THE METHOD: {ch['key_technique']}]
Numbered steps with timing and sensory cues. Each step feels immediately doable.
(380–460 words)

[A REAL PERSON'S STORY]
Name, age, situation, struggle, turning point, result.
Make it emotionally resonant — readers should see themselves.
(260–320 words)

[YOUR ROADMAP THIS WEEK]
3–5 concrete daily actions with specific timing (morning/evening/etc.).
(260–320 words)

[WHEN IT GETS HARD]
Address 2–3 real obstacles with empathetic, practical solutions.
End with an encouraging, memorable closing line.
(180–240 words)

[BRIDGE TO NEXT CHAPTER]
2–3 sentences: lesson learned + intriguing teaser for next chapter.
(60–80 words)

TONE: Warm, direct, occasionally witty — like a wise friend, never a textbook.
LANGUAGE: {language}
Plain paragraphs only. No markdown headings or bullet symbols.
Return ONLY the chapter text.
"""
    msgs = [
        {"role":"system","content":"You are a master storyteller and self-help author. Write with warmth, depth, originality, and zero repetition."},
        {"role":"user","content":prompt}
    ]
    content = call_groq(msgs, max_tokens=4500, temperature=0.78)
    words = len(content.split())
    if words < MIN_WORDS:
        print(f"   ⚠️  {words} words — regenerating ch{num}…")
        content = call_groq(msgs, max_tokens=5000, temperature=0.85)
    return content.strip()

def generate_full_book(title, language):
    print("📖 Generating outline…")
    outline = generate_outline(title, language)
    chapters_out, prev_topics = [], []
    for idx, ch in enumerate(outline["chapters"], 1):
        print(f"  ✍️  Chapter {idx}/8 → {ch['title']}")
        content = generate_chapter(ch, title, idx, language, prev_topics)
        prev_topics.append(f"Ch{idx}: {ch['title']} — {ch.get('unique_angle','')}")
        chapters_out.append({
            **ch,
            "content": content,
            "summary": f"Remember: {ch['key_technique']} — {ch['subtitle']}"
        })
        if idx < 8:
            print("⏳ Cooldown 25s…"); time.sleep(25)
    outline["chapters"] = chapters_out
    return outline

# ────────────────────────────────────────────────────────────
#  HTML GENERATOR  — luxury reading experience
# ────────────────────────────────────────────────────────────
def generate_html(book_data, theme, language):
    is_coloring = (BOOK_TYPE == "coloring")
    is_rtl      = (language == "ar")
    dir_attr    = 'dir="rtl"' if is_rtl else ''
    bside       = "right" if is_rtl else "left"
    year        = datetime.now().year
    divider     = theme["divider"]
    is_dark     = (theme["primary"] not in ["#FFFFFF","#F8F8F8","#FAFAFA"])

    author_val  = book_data.get("author", "Maria Talks")
    author_init = author_val[0].upper()
    title_val   = book_data.get("title","")
    subtitle_val= book_data.get("subtitle","")
    tagline_val = book_data.get("tagline","")
    desc_val    = book_data.get("description","")
    short_title = (title_val[:26]+"…") if len(title_val)>26 else title_val

    # ── Text colour helper ────────────────────────────────────
    def tc(opacity=1.0):
        if is_coloring:
            a = int(opacity * 255)
            return f"rgba(26,26,26,{opacity})"
        return f"rgba(255,255,255,{opacity})"

    # ── Benefits ──────────────────────────────────────────────
    benefits_html = "".join(
        f'<div class="benefit-row">'
        f'<span class="benefit-icon">✓</span>'
        f'<span class="benefit-text">{b}</span>'
        f'</div>'
        for b in book_data.get("key_benefits",[])
    )

    # ── TOC ───────────────────────────────────────────────────
    toc_html = "".join(
        f'<div class="toc-row" onclick="goTo({i})">'
        f'<span class="toc-num" style="color:{CHAPTER_COLORS[(i-1)%len(CHAPTER_COLORS)]}">{i:02d}</span>'
        f'<div class="toc-info">'
        f'<span class="toc-title">{ch["title"]}</span>'
        f'<span class="toc-sub">{ch["subtitle"]}</span>'
        f'</div>'
        f'<span class="toc-arr" style="color:{CHAPTER_COLORS[(i-1)%len(CHAPTER_COLORS)]}">→</span>'
        f'</div>'
        for i, ch in enumerate(book_data.get("chapters",[]),1)
    )

    # ── Chapters ──────────────────────────────────────────────
    chapters_html = ""
    for i, ch in enumerate(book_data.get("chapters",[]),1):
        color = CHAPTER_COLORS[(i-1) % len(CHAPTER_COLORS)]

        # Colorful gradient per chapter
        if is_coloring:
            ch_grad = f"linear-gradient(160deg, #FAFAFA 0%, #F4F4F4 100%)"
            splash_style = f"background:{ch_grad}; border-top: 8px solid {color};"
        else:
            ch_grad = (
                f"linear-gradient(160deg,"
                f"{theme['primary']} 0%,"
                f"{color}18 50%,"
                f"{theme['primary']} 100%)"
            )
            splash_style = f"background:{ch_grad};"

        # Parse content into paragraphs
        paras = [p.strip() for p in ch.get("content","").split("\n\n") if p.strip()]
        lead  = f'<p class="lead-para">{paras[0]}</p>' if paras else ""

        body_parts = []
        for j, p in enumerate(paras[1:], 1):
            body_parts.append(f'<p class="body-para">{p}</p>')
            if j % 4 == 0 and j < len(paras)-2:
                body_parts.append(
                    f'<div class="sec-div" style="color:{color}">'
                    f'<span>{divider} {divider} {divider}</span>'
                    f'</div>'
                )
        body_html = "\n".join(body_parts)

        # Coloring page boxes (special for coloring books)
        coloring_pages_html = ""
        if is_coloring:
            scenes = [p for p in paras if p.lower().startswith("scene")]
            for s_idx, scene in enumerate(scenes[:5], 1):
                cp_color = CHAPTER_COLORS[(s_idx-1) % len(CHAPTER_COLORS)]
                coloring_pages_html += f"""
<div class="coloring-page-box" style="border-color:{cp_color}">
  <div class="cp-header" style="background:{cp_color}15; border-bottom: 2px solid {cp_color}">
    <span class="cp-num" style="color:{cp_color}">🎨 Page {s_idx}</span>
  </div>
  <div class="cp-art-area">
    <!-- Coloring area placeholder with decorative border -->
    <div class="cp-illustration" style="border-color:{cp_color}40">
      <span class="cp-scene-text">{scene}</span>
    </div>
  </div>
</div>"""

        kp_html = "".join(
            f'<li><span class="kp-dot" style="background:{color}"></span><span>{pt}</span></li>'
            for pt in ch.get("key_points",[])
        )
        ex_html = "".join(
            f'<div class="ex-row">'
            f'<span class="ex-num" style="background:{color};color:{"#fff" if not is_coloring else "#fff"}">{j}</span>'
            f'<p>{ex}</p>'
            f'</div>'
            for j,ex in enumerate(ch.get("exercises",[]),1)
        )
        pq = ch.get("pull_quote","")
        pq_html = (
            f'<blockquote class="pull-quote" style="border-color:{color};color:{color}">'
            f'"{pq}"'
            f'</blockquote>'
        ) if pq else ""

        chapters_html += f"""
<div class="page-break" id="ch{i}">

  <div class="ch-splash" style="{splash_style}">
    <div class="ch-meta">
      <span class="ch-label" style="color:{color}">CHAPTER</span>
      <span class="ch-number" style="color:{color}">{i}</span>
    </div>
    <h2 class="ch-title">{ch["title"]}</h2>
    <p class="ch-subtitle" style="color:{color}">{ch["subtitle"]}</p>
  </div>

  <div class="hook-banner" style="border-{bside}-color:{color}; background:{color}10">
    <span class="hook-deco" style="color:{color}">{divider}</span>
    <p class="hook-text">{ch.get("hook","")}</p>
  </div>

  <div class="kp-box" style="border-top:3px solid {color}">
    <p class="kp-label" style="color:{color}">🎯 KEY POINTS</p>
    <ul class="kp-list">{kp_html}</ul>
  </div>

  <div class="ch-body">
    {lead}
    {body_html}
  </div>

  {coloring_pages_html}
  {pq_html}

  <div class="technique-box" style="border-color:{color}">
    <span class="technique-tag" style="color:{color}">🔑 KEY TECHNIQUE</span>
    <p class="technique-name">{ch.get("key_technique","")}</p>
  </div>

  <div class="ex-box" style="border-{bside}-color:{color}">
    <p class="ex-label" style="color:{color}">✍ ACTION EXERCISES</p>
    {ex_html}
  </div>

  <div class="ch-summary">
    <span class="sum-icon">💡</span>
    <p class="sum-text">{ch.get("summary","")}</p>
  </div>

  <div class="ch-footer" style="background:{color}18; border-top: 2px solid {color}30">
    <span style="color:{color}; font-size:0.75rem; letter-spacing:3px; text-transform:uppercase;">
      {ch["title"]}
    </span>
    <span style="color:{tc(0.35)}; font-size:0.75rem;">{title_val}</span>
  </div>

</div>
"""

    def to_paras(text, cls="body-para"):
        return "\n".join(
            f'<p class="{cls}">{p.strip()}</p>'
            for p in text.split("\n") if p.strip()
        )

    intro_html = to_paras(book_data.get("introduction",""))
    conc_html  = to_paras(book_data.get("conclusion",""))

    # ── CSS: dark vs coloring white ───────────────────────────
    bg_body   = theme["primary"]
    bg2       = theme["secondary"]
    txt       = theme["text"]
    acc       = theme["accent"]
    hi        = theme["highlight"]
    muted_c   = theme["muted"]
    ft_css    = theme["font_title_css"]
    fb_css    = theme["font_body_css"]
    ft_url    = theme["font_title"]
    fb_url    = theme["font_body"]

    # ════════════════════════════════════════════════════════════
    html = f"""<!DOCTYPE html>
<html lang="{language}" {dir_attr}>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title_val}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family={ft_url}&family={fb_url}&display=swap" rel="stylesheet">
<style>
/* ══════════════════════════════════════════════════════
   RESET
══════════════════════════════════════════════════════ */
*,*::before,*::after{{margin:0;padding:0;box-sizing:border-box}}

/* ══════════════════════════════════════════════════════
   ROOT — generous, readable scale
══════════════════════════════════════════════════════ */
:root{{
  --bg:      {bg_body};
  --bg2:     {bg2};
  --acc:     {acc};
  --hi:      {hi};
  --txt:     {txt};
  --muted:   {muted_c};
  --ft:      {ft_css};
  --fb:      {fb_css};
  --cg:      {theme["cover_gradient"]};

  /* ── Typography ── */
  --xs:   0.80rem;   /* captions, labels */
  --sm:   0.96rem;   /* small body */
  --base: 1.12rem;   /* standard body   ← bigger than v5 */
  --lg:   1.28rem;   /* large body      ← comfortable */
  --xl:   1.52rem;   /* section leads   ← impactful */
  --2xl:  2.00rem;   /* subtitles       */
  --3xl:  2.60rem;   /* titles          */
  --4xl:  3.80rem;   /* chapter numbers */

  /* ── Spacing — GENEROUS, pages breathe ── */
  --sp1:   8px;
  --sp2:  16px;
  --sp3:  28px;
  --sp4:  48px;
  --sp5:  72px;
  --sp6: 100px;

  --side:   28px;   /* side margins — wider */
  --radius: 18px;
  --max:    520px;  /* comfortable line length */
}}

/* ══════════════════════════════════════════════════════
   BASE
══════════════════════════════════════════════════════ */
html{{scroll-behavior:smooth}}
body{{
  background:var(--bg);
  color:var(--txt);
  font-family:var(--fb);
  font-size:var(--base);
  line-height:2.0;          /* roomy line spacing */
  max-width:var(--max);
  margin:0 auto;
  -webkit-font-smoothing:antialiased;
  -moz-osx-font-smoothing:grayscale;
  word-wrap:break-word;
}}

/* ══════════════════════════════════════════════════════
   READING PROGRESS
══════════════════════════════════════════════════════ */
#rp{{
  position:fixed;top:0;left:0;height:4px;width:0;
  background:linear-gradient(90deg,var(--acc),var(--hi));
  z-index:999;transition:width .1s linear;
}}

/* ══════════════════════════════════════════════════════
   COVER PAGE
══════════════════════════════════════════════════════ */
.cover{{
  min-height:100vh;
  background:var(--cg);
  position:relative;overflow:hidden;
  display:flex;flex-direction:column;
  justify-content:flex-end;
  padding:var(--sp6) var(--side) var(--sp5);
}}
.cover::before{{
  content:'';position:absolute;top:-100px;right:-100px;
  width:420px;height:420px;border-radius:50%;
  background:var(--acc);opacity:.06;
}}
.cover::after{{
  content:'';position:absolute;bottom:180px;right:-70px;
  width:260px;height:260px;border-radius:50%;
  border:2px solid var(--acc);opacity:.12;
}}
.cover-top{{
  position:absolute;top:var(--sp3);
  left:var(--side);right:var(--side);
  display:flex;justify-content:space-between;align-items:center;
}}
.cover-badge{{
  background:var(--acc);color:var(--bg);
  font-size:var(--xs);font-weight:800;
  letter-spacing:2.5px;text-transform:uppercase;
  padding:5px 16px;border-radius:20px;
}}
.cover-yr{{font-size:var(--xs);color:{tc(0.3)};letter-spacing:2px;}}
.cover-emoji{{font-size:80px;margin-bottom:var(--sp3);display:block;}}
.cover-rule{{
  width:64px;height:5px;background:var(--acc);
  border-radius:2px;margin-bottom:var(--sp3);
}}
.cover-title{{
  font-family:var(--ft);
  font-size:clamp(2.2rem,7vw,var(--3xl));
  font-weight:700;
  color:{"#1A1A1A" if is_coloring else "#fff"};
  line-height:1.12;margin-bottom:var(--sp2);
}}
.cover-subtitle{{
  font-family:var(--fb);font-style:italic;
  font-size:var(--sm);color:var(--acc);
  margin-bottom:var(--sp5);line-height:1.7;
}}
.cover-author{{
  display:flex;align-items:center;gap:14px;
  padding-top:var(--sp3);
  border-top:1px solid {tc(0.1)};
}}
.cover-dot{{
  width:42px;height:42px;border-radius:50%;
  background:var(--acc);color:var(--bg);
  display:flex;align-items:center;justify-content:center;
  font-family:var(--ft);font-size:var(--lg);font-weight:700;
}}
.cover-by{{
  font-size:var(--xs);letter-spacing:3px;
  text-transform:uppercase;color:{tc(0.5)};
}}

/* ══════════════════════════════════════════════════════
   NAVBAR (screen only)
══════════════════════════════════════════════════════ */
.navbar{{
  position:sticky;top:0;z-index:100;
  background:{"rgba(255,255,255,0.95)" if is_coloring else "rgba(0,0,0,0.90)"};
  backdrop-filter:blur(24px);
  border-bottom:1px solid {tc(0.07)};
  padding:14px var(--side);
  display:flex;justify-content:space-between;align-items:center;
}}
.nav-name{{
  font-family:var(--ft);font-size:var(--xs);
  color:var(--acc);font-weight:700;letter-spacing:.5px;
}}
.nav-pct{{font-size:var(--xs);color:var(--muted);}}

/* ══════════════════════════════════════════════════════
   GENERIC SECTION  (description, toc, intro, conclusion)
══════════════════════════════════════════════════════ */
.section{{
  padding:var(--sp6) var(--side) var(--sp5);
}}
.section+.section{{
  border-top:1px solid {tc(0.05)};
}}
.sec-label{{
  display:block;
  font-size:var(--xs);letter-spacing:3px;
  text-transform:uppercase;color:var(--acc);
  margin-bottom:var(--sp3);font-weight:600;
}}
.page-h2{{
  font-family:var(--ft);
  font-size:var(--3xl);font-weight:700;
  color:{"#1A1A1A" if is_coloring else "#fff"};
  margin-bottom:var(--sp4);line-height:1.2;
}}

/* ── Description text ── */
.desc-text{{
  font-size:var(--lg);line-height:2.1;
  color:{tc(0.82)};
  margin-bottom:var(--sp5);
}}

/* ── Benefits ── */
.benefit-row{{
  display:flex;align-items:flex-start;gap:16px;
  padding:18px 20px;
  background:{tc(0.04) if not is_coloring else "rgba(0,0,0,0.03)"};
  border-radius:var(--radius);
  border-{bside}:4px solid var(--acc);
  margin-bottom:14px;
}}
.benefit-icon{{
  color:var(--acc);font-weight:900;
  font-size:var(--lg);line-height:1.5;flex-shrink:0;
}}
.benefit-text{{
  font-size:var(--base);color:{tc(0.86)};line-height:1.8;
}}

/* ── TOC ── */
.toc-row{{
  display:flex;align-items:center;gap:18px;
  padding:20px 0;
  border-bottom:1px solid {tc(0.05)};
  cursor:pointer;transition:opacity .15s;
}}
.toc-row:hover{{opacity:.7;}}
.toc-num{{
  font-family:var(--ft);font-size:var(--xl);
  font-weight:700;min-width:42px;
}}
.toc-info{{flex:1;}}
.toc-title{{
  font-size:var(--base);font-weight:600;
  color:{"#1A1A1A" if is_coloring else "#fff"};
  display:block;margin-bottom:4px;
}}
.toc-sub{{font-size:var(--xs);color:var(--muted);display:block;}}
.toc-arr{{font-size:var(--lg);}}

/* ══════════════════════════════════════════════════════
   CHAPTER — the reading experience
══════════════════════════════════════════════════════ */

/* Splash header */
.ch-splash{{
  padding:var(--sp6) var(--side) var(--sp5);
  text-align:center;
}}
.ch-meta{{
  display:inline-flex;flex-direction:column;align-items:center;
  border:2px solid currentColor;
  border-radius:var(--radius);
  padding:12px 32px;margin-bottom:var(--sp3);
  background:{"rgba(0,0,0,0.04)" if is_coloring else "rgba(255,255,255,0.05)"};
}}
.ch-label{{
  font-size:0.6rem;letter-spacing:5px;
  text-transform:uppercase;font-weight:700;
}}
.ch-number{{
  font-family:var(--ft);font-size:var(--4xl);
  font-weight:700;line-height:1;
}}
.ch-title{{
  font-family:var(--ft);font-size:var(--3xl);
  font-weight:700;
  color:{"#1A1A1A" if is_coloring else "#fff"};
  margin-bottom:var(--sp2);line-height:1.2;
}}
.ch-subtitle{{
  font-family:var(--fb);font-style:italic;
  font-size:var(--base);
}}

/* Hook */
.hook-banner{{
  padding:var(--sp4) var(--side);
  display:flex;gap:var(--sp2);align-items:flex-start;
  margin-bottom:var(--sp2);
  border-{bside}-width:5px;border-{bside}-style:solid;
}}
.hook-deco{{font-size:var(--xl);line-height:1;flex-shrink:0;}}
.hook-text{{
  font-family:var(--ft);font-style:italic;
  font-size:var(--xl);
  color:{"#222" if is_coloring else "rgba(255,255,255,0.93)"};
  line-height:1.65;
}}

/* Key points */
.kp-box{{
  padding:var(--sp4) var(--side) var(--sp5);
  background:var(--bg2);
  border-top-width:3px;border-top-style:solid;
}}
.kp-label{{
  font-size:var(--xs);letter-spacing:3px;
  text-transform:uppercase;font-weight:700;
  margin-bottom:var(--sp3);
}}
.kp-list{{list-style:none;}}
.kp-list li{{
  display:flex;gap:14px;align-items:flex-start;
  padding:14px 18px;
  background:{"rgba(0,0,0,0.03)" if is_coloring else "rgba(255,255,255,0.04)"};
  border-radius:12px;margin-bottom:12px;
  font-size:var(--base);color:{tc(0.87)};
  line-height:1.8;
}}
.kp-dot{{
  width:10px;height:10px;border-radius:50%;
  flex-shrink:0;margin-top:10px;
}}

/* Body — MAIN READING ZONE */
.ch-body{{
  padding:var(--sp5) var(--side) var(--sp4);
}}

/* Lead paragraph — bigger, impactful */
.lead-para{{
  font-family:var(--ft);
  font-size:var(--xl);
  line-height:1.9;
  color:{"#111" if is_coloring else "rgba(255,255,255,0.96)"};
  margin-bottom:var(--sp5);
  font-weight:400;
}}

/* Standard body paragraphs — CRYSTAL CLEAR */
.body-para{{
  font-size:var(--lg);       /* 1.28rem — no eye strain */
  line-height:2.1;           /* airy, readable */
  color:{"#2A2A2A" if is_coloring else "rgba(255,255,255,0.90)"};
  margin-bottom:var(--sp4);  /* generous paragraph gap */
  letter-spacing:0.015em;
}}

/* Decorative section divider */
.sec-div{{
  text-align:center;
  padding:var(--sp3) 0 var(--sp4);
  font-size:var(--xl);
  letter-spacing:20px;
  opacity:.45;
}}

/* Pull quote — magazine-quality */
.pull-quote{{
  font-family:var(--ft);font-style:italic;
  font-size:var(--xl);
  line-height:1.75;
  margin:0 var(--side) var(--sp5);
  padding:var(--sp4) var(--sp3);
  border-top:2px solid currentColor;
  border-bottom:2px solid currentColor;
  text-align:center;
  position:relative;
}}
.pull-quote::before{{
  content:'"';
  position:absolute;top:-28px;left:50%;
  transform:translateX(-50%);
  font-size:5rem;
  opacity:.3;line-height:1;
  font-family:var(--ft);
}}

/* Technique badge */
.technique-box{{
  margin:0 var(--side) var(--sp4);
  padding:var(--sp3) var(--sp3);
  border:2px solid;border-radius:var(--radius);
  background:{"rgba(0,0,0,0.03)" if is_coloring else "rgba(255,255,255,0.05)"};
}}
.technique-tag{{
  display:block;font-size:var(--xs);
  letter-spacing:2.5px;text-transform:uppercase;
  margin-bottom:var(--sp1);font-weight:700;
}}
.technique-name{{
  font-family:var(--ft);font-size:var(--xl);
  font-weight:700;
  color:{"#1A1A1A" if is_coloring else "#fff"};
}}

/* Exercises */
.ex-box{{
  margin:0 var(--side) var(--sp4);
  padding:var(--sp3) var(--sp3);
  background:{"rgba(0,0,0,0.03)" if is_coloring else "rgba(255,255,255,0.04)"};
  border-radius:var(--radius);
  border-{bside}-width:5px;border-{bside}-style:solid;
}}
.ex-label{{
  font-size:var(--xs);letter-spacing:3px;
  text-transform:uppercase;font-weight:700;
  margin-bottom:var(--sp3);
}}
.ex-row{{
  display:flex;gap:16px;align-items:flex-start;
  margin-bottom:var(--sp3);
}}
.ex-row:last-child{{margin-bottom:0;}}
.ex-num{{
  width:32px;height:32px;border-radius:50%;
  display:flex;align-items:center;justify-content:center;
  font-weight:800;font-size:var(--sm);flex-shrink:0;
  font-family:var(--ft);
}}
.ex-row p{{
  font-size:var(--base);
  color:{"#2A2A2A" if is_coloring else "rgba(255,255,255,0.87)"};
  line-height:1.8;
}}

/* Chapter summary */
.ch-summary{{
  display:flex;gap:18px;align-items:flex-start;
  margin:0 var(--side) var(--sp3);
  padding:var(--sp3) var(--sp3);
  background:{"rgba(0,0,0,0.04)" if is_coloring else "rgba(255,255,255,0.05)"};
  border-radius:var(--radius);
}}
.sum-icon{{font-size:1.6rem;flex-shrink:0;}}
.sum-text{{
  font-style:italic;font-size:var(--base);
  color:{tc(0.78)};line-height:1.85;
}}

/* Chapter footer */
.ch-footer{{
  display:flex;justify-content:space-between;align-items:center;
  padding:14px var(--side);
  margin-bottom:var(--sp2);
}}

/* ── Coloring page special boxes ── */
.coloring-page-box{{
  margin:var(--sp4) var(--side);
  border:3px solid;border-radius:var(--radius);
  overflow:hidden;
  page-break-inside:avoid;break-inside:avoid;
}}
.cp-header{{
  padding:14px 20px;
  display:flex;align-items:center;gap:12px;
}}
.cp-num{{
  font-family:var(--ft);font-size:var(--base);font-weight:700;
}}
.cp-art-area{{padding:var(--sp3);}}
.cp-illustration{{
  min-height:260px;
  border:2px dashed;border-radius:12px;
  display:flex;align-items:center;justify-content:center;
  padding:var(--sp3);
  background:rgba(255,255,255,0.6);
}}
.cp-scene-text{{
  font-size:var(--sm);color:#555;
  text-align:center;line-height:1.8;
  font-style:italic;
}}

/* ── Author card ── */
.author-card{{
  text-align:center;
  padding:0 var(--side) var(--sp5);
}}
.author-av{{
  width:110px;height:110px;border-radius:50%;
  background:{"rgba(0,0,0,0.06)" if is_coloring else "rgba(255,255,255,0.07)"};
  border:3px solid var(--acc);
  display:flex;align-items:center;justify-content:center;
  font-size:3.2rem;margin:0 auto var(--sp3);
}}
.author-name{{
  font-family:var(--ft);font-size:var(--2xl);
  font-weight:700;
  color:{"#1A1A1A" if is_coloring else "#fff"};
  margin-bottom:var(--sp2);
}}
.author-bio{{
  font-size:var(--base);color:{tc(0.72)};
  line-height:1.95;max-width:400px;margin:0 auto;
}}

/* ── Back cover ── */
.back-cover{{
  min-height:60vh;
  background:var(--cg);
  padding:var(--sp6) var(--side);
  display:flex;flex-direction:column;
  justify-content:center;align-items:center;
  text-align:center;gap:var(--sp4);
}}
.bc-title{{
  font-family:var(--ft);font-size:var(--3xl);
  font-weight:700;
  color:{"#1A1A1A" if is_coloring else "#fff"};
}}
.bc-tagline{{
  font-style:italic;font-size:var(--lg);
  color:{tc(0.72)};
  max-width:400px;line-height:1.9;
}}
.bc-badge{{
  background:var(--acc);color:var(--bg);
  padding:14px 36px;border-radius:50px;
  font-weight:800;font-size:var(--base);
  letter-spacing:.5px;
}}

/* ══════════════════════════════════════════════════════
   DOWNLOAD BUTTONS (screen)
══════════════════════════════════════════════════════ */
.dl-btns{{
  position:fixed;bottom:24px;right:22px;
  display:flex;flex-direction:column;gap:10px;z-index:998;
}}
.btn{{
  background:var(--acc);color:var(--bg);
  border:none;border-radius:50px;
  padding:14px 24px;font-weight:800;
  cursor:pointer;
  font-family:var(--ft);font-size:var(--sm);
  box-shadow:0 6px 28px rgba(0,0,0,.45);
  transition:transform .2s,opacity .15s;
}}
.btn:hover{{transform:translateY(-3px);opacity:.9;}}
.btn-mob{{
  background:{"#f0f0f0" if is_coloring else "rgba(255,255,255,0.1)"};
  color:{"#222" if is_coloring else "#fff"};
  border:2px solid var(--acc);
}}

/* ══════════════════════════════════════════════════════
   PRINT / PDF
══════════════════════════════════════════════════════ */
@page{{size:6in 9in;margin:0;}}
@page:blank{{display:none;}}

@media print{{
  .navbar,.dl-btns,#rp{{display:none!important;}}
  body{{max-width:100%!important;}}
  .page-break{{page-break-before:always;break-before:page;}}
  .ch-summary,.technique-box,.ex-box,.kp-box,
  .hook-banner,.pull-quote,.benefit-row,.author-card,
  .coloring-page-box{{page-break-inside:avoid;break-inside:avoid;}}
  h1,h2,h3,h4,h5{{page-break-after:avoid;break-after:avoid;}}
  .cover{{height:100vh;page-break-after:always;break-after:page;}}
  .back-cover{{page-break-after:avoid;break-after:avoid;}}
  /* Coloring books: white background always */
  {'body{background:#fff!important;color:#111!important;}' if is_coloring else ''}
}}

@media screen{{
  .page-break{{
    border-top:1px dashed {tc(0.05)};
    margin-top:48px;padding-top:48px;
  }}
}}
</style>
</head>
<body>
<div id="rp"></div>

<!-- COVER ──────────────────────────────────────── -->
<section class="cover">
  <div class="cover-top">
    <span class="cover-badge">{theme["emoji"]} Book</span>
    <span class="cover-yr">{year}</span>
  </div>
  <span class="cover-emoji">{theme["emoji"]}</span>
  <div class="cover-rule"></div>
  <h1 class="cover-title">{title_val}</h1>
  <p class="cover-subtitle">{subtitle_val}</p>
  <div class="cover-author">
    <div class="cover-dot">{author_init}</div>
    <span class="cover-by">by {author_val}</span>
  </div>
</section>

<!-- NAVBAR ─────────────────────────────────────── -->
<nav class="navbar">
  <span class="nav-name">{short_title}</span>
  <span class="nav-pct" id="pct">0% read</span>
</nav>

<!-- DESCRIPTION ────────────────────────────────── -->
<section class="section page-break" style="background:var(--bg2)">
  <span class="sec-label">About This Book</span>
  <p class="desc-text">{desc_val}</p>
  <span class="sec-label">What You Will Learn</span>
  {benefits_html}
</section>

<!-- TABLE OF CONTENTS ──────────────────────────── -->
<section class="section page-break">
  <h2 class="page-h2">Table of Contents</h2>
  {toc_html}
</section>

<!-- INTRODUCTION ───────────────────────────────── -->
<section class="section page-break">
  <h2 class="page-h2">Introduction</h2>
  {intro_html}
</section>

<!-- CHAPTERS ───────────────────────────────────── -->
{chapters_html}

<!-- CONCLUSION ─────────────────────────────────── -->
<section class="section page-break">
  <h2 class="page-h2">Conclusion</h2>
  {conc_html}
</section>

<!-- ABOUT THE AUTHOR ───────────────────────────── -->
<section class="section page-break">
  <h2 class="page-h2">About the Author</h2>
  <div class="author-card">
    <div class="author-av">{theme["emoji"]}</div>
    <p class="author-name">{author_val}</p>
    <p class="author-bio">{book_data.get("about_author","")}</p>
  </div>
</section>

<!-- BACK COVER ─────────────────────────────────── -->
<section class="back-cover page-break">
  <h2 class="bc-title">{title_val}</h2>
  <p class="bc-tagline">{tagline_val}</p>
  <div class="bc-badge">✦ Professional Edition {year}</div>
</section>

<!-- DOWNLOAD BUTTONS ───────────────────────────── -->
<div class="dl-btns">
  <button class="btn"     onclick="kdp()">📚 KDP 6×9 in</button>
  <button class="btn btn-mob" onclick="mob()">📱 Mobile PDF</button>
</div>

<script>
/* Reading progress */
window.addEventListener('scroll',function(){{
  var h=document.documentElement.scrollHeight-innerHeight;
  var v=h>0?Math.round(scrollY/h*100):0;
  document.getElementById('rp').style.width=v+'%';
  document.getElementById('pct').textContent=v+'% read';
}});

function goTo(n){{
  var el=document.getElementById('ch'+n);
  if(el)el.scrollIntoView({{behavior:'smooth'}});
}}

function safeName(){{
  var t=document.querySelector('.cover-title');
  return (t?t.textContent:'book')
    .replace(/[^\w\s\u0600-\u06FF\u00C0-\u024F-]/g,'')
    .trim().replace(/\s+/g,'_').slice(0,50);
}}

function hide(){{
  ['.dl-btns','.navbar','#rp'].forEach(function(s){{
    var e=document.querySelector(s);if(e)e.style.display='none';
  }});
}}
function show(){{
  var d=document.querySelector('.dl-btns');
  var n=document.querySelector('.navbar');
  var r=document.getElementById('rp');
  if(d)d.style.display='flex';
  if(n)n.style.display='flex';
  if(r)r.style.display='block';
}}

function doPrint(w,h,u,name){{
  var s=document.createElement('style');
  s.id='_ps';
  s.textContent='@page{{size:'+w+u+' '+h+u+';margin:0;}}';
  var old=document.getElementById('_ps');if(old)old.remove();
  document.head.appendChild(s);
  document.title=name;
  hide();
  requestAnimationFrame(function(){{
    setTimeout(function(){{
      window.print();
      setTimeout(function(){{
        show();
        var x=document.getElementById('_ps');if(x)x.remove();
      }},1500);
    }},80);
  }});
}}

function kdp(){{doPrint(6,9,'in',safeName()+'_KDP_6x9');}}
function mob(){{doPrint(120,213,'mm',safeName()+'_Mobile');}}
</script>
</body>
</html>"""
    return html

# ────────────────────────────────────────────────────────────
#  MAIN
# ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    mode = "🎨 COLORING BOOK" if BOOK_TYPE == "coloring" else "📚 STANDARD BOOK"
    print(f"🚀 Book Generator v7.0 — {mode}")

    book_title = os.environ.get(
        "BOOK_TITLE",
        "LE PROTOCOLE DE L'OMBRE — 30 jours de conditionnement mental stoïque"
    )
    language = os.environ.get("BOOK_LANGUAGE", "fr")

    if not GROQ_API_KEY:
        print("❌ GROQ_API_KEY not set."); sys.exit(1)

    try:
        theme_name = detect_theme(book_title)
        theme      = BOOK_THEMES.get(theme_name, BOOK_THEMES["default"])
        print(f"🎨 Theme: {theme_name}  |  Language: {language}  |  Type: {BOOK_TYPE}")

        book_data = generate_full_book(book_title, language)

        print("🖥️  Building HTML…")
        html = generate_html(book_data, theme, language)

        out = "book_output.html"
        with open(out, "w", encoding="utf-8") as f:
            f.write(html)

        print(f"\n✅ Saved → {out}")
        print("──────────────────────────────────────────────")
        print("📚 Amazon KDP  → click 'KDP 6×9 in'  → Save as PDF")
        print("📱 Gumroad/Mobile → click 'Mobile PDF' → Save as PDF")
        print("──────────────────────────────────────────────")
        if BOOK_TYPE == "coloring":
            print("🎨 COLORING BOOK: white background, illustrations described")
            print("   → Send scene descriptions to illustrator or Midjourney")
    except Exception as e:
        print(f"❌ {e}"); sys.exit(1)
