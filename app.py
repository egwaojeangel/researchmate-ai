"""
ResearchMate — AI Research Assistant
Backend: Flask + Groq (Llama 3.3 70B)
Features: PDF chat, auto-summarise, section extraction, literature review, related papers
"""

import os
import json
import re
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

try:
    import fitz
    PDF_OK = True
except ImportError:
    PDF_OK = False

app = Flask(__name__, static_folder='.')
CORS(app)

GROQ_API_KEY = os.environ.get('GROQ_API_KEY', '')
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

print("=" * 55)
print("  ResearchMate AI")
print(f"  Groq API : {'Connected ✓' if client else 'Missing key ✗'}")
print(f"  PDF      : {'PyMuPDF ✓' if PDF_OK else 'Not installed ✗'}")
print("=" * 55)

papers = {}


def extract_pdf(file_bytes):
    if not PDF_OK:
        return ""
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        return text.strip()
    except Exception as e:
        print(f"PDF error: {e}")
        return ""


def call_groq(system_prompt, user_prompt, max_tokens=3000, json_mode=False):
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_prompt}
            ],
            temperature=0.5,
            max_tokens=max_tokens,
        )
        raw = response.choices[0].message.content.strip()
        if json_mode:
            raw = re.sub(r'^```json\s*', '', raw)
            raw = re.sub(r'^```\s*', '', raw)
            raw = re.sub(r'\s*```$', '', raw)
            m = re.search(r'\{.*\}', raw, re.DOTALL)
            if m: raw = m.group()
            return json.loads(raw)
        return raw
    except Exception as e:
        print(f"Groq error: {e}")
        return {"error": str(e)} if json_mode else f"Error: {str(e)}"


# ── SECTION EXTRACTION CONFIG ──
SECTION_PROMPTS = {
    "contributions": {
        "label": "Contributions",
        "instruction": """Extract and clearly present the research contributions of this paper.
List each contribution as a distinct point. Include:
- The main novel contribution(s)
- Technical innovations introduced
- Theoretical contributions if any
- Practical contributions or applications
Format each as a numbered point with a bold title and explanation."""
    },
    "methodology": {
        "label": "Methodology",
        "instruction": """Extract and explain the methodology of this paper in detail.
Cover:
- The overall research approach/framework
- Data collection or dataset used
- Model architecture or algorithm design
- Training procedure or experimental setup
- Evaluation metrics used
Write in clear academic prose with subsections where appropriate."""
    },
    "results": {
        "label": "Results & Findings",
        "instruction": """Extract all results and findings from this paper.
Include:
- Quantitative results (numbers, metrics, benchmarks)
- Qualitative findings
- Comparison with baselines or prior work
- Ablation study results if present
- Key tables or figures described in the text
Present clearly with specific numbers where mentioned."""
    },
    "limitations": {
        "label": "Limitations",
        "instruction": """Extract and elaborate on all limitations discussed in this paper.
Include:
- Limitations explicitly stated by the authors
- Limitations you can infer from the methodology or results
- Dataset or evaluation limitations
- Scope limitations (what the method does NOT handle)
- Computational or practical limitations
Be honest and thorough."""
    },
    "future_work": {
        "label": "Future Work",
        "instruction": """Extract all future work directions mentioned or implied in this paper.
Include:
- Explicit future work stated by the authors
- Open problems identified
- Extensions suggested
- Potential improvements to the current method
- Broader research directions this work opens up
Number each direction and explain why it matters."""
    },
    "conclusion": {
        "label": "Conclusion",
        "instruction": """Extract and present the conclusion of this paper.
Include:
- What problem was solved and how
- Summary of key results achieved
- The broader significance/impact of this work
- Final takeaways the authors want readers to remember
Write as a coherent summary, not bullet points."""
    },
    "references": {
        "label": "Key References",
        "instruction": """Extract the most important references cited in this paper.
For each key reference include:
- Authors and year
- Title (if mentioned)
- Why it is cited / its relevance to this paper
Focus on the most frequently cited or most important works — up to 15 references.
Format as a numbered list."""
    }
}


