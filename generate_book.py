#!/usr/bin/env python3
"""
📚 Professional Book Generator - Powered by Groq
Version 5.0 – Zero Blank Pages, Amazon KDP Ready, window.print() engine
"""

import os
import json
import sys
import requests
import time
from datetime import datetime

# ============================================================
# CONFIGURATION
# ============================================================
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama-3.1-8b-instant"
MIN_WORDS_PER_CHAPTER = int(os.environ.get("MIN_WORDS_PER_CHAPTER", "1500"))
MAX_RETRIES = 7
INITIAL_DELAY = 15
BOOK_FORMAT = os.environ.get("BOOK_FORMAT", "pdf")

# ============================================================
# THEMES
# ============================================================
BOOK_THEMES = {
    "business": {
        "primary": "#0d0d0d", "secondary": "#111827", "accent": "#f59e0b",
        "text": "#f3f4f6", "highlight": "#fbbf24", "font_title": "Playfair Display",
        "font_body": "Lora", "emoji": "💼",
        "gradient": "linear-gradient(160deg, #0d0d0d 0%, #1c1917 40%, #292524 100%)",
        "cover_gradient": "linear-gradient(160deg, #1c1917 0%, #292524 50%, #44403c 100%)",
        "cover_accent": "#f59e0b"
    },
    "self_help": {
        "primary": "#1e1b4b", "secondary": "#312e81", "accent": "#a78bfa",
        "text": "#ede9fe", "highlight": "#c4b5fd", "font_title": "Nunito",
        "font_body": "Open Sans", "emoji": "✨",
        "gradient": "linear-gradient(160deg, #1e1b4b 0%, #312e81 50%, #3730a3 100%)",
        "cover_gradient": "linear-gradient(160deg, #0f0c29 0%, #302b63 50%, #24243e 100%)",
        "cover_accent": "#a78bfa"
    },
    "technology": {
        "primary": "#030712", "secondary": "#0f172a", "accent": "#22d3ee",
        "text": "#e2e8f0", "highlight": "#38bdf8", "font_title": "Montserrat",
        "font_body": "Source Sans Pro", "emoji": "🤖",
        "gradient": "linear-gradient(160deg, #030712 0%, #0f172a 50%, #1e293b 100%)",
        "cover_gradient": "linear-gradient(160deg, #020617 0%, #0f172a 60%, #1e293b 100%)",
        "cover_accent": "#22d3ee"
    },
    "default": {
        "primary": "#0d0d0d", "secondary": "#171717", "accent": "#f97316",
        "text": "#f5f5f5", "highlight": "#fb923c", "font_title": "Playfair Display",
        "font_body": "Georgia", "emoji": "📖",
        "gradient": "linear-gradient(160deg, #0d0d0d 0%, #171717 50%, #262626 100%)",
        "cover_gradient": "linear-gradient(160deg, #0d0d0d 0%, #1c1c1c 60%, #2a2a2a 100%)",
        "cover_accent": "#f97316"
    }
}

def detect_theme(title: str, language: str = "en") -> str:
    title_lower = title.lower()
    keywords = {
        "business": ["business", "startup", "entrepreneur", "sales", "marketing", "affaires", "negocio"],
        "self_help": ["confidence", "mindset", "habit", "success", "motivation", "confiance", "reussir"],
        "technology": ["ai", "coding", "tech", "software", "digital", "technologie"]
    }
    for theme, words in keywords.items():
        if any(w in title_lower for w in words):
            return theme
    return "default"

# ============================================================
# GROQ CALL WITH RATE LIMIT HANDLING
# ============================================================
def call_groq(messages, max_tokens=3000, temperature=0.7):
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": MODEL,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "top_p": 0.9
    }
    delay = INITIAL_DELAY
    for attempt in range(MAX_RETRIES):
        resp = requests.post(GROQ_API_URL, headers=headers, json=payload)
        if resp.status_code == 200:
            return resp.json()["choices"][0]["message"]["content"]
        elif resp.status_code == 429:
            print(f"⚠️ Rate limit hit (Attempt {attempt + 1}/{MAX_RETRIES}). Retrying in {delay}s...")
            time.sleep(delay)
            delay += 15
        else:
            raise Exception(f"Groq API error {resp.status_code}: {resp.text}")
    raise Exception("Max retries exceeded. تأكد من حساب Groq ديالك.")

