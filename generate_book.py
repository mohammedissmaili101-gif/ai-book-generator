#!/usr/bin/env python3
import os
import json
import re
import requests

# التحسين: تم تعزيز دوال المعالجة لمنع الأخطاء الشائعة
def clean_french_grammar(text: str) -> str:
    """تنظيف النصوص من الأخطاء النحوية وتكرارات الذكاء الاصطناعي"""
    replacements = {
        r"La conditionnement": "Le conditionnement",
        r"la conditionnement": "le conditionnement",
        r"as-built": "as-tu bâti",
        r"lalaitoall": "",
        r"texploiter": "l'exploiter",
        r"Vous allez apprendre à": "Apprenez à",
        r"Dans ce chapitre": "",
        r"Nous allons voir": ""
    }
    for pattern, repl in replacements.items():
        text = re.sub(pattern, repl, text, flags=re.IGNORECASE)
    return text.strip()

def generate_single_chapter_content(book_title: str, chapter: dict, language: str = "fr") -> dict:
    """توليد محتوى كل فصل بشكل مستقل لمنع التكرار"""
    
    # التحسين: برومبت أكثر صرامة لمنع الحشو (Fluff)
    system_prompt = (
        "Tu es un coach expert en psychologie stoïcienne. Ton style : froid, percutant, direct. "
        "Interdiction totale de faire des introductions inutiles (pas de 'Dans ce chapitre', 'Nous allons voir'). "
        "Écris en français impeccable."
    )

    user_prompt = f"""
    Sujet du livre : "{book_title}"
    Titre du chapitre {chapter['number']} : "{chapter['title']}"
    Objectif du chapitre : {chapter.get('focus', '')}
    
    Règles strictes :
    1. Commence directement par le contenu.
    2. Minimum 800 mots.
    3. Utilise des paragraphes courts (max 3 phrases).
    4. Termine par une question de 'Shadow Work' brutale.
    5. Fournis le contenu au format JSON : {{"hook": "...", "content": "...", "exercises": ["...", "..."], "summary": "..."}}
    """

    # هنا يتم استدعاء API بنفس المنطق السابق ولكن مع System Prompt أقوى
    # (باقي كود الاتصال بـ Groq يبقى كما هو لضمان التوافق)
    # ...
    return {"hook": "...", "content": "...", "exercises": [], "summary": "..."}

# ملاحظة: يجب استبدال الدوال القديمة بهذه النسخ المحسنة في ملفك الأصلي.
