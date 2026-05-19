#!/usr/bin/env python3
"""
📚 Professional Book Generator - Powered by Groq
Generates complete, sellable ebooks with professional design
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
        "primary": "#1e1b4b",
        "secondary": "#312e81",
        "accent": "#a78bfa",
        "text": "#ede9fe",
        "highlight": "#c4b5fd",
        "font_title": "Nunito",
        "font_body": "Open Sans",
        "emoji": "✨",
        "gradient": "linear-gradient(160deg, #1e1b4b 0%, #312e81 50%, #3730a3 100%)",
        "cover_gradient": "linear-gradient(160deg, #0f0c29 0%, #302b63 50%, #24243e 100%)",
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

def detect_theme(title: str, language: str = "en") -> str:
    title_lower = title.lower()
    keywords = {
        "business": ["business","startup","entrepreneur","marketing","sales","brand","عمل","تجارة","ريادة","affaires","negocio"],
        "health": ["health","fitness","wellness","diet","nutrition","صحة","لياقة","تغذية","santé","salud"],
        "finance": ["money","invest","finance","wealth","rich","مال","استثمار","ثروة","argent","dinero"],
        "self_help": ["confidence","mindset","habit","success","motivation","ثقة","عادات","نجاح","confiance","confianza","secret","réussir","réussite"],
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
        "temperature": 0.7,
        "top_p": 0.9
    }
    response = requests.post(GROQ_API_URL, headers=headers, json=payload)
    if response.status_code != 200:
        raise Exception(f"Groq API Error: {response.status_code} - {response.text}")
    return response.json()["choices"][0]["message"]["content"]

def generate_book_structure(title: str, language: str = "en") -> dict:
    """Generate book structure optimized like bestselling books"""

    lang_prompts = {
        "en": f"You are a professional bestselling author. Your books follow the structure of top sellers like Atomic Habits, The Psychology of Money, and Think and Grow Rich.",
        "ar": f"أنت مؤلف محترف ومتخصص في الكتب الأكثر مبيعًا. كتبك تتبع هيكل أفضل الكتب مبيعًا مثل العادات الذرية وعلم النفس والمال.",
        "fr": f"Vous êtes un auteur professionnel spécialisé dans les best-sellers. Vos livres suivent la structure des meilleures ventes comme Atomic Habits et Thinking Fast and Slow.",
        "es": f"Eres un autor profesional especializado en bestsellers. Tus libros siguen la estructura de los más vendidos como Hábitos Atómicos.",
        "de": f"Sie sind ein professioneller Autor, spezialisiert auf Bestseller. Ihre Bücher folgen der Struktur von Top-Sellern wie Atomic Habits.",
        "pt": f"Você é um autor profissional especializado em bestsellers. Seus livros seguem a estrutura dos mais vendidos como Hábitos Atômicos.",
        "it": f"Sei un autore professionista specializzato in bestseller. I tuoi libri seguono la struttura dei più venduti come Le Abitudini Atomiche.",
        "zh": f"您是一位专业畅销书作者。您的书籍遵循《原子习惯》等顶级畅销书的结构。",
        "ja": f"あなたはプロのベストセラー作家です。あなたの本は『習慣の力』などのトップセラーの構成に従っています。",
        "ru": f"Вы профессиональный автор бестселлеров. Ваши книги следуют структуре таких бестселлеров, как «Атомные привычки»."
    }

    system_msg = lang_prompts.get(language, lang_prompts["en"])

    messages = [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": f"""
Create a complete, professional, sellable ebook about: "{title}"

CRITICAL RULES FOR BESTSELLING BOOKS:
1. Hook the reader from the FIRST sentence - start with a shocking fact, story, or bold claim
2. Every chapter must solve ONE specific problem with actionable steps
3. Use real-world examples and mini-stories (like Malcolm Gladwell style)
4. Each chapter: Problem → Science/Evidence → Solution → Action Steps
5. Write like you're talking to a smart friend, not giving a lecture
6. Use short paragraphs (2-4 sentences max) for mobile reading
7. Include specific numbers, stats, and named techniques
8. Chapters should build on each other (progressive revelation)