# ═══════════════════════════════════════════
#  ROUTES
# ═══════════════════════════════════════════

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')


@app.route('/api/upload', methods=['POST'])
def upload_paper():
    try:
        if not client:
            return jsonify({"error": "API key missing."}), 500
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded."}), 400

        f = request.files['file']
        if not f.filename.lower().endswith('.pdf'):
            return jsonify({"error": "Only PDF files are supported."}), 400

        file_bytes = f.read()
        text = extract_pdf(file_bytes)

        if not text or len(text) < 100:
            return jsonify({"error": "Could not extract text. Make sure it is not a scanned image PDF."}), 400

        import hashlib, time
        paper_id = hashlib.md5(f.filename.encode() + str(time.time()).encode()).hexdigest()[:12]

        papers[paper_id] = {
            "filename": f.filename,
            "text": text[:16000],
            "full_length": len(text),
            "history": [],
            "extractions": {}  # cache extracted sections
        }

        return jsonify({
            "paper_id": paper_id,
            "filename": f.filename,
            "char_count": len(text),
            "truncated": len(text) > 16000
        })

    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route('/api/summarise', methods=['POST'])
def summarise():
    try:
        data = request.get_json()
        paper_id = data.get('paper_id')
        if paper_id not in papers:
            return jsonify({"error": "Paper not found."}), 404

        paper = papers[paper_id]
        result = call_groq(
            system_prompt="You are an expert academic research assistant. Respond only with valid JSON, no markdown, no backticks.",
            user_prompt=f"""Analyse this research paper and return a structured summary as JSON.

PAPER TEXT:
{paper['text']}

Return ONLY this JSON structure:
{{
  "title": "<paper title>",
  "authors": "<authors if found, else Unknown>",
  "year": "<year if found, else Unknown>",
  "field": "<research field>",
  "one_line": "<one sentence capturing the paper in plain English>",
  "problem": "<what problem does this paper address?>",
  "methodology": "<brief methodology summary>",
  "key_findings": ["<finding 1>", "<finding 2>", "<finding 3>", "<finding 4>"],
  "contributions": "<main contributions summary>",
  "limitations": "<key limitations>",
  "keywords": ["<kw1>", "<kw2>", "<kw3>", "<kw4>", "<kw5>"],
  "difficulty": "introductory|intermediate|advanced",
  "recommended_for": "<who should read this and why>"
}}""",
            json_mode=True
        )

        if "error" in result:
            return jsonify(result), 500
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/extract', methods=['POST'])
def extract_section():
    """Extract a specific section from the paper."""
    try:
        data = request.get_json()
        paper_id = data.get('paper_id')
        section  = data.get('section', '').lower()

        if paper_id not in papers:
            return jsonify({"error": "Paper not found."}), 404

        if section not in SECTION_PROMPTS:
            return jsonify({"error": f"Unknown section: {section}"}), 400

        paper = papers[paper_id]

        # Return cached extraction if available
        if section in paper['extractions']:
            return jsonify({
                "section": section,
                "label": SECTION_PROMPTS[section]['label'],
                "content": paper['extractions'][section],
                "cached": True
            })

        cfg = SECTION_PROMPTS[section]
        content = call_groq(
            system_prompt="""You are an expert academic research analyst. 
Extract and present the requested section from the paper clearly and thoroughly.
Use proper formatting — numbered lists, bold headings where appropriate.
If the section is not explicitly present, infer it from the content and say so.""",
            user_prompt=f"""{cfg['instruction']}

PAPER TEXT:
{paper['text']}""",
            max_tokens=2000
        )

        if content.startswith("Error:"):
            return jsonify({"error": content}), 500

        # Cache it
        paper['extractions'][section] = content

        return jsonify({
            "section": section,
            "label": cfg['label'],
            "content": content,
            "cached": False
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        paper_id = data.get('paper_id')
        question = data.get('question', '').strip()

        if not question:
            return jsonify({"error": "Please ask a question."}), 400
        if paper_id not in papers:
            return jsonify({"error": "Paper not found."}), 404

        paper = papers[paper_id]
        history_text = ""
        for turn in paper['history'][-6:]:
            history_text += f"User: {turn['q']}\nAssistant: {turn['a']}\n\n"

        answer = call_groq(
            system_prompt="""You are an expert research assistant helping a user understand a scientific paper.
Answer questions clearly and accurately based on the paper content.
If the answer is not in the paper, say so honestly. Be concise but thorough.""",
            user_prompt=f"""PAPER TEXT:
{paper['text']}

CONVERSATION HISTORY:
{history_text}
USER QUESTION: {question}""",
            max_tokens=1200
        )

        paper['history'].append({"q": question, "a": answer})
        return jsonify({"answer": answer, "question": question})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/literature-review', methods=['POST'])
def literature_review():
    try:
        data = request.get_json()
        paper_id = data.get('paper_id')
        topic    = data.get('topic', '').strip()

        if paper_id not in papers:
            return jsonify({"error": "Paper not found."}), 404

        paper = papers[paper_id]
        review = call_groq(
            system_prompt="You are an expert academic writer specialising in literature reviews. Write in formal scholarly prose.",
            user_prompt=f"""Based on this research paper, generate a structured mini literature review on: "{topic or 'the paper\'s main subject'}"

PAPER TEXT:
{paper['text']}

Write with these sections:
1. **Introduction** — introduce the topic and its importance (2-3 sentences)
2. **Background & Context** — what existed before this work (3-4 sentences)
3. **Current Approaches** — summarise the approach and related methods (4-5 sentences)
4. **Key Themes** — identify 3-4 recurring themes
5. **Gaps & Future Directions** — what remains unsolved (3-4 sentences)
6. **Conclusion** — wrap up (2-3 sentences)

Write in flowing academic prose. No bullet points inside sections.""",
            max_tokens=2000
        )

        return jsonify({"review": review, "topic": topic or "Main subject"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/related-papers', methods=['POST'])
def related_papers():
    try:
        data = request.get_json()
        paper_id = data.get('paper_id')
        if paper_id not in papers:
            return jsonify({"error": "Paper not found."}), 404

        paper = papers[paper_id]
        result = call_groq(
            system_prompt="You are an expert research librarian. Respond only with valid JSON, no markdown, no backticks.",
            user_prompt=f"""Based on this paper, suggest related works and research directions.

PAPER TEXT:
{paper['text'][:6000]}

Return ONLY this JSON:
{{
  "seminal_works": [
    {{"title": "<title>", "authors": "<authors>", "year": "<year>", "why": "<relevance>"}}
  ],
  "recent_advances": [
    {{"title": "<title>", "authors": "<authors>", "year": "<year>", "why": "<relevance>"}}
  ],
  "research_directions": [
    {{"direction": "<direction>", "description": "<why worth exploring>", "difficulty": "easy|medium|hard"}}
  ],
  "datasets": [
    {{"name": "<name>", "description": "<what it contains>", "url": "<URL or empty>"}}
  ],
  "search_terms": ["<term1>", "<term2>", "<term3>", "<term4>", "<term5>"]
}}

Include 3 seminal works, 3 recent advances, 3 research directions, 2-3 datasets.""",
            json_mode=True
        )

        if "error" in result:
            return jsonify(result), 500
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/health')
def health():
    return jsonify({"status": "ok", "model": "llama-3.3-70b-versatile", "pdf": PDF_OK})


if __name__ == '__main__':
    print("\n  ResearchMate running at http://localhost:5000\n")
    app.run(debug=True, host='0.0.0.0', port=5000)