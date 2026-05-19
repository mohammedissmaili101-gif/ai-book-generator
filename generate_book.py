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
MODEL = "llama-3.3-70b-versatile"  # Best free model on Groq

# ============================================================
# BOOK THEMES - Colors & Styles per niche
# ============================================================
BOOK_THEMES = {
    "business": {
        "primary": "#1a1a2e",
        "secondary": "#16213e",
        "accent": "#e94560",
        "text": "#eaeaea",
        "highlight": "#f5a623",
        "font_title": "Playfair Display",
        "font_body": "Lora",
        "emoji": "💼",
        "gradient": "linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%)"
    },
    "health": {
        "primary": "#1b4332",
        "secondary": "#2d6a4f",
        "accent": "#95d5b2",
        "text": "#f8f9fa",
        "highlight": "#74c69d",
        "font_title": "Merriweather",
        "font_body": "Source Serif Pro",
        "emoji": "🌿",
        "gradient": "linear-gradient(135deg, #1b4332 0%, #2d6a4f 50%, #40916c 100%)"
    },
    "finance": {
        "primary": "#0d1b2a",
        "secondary": "#1b263b",
        "accent": "#ffd700",
        "text": "#e0e0e0",
        "highlight": "#c9a84c",
        "font_title": "EB Garamond",
        "font_body": "Libre Baskerville",
        "emoji": "💰",
        "gradient": "linear-gradient(135deg, #0d1b2a 0%, #1b263b 50%, #415a77 100%)"
    },
    "self_help": {
        "primary": "#2d00f7",
        "secondary": "#6a00f4",
        "accent": "#ff9e00",
        "text": "#ffffff",
        "highlight": "#ffdd00",
        "font_title": "Nunito",
        "font_body": "Open Sans",
        "emoji": "✨",
        "gradient": "linear-gradient(135deg, #2d00f7 0%, #6a00f4 50%, #8900f2 100%)"
    },
    "technology": {
        "primary": "#0a0a0a",
        "secondary": "#1a1a1a",
        "accent": "#00ff88",
        "text": "#e0e0e0",
        "highlight": "#00d4ff",
        "font_title": "Space Mono",
        "font_body": "IBM Plex Mono",
        "emoji": "🤖",
        "gradient": "linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 50%, #2a2a2a 100%)"
    },
    "spirituality": {
        "primary": "#2c1654",
        "secondary": "#44237a",
        "accent": "#c77dff",
        "text": "#f0e6ff",
        "highlight": "#e0aaff",
        "font_title": "Cormorant Garamond",
        "font_body": "Crimson Text",
        "emoji": "🔮",
        "gradient": "linear-gradient(135deg, #2c1654 0%, #44237a 50%, #7b2d8b 100%)"
    },
    "cooking": {
        "primary": "#5c1a1a",
        "secondary": "#8b2500",
        "accent": "#ff6b35",
        "text": "#fff8f0",
        "highlight": "#ffa552",
        "font_title": "Dancing Script",
        "font_body": "Quattrocento",
        "emoji": "🍳",
        "gradient": "linear-gradient(135deg, #5c1a1a 0%, #8b2500 50%, #c1440e 100%)"
    },
    "travel": {
        "primary": "#003049",
        "secondary": "#023e8a",
        "accent": "#fcbf49",
        "text": "#eae2b7",
        "highlight": "#f77f00",
        "font_title": "Josefin Sans",
        "font_body": "Raleway",
        "emoji": "✈️",
        "gradient": "linear-gradient(135deg, #003049 0%, #023e8a 50%, #0077b6 100%)"
    },
    "default": {
        "primary": "#212529",
        "secondary": "#343a40",
        "accent": "#fd7e14",
        "text": "#f8f9fa",
        "highlight": "#ffc107",
        "font_title": "Playfair Display",
        "font_body": "Georgia",
        "emoji": "📖",
        "gradient": "linear-gradient(135deg, #212529 0%, #343a40 50%, #495057 100%)"
    }
}