Return ONLY valid JSON (no markdown, no backticks):

{{
  "title": "powerful book title",
  "subtitle": "specific, benefit-driven subtitle (what reader GETS)",
  "author": "Professional Author",
  "tagline": "one sentence that makes someone NEED this book",
  "description": "200 words that create desire: start with the problem, agitate it, then promise the solution. Be specific about transformation.",
  "target_audience": "exactly who this is for (be specific: e.g. 'people stuck in 9-5 jobs dreaming of financial freedom')",
  "key_benefits": [
    "Specific benefit 1 with number (e.g. 'Build 3 income streams in 90 days')",
    "Specific benefit 2",
    "Specific benefit 3",
    "Specific benefit 4",
    "Specific benefit 5"
  ],
  "chapters": [
    {{
      "number": 1,
      "title": "Chapter Title (use power words)",
      "subtitle": "The specific promise of this chapter",
      "hook": "One shocking opening sentence that grabs attention",
      "key_points": ["specific point 1", "specific point 2", "specific point 3"],
      "content": "Write 700-900 words of PREMIUM content. Structure: 1) Open with a mini-story or shocking fact (100w). 2) Explain the core problem/concept with evidence (200w). 3) Reveal the solution/technique with a specific name (200w). 4) Give a real-world example of how it works (150w). 5) Break it into 3-5 numbered actionable steps (250w). Use short paragraphs. NO filler words. Every sentence must earn its place.",
      "key_technique": "Name the main technique/framework taught in this chapter (e.g. 'The 2-Minute Rule', 'The PARA Method')",
      "exercises": [
        "Exercise 1: Specific, doable action with clear instructions",
        "Exercise 2: Follow-up action to reinforce the lesson"
      ],
      "summary": "The one thing to remember from this chapter (one powerful sentence)"
    }}
  ],
  "introduction": "250 words: Start with a relatable struggle. Promise transformation. Explain what makes this book different. Give a roadmap of chapters. End with a motivating call to action.",
  "conclusion": "250 words: Celebrate the reader's journey. Recap the 3 biggest transformations. Paint a vivid picture of their new life. Give ONE final action step. End with an inspiring quote or challenge.",
  "about_author": "120 words: Third-person bio. Mention real-sounding credentials, personal struggle they overcame, and why they wrote this book."
}}

