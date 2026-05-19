```python
#!/usr/bin/env python3
"""
📚 Professional Book Generator - Powered by Groq
Generates complete, sellable ebooks — PDF direct sell or Amazon KDP
Optimized with Two-Step Generation to eliminate repetitions and PDF clipping.
"""

import os
import json
import sys
import re
import requests
from datetime import datetime

# ============================================================
# GROQ API CONFIGURATION
# ============================================================
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama-3.3-70b-versatile"

# ============================================================
# BOOK FORMAT CONFIG
# ============================================================
# "pdf"  → mobile 120×213mm, dark design, html2pdf download button
# "kdp"  → Amazon KDP 6×9 inch (152×228mm), white background, print-ready
BOOK_FORMAT = os.environ.get("BOOK_FORMAT", "pdf")  # "pdf" or "kdp"

# ============================================================
# BOOK THEMES
# ============================================================
BOOK_THEMES = {
    "business": {
        "primary": "#0d0d0d",
        "secondary": "#111827",
        "accent": "#f59e0b",
        "text": "#f3f4f6",
        "highlight": "#fbbf24",
        "font_title": "Playfair Display",
        "font_body": "Lora",
        "emoji": "💼",
        "gradient": "linear-gradient(160deg, #0d0d0d 0%, #1c1917 40%, #292524 100%)",
        "cover_gradient": "linear-gradient(160deg, #1c1917 0%, #292524 50%, #44403c 100%)",
        "cover_accent": "#f59e0b"
    },
    "health": {
        "primary": "#052e16",
        "secondary": "#14532d",
        "accent": "#4ade80",
        "text": "#f0fdf4",
        "highlight": "#86efac",
        "font_title": "Merriweather",
        "font_body": "Source Serif Pro",
        "emoji": "🌿",
        "gradient": "linear-gradient(160deg, #052e16 0%, #14532d 50%, #166534 100%)",
        "cover_gradient": "linear-gradient(160deg, #052e16 0%, #14532d 60%, #15803d 100%)",
        "cover_accent": "#4ade80"
    },
    "finance": {
        "primary": "#0a0a0a",
        "secondary": "#111",
        "accent": "#ffd700",
        "text": "#e5e5e5",
        "highlight": "#fbbf24",
        "font_title": "EB Garamond",
        "font_body": "Libre Baskerville",
        "emoji": "💰",
        "gradient": "linear-gradient(160deg, #0a0a0a 0%, #111 50%, #1c1c1c 100%)",
        "cover_gradient": "linear-gradient(160deg, #0a0a0a 0%, #171717 60%, #262626 100%)",
        "cover_accent": "#ffd700"
    },
    "self_help": {
        "primary": "#0a0a0a",
        "secondary": "#111111",
        "accent": "#a78bfa",
        "text": "#ede9fe",
        "highlight": "#c4b5fd",
        "font_title": "Montserrat",
        "font_body": "Open Sans",
        "emoji": "✨",
        "gradient": "linear-gradient(160deg, #0a0a0a 0%, #111111 50%, #1c1c1c 100%)",
        "cover_gradient": "linear-gradient(160deg, #0b0b0b 0%, #111111 50%, #1a1a1a 100%)",
        "cover_accent": "#a78bfa"
    },
    "technology": {
        "primary": "#030712",
        "secondary": "#0f172a",
        "accent": "#22d3ee",
        "text": "#e2e8f0",
        "highlight": "#38bdf8",
        "font_title": "Montserrat",
        "font_body": "Source Sans Pro",
        "emoji": "🤖",
        "gradient": "linear-gradient(160deg, #030712 0%, #0f172a 50%, #1e293b 100%)",
        "cover_gradient": "linear-gradient(160deg, #020617 0%, #0f172a 60%, #1e293b 100%)",
        "cover_accent": "#22d3ee"
    },
    "spirituality": {
        "primary": "#1a0533",
        "secondary": "#2d0a4e",
        "accent": "#e879f9",
        "text": "#fae8ff",
        "highlight": "#d946ef",
        "font_title": "Cormorant Garamond",
        "font_body": "Crimson Text",
        "emoji": "🔮",
        "gradient": "linear-gradient(160deg, #1a0533 0%, #2d0a4e 50%, #4a044e 100%)",
        "cover_gradient": "linear-gradient(160deg, #0f0020 0%, #2d0a4e 60%, #4a044e 100%)",
        "cover_accent": "#e879f9"
    },
    "cooking": {
        "primary": "#1c0500",
        "secondary": "#431407",
        "accent": "#fb923c",
        "text": "#fff7ed",
        "highlight": "#fdba74",
        "font_title": "Dancing Script",
        "font_body": "Quattrocento",
        "emoji": "🍳",
        "gradient": "linear-gradient(160deg, #1c0500 0%, #431407 50%, #7c2d12 100%)",
        "cover_gradient": "linear-gradient(160deg, #1c0500 0%, #431407 60%, #9a3412 100%)",
        "cover_accent": "#fb923c"
    },
    "travel": {
        "primary": "#0c1a2e",
        "secondary": "#0f2846",
        "accent": "#fbbf24",
        "text": "#fef3c7",
        "highlight": "#f59e0b",
        "font_title": "Josefin Sans",
        "font_body": "Raleway",
        "emoji": "✈️",
        "gradient": "linear-gradient(160deg, #0c1a2e 0%, #0f2846 50%, #1e3a5f 100%)",
        "cover_gradient": "linear-gradient(160deg, #030e1c 0%, #0f2846 60%, #1e3a5f 100%)",
        "cover_accent": "#fbbf24"
    },
    "default": {
        "primary": "#0d0d0d",
        "secondary": "#171717",
        "accent": "#f97316",
        "text": "#f5f5f5",
        "highlight": "#fb923c",
        "font_title": "Playfair Display",
        "font_body": "Georgia",
        "emoji": "📖",
        "gradient": "linear-gradient(160deg, #0d0d0d 0%, #171717 50%, #262626 100%)",
        "cover_gradient": "linear-gradient(160deg, #0d0d0d 0%, #1c1c1c 60%, #2a2a2a 100%)",
        "cover_accent": "#f97316"
    }
}

def clean_french_grammar(text: str) -> str:
    """Post-processing filter to fix common AI French mistakes"""
    replacements = {
        r"\bla conditionnement\b": "le conditionnement",
        r"\bLa conditionnement\b": "Le conditionnement",
        r"\bvos douts\b": "vos doutes",
        r"\bcombien de fois as-built\b": "combien de fois as-tu bâti",
        r"\blalaitoall\b": "",  # Remove random AI hallucinations
        r"\btexploiter\b": "l'exploiter"
    }
    for pattern, repl in replacements.items():
        text = re.sub(pattern, repl, text, flags=re.IGNORECASE)
    return text

def detect_theme(title: str, language: str = "en") -> str:
    title_lower = title.lower()
    keywords = {
        "business": ["business","startup","entrepreneur","marketing","sales","brand","عمل","تجارة","ريادة","affaires","negocio"],
        "health": ["health","fitness","wellness","diet","nutrition","صحة","لياقة","تغذية","santé","salud"],
        "finance": ["money","invest","finance","wealth","rich","مال","استثمار","ثروة","argent","dinero"],
        "self_help": ["confidence","mindset","habit","success","motivation","discipline","ombre","shadow","protocole","ثقة","عادات","نجاح","confiance","confianza","secret","réussir","réussite"],
        "technology": ["ai","coding","tech","software","digital","تقنية","برمجة","ذكاء اصطناعي","technologie"],
        "spirituality": ["spiritual","meditation","soul","mindfulness","روحانية","تأمل","روح","spiritualité"],
        "cooking": ["cook","recipe","food","kitchen","طبخ","وصفة","طعام","cuisine","cocina"],
        "travel": ["travel","adventure","journey","trip","سفر","مغامرة","رحلة","voyage","viaje"]
    }
    for theme, words in keywords.items():
        if any(word in title_lower for word in words):
            return theme
    return "default"

def call_groq(messages: list, max_tokens: int = 4000) -> str:
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": MODEL,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": 0.75,
        "top_p": 0.9
    }
    response = requests.post(GROQ_API_URL, headers=headers, json=payload)
    if response.status_code != 200:
        raise Exception(f"Groq API Error: {response.status_code} - {response.text}")
    return response.json()["choices"][0]["message"]["content"]


# ============================================================
# 🔥 NEW TWO-STEP ENGINE GENERATORS
# ============================================================

def generate_book_structure(title: str, language: str = "en") -> dict:
    """Step 1: Generates ONLY the structural metadata and chapter list with briefs"""
    
    lang_prompts = {
        "en": "You are a professional bestselling author. Your books follow the structure of top sellers like Atomic Habits and The Psychology of Money.",
        "ar": "أنت مؤلف محترف ومتخصص في الكتب الأكثر مبيعًا. كتبك تتبع هيكل أفضل الكتب مبيعًا.",
        "fr": "Vous êtes un auteur professionnel de best-sellers. Votre ton est froid, élégant, stoïque et percutant (Maria Talks d'élite).",
    }
    
    system_msg = lang_prompts.get(language, lang_prompts["en"])

    messages = [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": f"""
Create the metadata and strategic chapter index for a premium workbook about: "{title}"

Rules:
1. Return ONLY a valid JSON object. No intro/outro commentary, no markdown ticks.
2. Formulate chapters to address progressive levels of deep psychology or stoicism.
3. Language of output: {language}.

Format EXACTLY as:
{{
  "title": "powerful book title",
  "subtitle": "benefit-driven subtitle",
  "author": "Maria Talks",
  "tagline": "one percutant sentence that makes someone NEED this workbook",
  "description": "200 words explaining the psychological transition this workbook will trigger.",
  "target_audience": "young adults seeking raw mental performance",
  "keywords": ["keyword1", "keyword2"],
  "categories": ["Personal Growth", "Stoicism"],
  "key_benefits": [
    "Specific benefit 1",
    "Specific benefit 2",
    "Specific benefit 3",
    "Specific benefit 4",
    "Specific benefit 5"
  ],
  "chapters": [
    {{
      "number": 1,
      "title": "Chapter Title",
      "subtitle": "The specific promise/goal of this chapter",
      "focus": "A short brief of what psychological problem this chapter must address."
    }},
    {{
      "number": 2,
      "title": "Chapter Title",
      "subtitle": "Chapter promise",
      "focus": "Brief"
    }},
    {{
      "number": 3,
      "title": "Chapter Title",
      "subtitle": "Chapter promise",
      "focus": "Brief"
    }},
    {{
      "number": 4,
      "title": "Chapter Title",
      "subtitle": "Chapter promise",
      "focus": "Brief"
    }},
    {{
      "number": 5,
      "title": "Chapter Title",
      "subtitle": "Chapter promise",
      "focus": "Brief"
    }},
    {{
      "number": 6,
      "title": "Chapter Title",
      "subtitle": "Chapter promise",
      "focus": "Brief"
    }},
    {{
      "number": 7,
      "title": "Chapter Title",
      "subtitle": "Chapter promise",
      "focus": "Brief"
    }},
    {{
      "number": 8,
      "title": "Chapter Title",
      "subtitle": "Chapter promise",
      "focus": "Brief"
    }}
  ],
  "introduction": "300 words introducing the concept of this book with zero fluff. Go straight to raw, percutant truths.",
  "conclusion": "300 words summarizing the ultimate transition and final call to action.",
  "about_author": "150 words third-person strategic biography of Maria Talks.",
  "back_cover_description": "Compelling back cover copy."
}}
"""}
    ]

    content = call_groq(messages, max_tokens=3000).strip()
    if "```json" in content:
        content = content.split("```json")[1].split("```")[0]
    elif "```" in content:
        content = content.split("```")[1].split("```")[0]
    content = content.strip()

    start = content.find('{')
    end = content.rfind('}') + 1
    structure = json.loads(content[start:end])
    
    # Clean structure texts
    structure["introduction"] = clean_french_grammar(structure.get("introduction", ""))
    structure["conclusion"] = clean_french_grammar(structure.get("conclusion", ""))
    structure["description"] = clean_french_grammar(structure.get("description", ""))
    return structure


