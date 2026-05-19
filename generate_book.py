#!/usr/bin/env python3
"""
📚 Professional Book Generator - Powered by Groq
Version 4.1 – Flawless, Stable, no blank pages, Amazon KDP Ready
"""

import os
import json
import sys
import re
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
        "business": ["business","startup","entrepreneur","sales","marketing","affaires","negocio"],
        "self_help": ["confidence","mindset","habit","success","motivation","confiance","réussir"],
        "technology": ["ai","coding","tech","software","digital","technologie"]
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
    raise Exception("Max retries exceeded for rate limit. حاول تنقص من طول الفصول أو تأكد من حساب Groq ديالك.")

def clean_json(text):
    text = text.strip()
    if "```json" in text:
        text = text.split("
```json")[1].split("```")[0]
    elif "```" in text:
        text = text.split("
```")[1].split("```")[0]
    start = text.find('{')
    end = text.rfind('}') + 1
    return text[start:end] if start != -1 and end else text

# ============================================================
# STEP 1: BOOK OUTLINE
# ============================================================
def generate_outline(title, language):
    lang_prompt = {
        "en": "You are a professional bestselling author. Create a compelling book outline.",
        "fr": "Vous êtes un auteur à succès. Créez un plan de livre convaincant."
    }.get(language, "You are a professional author.")
    
    prompt = f"""
Create a detailed book outline for a sellable ebook: "{title}"

Return ONLY valid JSON (no markdown) with this exact structure:
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
Write 8 chapters. Language: {language}.
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
    if words < MIN_WORDS_PER_CHAPTER and MAX_RETRIES > 0:
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
            print("⏳ Cooling down for 25 seconds to respect Groq API limits...")
            time.sleep(25)   
            
    outline["chapters"] = final_chapters
    return outline

# ============================================================
# HTML GENERATION – FULL CSS WITH KDP & BLANK PAGE FIXES
# ============================================================
def generate_pdf_html(book_data, theme, language):
    is_rtl = language == "ar"
    dir_attr = 'dir="rtl"' if is_rtl else ''
    border_side = 'right' if is_rtl else 'left'
    year = datetime.now().year

    chapters_html = ""
    for i, ch in enumerate(book_data.get("chapters", []), 1):
        key_points_html = "".join(f'<li class="key-point"><span class="kp-arrow">→</span><span>{pt}</span></li>' for pt in ch.get("key_points", []))
        exercises_html = "".join(f'<div class="exercise-item"><span class="exercise-num">{j}</span><p>{ex}</p></div>' for j, ex in enumerate(ch.get("exercises", []), 1))
        paragraphs = [p.strip() for p in ch.get("content", "").split('\n\n') if p.strip()]
        content_html = "".join(f'<p class="body-text">{p}</p>' for p in paragraphs)
        hook_html = f'<div class="chapter-hook">&ldquo;{ch.get("hook","")}&rdquo;</div>' if ch.get("hook") else ""
        technique_html = f'<div class="technique-badge"><span class="technique-label">🔑 KEY TECHNIQUE</span><span class="technique-name">{ch.get("key_technique","")}</span></div>' if ch.get("key_technique") else ""

        chapters_html += f'''
<div class="chapter-wrapper new-page">
<section class="chapter" id="chapter-{i}">
    <div class="chapter-header">
        <div class="chapter-meta"><div class="chapter-number-badge"><span class="ch-label">CHAPTER</span><span class="ch-num">{ch.get("number", i)}</span></div></div>
        <h2 class="chapter-title">{ch.get("title","")}</h2>
        <p class="chapter-subtitle">{ch.get("subtitle","")}</p>
    </div>
    {hook_html}
    <div class="chapter-body">
        <div class="key-points-box"><h4 class="box-label">🎯 KEY POINTS</h4><ul class="key-points-list">{key_points_html}</ul></div>
        <div class="chapter-content">{content_html}</div>
        {technique_html}
        <div class="exercises-section"><h4 class="box-label">✍️ ACTION EXERCISES</h4><div class="exercises-list">{exercises_html}</div></div>
        <div class="chapter-summary"><span class="summary-icon">💡</span><p class="summary-text">{ch.get("summary","")}</p></div>
    </div>
</section>
</div>'''

    benefits_html = "".join(f'<div class="benefit-item"><span class="benefit-check">✓</span><span class="benefit-text">{b}</span></div>' for b in book_data.get("key_benefits", []))
    toc_html = "".join(f'<div class="toc-item" onclick="scrollToChapter({i})"><span class="toc-num">0{i}</span><div class="toc-text"><span class="toc-title">{ch.get("title","")}</span><span class="toc-sub">{ch.get("subtitle","")}</span></div><span class="toc-arrow">→</span></div>' for i, ch in enumerate(book_data.get("chapters", []), 1))
    intro_html = "".join(f'<p class="body-text">{p.strip()}</p>' for p in book_data.get("introduction", "").split('\n') if p.strip())
    conc_html = "".join(f'<p class="body-text">{p.strip()}</p>' for p in book_data.get("conclusion", "").split('\n') if p.strip())

    title_short = book_data.get('title', '')[:28] + "…" if len(book_data.get('title', '')) > 28 else book_data.get('title', '')

    html = f'''<!DOCTYPE html>
<html lang="{language}" {dir_attr}>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{book_data.get("title","")}</title>
<link href="https://fonts.googleapis.com/css2?family={theme["font_title"].replace(' ','+')},wght@400;700;900&family={theme["font_body"].replace(' ','+')},wght@300;400;600&display=swap" rel="stylesheet">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
:root{{--primary:{theme["primary"]};--secondary:{theme["secondary"]};--accent:{theme["accent"]};--text:{theme["text"]};--highlight:{theme["highlight"]};--gradient:{theme["gradient"]};--cover-gradient:{theme["cover_gradient"]};--cover-accent:{theme["cover_accent"]};--font-title:'{theme["font_title"]}',Georgia,serif;--font-body:'{theme["font_body"]}',Georgia,serif;--size-xs:0.75rem;--size-sm:0.875rem;--size-base:1rem;--size-lg:1.125rem;--size-xl:1.375rem;--size-2xl:1.75rem;--gap-sm:12px;--gap-md:24px;--gap-lg:40px;--gap-xl:56px;--side:22px;--radius:14px}}
html{{scroll-behavior:smooth}}
body{{background:var(--primary);color:var(--text);font-family:var(--font-body);font-size:var(--size-base);line-height:1.85;max-width:480px;margin:0 auto;word-wrap:break-word}}
.cover-page{{min-height:100vh;background:var(--cover-gradient);display:flex;flex-direction:column;justify-content:flex-end;align-items:flex-start;padding:60px var(--side) 50px;position:relative;overflow:hidden}}
.cover-page::before{{content:'';position:absolute;top:-80px;right:-80px;width:320px;height:320px;border-radius:50%;background:var(--cover-accent);opacity:0.08}}
.cover-page::after{{content:'';position:absolute;bottom:120px;right:-40px;width:180px;height:180px;border-radius:50%;border:2px solid var(--cover-accent);opacity:0.15}}
.cover-top-bar{{position:absolute;top:var(--side);left:var(--side);right:var(--side);display:flex;justify-content:space-between;align-items:center}}
.cover-genre-tag{{background:var(--cover-accent);color:var(--primary);font-size:var(--size-xs);font-weight:800;letter-spacing:2px;text-transform:uppercase;padding:5px 14px;border-radius:20px}}
.cover-year{{font-size:var(--size-xs);color:rgba(255,255,255,0.35);letter-spacing:2px}}
.cover-emoji{{font-size:64px;margin-bottom:28px;display:block}}
.cover-line{{width:60px;height:4px;background:var(--cover-accent);border-radius:2px;margin-bottom:20px}}
.cover-title{{font-family:var(--font-title);font-size:clamp(1.9rem,6vw,2.6rem);font-weight:900;color:#fff;line-height:1.15;margin-bottom:14px}}
.cover-subtitle{{font-size:var(--size-sm);color:var(--cover-accent);font-style:italic;margin-bottom:36px}}
.cover-author-row{{display:flex;align-items:center;gap:10px;padding-top:24px;border-top:1px solid rgba(255,255,255,0.12);width:100%}}
.cover-author-dot{{width:36px;height:36px;background:var(--cover-accent);border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:16px;font-weight:900;color:var(--primary)}}
.cover-author-name{{font-size:var(--size-xs);letter-spacing:3px;text-transform:uppercase;color:rgba(255,255,255,0.6)}}
.nav-bar{{position:sticky;top:0;background:rgba(0,0,0,0.92);backdrop-filter:blur(20px);border-bottom:1px solid rgba(255,255,255,0.08);padding:13px var(--side);display:flex;justify-content:space-between;align-items:center;z-index:100}}
.nav-title{{font-family:var(--font-title);font-size:var(--size-xs);color:var(--accent);font-weight:700}}
.nav-progress-text{{font-size:var(--size-xs);color:rgba(255,255,255,0.35)}}
.description-page{{padding:var(--gap-xl) var(--side);background:var(--secondary);border-bottom:3px solid var(--accent)}}
.section-label{{font-size:var(--size-xs);letter-spacing:3px;text-transform:uppercase;color:var(--accent);margin-bottom:14px;display:block}}
.description-text{{font-size:var(--size-base);line-height:1.85;color:rgba(255,255,255,0.78);margin-bottom:var(--gap-lg)}}
.benefit-item{{display:flex;align-items:flex-start;gap:12px;padding:13px 15px;background:rgba(255,255,255,0.04);border-radius:var(--radius);border-{border_side}:3px solid var(--accent);margin-bottom:10px}}
.benefit-check{{color:var(--accent);font-weight:900;font-size:var(--size-lg)}}
.benefit-text{{font-size:var(--size-sm);color:rgba(255,255,255,0.82)}}
.toc-page{{padding:var(--gap-xl) var(--side);background:var(--primary)}}
.page-title{{font-family:var(--font-title);font-size:var(--size-2xl);font-weight:900;color:#fff;margin-bottom:var(--gap-md)}}
.toc-item{{display:flex;align-items:center;gap:14px;padding:14px 0;border-bottom:1px solid rgba(255,255,255,0.06);cursor:pointer}}
.toc-num{{font-family:var(--font-title);font-size:var(--size-lg);font-weight:900;color:var(--accent);min-width:34px}}
.toc-text{{flex:1}}
.toc-title{{font-size:var(--size-sm);font-weight:600;color:#fff}}
.toc-sub{{font-size:var(--size-xs);color:rgba(255,255,255,0.4)}}
.intro-page,.conclusion-page,.author-page{{padding:var(--gap-xl) var(--side)}}
.chapter-header{{background:var(--gradient);padding:var(--gap-xl) var(--side) var(--gap-lg);text-align:center}}
.chapter-number-badge{{display:inline-flex;flex-direction:column;align-items:center;background:rgba(255,255,255,0.08);border:2px solid var(--accent);border-radius:var(--radius);padding:8px 22px}}
.ch-label{{font-size:0.6rem;letter-spacing:4px;color:var(--accent);text-transform:uppercase}}
.ch-num{{font-family:var(--font-title);font-size:2rem;font-weight:900;color:#fff;line-height:1}}
.chapter-title{{font-family:var(--font-title);font-size:var(--size-2xl);font-weight:900;color:#fff;margin-bottom:10px}}
.chapter-subtitle{{color:var(--accent);font-size:var(--size-sm);font-style:italic}}
.chapter-hook{{margin:var(--gap-md) var(--side) 0;padding:18px 20px;border-{border_side}:4px solid var(--accent);background:rgba(255,255,255,0.03);font-style:italic}}
.body-text{{margin-bottom:18px;line-height:1.9;color:rgba(255,255,255,0.82)}}
.key-points-box{{padding:20px;background:rgba(255,255,255,0.03);border-radius:var(--radius);margin-bottom:var(--gap-md)}}
.key-point{{display:flex;gap:10px;padding:9px 12px;background:rgba(255,255,255,0.04);border-radius:8px;margin-bottom:8px}}
.technique-badge{{padding:16px 18px;background:linear-gradient(135deg,rgba(255,255,255,0.07),rgba(255,255,255,0.03));border-radius:var(--radius);border:1px solid var(--accent);margin-bottom:var(--gap-md)}}
.exercises-section{{padding:20px;background:rgba(255,255,255,0.03);border-radius:var(--radius);border-{border_side}:4px solid var(--highlight);margin-bottom:var(--gap-md)}}
.exercise-item{{display:flex;gap:12px;margin-bottom:12px}}
.exercise-num{{background:var(--highlight);color:var(--primary);width:26px;height:26px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:900}}
.chapter-summary{{display:flex;gap:14px;padding:18px 20px;background:rgba(255,255,255,0.04);border-radius:var(--radius);font-style:italic}}
.back-cover{{min-height:55vh;background:var(--cover-gradient);padding:var(--gap-xl) var(--side);display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center}}
.edition-badge{{background:var(--cover-accent);color:var(--primary);padding:12px 28px;border-radius:50px;font-weight:900}}

/* Controls Styling */
.controls {{position:fixed;bottom:22px;right:18px;display:flex;flex-direction:column;gap:10px;z-index:998}}
.btn {{background:var(--accent);color:var(--primary);border:none;border-radius:50px;padding:13px 20px;font-weight:900;cursor:pointer;font-family:var(--font-title);box-shadow: 0 4px 15px rgba(0,0,0,0.5); transition: 0.3s;}}
.btn:hover {{transform: translateY(-2px); opacity:0.9;}}
.btn-kdp {{background:#f59e0b;}}

/* Blank Page Fixes */
@media print {{
    .nav-bar, .controls, #reading-progress {{display:none !important}} 
    .new-page {{page-break-before: always; break-before: page;}}
}}
</style>
<script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"></script>
</head>
<body>
<div id="reading-progress"></div>
<section class="cover-page"><div class="cover-top-bar"><span class="cover-genre-tag">{theme["emoji"]} Book</span><span class="cover-year">{year}</span></div><span class="cover-emoji">{theme["emoji"]}</span><div class="cover-line"></div><h1 class="cover-title">{book_data.get("title","")}</h1><p class="cover-subtitle">{book_data.get("subtitle","")}</p><div class="cover-author-row"><div class="cover-author-dot">{book_data.get("author","?")[0].upper()}</div><span class="cover-author-name">by {book_data.get("author","Professional Author")}</span></div></section>
<nav class="nav-bar"><span class="nav-title">{title_short}</span><span class="nav-progress-text" id="progress-text">0% read</span></nav>
<section class="description-page new-page"><span class="section-label">About This Book</span><p class="description-text">{book_data.get("description","")}</p><span class="section-label">What You Will Learn</span><div class="benefits-list">{benefits_html}</div></section>
<section class="toc-page new-page"><h2 class="page-title">Table of Contents</h2>{toc_html}</section>
<section class="intro-page new-page"><h2 class="page-title">Introduction</h2>{intro_html}</section>
{chapters_html}
<section class="conclusion-page new-page"><h2 class="page-title">Conclusion</h2>{conc_html}</section>
<section class="author-page new-page"><h2 class="page-title">About the Author</h2><div class="author-card"><div class="author-avatar">{theme["emoji"]}</div><p class="author-name">{book_data.get("author","Professional Author")}</p><p class="author-bio">{book_data.get("about_author","")}</p></div></section>
<section class="back-cover new-page"><h2 class="back-cover-title">{book_data.get("title","")}</h2><p class="back-cover-text">{book_data.get("tagline","")}</p><div class="edition-badge">✦ Professional Edition {year}</div></section>

<div class="controls">
    <button class="btn btn-kdp" id="kdp-btn" onclick="downloadKDP()">📚 Download KDP (6x9)</button>
    <button class="btn" id="pdf-btn" onclick="downloadPDF()">📱 Download Mobile PDF</button>
</div>

<script>
window.addEventListener('scroll',()=>{{const pct=(window.scrollY/(document.documentElement.scrollHeight-window.innerHeight))*100;document.getElementById('reading-progress').style.width=pct+'%';document.getElementById('progress-text').textContent=Math.round(pct)+'% read';}});
function scrollToChapter(n){{document.getElementById('chapter-'+n)?.scrollIntoView({{behavior:'smooth'}});}}

function hideUI() {{
    document.querySelector('.controls').style.display = 'none';
    document.getElementById('reading-progress').style.display = 'none';
    document.querySelector('.nav-bar').style.display = 'none';
}}

function restoreUI() {{
    document.querySelector('.controls').style.display = 'flex';
    document.getElementById('reading-progress').style.display = 'block';
    document.querySelector('.nav-bar').style.display = 'flex';
}}

const getSafeName = () => {{
    const title=document.querySelector('.cover-title')?.textContent||'book';
    return title.replace(/[^\\w\\s-]/g,'').trim().replace(/\\s+/g,'_').substring(0,50);
}}

// 📱 Mobile Format Export
async function downloadPDF(){{
    const btn=document.getElementById('pdf-btn');
    const originalText = btn.innerHTML;
    btn.innerHTML='⏳ Preparing...';
    hideUI();
    const opt={{
        margin:0, filename: getSafeName() + '_Mobile.pdf',
        image:{{type:'jpeg',quality:0.98}},
        html2canvas:{{scale:2,useCORS:true,backgroundColor:'{theme["primary"]}'}},
        jsPDF:{{unit:'mm',format:[120,213],orientation:'portrait'}},
        pagebreak: {{ mode: ['css'], before: '.new-page' }}
    }};
    try{{ await html2pdf().set(opt).from(document.body).save(); }}
    catch(e){{ console.error(e); window.print(); }}
    finally{{ restoreUI(); btn.innerHTML = originalText; }}
}}

// 📚 Amazon KDP Format Export (6x9 inches)
async function downloadKDP(){{
    const btn=document.getElementById('kdp-btn');
    const originalText = btn.innerHTML;
    btn.innerHTML='⏳ Preparing KDP...';
    hideUI();
    
    // KDP Print settings: 6x9 inches (152.4 x 228.6 mm)
    const opt={{
        margin: [0, 0, 0, 0], // Full Bleed format
        filename: getSafeName() + '_KDP_6x9.pdf',
        image:{{type:'jpeg',quality:1.0}},
        html2canvas:{{scale:3,useCORS:true,backgroundColor:'{theme["primary"]}'}}, // Higher scale for print quality
        jsPDF:{{unit:'in',format:[6, 9],orientation:'portrait'}},
        pagebreak: {{ mode: ['css'], before: '.new-page' }}
    }};
    try{{ await html2pdf().set(opt).from(document.body).save(); }}
    catch(e){{ console.error(e); window.print(); }}
    finally{{ restoreUI(); btn.innerHTML = originalText; }}
}}
</script>
</body>
</html>'''

    return html

# ============================================================
# MAIN EXECUTION
# ============================================================
if __name__ == "__main__":
    print("🚀 Starting Professional Book Generator...")
    
    book_title = "LE PROTOCOLE DE L'OMBRE premium 30 days ghost mode mental conditioning"
    language = "fr"  
    
    try:
        theme_name = detect_theme(book_title, language)
        theme = BOOK_THEMES.get(theme_name, BOOK_THEMES["default"])
        
        book_data = generate_full_book(book_title, language)
        
        print("🎨 Generating HTML format...")
        final_html = generate_pdf_html(book_data, theme, language)
        
        output_file = "book_output.html"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(final_html)
            
        print(f"✅ Book generated successfully! Saved to {output_file}")
        print("يمكنك الآن فتح الملف book_output.html في المتصفح ديالك وتصديره بصيغة KDP أو Mobile بدون صفحات بيضاء.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