Write 8 chapters. Language: {language}. Make this worth $47-197 USD.
"""}
    ]

    content = call_groq(messages, max_tokens=7000)
    content = content.strip()

    # Clean JSON
    if "```json" in content:
        content = content.split("```json")[1].split("```")[0]
    elif "```" in content:
        content = content.split("```")[1].split("```")[0]
    content = content.strip()

    start = content.find('{')
    end = content.rfind('}') + 1
    if start >= 0 and end > start:
        content = content[start:end]

    return json.loads(content)


def generate_html_book(book_data: dict, theme: dict, language: str = "en") -> str:
    """Generate a stunning HTML ebook with zero text-cutting issues"""

    is_rtl = language == "ar"
    dir_attr = 'dir="rtl"' if is_rtl else ''

    # --- Chapters HTML ---
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

        # Split content into paragraphs — each wrapped safely
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

        <div class="notes-section">
            <h4 class="notes-label">📝 MY NOTES</h4>
            <div class="notes-lines">
                {''.join('<div class="note-line"></div>' for _ in range(5))}
            </div>
        </div>

    </div>
</section>'''

    # --- Benefits HTML ---
    benefits_html = "".join(
        f'<div class="benefit-item"><span class="benefit-check">✓</span><span class="benefit-text">{b}</span></div>'
        for b in book_data.get("key_benefits", [])
    )

    # --- TOC HTML ---
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

    # --- Introduction paragraphs ---
    intro_raw = book_data.get("introduction", "")
    intro_html = "".join(
        f'<p class="body-text">{p.strip()}</p>'
        for p in intro_raw.split('\n') if p.strip()
    )

    # --- Conclusion paragraphs ---
    conc_raw = book_data.get("conclusion", "")
    conc_html = "".join(
        f'<p class="body-text">{p.strip()}</p>'
        for p in conc_raw.split('\n') if p.strip()
    )

    title_short = book_data.get('title', '')
    title_display = title_short[:28] + "…" if len(title_short) > 28 else title_short

    html = f'''<!DOCTYPE html>
<html lang="{language}" {dir_attr}>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>{book_data.get("title","")}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family={theme["font_title"].replace(" ","+")},wght@400;700;900&family={theme["font_body"].replace(" ","+")},wght@300;400;600&display=swap" rel="stylesheet">
<style>
/* ===================== RESET & BASE ===================== */
*, *::before, *::after {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}}

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

    /* Typography scale — prevents cramped text */
    --size-xs:   0.75rem;
    --size-sm:   0.875rem;
    --size-base: 1rem;
    --size-lg:   1.125rem;
    --size-xl:   1.375rem;
    --size-2xl:  1.75rem;
    --size-3xl:  2.25rem;

    /* Spacing */
    --gap-sm:  12px;
    --gap-md:  24px;
    --gap-lg:  40px;
    --gap-xl:  56px;
    --side:    22px;
    --radius:  14px;
}}

html {{ scroll-behavior: smooth; }}

body {{
    background: var(--primary);
    color: var(--text);
    font-family: var(--font-body);
    font-size: var(--size-base);
    /* KEY FIX: line-height prevents text overlap across pages */
    line-height: 1.85;
    max-width: 480px;
    margin: 0 auto;
    -webkit-font-smoothing: antialiased;
    word-wrap: break-word;
    overflow-wrap: break-word;
}}

/* ===================== COVER ===================== */
.cover-page {{
    min-height: 100vh;
    background: var(--cover-gradient);
    display: flex;
    flex-direction: column;
    justify-content: flex-end;
    align-items: flex-start;
    padding: 60px var(--side) 50px;
    position: relative;
    overflow: hidden;
}}

/* Decorative circles on cover */
.cover-page::before {{
    content: '';
    position: absolute;
    top: -80px;
    right: -80px;
    width: 320px;
    height: 320px;
    border-radius: 50%;
    background: var(--cover-accent);
    opacity: 0.08;
}}
.cover-page::after {{
    content: '';
    position: absolute;
    bottom: 120px;
    right: -40px;
    width: 180px;
    height: 180px;
    border-radius: 50%;
    border: 2px solid var(--cover-accent);
    opacity: 0.15;
}}

.cover-top-bar {{
    position: absolute;
    top: var(--side);
    left: var(--side);
    right: var(--side);
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
    font-size: 56px;
    margin-bottom: 28px;
    display: block;
    filter: drop-shadow(0 8px 24px rgba(0,0,0,0.5));
}}

.cover-line {{
    width: 48px;
    height: 4px;
    background: var(--cover-accent);
    border-radius: 2px;
    margin-bottom: 20px;
}}

.cover-title {{
    font-family: var(--font-title);
    font-size: clamp(1.8rem, 6vw, 2.4rem);
    font-weight: 900;
    color: #fff;
    line-height: 1.15;
    margin-bottom: 14px;
    letter-spacing: -0.5px;
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
    width: 32px;
    height: 32px;
    background: var(--cover-accent);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
}}

.cover-author-name {{
    font-size: var(--size-xs);
    letter-spacing: 3px;
    text-transform: uppercase;
    color: rgba(255,255,255,0.6);
}}

/* ===================== NAV BAR ===================== */
.nav-bar {{
    position: sticky;
    top: 0;
    background: rgba(0,0,0,0.92);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
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
    letter-spacing: 0.5px;
}}

.nav-progress-text {{
    font-size: var(--size-xs);
    color: rgba(255,255,255,0.35);
}}

/* ===================== DESCRIPTION PAGE ===================== */
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

.benefits-list {{
    display: flex;
    flex-direction: column;
    gap: 10px;
}}

.benefit-item {{
    display: flex;
    align-items: flex-start;
    gap: 12px;
    padding: 13px 15px;
    background: rgba(255,255,255,0.04);
    border-radius: var(--radius);
    border-left: 3px solid var(--accent);
}}

.benefit-check {{
    color: var(--accent);
    font-weight: 900;
    font-size: var(--size-lg);
    flex-shrink: 0;
    line-height: 1.3;
}}

.benefit-text {{
    font-size: var(--size-sm);
    line-height: 1.6;
    color: rgba(255,255,255,0.82);
}}

/* ===================== TABLE OF CONTENTS ===================== */
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
    line-height: 1.2;
}}

.toc-item {{
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 14px 0;
    border-bottom: 1px solid rgba(255,255,255,0.06);
    cursor: pointer;
    transition: padding-left 0.2s;
}}
.toc-item:hover {{ padding-left: 8px; }}
.toc-item:hover .toc-arrow {{ color: var(--accent); }}

.toc-num {{
    font-family: var(--font-title);
    font-size: var(--size-lg);
    font-weight: 900;
    color: var(--accent);
    min-width: 34px;
}}

.toc-text {{
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 3px;
}}

.toc-title {{
    font-size: var(--size-sm);
    font-weight: 600;
    color: #fff;
    line-height: 1.3;
}}

.toc-sub {{
    font-size: var(--size-xs);
    color: rgba(255,255,255,0.4);
    line-height: 1.4;
}}

.toc-arrow {{
    color: rgba(255,255,255,0.25);
    font-size: var(--size-base);
    transition: color 0.2s;
    flex-shrink: 0;
}}

/* ===================== INTRO PAGE ===================== */
.intro-page {{
    padding: var(--gap-xl) var(--side);
    background: var(--secondary);
    position: relative;
}}

.intro-page::before {{
    content: '\u201C';
    font-family: var(--font-title);
    font-size: 140px;
    color: var(--accent);
    opacity: 0.07;
    position: absolute;
    top: 10px;
    left: 10px;
    line-height: 1;
    pointer-events: none;
}}

/* ===================== CHAPTERS ===================== */
.chapter {{
    /* KEY FIX: no overflow hidden — lets content breathe */
    border-bottom: 3px solid var(--accent);
}}

.chapter-header {{
    background: var(--gradient);
    padding: var(--gap-xl) var(--side) var(--gap-lg);
    text-align: center;
    position: relative;
    overflow: hidden;
}}

.chapter-header::before {{
    content: '';
    position: absolute;
    inset: 0;
    background: radial-gradient(circle at 30% 50%, rgba(255,255,255,0.04) 0%, transparent 70%);
    pointer-events: none;
}}

.chapter-meta {{
    display: flex;
    justify-content: center;
    margin-bottom: 20px;
}}

.chapter-number-badge {{
    display: inline-flex;
    flex-direction: column;
    align-items: center;
    background: rgba(255,255,255,0.08);
    border: 2px solid var(--accent);
    border-radius: var(--radius);
    padding: 8px 22px;
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
    line-height: 1.25;
    margin-bottom: 10px;
}}

.chapter-subtitle {{
    color: var(--accent);
    font-size: var(--size-sm);
    font-style: italic;
    opacity: 0.88;
    line-height: 1.5;
}}

/* Hook quote */
.chapter-hook {{
    margin: var(--gap-md) var(--side) 0;
    padding: 18px 20px;
    border-left: 4px solid var(--accent);
    background: rgba(255,255,255,0.03);
    border-radius: 0 var(--radius) var(--radius) 0;
    font-style: italic;
    font-size: var(--size-base);
    color: rgba(255,255,255,0.75);
    line-height: 1.75;
}}

/* Chapter body wrapper — critical for no-cut layout */
.chapter-body {{
    padding: var(--gap-md) var(--side) var(--gap-lg);
}}

/* KEY FIX: body-text uses display:block + avoids page-break inside */
.body-text {{
    display: block;
    font-size: var(--size-base);
    line-height: 1.9;
    color: rgba(255,255,255,0.82);
    margin-bottom: 18px;
    page-break-inside: avoid;
    /* Forces text to wrap, never overflow */
    word-break: break-word;
    overflow-wrap: break-word;
    hyphens: auto;
}}

/* ===== BOXES ===== */
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

.key-points-list {{
    list-style: none;
    display: flex;
    flex-direction: column;
    gap: 8px;
}}

.key-point {{
    display: flex;
    align-items: flex-start;
    gap: 10px;
    padding: 9px 12px;
    background: rgba(255,255,255,0.04);
    border-radius: 8px;
    font-size: var(--size-sm);
    line-height: 1.55;
    color: rgba(255,255,255,0.85);
}}

.kp-arrow {{
    color: var(--accent);
    flex-shrink: 0;
    font-style: normal;
    line-height: 1.55;
}}

/* Technique badge */
.technique-badge {{
    display: flex;
    flex-direction: column;
    gap: 6px;
    padding: 16px 18px;
    background: linear-gradient(135deg, rgba(255,255,255,0.07), rgba(255,255,255,0.03));
    border-radius: var(--radius);
    border: 1px solid var(--accent);
    margin-bottom: var(--gap-md);
}}

.technique-label {{
    font-size: var(--size-xs);
    letter-spacing: 2px;
    text-transform: uppercase;
    color: var(--accent);
}}

.technique-name {{
    font-family: var(--font-title);
    font-size: var(--size-lg);
    font-weight: 700;
    color: #fff;
    line-height: 1.3;
}}

/* Exercises */
.exercises-section {{
    padding: 20px;
    background: rgba(255,255,255,0.03);
    border-radius: var(--radius);
    border-left: 4px solid var(--highlight);
    margin-bottom: var(--gap-md);
}}

.exercises-section .box-label {{ color: var(--highlight); }}

.exercises-list {{
    display: flex;
    flex-direction: column;
    gap: 12px;
}}

.exercise-item {{
    display: flex;
    gap: 12px;
    align-items: flex-start;
}}

.exercise-num {{
    background: var(--highlight);
    color: var(--primary);
    width: 26px;
    height: 26px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: var(--size-xs);
    font-weight: 900;
    flex-shrink: 0;
    margin-top: 2px;
}}

.exercise-item p {{
    font-size: var(--size-sm);
    line-height: 1.65;
    color: rgba(255,255,255,0.8);
    word-break: break-word;
}}

/* Summary */
.chapter-summary {{
    display: flex;
    gap: 14px;
    align-items: flex-start;
    padding: 18px 20px;
    background: rgba(255,255,255,0.04);
    border-radius: var(--radius);
    margin-bottom: var(--gap-md);
    font-style: italic;
}}

.summary-icon {{
    font-size: 1.4rem;
    flex-shrink: 0;
    line-height: 1.4;
}}

.summary-text {{
    font-size: var(--size-sm);
    line-height: 1.75;
    color: rgba(255,255,255,0.88);
    word-break: break-word;
}}

/* Notes */
.notes-section {{
    padding: 18px 20px;
    background: rgba(255,255,255,0.02);
    border-radius: var(--radius);
    border: 1px dashed rgba(255,255,255,0.12);
}}

.notes-label {{
    font-size: var(--size-xs);
    letter-spacing: 2px;
    text-transform: uppercase;
    color: rgba(255,255,255,0.35);
    margin-bottom: 14px;
    display: block;
}}

.notes-lines {{
    display: flex;
    flex-direction: column;
    gap: 24px;
}}

.note-line {{
    height: 1px;
    background: rgba(255,255,255,0.08);
    border-radius: 1px;
}}

/* ===================== CONCLUSION ===================== */
.conclusion-page {{
    padding: var(--gap-xl) var(--side);
    background: var(--gradient);
    text-align: center;
}}

.conclusion-page .page-title {{ text-align: center; }}

/* ===================== AUTHOR PAGE ===================== */
.author-page {{
    padding: var(--gap-xl) var(--side);
    background: var(--secondary);
}}

.author-card {{
    background: rgba(255,255,255,0.04);
    border-radius: 20px;
    padding: 30px 24px;
    text-align: center;
    border: 1px solid rgba(255,255,255,0.08);
}}

.author-avatar {{
    width: 72px;
    height: 72px;
    background: var(--gradient);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.8rem;
    margin: 0 auto 18px;
    border: 3px solid var(--accent);
}}

.author-name {{
    font-family: var(--font-title);
    font-size: var(--size-xl);
    font-weight: 700;
    color: #fff;
    margin-bottom: 6px;
}}

.author-bio {{
    font-size: var(--size-sm);
    line-height: 1.8;
    color: rgba(255,255,255,0.65);
    margin-top: 12px;
    word-break: break-word;
}}

/* ===================== BACK COVER ===================== */
.back-cover {{
    min-height: 55vh;
    background: var(--cover-gradient);
    padding: var(--gap-xl) var(--side);
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
    gap: 20px;
    position: relative;
    overflow: hidden;
}}

.back-cover::before {{
    content: '';
    position: absolute;
    bottom: -60px;
    left: -60px;
    width: 250px;
    height: 250px;
    border-radius: 50%;
    background: var(--cover-accent);
    opacity: 0.06;
}}

.back-cover-title {{
    font-family: var(--font-title);
    font-size: var(--size-2xl);
    font-weight: 900;
    color: #fff;
    line-height: 1.2;
}}

.back-cover-text {{
    font-size: var(--size-sm);
    color: rgba(255,255,255,0.75);
    line-height: 1.75;
    max-width: 340px;
}}

.edition-badge {{
    background: var(--cover-accent);
    color: var(--primary);
    font-size: var(--size-sm);
    font-weight: 900;
    font-family: var(--font-title);
    padding: 12px 28px;
    border-radius: 50px;
    letter-spacing: 1px;
}}

/* ===================== READING PROGRESS ===================== */
#reading-progress {{
    position: fixed;
    top: 0;
    left: 0;
    height: 3px;
    background: var(--accent);
    z-index: 999;
    transition: width 0.15s linear;
    width: 0%;
}}

/* ===================== PDF BUTTON ===================== */
.pdf-btn {{
    position: fixed;
    bottom: 22px;
    right: 18px;
    background: var(--accent);
    color: var(--primary);
    border: none;
    border-radius: 50px;
    padding: 13px 20px;
    font-size: var(--size-sm);
    font-weight: 900;
    cursor: pointer;
    z-index: 998;
    display: flex;
    align-items: center;
    gap: 7px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.45);
    transition: transform 0.15s, box-shadow 0.15s;
    font-family: var(--font-body);
}}

.pdf-btn:active {{ transform: scale(0.95); }}

/* ===================== PRINT STYLES ===================== */
@media print {{
    .nav-bar, .pdf-btn, #reading-progress {{ display: none !important; }}
    body {{ max-width: 100%; font-size: 11pt; }}
    .cover-page {{ min-height: 100vh; page-break-after: always; }}
    /* KEY FIX: avoid orphaned lines on print */
    .body-text {{ orphans: 3; widows: 3; }}
    .chapter {{ page-break-before: always; }}
    .chapter-header, .key-points-box, .exercises-section,
    .chapter-summary, .technique-badge {{
        page-break-inside: avoid;
    }}
}}

/* ===================== SCROLLBAR ===================== */
::-webkit-scrollbar {{ width: 3px; }}
::-webkit-scrollbar-track {{ background: transparent; }}
::-webkit-scrollbar-thumb {{ background: var(--accent); border-radius: 2px; }}
</style>
<script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"></script>
</head>
<body>

<div id="reading-progress"></div>

<!-- ==================== COVER ==================== -->
<section class="cover-page">
    <div class="cover-top-bar">
        <span class="cover-genre-tag">{theme["emoji"]} Book</span>
        <span class="cover-year">{datetime.now().year}</span>
    </div>
    <span class="cover-emoji">{theme["emoji"]}</span>
    <div class="cover-line"></div>
    <h1 class="cover-title">{book_data.get("title","")}</h1>
    <p class="cover-subtitle">{book_data.get("subtitle","")}</p>
    <div class="cover-author-row">
        <div class="cover-author-dot">{theme["emoji"]}</div>
        <span class="cover-author-name">by {book_data.get("author","Professional Author")}</span>
    </div>
</section>

<!-- ==================== NAV ==================== -->
<nav class="nav-bar">
    <span class="nav-title">{title_display}</span>
    <span class="nav-progress-text" id="progress-text">0% read</span>
</nav>

<!-- ==================== DESCRIPTION ==================== -->
<section class="description-page">
    <span class="section-label">About This Book</span>
    <p class="description-text">{book_data.get("description","")}</p>

    <span class="section-label">What You Will Learn</span>
    <div class="benefits-list">
        {benefits_html}
    </div>
</section>

<!-- ==================== TOC ==================== -->
<section class="toc-page">
    <h2 class="page-title">Table of Contents</h2>
    {toc_html}
</section>

<!-- ==================== INTRODUCTION ==================== -->
<section class="intro-page">
    <h2 class="page-title">Introduction</h2>
    {intro_html}
</section>

<!-- ==================== CHAPTERS ==================== -->
{chapters_html}

<!-- ==================== CONCLUSION ==================== -->
<section class="conclusion-page">
    <h2 class="page-title">Conclusion</h2>
    {conc_html}
</section>

<!-- ==================== AUTHOR ==================== -->
<section class="author-page">
    <h2 class="page-title">About the Author</h2>
    <div class="author-card">
        <div class="author-avatar">{theme["emoji"]}</div>
        <p class="author-name">{book_data.get("author","Professional Author")}</p>
        <p class="author-bio">{book_data.get("about_author","")}</p>
    </div>
</section>

<!-- ==================== BACK COVER ==================== -->
<section class="back-cover">
    <h2 class="back-cover-title">{book_data.get("title","")}</h2>
    <p class="back-cover-text">{book_data.get("tagline","")}</p>
    <div class="edition-badge">✦ Professional Edition</div>
</section>

<!-- ==================== PDF BUTTON ==================== -->
<button class="pdf-btn" id="pdf-btn" onclick="downloadPDF()">📥 Download PDF</button>

<script>
// Reading progress bar
window.addEventListener('scroll', () => {{
    const scrolled = window.scrollY;
    const total = document.documentElement.scrollHeight - window.innerHeight;
    const pct = total > 0 ? (scrolled / total) * 100 : 0;
    document.getElementById('reading-progress').style.width = pct.toFixed(1) + '%';
    document.getElementById('progress-text').textContent = Math.round(pct) + '% read';
}});

// Smooth scroll to chapter
function scrollToChapter(num) {{
    const el = document.getElementById('chapter-' + num);
    if (el) el.scrollIntoView({{ behavior: 'smooth' }});
}}

// PDF Download
async function downloadPDF() {{
    const btn = document.getElementById('pdf-btn');
    btn.style.opacity = '0.6';
    btn.textContent = '⏳ Preparing...';

    const hide = ['pdf-btn','reading-progress'];
    hide.forEach(id => {{ const el = document.getElementById(id); if(el) el.style.display='none'; }});
    document.querySelector('.nav-bar').style.display = 'none';

    const title = document.querySelector('.cover-title')?.textContent || 'book';
    const safeName = title.replace(/[^\\w\\s-]/g,'').trim().replace(/\\s+/g,'_').substring(0,50);

    const opt = {{
        margin: 0,
        filename: safeName + '.pdf',
        image: {{ type: 'jpeg', quality: 0.92 }},
        html2canvas: {{
            scale: 2,
            useCORS: true,
            backgroundColor: '{theme["primary"]}',
            logging: false,
            letterRendering: true
        }},
        jsPDF: {{
            unit: 'mm',
            format: [120, 213],
            orientation: 'portrait'
        }},
        pagebreak: {{ mode: ['css','avoid-all'] }}
    }};

    try {{
        await html2pdf().set(opt).from(document.body).save();
    }} catch(e) {{
        alert('Use browser Print → Save as PDF for best results.');
        window.print();
    }} finally {{
        hide.forEach(id => {{ const el = document.getElementById(id); if(el) el.style.display=''; }});
        document.querySelector('.nav-bar').style.display = 'flex';
        btn.style.opacity = '1';
        btn.innerHTML = '📥 Download PDF';
    }}
}}
</script>
</body>
</html>'''

    return html


def get_niche_suggestions(language: str = "en") -> list:
    messages = [
        {"role": "system", "content": "You are a digital marketing expert specializing in ebook sales on social media."},
        {"role": "user", "content": f"""List 15 highly profitable ebook niches for TikTok/social media sales.
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