def generate_single_chapter_content(book_title: str, chapter: dict, language: str = "en") -> dict:
    """Step 2: Generates deep, premium content for exactly ONE chapter to prevent repetitions"""
    
    system_prompt = (
        "You are an elite psychological coach and stoic philosopher. You write in flawless, "
        "cold, gender-neutral, and highly strategic French. Your persona is 'Maria Talks'. "
        "Never use fluffy clichés. Always write in short, punchy paragraphs (2-4 sentences max)."
    )

    user_prompt = f"""
Book: "{book_title}"
Write all the internal sections for Chapter {chapter['number']}: "{chapter['title']}"
Chapter Promise: {chapter['subtitle']}
Focus/Brief of this Chapter: {chapter.get('focus', '')}

CRITICAL RULES:
1. Write in flawless, elegant, and neutral/unisexe French (No brackets like 'fatigué(e)', use terms like 'Si la fatigue te freine').
2. Do NOT use introductory filler phrases like 'Dans ce chapitre nous allons voir...' or 'Dans cette section...'. Jump directly into the raw content.
3. Write a deep and detailed master content of minimum 800 words. Split it into multiple short paragraphs. 
4. Provide a powerful, unsettling Shadow Work question.

Output ONLY a raw, valid JSON matching this schema:
{{
  "hook": "One shocking and percutant opening hook sentence.",
  "key_points": [
    "Specific point 1",
    "Specific point 2",
    "Specific point 3"
  ],
  "content": "A highly detailed, raw, cold 800-word analysis. Give specific names, psychological reasons, and a concrete stoic strategy. Make it extremely valuable.",
  "key_technique": "A named advanced stoic or psychological technique.",
  "exercises": [
    "Exercise 1: Actionable, difficult but necessary practical real-world task.",
    "Exercise 2: An uncomfortable, deep Shadow Work question confronting their ego."
  ],
  "summary": "One powerful, icy, memorable closing takeaway sentence."
}}
"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    content = call_groq(messages, max_tokens=4000).strip()
    if "```json" in content:
        content = content.split("```json")[1].split("```")[0]
    elif "```" in content:
        content = content.split("```")[1].split("```")[0]
    content = content.strip()

    start = content.find('{')
    end = content.rfind('}') + 1
    ch_data = json.loads(content[start:end])
    
    # Post-process grammar cleaning on output text
    if "content" in ch_data:
        ch_data["content"] = clean_french_grammar(ch_data["content"])
    if "hook" in ch_data:
        ch_data["hook"] = clean_french_grammar(ch_data["hook"])
    if "summary" in ch_data:
        ch_data["summary"] = clean_french_grammar(ch_data["summary"])
        
    return ch_data


# ============================================================
# FORMAT 1: PDF DIRECT SELL (dark, mobile-optimized)
# ============================================================
def generate_pdf_html(book_data: dict, theme: dict, language: str = "en") -> str:
    """Dark mobile-optimized HTML for direct PDF selling (Fully Responsive & Non-Clipping)"""

    is_rtl = language == "ar"
    dir_attr = 'dir="rtl"' if is_rtl else ''
    border_side = 'right' if is_rtl else 'left'

    chapters_html = ""
    for i, chapter in enumerate(book_data.get("chapters", []), 1):

        key_points_html = "".join(
            f'<li class="key-point"><span class="kp-arrow">→</span><span>{pt}</span></li>'
            for pt in chapter.get("key_points", [])
        )

        exercises_html = "".join(
            f'''<div class="exercise-item">
                    <span class="exercise-num">{j}</span>
                    <p>{ex}</p>
                </div>'''
            for j, ex in enumerate(chapter.get("exercises", []), 1)
        )

        raw_content = chapter.get("content", "")
        paragraphs = [p.strip() for p in raw_content.split('\n') if p.strip()]
        content_html = "".join(f'<p class="body-text">{p}</p>' for p in paragraphs)

        hook = chapter.get("hook", "")
        hook_html = f'<div class="chapter-hook">&ldquo;{hook}&rdquo;</div>' if hook else ""

        key_technique = chapter.get("key_technique", "")
        technique_html = f'''<div class="technique-badge">
            <span class="technique-label">🔑 KEY TECHNIQUE</span>
            <span class="technique-name">{key_technique}</span>
        </div>''' if key_technique else ""

        chapters_html += f'''
<div class="chapter-wrapper page-break">
<section class="chapter" id="chapter-{i}">
    <div class="chapter-header">
        <div class="chapter-meta">
            <div class="chapter-number-badge">
                <span class="ch-label">CHAPTER</span>
                <span class="ch-num">{chapter.get("number", i)}</span>
            </div>
        </div>
        <h2 class="chapter-title">{chapter.get("title", "")}</h2>
        <p class="chapter-subtitle">{chapter.get("subtitle", "")}</p>
    </div>

    {hook_html}

    <div class="chapter-body">
        <div class="key-points-box">
            <h4 class="box-label">🎯 KEY POINTS</h4>
            <ul class="key-points-list">{key_points_html}</ul>
        </div>

        <div class="chapter-content">
            {content_html}
        </div>

        {technique_html}

        <div class="exercises-section">
            <h4 class="box-label">✍️ ACTION EXERCISES</h4>
            <div class="exercises-list">{exercises_html}</div>
        </div>

        <div class="chapter-summary">
            <span class="summary-icon">💡</span>
            <p class="summary-text">{chapter.get("summary", "")}</p>
        </div>
    </div>
</section>
</div>'''

    benefits_html = "".join(
        f'<div class="benefit-item"><span class="benefit-check">✓</span><span class="benefit-text">{b}</span></div>'
        for b in book_data.get("key_benefits", [])
    )

    toc_html = "".join(
        f'''<div class="toc-item" onclick="scrollToChapter({i})">
            <span class="toc-num">0{i}</span>
            <div class="toc-text">
                <span class="toc-title">{ch.get("title","")}</span>
                <span class="toc-sub">{ch.get("subtitle","")}</span>
            </div>
            <span class="toc-arrow">→</span>
        </div>'''
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

    title_short = book_data.get('title', '')
    title_display = title_short[:28] + "…" if len(title_short) > 28 else title_short
    year = datetime.now().year

    html = f'''<!DOCTYPE html>
<html lang="{language}" {dir_attr}>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{book_data.get("title","")}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family={theme["font_title"].replace(" ","+")},wght@400;700;900&family={theme["font_body"].replace(" ","+")},wght@300;400;600&display=swap" rel="stylesheet">
<style>
*, *::before, *::after {{ margin:0; padding:0; box-sizing:border-box; }}
:root {{
    --primary:   {theme["primary"]};
    --secondary: {theme["secondary"]};
    --accent:    {theme["accent"]};
    --text:      {theme["text"]};
    --highlight: {theme["highlight"]};
    --gradient:  {theme["gradient"]};
    --cover-gradient: {theme["cover_gradient"]};
    --cover-accent:   {theme["cover_accent"]};
    --font-title: '{theme["font_title"]}', Georgia, serif;
    --font-body:  '{theme["font_body"]}', Georgia, serif;
    --size-xs: 0.75rem; --size-sm: 0.875rem; --size-base: 1rem;
    --size-lg: 1.125rem; --size-xl: 1.375rem;
    --size-2xl: 1.75rem; --size-3xl: 2.25rem;
    --gap-sm: 12px; --gap-md: 24px; --gap-lg: 40px;
    --gap-xl: 56px; --side: 22px; --radius: 14px;
}}
html {{ scroll-behavior: smooth; }}
body {{
    background: var(--primary);
    color: var(--text);
    font-family: var(--font-body);
    font-size: var(--size-base);
    line-height: 1.85;
    max-width: 480px;
    margin: 0 auto;
    -webkit-font-smoothing: antialiased;
    word-wrap: break-word;
    overflow-wrap: break-word;
}}

/* ====== COVER ====== */
.cover-page {{
    height: 297mm; /* Standard static height to prevent layout shifting on PDF engine */
    box-sizing: border-box;
    background: var(--cover-gradient);
    display: block;
    padding-top: 85mm; /* Flexless center positioning */
    padding-left: var(--side);
    padding-right: var(--side);
    position: relative;
    overflow: hidden;
}}
.cover-page::before {{
    content: '';
    position: absolute;
    top: -80px; right: -80px;
    width: 320px; height: 320px;
    border-radius: 50%;
    background: var(--cover-accent);
    opacity: 0.08;
}}
.cover-page::after {{
    content: '';
    position: absolute;
    bottom: 120px; right: -40px;
    width: 180px; height: 180px;
    border-radius: 50%;
    border: 2px solid var(--cover-accent);
    opacity: 0.15;
}}
.cover-circle-big {{
    position: absolute;
    top: 30px; left: 50%;
    transform: translateX(-50%);
    width: 200px; height: 200px;
    border-radius: 50%;
    border: 40px solid var(--cover-accent);
    opacity: 0.06;
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
.cover-year {{ font-size: var(--size-xs); color: rgba(255,255,255,0.35); letter-spacing: 2px; }}
.cover-emoji {{
    font-size: 64px;
    margin-bottom: 28px;
    display: block;
    filter: drop-shadow(0 8px 24px rgba(0,0,0,0.5));
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
    letter-spacing: -0.5px;
    text-shadow: 0 2px 20px rgba(0,0,0,0.5);
}}
.cover-subtitle {{
    font-size: var(--size-sm);
    color: var(--cover-accent);
    font-style: italic;
    margin-bottom: 36px;
    line-height: 1.5;
    opacity: 0.9;
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
    display: flex; align-items: center; justify-content: center;
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

/* ====== NAV ====== */
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
.nav-progress-text {{ font-size: var(--size-xs); color: rgba(255,255,255,0.35); }}

/* ====== DESCRIPTION ====== */
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
.benefits-list {{ display: flex; flex-direction: column; gap: 10px; }}
.benefit-item {{
    display: flex; align-items: flex-start; gap: 12px;
    padding: 13px 15px;
    background: rgba(255,255,255,0.04);
    border-radius: var(--radius);
    border-{border_side}: 3px solid var(--accent);
}}
.benefit-check {{ color: var(--accent); font-weight: 900; font-size: var(--size-lg); flex-shrink: 0; line-height: 1.3; }}
.benefit-text {{ font-size: var(--size-sm); line-height: 1.6; color: rgba(255,255,255,0.82); }}

/* ====== TOC ====== */
.toc-page {{ padding: var(--gap-xl) var(--side); background: var(--primary); }}
.page-title {{
    font-family: var(--font-title);
    font-size: var(--size-2xl);
    font-weight: 900;
    color: #fff;
    margin-bottom: var(--gap-md);
    line-height: 1.2;
}}
.toc-item {{
    display: flex; align-items: center; gap: 14px;
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
.toc-text {{ flex: 1; display: flex; flex-direction: column; gap: 3px; }}
.toc-title {{ font-size: var(--size-sm); font-weight: 600; color: #fff; line-height: 1.3; }}
.toc-sub {{ font-size: var(--size-xs); color: rgba(255,255,255,0.4); }}
.toc-arrow {{ color: rgba(255,255,255,0.25); font-size: var(--size-base); flex-shrink: 0; }}

/* ====== INTRO ====== */
.intro-page {{
    padding: var(--gap-xl) var(--side);
    background: var(--secondary);
    position: relative;
}}

/* ====== CHAPTERS ====== */
.chapter-wrapper {{
    display: block;
    position: relative;
}}
.chapter {{
    border-bottom: 3px solid var(--accent);
}}
.chapter-header {{
    background: var(--gradient);
    padding: var(--gap-xl) var(--side) var(--gap-lg);
    text-align: center;
    position: relative;
    overflow: hidden;
}}
.chapter-meta {{ display: flex; justify-content: center; margin-bottom: 20px; }}
.chapter-number-badge {{
    display: inline-flex; flex-direction: column; align-items: center;
    background: rgba(255,255,255,0.08);
    border: 2px solid var(--accent);
    border-radius: var(--radius);
    padding: 8px 22px;
}}
.ch-label {{ font-size: 0.6rem; letter-spacing: 4px; color: var(--accent); text-transform: uppercase; }}
.ch-num {{ font-family: var(--font-title); font-size: 2rem; font-weight: 900; color: #fff; line-height: 1; }}
.chapter-title {{
    font-family: var(--font-title);
    font-size: var(--size-2xl);
    font-weight: 900;
    color: #fff;
    line-height: 1.25;
    margin-bottom: 10px;
}}
.chapter-subtitle {{ color: var(--accent); font-size: var(--size-sm); font-style: italic; opacity: 0.88; line-height: 1.5; }}
.chapter-hook {{
    margin: var(--gap-md) var(--side) 0;
    padding: 18px 20px;
    border-{border_side}: 4px solid var(--accent);
    background: rgba(255,255,255,0.03);
    font-style: italic;
    font-size: var(--size-base);
    color: rgba(255,255,255,0.75);
    line-height: 1.75;
}}
.chapter-body {{ padding: var(--gap-md) var(--side) var(--gap-lg); }}
.body-text {{
    display: block;
    font-size: var(--size-base);
    line-height: 1.9;
    color: rgba(255,255,255,0.82);
    margin-bottom: 18px;
    word-break: break-word;
    overflow-wrap: break-word;
}}
.box-label {{
    font-size: var(--size-xs);
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 14px;
    display: block;
}}
.key-points-box {{
    padding: 20px;
    background: rgba(255,255,255,0.03);
    border-radius: var(--radius);
    border: 1px solid rgba(255,255,255,0.08);
    margin-bottom: var(--gap-md);
}}
.key-points-box .box-label {{ color: var(--accent); }}
.key-points-list {{ list-style: none; display: flex; flex-direction: column; gap: 8px; }}
.key-point {{
    display: flex; align-items: flex-start; gap: 10px;
    padding: 9px 12px;
    background: rgba(255,255,255,0.04);
    border-radius: 8px;
    font-size: var(--size-sm);
    line-height: 1.55;
    color: rgba(255,255,255,0.85);
}}
.kp-arrow {{ color: var(--accent); flex-shrink: 0; }}
.technique-badge {{
    display: flex; flex-direction: column; gap: 6px;
    padding: 16px 18px;
    background: linear-gradient(135deg, rgba(255,255,255,0.07), rgba(255,255,255,0.03));
    border-radius: var(--radius);
    border: 1px solid var(--accent);
    margin-bottom: var(--gap-md);
}}
.technique-label {{ font-size: var(--size-xs); letter-spacing: 2px; text-transform: uppercase; color: var(--accent); }}
.technique-name {{ font-family: var(--font-title); font-size: var(--size-lg); font-weight: 700; color: #fff; line-height: 1.3; }}
.exercises-section {{
    padding: 20px;
    background: rgba(255,255,255,0.03);
    border-radius: var(--radius);
    border-{border_side}: 4px solid var(--highlight);
    margin-bottom: var(--gap-md);
}}
.exercises-section .box-label {{ color: var(--highlight); }}
.exercises-list {{ display: flex; flex-direction: column; gap: 12px; }}
.exercise-item {{ display: flex; gap: 12px; align-items: flex-start; }}
.exercise-num {{
    background: var(--highlight);
    color: var(--primary);
    width: 26px; height: 26px;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: var(--size-xs); font-weight: 900;
    flex-shrink: 0; margin-top: 2px;
}}
.exercise-item p {{ font-size: var(--size-sm); line-height: 1.65; color: rgba(255,255,255,0.8); }}
.chapter-summary {{
    display: flex; gap: 14px; align-items: flex-start;
    padding: 18px 20px;
    background: rgba(255,255,255,0.04);
    border-radius: var(--radius);
    margin-bottom: var(--gap-md);
    font-style: italic;
}}
.summary-icon {{ font-size: 1.4rem; flex-shrink: 0; }}
.summary-text {{ font-size: var(--size-sm); line-height: 1.75; color: rgba(255,255,255,0.88); }}

/* ====== CONCLUSION / AUTHOR / BACK ====== */
.conclusion-page {{ padding: var(--gap-xl) var(--side); background: var(--gradient); }}
.author-page {{ padding: var(--gap-xl) var(--side); background: var(--secondary); }}
.author-card {{
    background: rgba(255,255,255,0.04);
    border-radius: 20px; padding: 30px 24px;
    text-align: center;
    border: 1px solid rgba(255,255,255,0.08);
}}
.author-avatar {{
    width: 72px; height: 72px;
    background: var(--gradient);
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.8rem;
    margin: 0 auto 18px;
    border: 3px solid var(--accent);
}}
.author-name {{ font-family: var(--font-title); font-size: var(--size-xl); font-weight: 700; color: #fff; margin-bottom: 6px; }}
.author-bio {{ font-size: var(--size-sm); line-height: 1.8; color: rgba(255,255,255,0.65); margin-top: 12px; }}
.back-cover {{
    min-height: 55vh;
    background: var(--cover-gradient);
    padding: var(--gap-xl) var(--side);
    display: flex; flex-direction: column;
    justify-content: center; align-items: center;
    text-align: center; gap: 20px;
    position: relative; overflow: hidden;
}}
.back-cover-title {{ font-family: var(--font-title); font-size: var(--size-2xl); font-weight: 900; color: #fff; line-height: 1.2; }}
.back-cover-text {{ font-size: var(--size-sm); color: rgba(255,255,255,0.75); line-height: 1.75; max-width: 340px; }}
.edition-badge {{
    background: var(--cover-accent); color: var(--primary);
    font-size: var(--size-sm); font-weight: 900;
    font-family: var(--font-title);
    padding: 12px 28px; border-radius: 50px;
}}

/* ====== PROGRESS ====== */
#reading-progress {{
    position: fixed; top: 0; left: 0;
    height: 3px; background: var(--accent);
    z-index: 999; transition: width 0.15s linear; width: 0%;
}}

/* ====== PDF BUTTON ====== */
.pdf-btn {{
    position: fixed; bottom: 22px; right: 18px;
    background: var(--accent); color: var(--primary);
    border: none; border-radius: 50px;
    padding: 13px 20px; font-size: var(--size-sm);
    font-weight: 900; cursor: pointer; z-index: 998;
    display: flex; align-items: center; gap: 7px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.45);
    transition: transform 0.15s;
    font-family: var(--font-body);
}}
.pdf-btn:active {{ transform: scale(0.95); }}

/* ====== CRITICAL RESOLUTION FOR BLANK PAGES & CLIPPING ====== */
.page-break {{
    page-break-inside: avoid !important;
    break-inside: avoid !important;
    margin-bottom: 0 !important;
    padding-bottom: 10px !important;
}}

@media print {{
    .nav-bar, .pdf-btn, #reading-progress {{ display: none !important; }}
    body {{ max-width: 100% !important; width: 100% !important; font-size: 11pt; background: var(--primary) !important; }}
    .cover-page, .description-page, .toc-page, .intro-page, .chapter-wrapper, .conclusion-page, .author-page, .back-cover {{
        page-break-after: always !important;
        break-after: always !important;
        page-break-inside: avoid !important;
        break-inside: avoid !important;
    }}
}}
::-webkit-scrollbar {{ width: 3px; }}
::-webkit-scrollbar-track {{ background: transparent; }}
::-webkit-scrollbar-thumb {{ background: var(--accent); border-radius: 2px; }}
</style>
<script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"></script>
</head>
<body>

<div id="reading-progress"></div>

<section class="cover-page page-break">
    <div class="cover-circle-big"></div>
    <div class="cover-top-bar">
        <span class="cover-genre-tag">{theme["emoji"]} Book</span>
        <span class="cover-year">{year}</span>
    </div>
    <span class="cover-emoji">{theme["emoji"]}</span>
    <div class="cover-line"></div>
    <h1 class="cover-title">{book_data.get("title","")}</h1>
    <p class="cover-subtitle">{book_data.get("subtitle","")}</p>
    <div class="cover-author-row">
        <div class="cover-author-dot">{book_data.get("author","?")[0].upper()}</div>
        <span class="cover-author-name">by {book_data.get("author","Professional Author")}</span>
    </div>
</section>

<nav class="nav-bar">
    <span class="nav-title">{title_display}</span>
    <span class="nav-progress-text" id="progress-text">0% read</span>
</nav>

<section class="description-page page-break">
    <span class="section-label">About This Book</span>
    <p class="description-text">{book_data.get("description","")}</p>
    <span class="section-label">What You Will Learn</span>
    <div class="benefits-list">{benefits_html}</div>
</section>

<section class="toc-page page-break">
    <h2 class="page-title">Table of Contents</h2>
    {toc_html}
</section>

<section class="intro-page page-break">
    <h2 class="page-title">Introduction</h2>
    {intro_html}
</section>

{chapters_html}

<section class="conclusion-page page-break">
    <h2 class="page-title">Conclusion</h2>
    {conc_html}
</section>

<section class="author-page page-break">
    <h2 class="page-title">About the Author</h2>
    <div class="author-card">
        <div class="author-avatar">{theme["emoji"]}</div>
        <p class="author-name">{book_data.get("author","Professional Author")}</p>
        <p class="author-bio">{book_data.get("about_author","")}</p>
    </div>
</section>

<section class="back-cover page-break">
    <h2 class="back-cover-title">{book_data.get("title","")}</h2>
    <p class="back-cover-text">{book_data.get("tagline","")}</p>
    <div class="edition-badge">✦ Professional Edition {year}</div>
</section>

<button class="pdf-btn" id="pdf-btn" onclick="downloadPDF()">📥 Download PDF</button>

<script>
window.addEventListener('scroll', () => {{
    const pct = (window.scrollY / (document.documentElement.scrollHeight - window.innerHeight)) * 100;
    const progressEl = document.getElementById('reading-progress');
    const textEl = document.getElementById('progress-text');
    if(progressEl) progressEl.style.width = pct.toFixed(1) + '%';
    if(textEl) textEl.textContent = Math.round(pct) + '% read';
}});
function scrollToChapter(num) {{
    const el = document.getElementById('chapter-' + num);
    if (el) el.scrollIntoView({{ behavior: 'smooth' }});
}}
async function downloadPDF() {{
    const btn = document.getElementById('pdf-btn');
    btn.style.opacity = '0.6';
    btn.textContent = '⏳ Preparing...';
    
    // Hide UI elements completely before capture
    ['pdf-btn','reading-progress'].forEach(id => {{
        const el = document.getElementById(id);
        if(el) el.style.setProperty('display', 'none', 'important');
    }});
    const navbar = document.querySelector('.nav-bar');
    if(navbar) navbar.style.setProperty('display', 'none', 'important');
    
    const title = document.querySelector('.cover-title')?.textContent || 'book';
    const safeName = title.replace(/[^\\w\\s-]/g,'').trim().replace(/\\s+/g,'_').substring(0,50);
    
    const opt = {{
        margin: 0,
        filename: safeName + '.pdf',
        image: {{ type: 'jpeg', quality: 0.98 }},
        html2canvas: {{
            scale: 2, 
            useCORS: true,
            backgroundColor: '{theme["primary"]}',
            logging: false, 
            letterRendering: true,
            scrollY: 0,
            scrollX: 0
        }},
        jsPDF: {{
            unit: 'mm',
            format: [120, 213],
            orientation: 'portrait'
        }},
        // FIXED: avoid-all mode strictly eliminates shifted empty page breaks
        pagebreak: {{ mode: ['avoid-all', 'css'] }}
    }};
    try {{
        await html2pdf().set(opt).from(document.body).save();
    }} catch(e) {{
        console.error(e);
        window.print();
    }} finally {{
        // Restore UI elements safely
        ['pdf-btn','reading-progress'].forEach(id => {{
            const el = document.getElementById(id);
            if(el) el.style.display = '';
        }});
        if(navbar) navbar.style.display = 'flex';
        btn.style.opacity = '1';
        btn.innerHTML = '📥 Download PDF';
    }}
}}
</script>
</body>
</html>'''
    return html


# ============================================================
# FORMAT 2: AMAZON KDP (white background, 6×9 inch, print-ready)
# ============================================================
def generate_kdp_html(book_data: dict, theme: dict, language: str = "en") -> str:
    """Amazon KDP-ready HTML: white bg, 6x9 inch, print typography"""

    is_rtl = language == "ar"
    dir_attr = 'dir="rtl"' if is_rtl else ''
    year = datetime.now().year
    border_side = 'right' if is_rtl else 'left'

    accent = theme["cover_accent"]
    cover_emoji = theme["emoji"]

    chapters_html = ""
    for i, chapter in enumerate(book_data.get("chapters", []), 1):
        raw_content = chapter.get("content", "")
        paragraphs = [p.strip() for p in raw_content.split('\n') if p.strip()]
        content_html = "".join(f'<p class="body">{p}</p>' for p in paragraphs)

        exercises_html = "".join(
            f'<div class="exercise"><span class="ex-num">{j}.</span><span>{ex}</span></div>'
            for j, ex in enumerate(chapter.get("exercises", []), 1)
        )

        key_points_html = "".join(
            f'<li>{pt}</li>'
            for pt in chapter.get("key_points", [])
        )

        chapters_html += f'''
<div class="chapter-break page-break">
<section class="chapter">
    <div class="ch-header">
        <p class="ch-label">CHAPTER {chapter.get("number", i)}</p>
        <h2 class="ch-title">{chapter.get("title","")}</h2>
        <p class="ch-subtitle">{chapter.get("subtitle","")}</p>
        <div class="ch-rule"></div>
    </div>

    <blockquote class="ch-hook">{chapter.get("hook","")}</blockquote>

    <div class="sidebar">
        <p class="sidebar-label">IN THIS CHAPTER</p>
        <ul class="kp-list">{key_points_html}</ul>
    </div>

    {content_html}

    <div class="technique-box">
        <p class="box-title">🔑 KEY TECHNIQUE: {chapter.get("key_technique","")}</p>
    </div>

    <div class="exercises-box">
        <p class="box-title">✍️ ACTION STEPS</p>
        {exercises_html}
    </div>

    <div class="summary-box">
        <p>💡 <strong>Chapter Takeaway:</strong> {chapter.get("summary","")}</p>
    </div>
</section>
</div>'''

    toc_html = "".join(
        f'<div class="toc-row"><span class="toc-ch">Chapter {i}: {ch.get("title","")}</span><span class="toc-dots"></span></div>'
        for i, ch in enumerate(book_data.get("chapters", []), 1)
    )

    intro_html = "".join(
        f'<p class="body">{p.strip()}</p>'
        for p in book_data.get("introduction", "").split('\n') if p.strip()
    )
    conc_html = "".join(
        f'<p class="body">{p.strip()}</p>'
        for p in book_data.get("conclusion", "").split('\n') if p.strip()
    )

    html = f'''<!DOCTYPE html>
<html lang="{language}" {dir_attr}>
<head>
<meta charset="UTF-8">
<title>{book_data.get("title","")}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Garamond:wght@400;700&family=EB+Garamond:ital,wght@0,400;0,600;0,700;1,400&family=Montserrat:wght@400;700;900&display=swap" rel="stylesheet">
<style>
*, *::before, *::after {{ margin:0; padding:0; box-sizing:border-box; }}
:root {{
    --accent: {accent};
    --font-title: 'Montserrat', 'EB Garamond', serif;
    --font-body: 'EB Garamond', Georgia, serif;
}}
html {{ scroll-behavior: smooth; }}
body {{
    background: #fff;
    color: #111;
    font-family: var(--font-body);
    font-size: 12pt;
    line-height: 1.8;
    max-width: 152mm;
    margin: 0 auto;
    -webkit-font-smoothing: antialiased;
    word-wrap: break-word;
}}

/* ====== COVER (KDP) ====== */
.cover-page {{
    width: 152mm;
    height: 228mm;
    background: linear-gradient(170deg, #111 0%, #222 60%, #333 100%);
    display: block;
    padding-top: 45mm; /* Block layout without flex */
    text-align: center;
    padding-left: 15mm;
    padding-right: 15mm;
    position: relative;
    overflow: hidden;
}}
.cover-page::before {{
    content: '';
    position: absolute;
    top: -50px; left: -50px;
    width: 250px; height: 250px;
    border-radius: 50%;
    border: 40px solid {accent};
    opacity: 0.15;
}}
.cover-page::after {{
    content: '';
    position: absolute;
    bottom: -30px; right: -30px;
    width: 180px; height: 180px;
    border-radius: 50%;
    background: {accent};
    opacity: 0.08;
}}
.cover-accent-line {{
    width: 60px; height: 5px;
    background: {accent};
    border-radius: 3px;
    margin: 20px auto;
}}
.cover-emoji-kdp {{
    font-size: 64px;
    display: block;
    margin-bottom: 20px;
    filter: drop-shadow(0 4px 20px rgba(0,0,0,0.6));
}}
.cover-title-kdp {{
    font-family: var(--font-title);
    font-size: 2.2rem;
    font-weight: 900;
    color: #fff;
    line-height: 1.2;
    letter-spacing: -0.5px;
    text-shadow: 0 2px 20px rgba(0,0,0,0.5);
    margin-bottom: 12px;
}}
.cover-subtitle-kdp {{
    font-size: 1rem;
    color: {accent};
    font-style: italic;
    line-height: 1.5;
    opacity: 0.9;
    margin-bottom: 30px;
}}
.cover-author-kdp {{
    font-family: var(--font-title);
    font-size: 0.85rem;
    letter-spacing: 4px;
    text-transform: uppercase;
    color: rgba(255,255,255,0.5);
    margin-top: 10px;
}}
.cover-year-kdp {{
    position: absolute;
    bottom: 20px;
    font-size: 0.7rem;
    color: rgba(255,255,255,0.2);
    letter-spacing: 2px;
}}

/* ====== FRONT MATTER ====== */
.title-page {{
    height: 228mm;
    display: block;
    padding-top: 60mm;
    text-align: center;
    padding-left: 20mm;
    padding-right: 20mm;
}}
.tp-title {{
    font-family: var(--font-title);
    font-size: 2rem;
    font-weight: 900;
    color: #111;
    margin-bottom: 12px;
    line-height: 1.2;
}}
.tp-subtitle {{
    font-size: 1.1rem;
    color: #555;
    font-style: italic;
    margin-bottom: 40px;
}}
.tp-rule {{
    width: 80px; height: 3px;
    background: {accent};
    margin: 0 auto 40px;
    border-radius: 2px;
}}
.tp-author {{
    font-family: var(--font-title);
    font-size: 1rem;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: #333;
}}
.tp-year {{ margin-top: 30px; font-size: 0.8rem; color: #999; }}

.copyright-page {{ padding: 20mm; font-size: 9pt; color: #666; line-height: 1.7; }}
.copyright-page p {{ margin-bottom: 10px; }}

.toc-page {{ padding: 20mm; }}
.section-heading {{
    font-family: var(--font-title);
    font-size: 1.5rem;
    font-weight: 900;
    color: #111;
    border-bottom: 2px solid {accent};
    padding-bottom: 8px;
    margin-bottom: 24px;
}}
.toc-row {{
    display: flex;
    align-items: baseline;
    padding: 8px 0;
    border-bottom: 1px dotted #ddd;
    font-size: 10.5pt;
}}
.toc-ch {{ flex: 1; }}
.toc-dots {{ flex: 1; }}

.intro-page, .conclusion-page {{ padding: 20mm; }}

/* ====== CHAPTERS ====== */
.chapter {{ padding: 18mm 20mm 20mm; }}
.ch-header {{ margin-bottom: 24px; text-align: center; }}
.ch-label {{
    font-family: var(--font-title);
    font-size: 0.65rem;
    letter-spacing: 4px;
    text-transform: uppercase;
    color: {accent};
    margin-bottom: 8px;
}}
.ch-title {{
    font-family: var(--font-title);
    font-size: 1.8rem;
    font-weight: 900;
    color: #111;
    line-height: 1.2;
    margin-bottom: 8px;
}}
.ch-subtitle {{ font-size: 1rem; color: #555; font-style: italic; margin-bottom: 14px; }}
.ch-rule {{ width: 60px; height: 3px; background: {accent}; margin: 0 auto; border-radius: 2px; }}

blockquote.ch-hook {{
    margin: 20px 0;
    padding: 14px 20px;
    border-{border_side}: 4px solid {accent};
    background: #fafafa;
    font-style: italic;
    font-size: 10.5pt;
    color: #444;
    line-height: 1.7;
}}
.sidebar {{ background: #f7f7f7; border-radius: 8px; padding: 16px 18px; margin-bottom: 20px; border: 1px solid #e5e5e5; }}
.sidebar-label {{ font-family: var(--font-title); font-size: 0.6rem; letter-spacing: 3px; text-transform: uppercase; color: {accent}; margin-bottom: 10px; }}
.kp-list {{ padding-left: 18px; font-size: 10pt; line-height: 1.7; color: #333; }}
.kp-list li {{ margin-bottom: 4px; }}
.body {{ font-size: 11.5pt; line-height: 1.85; color: #1a1a1a; margin-bottom: 14px; text-align: justify; }}
.technique-box {{ background: #f0f0f0; border-radius: 8px; padding: 14px 18px; margin: 20px 0; border-{border_side}: 4px solid {accent}; }}
.exercises-box {{ background: #fefefe; border: 1px solid #e0e0e0; border-radius: 8px; padding: 16px 18px; margin: 20px 0; }}
.box-title {{ font-family: var(--font-title); font-size: 0.8rem; font-weight: 700; letter-spacing: 1px; text-transform: uppercase; color: #333; margin-bottom: 12px; }}
.exercise {{ display: flex; gap: 10px; margin-bottom: 10px; font-size: 10.5pt; line-height: 1.65; color: #333; }}
.ex-num {{ font-weight: 700; color: {accent}; flex-shrink: 0; }}
.summary-box {{ background: #fff9f0; border-radius: 8px; padding: 14px 18px; border: 1px solid #f0d080; font-size: 10.5pt; color: #333; line-height: 1.7; margin-top: 20px; }}

.author-page {{ padding: 20mm; }}
.author-name-kdp {{ font-family: var(--font-title); font-size: 1.4rem; font-weight: 700; margin-bottom: 10px; }}
.author-bio {{ font-size: 10.5pt; line-height: 1.8; color: #333; }}

/* ====== BACK COVER ====== */
.back-cover-kdp {{
    width: 152mm;
    min-height: 120mm;
    background: linear-gradient(170deg, #111 0%, #222 60%, #333 100%);
    padding: 20mm;
    color: #fff;
    position: relative;
    overflow: hidden;
}}
.back-cover-kdp::before {{ content: ''; position: absolute; bottom: -40px; left: -40px; width: 200px; height: 200px; border-radius: 50%; background: {accent}; opacity: 0.07; }}
.bc-title {{ font-family: var(--font-title); font-size: 1.4rem; font-weight: 900; color: #fff; margin-bottom: 16px; }}
.bc-description {{ font-size: 10pt; line-height: 1.8; color: rgba(255,255,255,0.75); margin-bottom: 20px; }}
.bc-benefits {{ list-style: none; margin-bottom: 24px; }}
.bc-benefits li {{ font-size: 9.5pt; color: rgba(255,255,255,0.85); padding: 5px 0; border-bottom: 1px solid rgba(255,255,255,0.08); padding-left: 18px; position: relative; }}
.bc-benefits li::before {{ content: '✓'; position: absolute; left: 0; color: {accent}; font-weight: 900; }}
.bc-author {{ font-size: 9pt; color: rgba(255,255,255,0.4); letter-spacing: 2px; text-transform: uppercase; }}

.kdp-btn {{
    position: fixed; bottom: 22px; right: 18px;
    background: {accent}; color: #111;
    border: none; border-radius: 50px;
    padding: 13px 20px; font-size: 0.9rem;
    font-weight: 900; cursor: pointer; z-index: 998;
    display: flex; align-items: center; gap: 7px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.25);
    font-family: var(--font-title);
}}

/* ====== PRINT RESOLUTION FOR KDP ====== */
.page-break {{
    page-break-before: always !important;
    break-before: always !important;
    page-break-inside: avoid !important;
    break-inside: avoid !important;
}}

@media print {{
    .kdp-btn {{ display: none !important; }}
    body {{ max-width: 152mm !important; width: 152mm !important; font-size: 11.5pt; background: #fff !important; }}
    .cover-page, .title-page, .copyright-page, .toc-page, .intro-page, .chapter-break, .conclusion-page, .author-page, .back-cover-kdp {{
        page-break-after: always !important;
        break-after: always !important;
    }}
}}
</style>
<script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"></script>
</head>
<body>

<section class="cover-page page-break">
    <span class="cover-emoji-kdp">{cover_emoji}</span>
    <div class="cover-accent-line"></div>
    <h1 class="cover-title-kdp">{book_data.get("title","")}</h1>
    <p class="cover-subtitle-kdp">{book_data.get("subtitle","")}</p>
    <p class="cover-author-kdp">by {book_data.get("author","Professional Author")}</p>
    <span class="cover-year-kdp">{year}</span>
</section>

<section class="title-page page-break">
    <h1 class="tp-title">{book_data.get("title","")}</h1>
    <p class="tp-subtitle">{book_data.get("subtitle","")}</p>
    <div class="tp-rule"></div>
    <p class="tp-author">{book_data.get("author","Professional Author")}</p>
    <p class="tp-year">{year}</p>
</section>

<section class="copyright-page page-break">
    <p><strong>{book_data.get("title","")}</strong></p>
    <p>Copyright © {year} {book_data.get("author","Professional Author")}. All rights reserved.</p>
    <p>No part of this publication may be reproduced, distributed, or transmitted in any form without the prior written permission of the publisher.</p>
    <p>Published independently via KDP Publishing.</p>
    <p>First Edition, {year}.</p>
</section>

<section class="toc-page page-break">
    <h2 class="section-heading">Table of Contents</h2>
    <div class="toc-row"><span class="toc-ch">Introduction</span></div>
    {toc_html}
    <div class="toc-row"><span class="toc-ch">Conclusion</span></div>
    <div class="toc-row"><span class="toc-ch">About the Author</span></div>
</section>

<section class="intro-page page-break">
    <h2 class="section-heading">Introduction</h2>
    {intro_html}
</section>

{chapters_html}

<section class="conclusion-page page-break">
    <h2 class="section-heading">Conclusion</h2>
    {conc_html}
</section>

<section class="author-page page-break">
    <h2 class="section-heading">About the Author</h2>
    <p class="author-name-kdp">{book_data.get("author","Professional Author")}</p>
    <p class="author-bio">{book_data.get("about_author","")}</p>
</section>

<section class="back-cover-kdp page-break">
    <p class="bc-title">{book_data.get("title","")}</p>
    <p class="bc-description">{book_data.get("back_cover_description", book_data.get("description",""))}</p>
    <ul class="bc-benefits">
        {"".join(f"<li>{b}</li>" for b in book_data.get("key_benefits",[]))}
    </ul>
    <p class="bc-author">by {book_data.get("author","Professional Author")}</p>
</section>

<button class="kdp-btn" id="kdp-btn" onclick="downloadKDP()">📥 Download for KDP</button>

<script>
async function downloadKDP() {{
    const btn = document.getElementById('kdp-btn');
    btn.style.opacity = '0.6';
    btn.textContent = '⏳ Preparing...';
    btn.style.setProperty('display', 'none', 'important');
    
    const title = '{book_data.get("title","book")}'.replace(/[^\\w\\s-]/g,'').trim().replace(/\\s+/g,'_').substring(0,50);
    const opt = {{
        margin: 0,
        filename: title + '_KDP.pdf',
        image: {{ type: 'jpeg', quality: 0.98 }},
        html2canvas: {{
            scale: 2, 
            useCORS: true,
            backgroundColor: '#ffffff',
            logging: false, 
            letterRendering: true,
            scrollY: 0,
            scrollX: 0
        }},
        jsPDF: {{
            unit: 'mm',
            format: [152, 228],
            orientation: 'portrait'
        }},
        pagebreak: {{ mode: ['avoid-all', 'css'] }}
    }};
    try {{
        await html2pdf().set(opt).from(document.body).save();
    }} catch(e) {{
        console.error(e);
        window.print();
    }} finally {{
        btn.style.display = 'flex';
        btn.style.opacity = '1';
        btn.textContent = '📥 Download for KDP';
    }}
}}
</script>
</body>
</html>'''
    return html


def get_niche_suggestions(language: str = "en") -> list:
    messages = [
        {"role": "system", "content": "You are a digital marketing expert specializing in ebook sales."},
        {"role": "user", "content": f"""List 15 highly profitable ebook niches for 2025.