def detect_theme(title: str, language: str = "en") -> str:
    """Detect book theme from title keywords"""
    title_lower = title.lower()
    
    keywords = {
        "business": ["business", "startup", "entrepreneur", "marketing", "sales", "brand", "عمل", "تجارة", "ريادة", "business", "affaires", "negocio"],
        "health": ["health", "fitness", "wellness", "diet", "nutrition", "صحة", "لياقة", "تغذية", "santé", "salud"],
        "finance": ["money", "invest", "finance", "wealth", "rich", "مال", "استثمار", "ثروة", "argent", "dinero", "finance"],
        "self_help": ["confidence", "mindset", "habit", "success", "motivation", "ثقة", "عادات", "نجاح", "confiance", "confianza"],
        "technology": ["ai", "coding", "tech", "software", "digital", "تقنية", "برمجة", "ذكاء اصطناعي", "technologie"],
        "spirituality": ["spiritual", "meditation", "soul", "mindfulness", "روحانية", "تأمل", "روح", "spiritualité"],
        "cooking": ["cook", "recipe", "food", "kitchen", "طبخ", "وصفة", "طعام", "cuisine", "cocina"],
        "travel": ["travel", "adventure", "journey", "trip", "سفر", "مغامرة", "رحلة", "voyage", "viaje"]
    }
    
    for theme, words in keywords.items():
        if any(word in title_lower for word in words):
            return theme
    return "default"