def clean_json(text):
    text = text.strip()
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0]
    elif "```" in text:
        text = text.split("```")[1].split("```")[0]
    start = text.find('{')
    end = text.rfind('}') + 1
    return text[start:end] if start != -1 and end else text

# ============================================================
# STEP 1: BOOK OUTLINE
# ============================================================
def generate_outline(title, language):
    lang_prompt = {
        "en": "You are a professional bestselling author. Create a compelling book outline.",
        "fr": "Vous etes un auteur a succes. Creez un plan de livre convaincant.",
        "ar": "انت كاتب محترف ومشهور. اكتب مخططا مقنعا لكتاب."
    }.get(language, "You are a professional author.")

    prompt = f"""
Create a detailed book outline for a sellable ebook: "{title}"

Return ONLY valid JSON (no markdown, no backticks) with this exact structure:
{{
  "title": "Main title",
  "subtitle": "Benefit-driven subtitle",
  "author": "Professional Author",
  "tagline": "One irresistible sentence",
  "description": "200 words describing problem and transformation",
  "target_audience": "Specific reader",
  "keywords": ["kw1","kw2","kw3","kw4","kw5"],
  "categories": ["Primary","Secondary"],
  "key_benefits": ["Benefit1","Benefit2","Benefit3","Benefit4","Benefit5"],
  "chapters": [
    {{
      "number": 1,
      "title": "Chapter title",
      "subtitle": "Promise",
      "hook": "Shocking opening sentence",
      "key_points": ["Point1","Point2","Point3"],
      "key_technique": "Named technique",
      "exercises": ["Ex1","Ex2"]
    }}
  ],
  "introduction": "300 words",
  "conclusion": "300 words",
  "about_author": "150 words bio",
  "back_cover_description": "120 words"
}}
Write exactly 8 chapters. Language: {language}.
"""
    messages = [{"role": "system", "content": lang_prompt}, {"role": "user", "content": prompt}]
    content = call_groq(messages, max_tokens=4000, temperature=0.8)
    return json.loads(clean_json(content))

# ============================================================
# STEP 2: GENERATE ONE CHAPTER
# ============================================================
def generate_chapter_content(ch_plan, book_title, chapter_num, language):
    prompt = f"""
Write a premium book chapter for "{book_title}".

Chapter {chapter_num}: {ch_plan['title']}
Subtitle: {ch_plan['subtitle']}
Hook: {ch_plan['hook']}
Main technique: {ch_plan['key_technique']}
Exercises: {', '.join(ch_plan['exercises'])}

Write at least {MIN_WORDS_PER_CHAPTER} words following this structure:

1. Opening story or shocking fact (150-200 words)
2. Core problem with psychological/neuroscientific explanation (300-400 words)
3. Scientific or philosophical evidence (300-400 words)
4. Step-by-step solution: {ch_plan['key_technique']} (400-500 words)
5. Real-world case study (250-350 words)
6. Concrete actionable steps (3-5) with timing (300-400 words)
7. Common obstacles and solutions (200-300 words)
8. Summary and bridge to next chapter (100-150 words)

Use short paragraphs, no markdown headings. Write in {language}. Include 2-3 citations (Author, year). Return only plain text.
"""
    messages = [
        {"role": "system", "content": "You are an expert author writing detailed, research-backed content."},
        {"role": "user", "content": prompt}
    ]
    content = call_groq(messages, max_tokens=4000, temperature=0.75)
    words = len(content.split())
    if words < MIN_WORDS_PER_CHAPTER:
        print(f"   ⚠️ Chapter {chapter_num} has {words} words, regenerating...")
        content = call_groq(messages, max_tokens=4500, temperature=0.85)
    return content.strip()

def generate_full_book(title, language):
    print("📖 Generating outline...")
    outline = generate_outline(title, language)
    final_chapters = []
    total = len(outline["chapters"])
    for idx, ch in enumerate(outline["chapters"], 1):
        print(f"  ✍️ Chapter {idx}/{total}: {ch['title']}")
        detailed = generate_chapter_content(ch, title, idx, language)
        final_chapters.append({
            "number": idx,
            "title": ch["title"],
            "subtitle": ch["subtitle"],
            "hook": ch["hook"],
            "key_points": ch["key_points"],
            "key_technique": ch["key_technique"],
            "exercises": ch["exercises"],
            "content": detailed,
            "summary": f"Remember: {ch['key_technique']} – {ch['subtitle']}"
        })
        if idx < total:
            print("⏳ Cooling down 25 seconds...")
            time.sleep(25)
    outline["chapters"] = final_chapters
    return outline