Return ONLY a JSON array, no other text:
[
  {{
    "niche": "niche name",
    "title_idea": "specific book title idea",
    "why_profitable": "one sentence why it sells",
    "price_range": "$X-$Y"
  }}
]
Language: {language}"""}
    ]
    content = call_groq(messages, max_tokens=2000)
    content = content.strip()
    if "```json" in content:
        content = content.split("```json")[1].split("```")[0]
    elif "```" in content:
        content = content.split("```")[1].split("```")[0]
    start = content.find('[')
    end = content.rfind(']') + 1
    if start >= 0 and end > start:
        content = content[start:end]
    return json.loads(content)


def generate_suggestions_page(suggestions: list, language: str) -> str:
    items_html = ""
    for i, s in enumerate(suggestions, 1):
        items_html += f'''
        <div class="suggestion-card">
            <div class="suggestion-num">{i:02d}</div>
            <div class="suggestion-content">
                <h3>{s.get("niche","")}</h3>
                <p class="title-idea">💡 {s.get("title_idea","")}</p>
                <p class="why">{s.get("why_profitable","")}</p>
                <span class="price">{s.get("price_range","$20-50")}</span>
            </div>
        </div>'''
    return f'''<!DOCTYPE html>
<html lang="{language}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Profitable Book Niches 2025</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{background:#0a0a0a;color:#fff;font-family:system-ui;max-width:480px;margin:0 auto;padding:20px}}
h1{{font-size:1.8rem;text-align:center;margin-bottom:10px}}
.subtitle{{text-align:center;color:#888;margin-bottom:30px;font-size:.9rem}}
.suggestion-card{{background:#1a1a1a;border-radius:14px;padding:18px;margin-bottom:14px;border-left:4px solid #f97316;display:flex;gap:14px}}
.suggestion-num{{font-size:1.4rem;font-weight:900;color:#f97316;min-width:34px}}
h3{{font-size:1rem;margin-bottom:7px}}
.title-idea{{color:#fbbf24;font-size:.85rem;margin-bottom:5px}}
.why{{color:#888;font-size:.8rem;margin-bottom:9px}}
.price{{background:#f97316;color:#000;padding:3px 12px;border-radius:20px;font-size:.78rem;font-weight:700}}
</style>
</head>
<body>
<h1>🔥 Top Profitable Niches 2025</h1>
<p class="subtitle">Best ebook niches for TikTok & Amazon KDP</p>
{items_html}
</body>
</html>'''


def main():
    book_title  = os.environ.get("BOOK_TITLE", "")
    language    = os.environ.get("BOOK_LANGUAGE", "fr")  # Default to French for Maria Talks
    action      = os.environ.get("ACTION", "generate")
    author_name = os.environ.get("BOOK_AUTHOR", "").strip()
    book_format = os.environ.get("BOOK_FORMAT", "pdf")  # "pdf" or "kdp"

    if not GROQ_API_KEY:
        print("ERROR: GROQ_API_KEY not set!")
        sys.exit(1)

    os.makedirs("output", exist_ok=True)

    if action == "suggest":
        print(f"🎯 Getting niche suggestions [{language}]...")
        suggestions = get_niche_suggestions(language)
        suggestions_html = generate_suggestions_page(suggestions, language)
        with open("output/niche_suggestions.html", "w", encoding="utf-8") as f:
            f.write(suggestions_html)
        print("✅ output/niche_suggestions.html")

    elif action == "generate":
        if not book_title:
            print("ERROR: BOOK_TITLE not set!")
            sys.exit(1)

        fmt_label = "Amazon KDP (6×9 print)" if book_format == "kdp" else "PDF Direct Sell"
        print(f"📚 Generating: '{book_title}' [{language}] — Format: {fmt_label}")

        theme_key = detect_theme(book_title, language)
        theme = BOOK_THEMES[theme_key]
        print(f"🎨 Theme Detected: {theme_key} {theme['emoji']}")

        # STEP 1: Generate structural skeleton metadata
        print("✍️  [Phase 1] Writing Book Structure Skeleton...")
        book_data = generate_book_structure(book_title, language)

        # STEP 2: Loop through chapters and generate deep focused content for each one independently
        print("✍️  [Phase 2] Generating non-repetitive focused chapters...")
        completed_chapters = []
        for ch in book_data.get("chapters", []):
            print(f"🚀 Generating Chapter {ch['number']}: {ch['title']}...")
            try:
                ch_details = generate_single_chapter_content(book_title, ch, language)
                ch.update(ch_details)  # Merge details into chapter skeleton
                completed_chapters.append(ch)
            except Exception as e:
                print(f"⚠️ Error generating Chapter {ch['number']}: {e}. Retrying once...")
                # Simple single-retry mechanism to ensure robustness against API timeouts
                ch_details = generate_single_chapter_content(book_title, ch, language)
                ch.update(ch_details)
                completed_chapters.append(ch)
                
        book_data["chapters"] = completed_chapters

        if author_name:
            book_data["author"] = author_name

        with open("output/book_data.json", "w", encoding="utf-8") as f:
            json.dump(book_data, f, ensure_ascii=False, indent=2)

        print("🎨 Designing layout and compiling HTML...")
        if book_format == "kdp":
            html = generate_kdp_html(book_data, theme, language)
            format_suffix = "_KDP"
        else:
            html = generate_pdf_html(book_data, theme, language)
            format_suffix = "_PDF"

        safe_title = re.sub(r'[^\w\s-]', '', book_title).strip().replace(' ', '_')[:50]
        filename = f"output/{safe_title}_{language}{format_suffix}.html"

        with open(filename, "w", encoding="utf-8") as f:
            f.write(html)

        print(f"✅ Book generated: {filename}")
        print(f"📖 Title:    {book_data.get('title', book_title)}")
        print(f"📝 Chapters: {len(book_data.get('chapters', []))}")
        print(f"📦 Format:   {fmt_label}")

        metadata = {
            "generated_at": datetime.now().isoformat(),
            "title": book_data.get("title", book_title),
            "subtitle": book_data.get("subtitle", ""),
            "language": language,
            "theme": theme_key,
            "format": book_format,
            "chapters": len(book_data.get("chapters", [])),
            "file": filename
        }
        with open("output/metadata.json", "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()

```