def call_groq(messages: list, max_tokens: int = 4000) -> str:
    """Call Groq API"""
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
    """Generate complete book structure with Groq"""
    
    lang_prompts = {
        "en": f"You are a professional bestselling author and book designer. Create a comprehensive, sellable ebook about: '{title}'",
        "ar": f"أنت مؤلف محترف ومصمم كتب. أنشئ كتابًا إلكترونيًا شاملًا وقابلًا للبيع حول: '{title}'",
        "fr": f"Vous êtes un auteur professionnel et designer de livres. Créez un ebook complet et vendable sur: '{title}'",
        "es": f"Eres un autor profesional y diseñador de libros. Crea un ebook completo y vendible sobre: '{title}'",
        "de": f"Sie sind ein professioneller Autor und Buchdesigner. Erstellen Sie ein umfassendes, verkäufliches Ebook über: '{title}'",
        "pt": f"Você é um autor profissional e designer de livros. Crie um ebook completo e vendável sobre: '{title}'",
        "it": f"Sei un autore professionista e designer di libri. Crea un ebook completo e vendibile su: '{title}'",
        "zh": f"您是一位专业的畅销书作者和图书设计师。创建一本关于以下主题的完整、可销售的电子书：'{title}'",
        "ja": f"あなたはプロのベストセラー作家で本のデザイナーです。次のテーマについて完全で販売可能な電子書籍を作成してください：'{title}'",
        "ru": f"Вы профессиональный автор и дизайнер книг. Создайте полную, продаваемую электронную книгу на тему: '{title}'"
    }
    
    system_msg = lang_prompts.get(language, lang_prompts["en"])
    
    json_instruction = {
        "en": "Return ONLY valid JSON, no other text:",
        "ar": "أعد JSON فقط، بدون أي نص آخر:",
        "fr": "Retournez UNIQUEMENT du JSON valide, sans autre texte:",
        "es": "Devuelva SOLO JSON válido, sin otro texto:",
        "de": "Geben Sie NUR gültiges JSON zurück, keinen anderen Text:",
        "pt": "Retorne APENAS JSON válido, sem outro texto:",
        "it": "Restituisci SOLO JSON valido, nessun altro testo:",
        "zh": "仅返回有效的JSON，不要其他文本：",
        "ja": "有効なJSONのみを返してください。他のテキストは不要です：",
        "ru": "Верните ТОЛЬКО корректный JSON, без другого текста:"
    }
    
    messages = [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": f"""
{json_instruction.get(language, json_instruction["en"])}

{{
  "title": "book title",
  "subtitle": "compelling subtitle",
  "author": "Professional Author",
  "tagline": "one powerful sentence that sells the book",
  "description": "150 word compelling book description",
  "target_audience": "who this book is for",
  "key_benefits": ["benefit 1", "benefit 2", "benefit 3", "benefit 4", "benefit 5"],
  "chapters": [
    {{
      "number": 1,
      "title": "Chapter Title",
      "subtitle": "Chapter subtitle",
      "key_points": ["point 1", "point 2", "point 3"],
      "content": "600-800 words of professional chapter content with actionable insights, real examples, and practical advice. Make it engaging and valuable.",
      "exercises": ["Exercise 1: description", "Exercise 2: description"],
      "summary": "Chapter key takeaway in 2 sentences"
    }}
  ],
  "introduction": "200 word powerful introduction",
  "conclusion": "200 word inspiring conclusion",
  "about_author": "100 word author bio"
}}

Create 8-10 chapters. Make the content PROFESSIONAL, VALUABLE, and worth $50-200.
Language: {language}
"""}
    ]
    
    content = call_groq(messages, max_tokens=6000)
    
    # Clean JSON
    content = content.strip()
    if content.startswith("```json"):
        content = content[7:]
    if content.startswith("```"):
        content = content[3:]
    if content.endswith("```"):
        content = content[:-3]
    content = content.strip()
    
    # Find JSON object
    start = content.find('{')
    end = content.rfind('}') + 1
    if start >= 0 and end > start:
        content = content[start:end]
    
    return json.loads(content)

def generate_html_book(book_data: dict, theme: dict, language: str = "en") -> str:
    """Generate a stunning HTML ebook"""
    
    chapters_html = ""
    for i, chapter in enumerate(book_data.get("chapters", []), 1):
        
        key_points_html = ""
        for point in chapter.get("key_points", []):
            key_points_html += f'<li class="key-point">{point}</li>'
        
        exercises_html = ""
        for j, exercise in enumerate(chapter.get("exercises", []), 1):
            exercises_html += f'''
            <div class="exercise-item">
                <span class="exercise-num">{j}</span>
                <p>{exercise}</p>
            </div>'''
        
        # Format content paragraphs
        content = chapter.get("content", "")
        paragraphs = content.split('\n')
        content_html = ""
        for para in paragraphs:
            para = para.strip()
            if para:
                content_html += f'<p>{para}</p>'
        
        chapters_html += f'''
        <section class="chapter" id="chapter-{i}">
            <div class="chapter-header">
                <div class="chapter-number-badge">
                    <span class="ch-label">CHAPTER</span>
                    <span class="ch-num">{chapter.get("number", i)}</span>
                </div>
                <h2 class="chapter-title">{chapter.get("title", "")}</h2>
                <p class="chapter-subtitle">{chapter.get("subtitle", "")}</p>
            </div>
            
            <div class="key-points-box">
                <h4>🎯 Key Points</h4>
                <ul class="key-points-list">{key_points_html}</ul>
            </div>
            
            <div class="chapter-content">
                {content_html}
            </div>
            
            <div class="exercises-section">
                <h4>✍️ Action Exercises</h4>
                <div class="exercises-grid">{exercises_html}</div>
            </div>
            
            <div class="chapter-summary">
                <div class="summary-icon">💡</div>
                <p>{chapter.get("summary", "")}</p>
            </div>
            
            <div class="notes-section">
                <h4>📝 My Notes</h4>
                <div class="notes-lines">
                    {"".join(['<div class="note-line"></div>' for _ in range(6)])}
                </div>
            </div>
            
            <div class="page-break"></div>
        </section>'''
    
    benefits_html = ""
    for benefit in book_data.get("key_benefits", []):
        benefits_html += f'<div class="benefit-item"><span class="benefit-check">✓</span><span>{benefit}</span></div>'
    
    # TOC
    toc_html = ""
    for i, chapter in enumerate(book_data.get("chapters", []), 1):
        toc_html += f'''
        <div class="toc-item" onclick="document.getElementById('chapter-{i}').scrollIntoView({{behavior:'smooth'}})">
            <span class="toc-num">0{i}</span>
            <div class="toc-text">
                <span class="toc-title">{chapter.get("title", "")}</span>
                <span class="toc-sub">{chapter.get("subtitle", "")}</span>
            </div>
            <span class="toc-arrow">→</span>
        </div>'''
    
    dir_attr = 'dir="rtl"' if language == "ar" else ''
    
    html = f'''<!DOCTYPE html>
<html lang="{language}" {dir_attr}>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">
    <title>{book_data.get("title", "")}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family={theme["font_title"].replace(" ", "+")}:wght@400;700;900&family={theme["font_body"].replace(" ", "+")}:wght@300;400;600&display=swap" rel="stylesheet">
    <style>
        :root {{
            --primary: {theme["primary"]};
            --secondary: {theme["secondary"]};
            --accent: {theme["accent"]};
            --text: {theme["text"]};
            --highlight: {theme["highlight"]};
            --gradient: {theme["gradient"]};
            --font-title: '{theme["font_title"]}', serif;
            --font-body: '{theme["font_body"]}', serif;
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        html {{
            scroll-behavior: smooth;
        }}
        
        body {{
            background: #0a0a0a;
            color: var(--text);
            font-family: var(--font-body);
            font-size: 16px;
            line-height: 1.8;
            max-width: 480px;
            margin: 0 auto;
        }}
        
        /* ===== COVER PAGE ===== */
        .cover-page {{
            min-height: 100vh;
            background: var(--gradient);
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
            padding: 40px 30px;
            position: relative;
            overflow: hidden;
        }}
        
        .cover-page::before {{
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle at center, rgba(255,255,255,0.05) 0%, transparent 60%);
            animation: pulse 4s ease-in-out infinite;
        }}
        
        .cover-page::after {{
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: var(--accent);
        }}
        
        @keyframes pulse {{
            0%, 100% {{ transform: scale(1); opacity: 0.5; }}
            50% {{ transform: scale(1.1); opacity: 1; }}
        }}
        
        .cover-emoji {{
            font-size: 72px;
            margin-bottom: 20px;
            animation: float 3s ease-in-out infinite;
        }}
        
        @keyframes float {{
            0%, 100% {{ transform: translateY(0); }}
            50% {{ transform: translateY(-10px); }}
        }}
        
        .cover-title {{
            font-family: var(--font-title);
            font-size: 2.2rem;
            font-weight: 900;
            line-height: 1.2;
            color: #ffffff;
            margin-bottom: 15px;
            text-shadow: 0 2px 20px rgba(0,0,0,0.3);
        }}
        
        .cover-subtitle {{
            font-size: 1rem;
            color: var(--accent);
            font-style: italic;
            margin-bottom: 30px;
            opacity: 0.9;
        }}
        
        .cover-tagline {{
            background: rgba(255,255,255,0.1);
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 50px;
            padding: 12px 24px;
            font-size: 0.85rem;
            color: #fff;
            margin-bottom: 30px;
            backdrop-filter: blur(10px);
        }}
        
        .cover-author {{
            font-size: 0.9rem;
            color: var(--highlight);
            letter-spacing: 3px;
            text-transform: uppercase;
        }}
        
        .cover-divider {{
            width: 60px;
            height: 3px;
            background: var(--accent);
            margin: 20px auto;
            border-radius: 2px;
        }}
        
        /* ===== NAVIGATION ===== */
        .nav-bar {{
            position: sticky;
            top: 0;
            background: rgba(10,10,10,0.95);
            backdrop-filter: blur(20px);
            border-bottom: 1px solid rgba(255,255,255,0.1);
            padding: 15px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            z-index: 100;
        }}
        
        .nav-title {{
            font-family: var(--font-title);
            font-size: 0.85rem;
            color: var(--accent);
            font-weight: 700;
        }}
        
        .nav-progress {{
            font-size: 0.7rem;
            color: rgba(255,255,255,0.4);
        }}
        
        /* ===== DESCRIPTION PAGE ===== */
        .description-page {{
            padding: 50px 25px;
            background: var(--primary);
            border-bottom: 3px solid var(--accent);
        }}
        
        .section-label {{
            font-size: 0.7rem;
            letter-spacing: 4px;
            text-transform: uppercase;
            color: var(--accent);
            margin-bottom: 15px;
        }}
        
        .description-text {{
            font-size: 1rem;
            line-height: 1.9;
            color: rgba(255,255,255,0.8);
            margin-bottom: 30px;
        }}
        
        .benefits-grid {{
            display: flex;
            flex-direction: column;
            gap: 12px;
        }}
        
        .benefit-item {{
            display: flex;
            align-items: flex-start;
            gap: 12px;
            padding: 12px 15px;
            background: rgba(255,255,255,0.05);
            border-radius: 10px;
            border-left: 3px solid var(--accent);
            font-size: 0.9rem;
        }}
        
        .benefit-check {{
            color: var(--accent);
            font-weight: 900;
            font-size: 1rem;
            flex-shrink: 0;
        }}
        
        /* ===== TABLE OF CONTENTS ===== */
        .toc-page {{
            padding: 50px 25px;
            background: var(--secondary);
        }}
        
        .page-title {{
            font-family: var(--font-title);
            font-size: 1.8rem;
            font-weight: 900;
            color: #fff;
            margin-bottom: 30px;
        }}
        
        .toc-item {{
            display: flex;
            align-items: center;
            gap: 15px;
            padding: 15px 0;
            border-bottom: 1px solid rgba(255,255,255,0.08);
            cursor: pointer;
            transition: all 0.2s;
        }}
        
        .toc-item:hover {{
            padding-left: 10px;
        }}
        
        .toc-item:hover .toc-arrow {{
            color: var(--accent);
        }}
        
        .toc-num {{
            font-family: var(--font-title);
            font-size: 1.2rem;
            font-weight: 900;
            color: var(--accent);
            min-width: 35px;
        }}
        
        .toc-text {{
            flex: 1;
            display: flex;
            flex-direction: column;
            gap: 3px;
        }}
        
        .toc-title {{
            font-size: 0.95rem;
            font-weight: 600;
            color: #fff;
        }}
        
        .toc-sub {{
            font-size: 0.78rem;
            color: rgba(255,255,255,0.5);
        }}
        
        .toc-arrow {{
            color: rgba(255,255,255,0.3);
            font-size: 1.1rem;
            transition: color 0.2s;
        }}
        
        /* ===== INTRODUCTION ===== */
        .intro-page {{
            padding: 50px 25px;
            background: var(--primary);
            position: relative;
        }}
        
        .intro-page::before {{
            content: '"';
            font-family: var(--font-title);
            font-size: 150px;
            color: var(--accent);
            opacity: 0.1;
            position: absolute;
            top: 20px;
            left: 20px;
            line-height: 1;
        }}
        
        .intro-text {{
            font-size: 1.05rem;
            line-height: 2;
            color: rgba(255,255,255,0.85);
            position: relative;
            z-index: 1;
        }}
        
        /* ===== CHAPTERS ===== */
        .chapter {{
            padding: 0 0 30px 0;
            border-bottom: 3px solid var(--accent);
        }}
        
        .chapter-header {{
            background: var(--gradient);
            padding: 50px 25px 40px;
            text-align: center;
            position: relative;
            overflow: hidden;
        }}
        
        .chapter-number-badge {{
            display: inline-flex;
            flex-direction: column;
            align-items: center;
            background: rgba(255,255,255,0.1);
            border: 2px solid var(--accent);
            border-radius: 15px;
            padding: 8px 20px;
            margin-bottom: 20px;
        }}
        
        .ch-label {{
            font-size: 0.6rem;
            letter-spacing: 3px;
            color: var(--accent);
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
            font-size: 1.8rem;
            font-weight: 900;
            color: #fff;
            line-height: 1.3;
            margin-bottom: 10px;
        }}
        
        .chapter-subtitle {{
            color: var(--accent);
            font-size: 0.9rem;
            font-style: italic;
            opacity: 0.9;
        }}
        
        .key-points-box {{
            margin: 25px;
            padding: 20px;
            background: rgba(255,255,255,0.03);
            border-radius: 15px;
            border: 1px solid rgba(255,255,255,0.1);
        }}
        
        .key-points-box h4 {{
            color: var(--accent);
            font-size: 0.85rem;
            letter-spacing: 2px;
            text-transform: uppercase;
            margin-bottom: 15px;
        }}
        
        .key-points-list {{
            list-style: none;
            display: flex;
            flex-direction: column;
            gap: 8px;
        }}
        
        .key-point {{
            padding: 8px 12px;
            background: rgba(255,255,255,0.05);
            border-radius: 8px;
            font-size: 0.88rem;
            position: relative;
            padding-left: 25px;
        }}
        
        .key-point::before {{
            content: '→';
            position: absolute;
            left: 8px;
            color: var(--accent);
        }}
        
        .chapter-content {{
            padding: 0 25px;
        }}
        
        .chapter-content p {{
            margin-bottom: 18px;
            font-size: 0.95rem;
            line-height: 1.9;
            color: rgba(255,255,255,0.82);
        }}
        
        .exercises-section {{
            margin: 25px;
            padding: 20px;
            background: rgba(255,255,255,0.04);
            border-radius: 15px;
            border-left: 4px solid var(--highlight);
        }}
        
        .exercises-section h4 {{
            color: var(--highlight);
            font-size: 0.85rem;
            letter-spacing: 2px;
            text-transform: uppercase;
            margin-bottom: 15px;
        }}
        
        .exercises-grid {{
            display: flex;
            flex-direction: column;
            gap: 12px;
        }}
        
        .exercise-item {{
            display: flex;
            gap: 12px;
            align-items: flex-start;
            font-size: 0.88rem;
            color: rgba(255,255,255,0.8);
        }}
        
        .exercise-num {{
            background: var(--highlight);
            color: var(--primary);
            width: 24px;
            height: 24px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.75rem;
            font-weight: 900;
            flex-shrink: 0;
        }}
        
        .chapter-summary {{
            margin: 25px;
            padding: 20px 20px 20px 60px;
            background: rgba(255,255,255,0.05);
            border-radius: 15px;
            font-size: 0.95rem;
            font-style: italic;
            color: rgba(255,255,255,0.9);
            position: relative;
        }}
        
        .summary-icon {{
            position: absolute;
            left: 20px;
            top: 20px;
            font-size: 1.5rem;
        }}
        
        /* ===== NOTES SECTION ===== */
        .notes-section {{
            margin: 25px;
            padding: 20px;
            background: rgba(255,255,255,0.02);
            border-radius: 15px;
            border: 1px dashed rgba(255,255,255,0.15);
        }}
        
        .notes-section h4 {{
            color: rgba(255,255,255,0.4);
            font-size: 0.78rem;
            letter-spacing: 2px;
            text-transform: uppercase;
            margin-bottom: 15px;
        }}
        
        .note-line {{
            height: 1px;
            background: rgba(255,255,255,0.1);
            margin-bottom: 28px;
            border-radius: 1px;
        }}
        
        /* ===== CONCLUSION ===== */
        .conclusion-page {{
            padding: 50px 25px;
            background: var(--gradient);
            text-align: center;
        }}
        
        .conclusion-page .page-title {{
            text-align: center;
        }}
        
        .conclusion-text {{
            font-size: 1rem;
            line-height: 2;
            color: rgba(255,255,255,0.9);
            margin-bottom: 30px;
        }}
        
        /* ===== ABOUT AUTHOR ===== */
        .author-page {{
            padding: 50px 25px;
            background: var(--primary);
        }}
        
        .author-card {{
            background: rgba(255,255,255,0.05);
            border-radius: 20px;
            padding: 30px;
            text-align: center;
            border: 1px solid rgba(255,255,255,0.1);
        }}
        
        .author-avatar {{
            width: 80px;
            height: 80px;
            background: var(--gradient);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 2rem;
            margin: 0 auto 20px;
            border: 3px solid var(--accent);
        }}
        
        .author-name {{
            font-family: var(--font-title);
            font-size: 1.3rem;
            font-weight: 700;
            color: #fff;
            margin-bottom: 5px;
        }}
        
        .author-bio {{
            font-size: 0.9rem;
            line-height: 1.8;
            color: rgba(255,255,255,0.7);
            margin-top: 15px;
        }}
        
        /* ===== BACK COVER ===== */
        .back-cover {{
            min-height: 60vh;
            background: var(--gradient);
            padding: 50px 25px;
            text-align: center;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
        }}
        
        .back-cover-title {{
            font-family: var(--font-title);
            font-size: 1.5rem;
            font-weight: 900;
            color: #fff;
            margin-bottom: 20px;
        }}
        
        .back-cover-text {{
            font-size: 0.9rem;
            color: rgba(255,255,255,0.8);
            line-height: 1.8;
            max-width: 380px;
            margin-bottom: 30px;
        }}
        
        .price-badge {{
            background: var(--accent);
            color: var(--primary);
            font-size: 1.5rem;
            font-weight: 900;
            font-family: var(--font-title);
            padding: 15px 30px;
            border-radius: 50px;
            letter-spacing: 1px;
        }}
        
        /* ===== PAGE BREAK ===== */
        .page-break {{
            height: 20px;
            background: linear-gradient(to bottom, transparent, rgba(255,255,255,0.03));
        }}
        
        /* ===== SCROLLBAR ===== */
        ::-webkit-scrollbar {{
            width: 4px;
        }}
        
        ::-webkit-scrollbar-track {{
            background: #0a0a0a;
        }}
        
        ::-webkit-scrollbar-thumb {{
            background: var(--accent);
            border-radius: 2px;
        }}
        
        /* ===== READING PROGRESS ===== */
        #reading-progress {{
            position: fixed;
            top: 0;
            left: 0;
            height: 3px;
            background: var(--accent);
            z-index: 200;
            transition: width 0.1s;
        }}
        
        /* ===== PDF DOWNLOAD BUTTON ===== */
        .pdf-btn {{
            position: fixed;
            bottom: 25px;
            right: 20px;
            background: var(--accent);
            color: var(--primary);
            border: none;
            border-radius: 50px;
            padding: 14px 22px;
            font-size: 0.88rem;
            font-weight: 900;
            cursor: pointer;
            z-index: 999;
            display: flex;
            align-items: center;
            gap: 8px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.4);
            transition: all 0.2s;
            font-family: var(--font-body);
        }}
        
        .pdf-btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 25px rgba(0,0,0,0.5);
        }}
        
        .pdf-btn:active {{
            transform: scale(0.96);
        }}
        
        .pdf-btn.loading {{
            opacity: 0.7;
            pointer-events: none;
        }}
        
        @media print {{
            .nav-bar {{ display: none; }}
            .pdf-btn {{ display: none; }}
            #reading-progress {{ display: none; }}
            body {{ max-width: 100%; }}
            .cover-page {{ min-height: 100vh; page-break-after: always; }}
            .chapter {{ page-break-before: always; }}
        }}
    </style>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"></script>
</head>
<body>

<div id="reading-progress"></div>

<!-- COVER PAGE -->
<section class="cover-page">
    <div class="cover-emoji">{theme["emoji"]}</div>
    <h1 class="cover-title">{book_data.get("title", "")}</h1>
    <p class="cover-subtitle">{book_data.get("subtitle", "")}</p>
    <div class="cover-divider"></div>
    <div class="cover-tagline">{book_data.get("tagline", "")}</div>
    <p class="cover-author">by {book_data.get("author", "Professional Author")}</p>
</section>

<!-- NAV BAR -->
<nav class="nav-bar">
    <span class="nav-title">{book_data.get("title", "")[:30]}{"..." if len(book_data.get("title","")) > 30 else ""}</span>
    <span class="nav-progress" id="progress-text">0% read</span>
</nav>

<!-- DESCRIPTION PAGE -->
<section class="description-page">
    <p class="section-label">About This Book</p>
    <p class="description-text">{book_data.get("description", "")}</p>
    
    <p class="section-label">What You Will Learn</p>
    <div class="benefits-grid">
        {benefits_html}
    </div>
</section>

<!-- TABLE OF CONTENTS -->
<section class="toc-page">
    <h2 class="page-title">Table of Contents</h2>
    {toc_html}
</section>

<!-- INTRODUCTION -->
<section class="intro-page">
    <h2 class="page-title">Introduction</h2>
    <p class="intro-text">{book_data.get("introduction", "")}</p>
</section>

<!-- CHAPTERS -->
{chapters_html}

<!-- CONCLUSION -->
<section class="conclusion-page">
    <h2 class="page-title">Conclusion</h2>
    <p class="conclusion-text">{book_data.get("conclusion", "")}</p>
</section>

<!-- ABOUT AUTHOR -->
<section class="author-page">
    <h2 class="page-title">About the Author</h2>
    <div class="author-card">
        <div class="author-avatar">{theme["emoji"]}</div>
        <p class="author-name">{book_data.get("author", "Professional Author")}</p>
        <p class="author-bio">{book_data.get("about_author", "")}</p>
    </div>
</section>

<!-- BACK COVER -->
<section class="back-cover">
    <p class="back-cover-title">{book_data.get("title", "")}</p>
    <p class="back-cover-text">{book_data.get("tagline", "")}</p>
    <div class="price-badge">Professional Edition</div>
</section>

<!-- PDF DOWNLOAD BUTTON -->
<button class="pdf-btn" id="pdf-btn" onclick="downloadPDF()">
    📥 Download PDF
</button>

<script>
    // Reading progress
    window.addEventListener('scroll', () => {{
        const scrollTop = window.scrollY;
        const docHeight = document.documentElement.scrollHeight - window.innerHeight;
        const progress = (scrollTop / docHeight) * 100;
        document.getElementById('reading-progress').style.width = progress + '%';
        document.getElementById('progress-text').textContent = Math.round(progress) + '% read';
    }});

    // PDF Download
    function downloadPDF() {{
        const btn = document.getElementById('pdf-btn');
        btn.classList.add('loading');
        btn.innerHTML = '⏳ Preparing PDF...';
        
        const title = document.querySelector('.cover-title').textContent || 'ebook';
        const safeName = title.replace(/[^a-zA-Z0-9\u0600-\u06FF]/g, '_').substring(0, 50);
        
        const opt = {{
            margin: 0,
            filename: safeName + '.pdf',
            image: {{ type: 'jpeg', quality: 0.95 }},
            html2canvas: {{
                scale: 2,
                useCORS: true,
                backgroundColor: '#0a0a0a',
                logging: false
            }},
            jsPDF: {{
                unit: 'mm',
                format: [120, 213],
                orientation: 'portrait'
            }},
            pagebreak: {{ mode: ['avoid-all', 'css'] }}
        }};
        
        // Hide UI elements during PDF generation
        document.getElementById('pdf-btn').style.display = 'none';
        document.getElementById('reading-progress').style.display = 'none';
        document.querySelector('.nav-bar').style.display = 'none';
        
        html2pdf().set(opt).from(document.body).save().then(() => {{
            // Restore UI
            document.getElementById('pdf-btn').style.display = 'flex';
            document.getElementById('reading-progress').style.display = 'block';
            document.querySelector('.nav-bar').style.display = 'flex';
            btn.classList.remove('loading');
            btn.innerHTML = '📥 Download PDF';
        }}).catch(() => {{
            document.getElementById('pdf-btn').style.display = 'flex';
            document.querySelector('.nav-bar').style.display = 'flex';
            btn.classList.remove('loading');
            btn.innerHTML = '📥 Download PDF';
            alert('PDF ready! Use browser Print → Save as PDF for best quality.');
            window.print();
        }});
    }}
</script>

</body>
</html>'''
    
    return html

def get_niche_suggestions(language: str = "en") -> list:
    """Get profitable niche suggestions using Groq"""
    
    messages = [
        {"role": "system", "content": "You are a digital marketing expert specializing in ebook sales on social media."},
        {"role": "user", "content": f"""List 15 highly profitable ebook niches for TikTok/social media sales in {language}.
Return ONLY a JSON array, no other text:
[
  {{
    "niche": "niche name",
    "title_idea": "specific book title idea",
    "why_profitable": "one sentence why it sells",
    "price_range": "$X-$Y"
  }}
]

Focus on niches that:
- Solve urgent problems
- Appeal to mobile readers
- Are trending in 2024-2025
- Have proven sales on TikTok
Language for suggestions: {language}"""}
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
    """Main function"""
    # Get inputs from environment or arguments
    book_title = os.environ.get("BOOK_TITLE", "")
    language = os.environ.get("BOOK_LANGUAGE", "en")
    action = os.environ.get("ACTION", "generate")
    
    if not GROQ_API_KEY:
        print("ERROR: GROQ_API_KEY not set!")
        sys.exit(1)
    
    os.makedirs("output", exist_ok=True)
    
    if action == "suggest":
        print(f"🎯 Getting niche suggestions in {language}...")
        suggestions = get_niche_suggestions(language)
        
        # Save suggestions as HTML
        suggestions_html = generate_suggestions_page(suggestions, language)
        with open("output/niche_suggestions.html", "w", encoding="utf-8") as f:
            f.write(suggestions_html)
        print("✅ Suggestions saved to output/niche_suggestions.html")
        
    elif action == "generate":
        if not book_title:
            print("ERROR: BOOK_TITLE not set!")
            sys.exit(1)
        
        print(f"📚 Generating book: '{book_title}' in {language}...")
        
        # Detect theme
        theme_key = detect_theme(book_title, language)
        theme = BOOK_THEMES[theme_key]
        print(f"🎨 Theme: {theme_key} {theme['emoji']}")
        
        # Generate book structure
        print("✍️ Writing book content with Groq AI...")
        book_data = generate_book_structure(book_title, language)
        
        # Save JSON
        with open("output/book_data.json", "w", encoding="utf-8") as f:
            json.dump(book_data, f, ensure_ascii=False, indent=2)
        
        # Generate HTML
        print("🎨 Designing professional layout...")
        html = generate_html_book(book_data, theme, language)
        
        # Clean filename
        safe_title = re.sub(r'[^\w\s-]', '', book_title).strip().replace(' ', '_')[:50]
        filename = f"output/{safe_title}_{language}.html"
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write(html)
        
        print(f"✅ Book generated: {filename}")
        print(f"📖 Title: {book_data.get('title', book_title)}")
        print(f"📝 Chapters: {len(book_data.get('chapters', []))}")
        
        # Save metadata
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
    """Generate HTML page for niche suggestions"""
    items_html = ""
    for i, s in enumerate(suggestions, 1):
        items_html += f'''
        <div class="suggestion-card">
            <div class="suggestion-num">{i:02d}</div>
            <div class="suggestion-content">
                <h3>{s.get("niche", "")}</h3>
                <p class="title-idea">💡 {s.get("title_idea", "")}</p>
                <p class="why">{s.get("why_profitable", "")}</p>
                <span class="price">{s.get("price_range", "$20-50")}</span>
            </div>
        </div>'''
    
    return f'''<!DOCTYPE html>
<html lang="{language}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Profitable Book Niches 2025</title>
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ background:#0a0a0a; color:#fff; font-family:system-ui; max-width:480px; margin:0 auto; padding:20px; }}
h1 {{ font-size:1.8rem; text-align:center; margin-bottom:10px; color:#fff; }}
.subtitle {{ text-align:center; color:#888; margin-bottom:30px; font-size:0.9rem; }}
.suggestion-card {{ background:#1a1a1a; border-radius:15px; padding:20px; margin-bottom:15px; border-left:4px solid #fd7e14; display:flex; gap:15px; }}
.suggestion-num {{ font-size:1.5rem; font-weight:900; color:#fd7e14; min-width:35px; }}
h3 {{ font-size:1.05rem; margin-bottom:8px; color:#fff; }}
.title-idea {{ color:#ffc107; font-size:0.88rem; margin-bottom:6px; }}
.why {{ color:#888; font-size:0.82rem; margin-bottom:10px; }}
.price {{ background:#fd7e14; color:#000; padding:3px 12px; border-radius:20px; font-size:0.8rem; font-weight:700; }}
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
