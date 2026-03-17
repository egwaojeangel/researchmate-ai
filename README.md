# 📚 ResearchMate — AI-Powered Research Assistant

![Python](https://img.shields.io/badge/Python-3.8+-blue?style=flat-square&logo=python)
![Flask](https://img.shields.io/badge/Flask-3.x-black?style=flat-square&logo=flask)
![Groq](https://img.shields.io/badge/Groq-Llama%203.3%2070B-00a67e?style=flat-square&logo=meta)
![Render](https://img.shields.io/badge/Deployed-Render-46e3b7?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

**Core Stack:** Python · Flask · Groq API · Llama 3.3 70B · PyMuPDF · HTML · Tailwind CSS

An end-to-end AI web application that transforms how researchers, students, and academics interact with scientific papers. Upload any PDF and instantly extract key sections, chat with the paper, generate literature reviews, and discover related work — all powered by Llama 3.3 70B running on Groq's ultra-fast inference API.

---

## 📋 Table of Contents
- [Features](#features)
- [How to Run](#how-to-run)
- [Overview](#overview)
- [How the AI Works](#how-the-ai-works)
- [Section Extraction](#section-extraction)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting a Free Groq API Key](#getting-a-free-groq-api-key)
- [Deployment](#deployment)
- [Limitations](#limitations)
- [Future Work](#future-work)
- [Disclaimer](#disclaimer)

---

## Features

- **Section Extraction** — click any button to extract Contributions, Methodology, Results & Findings, Limitations, Future Work, Conclusion, or Key References — slides out instantly in a panel
- **Auto Summary** — structured breakdown of the paper including problem statement, methodology, key findings, contributions, limitations and keywords
- **Chat with Paper** — ask any question and get answers grounded directly in the paper's content
- **Literature Review Generator** — enter a topic and generate a structured academic literature review in flowing scholarly prose
- **Related Papers** — discover seminal works, recent advances, research directions, relevant datasets and search terms
- **User Authentication** — register and sign in with email and password
- **Clean Academic UI** — minimal white design inspired by academic journals, built with Lora serif typography
- **Fully Responsive** — works on desktop and mobile
- **Deployed on Render** — live public URL, no local setup required for users

---

## How to Run

### Prerequisites
- Python 3.8 or higher
- A free [Groq API key](https://console.groq.com) — takes 2 minutes to get

### 1. Clone the repository

```bash
git clone https://github.com/egwaojeangel/researchmate-ai.git
cd researchmate-ai
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Add your Groq API key

Create a `.env` file in the project folder:

```
GROQ_API_KEY=your-groq-api-key-here
```

### 4. Run the application

```bash
python run.py
```

Open your browser at: **http://localhost:5000**

---

## Overview

Reading and understanding research papers is one of the most time-consuming parts of academic work. A single paper can take hours to properly parse — identifying the core contributions, understanding the methodology, extracting key results, and situating the work within the broader literature.

ResearchMate solves this by acting as an AI research assistant that:

- **Extracts specific sections on demand** — click a button, the content slides out. No scrolling through 20 pages to find the limitations section
- **Answers questions about the paper** — ask anything and get a grounded, accurate response
- **Generates literature reviews** — enter a topic and get structured academic prose ready to use as a starting point
- **Maps the research landscape** — surfaces related works, open problems, useful datasets and search terms

The tool is designed for researchers, postgraduate students, undergraduate students writing dissertations, and anyone who regularly needs to engage with academic literature quickly and deeply.

---

## How the AI Works

When a PDF is uploaded, the backend extracts the raw text using **PyMuPDF** and stores it in memory. All AI features then call **Llama 3.3 70B** via Groq's inference API with carefully designed prompts for each task.

| Feature | Approach |
|---|---|
| Auto Summary | Structured JSON prompt — extracts 10+ fields in one call |
| Section Extraction | Dedicated prompt per section with formatting instructions |
| Chat | Conversational prompt with paper context + conversation history |
| Literature Review | Academic writing prompt with 6 structured sections |
| Related Papers | JSON prompt for seminal works, recent advances, datasets |

**Extracted sections are cached** — clicking the same button a second time returns the result instantly without another API call.

### Why Groq + Llama 3.3 70B

| Factor | Detail |
|---|---|
| Model | Llama 3.3 70B (Meta) |
| Inference Speed | ~500 tokens/second via Groq |
| Cost | Free tier — no credit card required |
| Response Time | 10–20 seconds per extraction |
| Context Window | 128K tokens — handles full papers |

---

## Section Extraction

The core feature of ResearchMate. Seven dedicated extraction buttons each trigger a focused AI analysis of the relevant section:

| Button | What It Extracts |
|---|---|
| **Contributions** | Novel contributions, technical innovations, theoretical and practical value |
| **Methodology** | Research approach, datasets used, model/algorithm design, training setup, evaluation metrics |
| **Results & Findings** | Quantitative results, comparisons with baselines, ablation studies, key numbers |
| **Limitations** | Author-stated and inferred limitations, scope boundaries, dataset and evaluation limitations |
| **Future Work** | Explicit future directions, open problems, suggested extensions, broader research opportunities |
| **Conclusion** | Summary of what was solved, key results, broader significance, final takeaways |
| **Key References** | Most important cited works with relevance explained, formatted as a numbered list |

Results slide out in a panel from the right. Press **Escape** or **Close** to dismiss. Each extraction is cached so repeated clicks are instant.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | HTML5, CSS3, Tailwind CSS (CDN), Vanilla JavaScript |
| Backend | Python 3.8+, Flask, Flask-CORS |
| AI Model | Llama 3.3 70B via Groq API |
| PDF Parsing | PyMuPDF (fitz) |
| Auth | Browser localStorage (client-side) |
| Deployment | Render (gunicorn) |
| Fonts | Lora (serif headings) + DM Sans (body) + DM Mono (labels) |
| Icons | Font Awesome 6 |

---

## Project Structure

```
researchmate-ai/
├── app.py              # Flask backend — upload, summarise, extract, chat, lit review, related
├── run.py              # Entry point — loads .env, starts server
├── index.html          # Complete frontend — single-file UI
├── requirements.txt    # Python dependencies
├── Procfile            # Render deployment config
├── .gitignore          # Excludes .env and __pycache__
└── README.md           # This file
```

---

## Getting a Free Groq API Key

1. Go to [console.groq.com](https://console.groq.com)
2. Sign up for a free account (no credit card needed)
3. Navigate to **API Keys** → **Create API Key**
4. Copy the key and add it to your `.env` file

Groq's free tier provides generous rate limits — more than enough for personal use and demos.

---

## Deployment

This app is deployed on **Render**. To deploy your own instance:

1. Push this repo to GitHub
2. Go to [render.com](https://render.com) → **New → Web Service**
3. Connect your GitHub repository
4. Set the following:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
5. Add an **Environment Variable:** `GROQ_API_KEY = your-key-here`
6. Click **Deploy**

Live in approximately 5 minutes. Free tier is sufficient for demo and portfolio use.

---

## Requirements

```
flask
flask-cors
groq
pymupdf
python-dotenv
gunicorn
```

```bash
pip install -r requirements.txt
```

---

## Limitations

- PDF text extraction may struggle with scanned image-based PDFs — the file must contain selectable text
- Paper text is truncated to ~16,000 characters to stay within API context limits — very long papers may lose content from the end
- No persistent database — papers and chat history exist only for the current server session and are lost on restart
- Section extraction quality depends on how well-structured the original paper is — informal preprints may yield less precise results
- Related papers are AI-suggested and may not reflect the most current literature — always verify on Google Scholar or Semantic Scholar
- Not suitable for high-traffic deployment without adding rate limiting

---

## Future Work

- [ ] Support for multi-paper comparison — upload two papers and compare their approaches
- [ ] Export full analysis as a formatted PDF report
- [ ] ArXiv URL input — paste a paper link instead of uploading a file
- [ ] Citation graph — visualise how the paper's references connect
- [ ] Persistent user accounts with saved paper history
- [ ] Highlight mode — show which part of the PDF each extraction came from
- [ ] Support for longer papers via chunked processing

---

## Disclaimer

> ⚠️ ResearchMate is an AI-assisted tool intended to **support and accelerate** engagement with research literature. It does not replace careful reading, critical analysis, or expert judgement. AI-extracted content should always be verified against the original paper before being used in academic work.

---

## Author

**Angel Egwaoje**

Machine Learning Engineer | AI Applications & Full-Stack Development

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue?style=flat-square&logo=linkedin)](https://www.linkedin.com/in/angel-egwaoje-416927280)
[![GitHub](https://img.shields.io/badge/GitHub-Follow-black?style=flat-square&logo=github)](https://github.com/egwaojeangel)