# ============================================================
# HTML GENERATION – window.print() engine, zero blank pages
# ============================================================
def generate_pdf_html(book_data, theme, language):
    is_rtl = language == "ar"
    dir_attr = 'dir="rtl"' if is_rtl else ''
    border_side = 'right' if is_rtl else 'left'
    year = datetime.now().year

    # ── Chapters HTML ──────────────────────────────────────────
    chapters_html = ""
    for i, ch in enumerate(book_data.get("chapters", []), 1):
        key_points_html = "".join(
            f'<li class="key-point"><span class="kp-arrow">&#8594;</span><span>{pt}</span></li>'
            for pt in ch.get("key_points", [])
        )
        exercises_html = "".join(
            f'<div class="exercise-item"><span class="exercise-num">{j}</span><p>{ex}</p></div>'
            for j, ex in enumerate(ch.get("exercises", []), 1)
        )
        paragraphs = [p.strip() for p in ch.get("content", "").split('\n\n') if p.strip()]
        content_html = "".join(f'<p class="body-text">{p}</p>' for p in paragraphs)
        hook_html = (
            f'<div class="chapter-hook">&#8220;{ch.get("hook","")}&#8221;</div>'
            if ch.get("hook") else ""
        )
        technique_html = (
            f'<div class="technique-badge">'
            f'<span class="technique-label">&#128273; KEY TECHNIQUE</span>'
            f'<span class="technique-name">{ch.get("key_technique","")}</span>'
            f'</div>'
            if ch.get("key_technique") else ""
        )

        chapters_html += f"""
<div class="chapter-wrapper page-break">
  <section class="chapter" id="chapter-{i}">
    <div class="chapter-header">
      <div class="chapter-meta">
        <div class="chapter-number-badge">
          <span class="ch-label">CHAPTER</span>
          <span class="ch-num">{ch.get("number", i)}</span>
        </div>
      </div>
      <h2 class="chapter-title">{ch.get("title","")}</h2>
      <p class="chapter-subtitle">{ch.get("subtitle","")}</p>
    </div>
    {hook_html}
    <div class="chapter-body">
      <div class="key-points-box">
        <h4 class="box-label">&#127919; KEY POINTS</h4>
        <ul class="key-points-list">{key_points_html}</ul>
      </div>
      <div class="chapter-content">{content_html}</div>
      {technique_html}
      <div class="exercises-section">
        <h4 class="box-label">&#9997; ACTION EXERCISES</h4>
        <div class="exercises-list">{exercises_html}</div>
      </div>
      <div class="chapter-summary">
        <span class="summary-icon">&#128161;</span>
        <p class="summary-text">{ch.get("summary","")}</p>
      </div>
    </div>
  </section>
</div>"""

    # ── Supporting sections HTML ───────────────────────────────
    benefits_html = "".join(
        f'<div class="benefit-item">'
        f'<span class="benefit-check">&#10003;</span>'
        f'<span class="benefit-text">{b}</span>'
        f'</div>'
        for b in book_data.get("key_benefits", [])
    )
    toc_html = "".join(
        f'<div class="toc-item" onclick="scrollToChapter({i})">'
        f'<span class="toc-num">0{i}</span>'
        f'<div class="toc-text">'
        f'<span class="toc-title">{ch.get("title","")}</span>'
        f'<span class="toc-sub">{ch.get("subtitle","")}</span>'
        f'</div>'
        f'<span class="toc-arrow">&#8594;</span>'
        f'</div>'
        for i, ch in enumerate(book_data.get("chapters", []), 1)
    )
    intro_html = "".join(
        f'<p class="body-text">{p.strip()}</p>'
        for p in book_data.get("introduction", "").split('\n') if p.strip()
    )
    conc_html = "".join(
        f'<p class="body-text">{p.strip()}</p>'
        for p in book_data.get("conclusion", "").split('\n') if p.strip()
    )

    title_val = book_data.get('title', '')
    title_short = (title_val[:28] + "…") if len(title_val) > 28 else title_val
    author_val = book_data.get("author", "Professional Author")
    author_initial = author_val[0].upper() if author_val else "A"

    # ── Font URL ───────────────────────────────────────────────
    font_title_url = theme["font_title"].replace(' ', '+')
    font_body_url  = theme["font_body"].replace(' ', '+')

    html = f"""<!DOCTYPE html>
<html lang="{language}" {dir_attr}>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{book_data.get("title","")}</title>
<link href="https://fonts.googleapis.com/css2?family={font_title_url}:wght@400;700;900&family={font_body_url}:wght@300;400;600&display=swap" rel="stylesheet">
<style>
/* ── Reset ──────────────────────────────────────────────── */
* {{ margin:0; padding:0; box-sizing:border-box; }}

/* ── CSS Variables ──────────────────────────────────────── */
:root {{
  --primary:       {theme["primary"]};
  --secondary:     {theme["secondary"]};
  --accent:        {theme["accent"]};
  --text:          {theme["text"]};
  --highlight:     {theme["highlight"]};
  --gradient:      {theme["gradient"]};
  --cover-gradient:{theme["cover_gradient"]};
  --cover-accent:  {theme["cover_accent"]};
  --font-title:    '{theme["font_title"]}', Georgia, serif;
  --font-body:     '{theme["font_body"]}',  Georgia, serif;
  --size-xs:   0.75rem;
  --size-sm:   0.875rem;
  --size-base: 1rem;
  --size-lg:   1.125rem;
  --size-xl:   1.375rem;
  --size-2xl:  1.75rem;
  --gap-sm:  12px;
  --gap-md:  24px;
  --gap-lg:  40px;
  --gap-xl:  56px;
  --side:    22px;
  --radius:  14px;
}}

/* ── Base ───────────────────────────────────────────────── */
html {{ scroll-behavior: smooth; }}
body {{
  background:  var(--primary);
  color:       var(--text);
  font-family: var(--font-body);
  font-size:   var(--size-base);
  line-height: 1.85;
  max-width:   480px;
  margin:      0 auto;
  word-wrap:   break-word;
}}

/* ── Reading progress bar (screen only) ─────────────────── */
#reading-progress {{
  position: fixed;
  top: 0; left: 0;
  height: 3px;
  width: 0%;
  background: var(--accent);
  z-index: 999;
  transition: width 0.1s;
}}

/* ── Cover ──────────────────────────────────────────────── */
.cover-page {{
  height: 100vh;               /* exact viewport – no overflow */
  background: var(--cover-gradient);
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  align-items: flex-start;
  padding: 60px var(--side) 50px;
  position: relative;
  overflow: hidden;
}}
.cover-page::before {{
  content: '';
  position: absolute; top: -80px; right: -80px;
  width: 320px; height: 320px;
  border-radius: 50%;
  background: var(--cover-accent);
  opacity: 0.08;
}}
.cover-page::after {{
  content: '';
  position: absolute; bottom: 120px; right: -40px;
  width: 180px; height: 180px;
  border-radius: 50%;
  border: 2px solid var(--cover-accent);
  opacity: 0.15;
}}
.cover-top-bar {{
  position: absolute;
  top: var(--side); left: var(--side); right: var(--side);
  display: flex;
  justify-content: space-between;
  align-items: center;
}}
.cover-genre-tag {{
  background: var(--cover-accent);
  color: var(--primary);
  font-size: var(--size-xs);
  font-weight: 800;
  letter-spacing: 2px;
  text-transform: uppercase;
  padding: 5px 14px;
  border-radius: 20px;
}}
.cover-year {{
  font-size: var(--size-xs);
  color: rgba(255,255,255,0.35);
  letter-spacing: 2px;
}}
.cover-emoji {{
  font-size: 64px;
  margin-bottom: 28px;
  display: block;
}}
.cover-line {{
  width: 60px; height: 4px;
  background: var(--cover-accent);
  border-radius: 2px;
  margin-bottom: 20px;
}}
.cover-title {{
  font-family: var(--font-title);
  font-size: clamp(1.9rem, 6vw, 2.6rem);
  font-weight: 900;
  color: #fff;
  line-height: 1.15;
  margin-bottom: 14px;
}}
.cover-subtitle {{
  font-size: var(--size-sm);
  color: var(--cover-accent);
  font-style: italic;
  margin-bottom: 36px;
}}
.cover-author-row {{
  display: flex;
  align-items: center;
  gap: 10px;
  padding-top: 24px;
  border-top: 1px solid rgba(255,255,255,0.12);
  width: 100%;
}}
.cover-author-dot {{
  width: 36px; height: 36px;
  background: var(--cover-accent);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  font-weight: 900;
  color: var(--primary);
}}
.cover-author-name {{
  font-size: var(--size-xs);
  letter-spacing: 3px;
  text-transform: uppercase;
  color: rgba(255,255,255,0.6);
}}

/* ── Nav bar (screen only) ───────────────────────────────── */
.nav-bar {{
  position: sticky; top: 0;
  background: rgba(0,0,0,0.92);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(255,255,255,0.08);
  padding: 13px var(--side);
  display: flex;
  justify-content: space-between;
  align-items: center;
  z-index: 100;
}}
.nav-title {{
  font-family: var(--font-title);
  font-size: var(--size-xs);
  color: var(--accent);
  font-weight: 700;
}}
.nav-progress-text {{
  font-size: var(--size-xs);
  color: rgba(255,255,255,0.35);
}}

/* ── Description page ────────────────────────────────────── */
.description-page {{
  padding: var(--gap-xl) var(--side);
  background: var(--secondary);
  border-bottom: 3px solid var(--accent);
}}
.section-label {{
  font-size: var(--size-xs);
  letter-spacing: 3px;
  text-transform: uppercase;
  color: var(--accent);
  margin-bottom: 14px;
  display: block;
}}
.description-text {{
  font-size: var(--size-base);
  line-height: 1.85;
  color: rgba(255,255,255,0.78);
  margin-bottom: var(--gap-lg);
}}
.benefit-item {{
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 13px 15px;
  background: rgba(255,255,255,0.04);
  border-radius: var(--radius);
  border-{border_side}: 3px solid var(--accent);
  margin-bottom: 10px;
}}
.benefit-check {{
  color: var(--accent);
  font-weight: 900;
  font-size: var(--size-lg);
}}
.benefit-text {{
  font-size: var(--size-sm);
  color: rgba(255,255,255,0.82);
}}

/* ── Table of contents ───────────────────────────────────── */
.toc-page {{
  padding: var(--gap-xl) var(--side);
  background: var(--primary);
}}
.page-title {{
  font-family: var(--font-title);
  font-size: var(--size-2xl);
  font-weight: 900;
  color: #fff;
  margin-bottom: var(--gap-md);
}}
.toc-item {{
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 14px 0;
  border-bottom: 1px solid rgba(255,255,255,0.06);
  cursor: pointer;
}}
.toc-num {{
  font-family: var(--font-title);
  font-size: var(--size-lg);
  font-weight: 900;
  color: var(--accent);
  min-width: 34px;
}}
.toc-text {{ flex: 1; }}
.toc-title {{
  font-size: var(--size-sm);
  font-weight: 600;
  color: #fff;
  display: block;
}}
.toc-sub {{
  font-size: var(--size-xs);
  color: rgba(255,255,255,0.4);
  display: block;
}}
.toc-arrow {{ color: var(--accent); }}

/* ── Intro / Conclusion / Author pages ───────────────────── */
.intro-page, .conclusion-page, .author-page {{
  padding: var(--gap-xl) var(--side);
}}

/* ── Chapter ─────────────────────────────────────────────── */
.chapter-header {{
  background: var(--gradient);
  padding: var(--gap-xl) var(--side) var(--gap-lg);
  text-align: center;
}}
.chapter-number-badge {{
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  background: rgba(255,255,255,0.08);
  border: 2px solid var(--accent);
  border-radius: var(--radius);
  padding: 8px 22px;
  margin-bottom: 16px;
}}
.ch-label {{
  font-size: 0.6rem;
  letter-spacing: 4px;
  color: var(--accent);
  text-transform: uppercase;
}}
.ch-num {{
  font-family: var(--font-title);
  font-size: 2rem;
  font-weight: 900;
  color: #fff;
  line-height: 1;
}}
.chapter-title {{
  font-family: var(--font-title);
  font-size: var(--size-2xl);
  font-weight: 900;
  color: #fff;
  margin-bottom: 10px;
}}
.chapter-subtitle {{
  color: var(--accent);
  font-size: var(--size-sm);
  font-style: italic;
}}
.chapter-hook {{
  margin: var(--gap-md) var(--side) 0;
  padding: 18px 20px;
  border-{border_side}: 4px solid var(--accent);
  background: rgba(255,255,255,0.03);
  font-style: italic;
}}
.chapter-body {{
  padding: var(--gap-lg) var(--side);
}}
.body-text {{
  margin-bottom: 18px;
  line-height: 1.9;
  color: rgba(255,255,255,0.82);
}}
.box-label {{
  font-size: var(--size-xs);
  letter-spacing: 3px;
  text-transform: uppercase;
  color: var(--accent);
  margin-bottom: 14px;
}}
.key-points-box {{
  padding: 20px;
  background: rgba(255,255,255,0.03);
  border-radius: var(--radius);
  margin-bottom: var(--gap-md);
}}
.key-points-list {{
  list-style: none;
  padding: 0;
}}
.key-point {{
  display: flex;
  gap: 10px;
  padding: 9px 12px;
  background: rgba(255,255,255,0.04);
  border-radius: 8px;
  margin-bottom: 8px;
}}
.kp-arrow {{ color: var(--accent); }}
.technique-badge {{
  padding: 16px 18px;
  background: linear-gradient(135deg, rgba(255,255,255,0.07), rgba(255,255,255,0.03));
  border-radius: var(--radius);
  border: 1px solid var(--accent);
  margin-bottom: var(--gap-md);
  display: flex;
  flex-direction: column;
  gap: 6px;
}}
.technique-label {{
  font-size: var(--size-xs);
  letter-spacing: 2px;
  color: var(--accent);
  text-transform: uppercase;
}}
.technique-name {{
  font-size: var(--size-base);
  font-weight: 700;
  color: #fff;
}}
.exercises-section {{
  padding: 20px;
  background: rgba(255,255,255,0.03);
  border-radius: var(--radius);
  border-{border_side}: 4px solid var(--highlight);
  margin-bottom: var(--gap-md);
}}
.exercise-item {{
  display: flex;
  gap: 12px;
  margin-bottom: 12px;
  align-items: flex-start;
}}
.exercise-num {{
  background: var(--highlight);
  color: var(--primary);
  width: 26px; height: 26px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 900;
  flex-shrink: 0;
}}
.chapter-summary {{
  display: flex;
  gap: 14px;
  padding: 18px 20px;
  background: rgba(255,255,255,0.04);
  border-radius: var(--radius);
  font-style: italic;
  align-items: flex-start;
}}
.summary-icon {{ font-size: 1.4rem; flex-shrink: 0; }}
.summary-text {{ color: rgba(255,255,255,0.78); }}

/* ── Author card ─────────────────────────────────────────── */
.author-card {{
  display: flex;
  flex-direction: column;
  gap: var(--gap-md);
  align-items: center;
  text-align: center;
}}
.author-avatar {{
  font-size: 56px;
  width: 90px; height: 90px;
  background: rgba(255,255,255,0.06);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid var(--accent);
}}
.author-name {{
  font-family: var(--font-title);
  font-size: var(--size-xl);
  font-weight: 900;
  color: #fff;
}}
.author-bio {{
  font-size: var(--size-sm);
  color: rgba(255,255,255,0.7);
  line-height: 1.8;
}}

/* ── Back cover ──────────────────────────────────────────── */
.back-cover {{
  height: 60vh;
  background: var(--cover-gradient);
  padding: var(--gap-xl) var(--side);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  gap: var(--gap-md);
}}
.back-cover-title {{
  font-family: var(--font-title);
  font-size: var(--size-2xl);
  font-weight: 900;
  color: #fff;
}}
.back-cover-text {{
  font-size: var(--size-base);
  color: rgba(255,255,255,0.72);
  max-width: 360px;
  line-height: 1.8;
}}
.edition-badge {{
  background: var(--cover-accent);
  color: var(--primary);
  padding: 12px 28px;
  border-radius: 50px;
  font-weight: 900;
  font-size: var(--size-sm);
}}

/* ── Download buttons (screen only) ─────────────────────── */
.controls {{
  position: fixed;
  bottom: 22px; right: 18px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  z-index: 998;
}}
.btn {{
  background: var(--accent);
  color: var(--primary);
  border: none;
  border-radius: 50px;
  padding: 13px 20px;
  font-weight: 900;
  cursor: pointer;
  font-family: var(--font-title);
  box-shadow: 0 4px 15px rgba(0,0,0,0.5);
  transition: transform 0.2s, opacity 0.2s;
  font-size: var(--size-sm);
}}
.btn:hover {{ transform: translateY(-2px); opacity: 0.9; }}
.btn-kdp {{ background: #f59e0b; }}

/* ══════════════════════════════════════════════════════════
   PRINT / PDF  –  the ONLY source of truth for page breaks
   ══════════════════════════════════════════════════════════ */
@page {{
  size: 6in 9in;   /* default = KDP; overridden by JS for mobile */
  margin: 0;
}}

/* Suppress any rogue blank page the browser might insert */
@page :blank {{ display: none; }}

@media print {{
  /* Hide all interactive chrome */
  .nav-bar,
  .controls,
  #reading-progress {{ display: none !important; }}

  /* Body has no max-width on paper */
  body {{ max-width: 100% !important; }}

  /* Every .page-break element starts on a fresh page */
  .page-break {{
    page-break-before: always;
    break-before: page;
  }}

  /* Never split these boxes across pages */
  .chapter-hook,
  .key-points-box,
  .technique-badge,
  .exercises-section,
  .chapter-summary,
  .benefit-item,
  .author-card {{
    page-break-inside: avoid;
    break-inside: avoid;
  }}

  /* Headings must stay with the content that follows */
  h1, h2, h3, h4 {{
    page-break-after: avoid;
    break-after: avoid;
  }}

  /* Cover fills exactly one page */
  .cover-page {{
    height: 100vh;
    page-break-after: always;
    break-after: page;
  }}

  /* Back cover – no trailing blank page */
  .back-cover {{
    page-break-after: avoid;
    break-after: avoid;
  }}
}}

/* ── Dashed dividers between sections (screen only) ─────── */
@media screen {{
  .page-break {{
    border-top: 1px dashed rgba(255,255,255,0.06);
    margin-top: 32px;
    padding-top: 32px;
  }}
}}
</style>
</head>
<body>

<div id="reading-progress"></div>

<!-- ── Cover ──────────────────────────────────────────────── -->
<section class="cover-page">
  <div class="cover-top-bar">
    <span class="cover-genre-tag">{theme["emoji"]} Book</span>
    <span class="cover-year">{year}</span>
  </div>
  <span class="cover-emoji">{theme["emoji"]}</span>
  <div class="cover-line"></div>
  <h1 class="cover-title">{book_data.get("title","")}</h1>
  <p class="cover-subtitle">{book_data.get("subtitle","")}</p>
  <div class="cover-author-row">
    <div class="cover-author-dot">{author_initial}</div>
    <span class="cover-author-name">by {author_val}</span>
  </div>
</section>

<!-- ── Sticky nav (screen) ───────────────────────────────── -->
<nav class="nav-bar">
  <span class="nav-title">{title_short}</span>
  <span class="nav-progress-text" id="progress-text">0% read</span>
</nav>

<!-- ── Description ───────────────────────────────────────── -->
<section class="description-page page-break">
  <span class="section-label">About This Book</span>
  <p class="description-text">{book_data.get("description","")}</p>
  <span class="section-label">What You Will Learn</span>
  <div class="benefits-list">{benefits_html}</div>
</section>

<!-- ── Table of Contents ─────────────────────────────────── -->
<section class="toc-page page-break">
  <h2 class="page-title">Table of Contents</h2>
  {toc_html}
</section>

<!-- ── Introduction ──────────────────────────────────────── -->
<section class="intro-page page-break">
  <h2 class="page-title">Introduction</h2>
  {intro_html}
</section>

<!-- ── Chapters ──────────────────────────────────────────── -->
{chapters_html}

<!-- ── Conclusion ────────────────────────────────────────── -->
<section class="conclusion-page page-break">
  <h2 class="page-title">Conclusion</h2>
  {conc_html}
</section>

<!-- ── About the Author ──────────────────────────────────── -->
<section class="author-page page-break">
  <h2 class="page-title">About the Author</h2>
  <div class="author-card">
    <div class="author-avatar">{theme["emoji"]}</div>
    <p class="author-name">{author_val}</p>
    <p class="author-bio">{book_data.get("about_author","")}</p>
  </div>
</section>

<!-- ── Back Cover ────────────────────────────────────────── -->
<section class="back-cover page-break">
  <h2 class="back-cover-title">{book_data.get("title","")}</h2>
  <p class="back-cover-text">{book_data.get("tagline","")}</p>
  <div class="edition-badge">&#10022; Professional Edition {year}</div>
</section>

<!-- ── Download buttons ───────────────────────────────────── -->
<div class="controls">
  <button class="btn btn-kdp" onclick="downloadKDP()">&#128218; Download KDP (6x9)</button>
  <button class="btn"         onclick="downloadMobile()">&#128241; Download Mobile PDF</button>
</div>

<script>
/* ── Reading-progress bar ──────────────────────────────── */
window.addEventListener('scroll', function () {{
  var scrolled  = window.scrollY;
  var total     = document.documentElement.scrollHeight - window.innerHeight;
  var pct       = total > 0 ? (scrolled / total) * 100 : 0;
  var bar  = document.getElementById('reading-progress');
  var text = document.getElementById('progress-text');
  if (bar)  bar.style.width = pct + '%';
  if (text) text.textContent = Math.round(pct) + '% read';
}});

/* ── Smooth scroll to chapter ─────────────────────────── */
function scrollToChapter(n) {{
  var el = document.getElementById('chapter-' + n);
  if (el) el.scrollIntoView({{ behavior: 'smooth' }});
}}

/* ── Safe file name ───────────────────────────────────── */
function getSafeName() {{
  var el = document.querySelector('.cover-title');
  var t  = el ? el.textContent : 'book';
  return t.replace(/[^\w\s-]/g, '').trim().replace(/\s+/g, '_').substring(0, 50);
}}

/* ── Hide / restore UI around print ──────────────────── */
function hideUI() {{
  var ctrl = document.querySelector('.controls');
  var bar  = document.getElementById('reading-progress');
  var nav  = document.querySelector('.nav-bar');
  if (ctrl) ctrl.style.display = 'none';
  if (bar)  bar.style.display  = 'none';
  if (nav)  nav.style.display  = 'none';
}}
function restoreUI() {{
  var ctrl = document.querySelector('.controls');
  var bar  = document.getElementById('reading-progress');
  var nav  = document.querySelector('.nav-bar');
  if (ctrl) ctrl.style.display = 'flex';
  if (bar)  bar.style.display  = 'block';
  if (nav)  nav.style.display  = 'flex';
}}

/* ── Inject a temporary @page override, print, remove ── */
function printWithSize(w, h, unit, filename) {{
  var styleId = 'print-size-override';
  var old = document.getElementById(styleId);
  if (old) old.remove();

  var s = document.createElement('style');
  s.id = styleId;
  s.textContent = '@page {{ size: ' + w + unit + ' ' + h + unit + '; margin: 0; }}';
  document.head.appendChild(s);

  document.title = filename;
  hideUI();

  /* Give browser one frame to apply the style, then print */
  requestAnimationFrame(function () {{
    setTimeout(function () {{
      window.print();
      /* Restore after dialog closes (best-effort) */
      setTimeout(function () {{
        restoreUI();
        var injected = document.getElementById(styleId);
        if (injected) injected.remove();
      }}, 1500);
    }}, 80);
  }});
}}

/* ── 📱 Mobile PDF  120 × 213 mm ────────────────────── */
function downloadMobile() {{
  printWithSize(120, 213, 'mm', getSafeName() + '_Mobile');
}}

/* ── 📚 Amazon KDP  6 × 9 in ────────────────────────── */
function downloadKDP() {{
  printWithSize(6, 9, 'in', getSafeName() + '_KDP_6x9');
}}
</script>
</body>
</html>"""

    return html

# ============================================================
# MAIN EXECUTION
# ============================================================
if __name__ == "__main__":
    print("🚀 Starting Professional Book Generator v5.0...")

    book_title = os.environ.get("BOOK_TITLE", "LE PROTOCOLE DE L'OMBRE premium 30 days ghost mode mental conditioning")
    language   = os.environ.get("BOOK_LANGUAGE", "fr")

    if not GROQ_API_KEY:
        print("❌ GROQ_API_KEY is not set.")
        sys.exit(1)

    try:
        theme_name = detect_theme(book_title, language)
        theme      = BOOK_THEMES.get(theme_name, BOOK_THEMES["default"])
        print(f"🎨 Theme detected: {theme_name}")

        book_data  = generate_full_book(book_title, language)

        print("🖥️  Generating HTML...")
        final_html = generate_pdf_html(book_data, theme, language)

        output_file = "book_output.html"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(final_html)

        print(f"✅ Done! Saved → {output_file}")
        print("افتح الملف في المتصفح ← اضغط KDP أو Mobile ← اختر 'Save as PDF' من dialog الطباعة.")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