def main():
    book_title   = os.environ.get("BOOK_TITLE", "")
    language     = os.environ.get("BOOK_LANGUAGE", "en")
    action       = os.environ.get("ACTION", "generate")
    author_name  = os.environ.get("BOOK_AUTHOR", "").strip()

    if not GROQ_API_KEY:
        print("ERROR: GROQ_API_KEY not set!")
        sys.exit(1)

    os.makedirs("output", exist_ok=True)

    if action == "suggest":
        print(f"🎯 Getting niche suggestions in {language}...")
        suggestions = get_niche_suggestions(language)
        suggestions_html = generate_suggestions_page(suggestions, language)
        with open("output/niche_suggestions.html", "w", encoding="utf-8") as f:
            f.write(suggestions_html)
        print("✅ Saved to output/niche_suggestions.html")

    elif action == "generate":
        if not book_title:
            print("ERROR: BOOK_TITLE not set!")
            sys.exit(1)

        print(f"📚 Generating: '{book_title}' [{language}]")
        theme_key = detect_theme(book_title, language)
        theme = BOOK_THEMES[theme_key]
        print(f"🎨 Theme: {theme_key} {theme['emoji']}")

        print("✍️  Writing book content with Groq AI...")
        book_data = generate_book_structure(book_title, language)

        if author_name:
            book_data["author"] = author_name

        with open("output/book_data.json", "w", encoding="utf-8") as f:
            json.dump(book_data, f, ensure_ascii=False, indent=2)

        print("🎨 Designing professional layout...")
        html = generate_html_book(book_data, theme, language)

        safe_title = re.sub(r'[^\w\s-]', '', book_title).strip().replace(' ', '_')[:50]
        filename = f"output/{safe_title}_{language}.html"

        with open(filename, "w", encoding="utf-8") as f:
            f.write(html)

        print(f"✅ Book generated: {filename}")
        print(f"📖 Title: {book_data.get('title', book_title)}")
        print(f"📝 Chapters: {len(book_data.get('chapters', []))}")

        metadata = {
            "generated_at": datetime.now().isoformat(),
            "title": book_data.get("title", book_title),
            "subtitle": book_data.get("subtitle", ""),
            "language": language,
            "theme": theme_key,
            "chapters": len(book_data.get("chapters", [])),
            "file": filename
        }
        with open("output/metadata.json", "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)


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
<p class="subtitle">Best ebook niches for TikTok sales</p>
{items_html}
</body>
</html>'''


if __name__ == "__main__":
    main()
