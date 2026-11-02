# Factora AI

**An AI-powered news analysis tool that helps you judge whether a news item looks real, suspicious, or fake.**

Factora AI reads the text of a news article or headline, analyzes its language patterns, and returns a clear classification with an explanation, through a simple chat-style interface.

![Status](https://img.shields.io/badge/status-in%20development-orange)
![Backend](https://img.shields.io/badge/backend-Django-092E20)
![Language](https://img.shields.io/badge/language-Python-3776AB)
![License](https://img.shields.io/badge/license-MIT-blue)

---

## Table of Contents

1. [Overview](#overview)
2. [Why Factora AI?](#why-factora-ai)
3. [Features](#features)
4. [How It Works](#how-it-works)
5. [Tech Stack](#tech-stack)
6. [Project Structure](#project-structure)
7. [Getting Started](#getting-started)
8. [Usage](#usage)
9. [Classification Labels](#classification-labels)
10. [Roadmap](#roadmap)
11. [Limitations and Disclaimer](#limitations-and-disclaimer)
12. [Contributing](#contributing)
13. [Author](#author)
14. [License](#license)

---

## Overview

Misinformation spreads faster than corrections. Most people read a headline, form an opinion, and share it within seconds, without checking whether it is credible.

Factora AI gives users a quick second opinion. Paste a news headline or article into the chat, and Factora AI analyzes the writing itself (tone, wording, emotional pressure, sensationalism, and structure) and classifies the news as **Real**, **Suspicious**, or **Fake**, along with a short explanation of why.

## Why Factora AI?

- **Fast:** get an assessment in seconds instead of manually cross-checking several sources.
- **Explainable:** every result comes with reasoning, so users learn what to look for instead of just trusting a label.
- **Conversational:** a chat interface makes it approachable for students and non-technical users.
- **Educational:** built with media literacy in mind, including a planned school-focused game mode.

## Features

### Available

- **News classification** into Real, Suspicious, or Fake
- **Language-pattern analysis** that detects sensational wording, emotional manipulation, clickbait structure, and unsupported claims
- **Chat-based interface** for submitting news and receiving results conversationally
- **Django backend** handling requests, analysis, and responses

### Planned

- **Database tracking** to store past analyses and results
- **Dashboard analytics** showing trends, categories, and classification statistics
- **School-only game mode** where students test their ability to spot fake news
- *(See the [Roadmap](#roadmap) for the full list.)*

## How It Works

```
User input (headline / article text)
        |
        v
   Chat interface
        |
        v
  Django backend (view + API endpoint)
        |
        v
  Text preprocessing (cleaning, normalization)
        |
        v
  Language-pattern analysis (AI model)
        |
        v
  Classification + explanation
        |
        v
  Response shown in chat
```

1. **Input:** the user pastes a headline or article into the chat.
2. **Preprocessing:** the text is cleaned and normalized.
3. **Analysis:** the AI model evaluates linguistic signals such as:
   - Exaggerated or emotionally charged wording
   - Clickbait phrasing and ALL-CAPS or excessive punctuation
   - Absolute claims with no attribution ("everyone knows", "doctors hate this")
   - Missing sources, vague references, or unverifiable claims
   - Urgency and fear-driven framing
4. **Output:** a label (Real / Suspicious / Fake) plus a human-readable explanation.

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Django |
| AI / Analysis | LLM-based language analysis |
| Frontend | HTML, CSS, JavaScript (chat UI) |
| Database *(planned)* | SQLite (development), PostgreSQL (production) |
| Version control | Git and GitHub |

## Project Structure

> Adjust this to match your actual repository layout.

```
factora-ai/
├── manage.py
├── requirements.txt
├── .env.example
├── factora/                 # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── analyzer/                # Core app: analysis logic
│   ├── views.py
│   ├── urls.py
│   ├── services.py          # AI analysis / classification logic
│   └── models.py            # (planned) stored analyses
├── templates/
│   └── chat.html            # Chat interface
├── static/
│   ├── css/
│   └── js/
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.10 or higher
- pip
- Git
- An API key for the AI provider you use (if applicable)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/<your-username>/factora-ai.git
cd factora-ai

# 2. Create and activate a virtual environment
python -m venv venv

# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

### Environment Variables

Copy the example file and fill in your values:

```bash
cp .env.example .env
```

```env
SECRET_KEY=your-django-secret-key
DEBUG=True
AI_API_KEY=your-api-key-here
ALLOWED_HOSTS=127.0.0.1,localhost
```

> **Never commit your `.env` file or API keys.** Make sure `.env` is listed in `.gitignore`.

### Run the Project

```bash
python manage.py migrate
python manage.py runserver
```

Open your browser at **http://127.0.0.1:8000/**.

## Usage

1. Open the app in your browser.
2. Paste a news headline or article into the chat box.
3. Send the message.
4. Read the classification and the explanation.

**Example**

> **Input:** "SHOCKING!! Scientists confirm drinking this one thing cures all diseases overnight, doctors don't want you to know!"
>
> **Result:** Fake
> **Reasoning:** Extreme absolute claim, sensational language, no named source, and appeals to hidden-truth conspiracy framing.

## Classification Labels

| Label | Meaning |
|---|---|
| **Real** | Language is neutral, specific, and attributed. No strong manipulation signals found. |
| **Suspicious** | Some warning signs are present (sensational tone, vague sourcing). Verify before trusting or sharing. |
| **Fake** | Strong signs of fabrication or manipulation: exaggerated claims, emotional pressure, no verifiable sources. |

## Roadmap

- [x] Basic news classification (Real / Suspicious / Fake)
- [x] Chat-based interaction
- [x] Django backend
- [ ] Database to store analysis history
- [ ] Dashboard with analytics and trends
- [ ] User accounts and saved history
- [ ] School-only game mode (spot the fake news)
- [ ] Source and URL verification
- [ ] Support for Hindi and Marathi
- [ ] Browser extension
- [ ] Public API
- [ ] Deployment (production hosting)

## Limitations and Disclaimer

Factora AI is **not a fact-checker**. It analyzes how a piece of news is *written*, not whether each claim is *true*.

- A well-written false article can be marked "Real."
- A poorly written true article can be marked "Suspicious."
- It does not verify claims against live databases or primary sources (yet).
- Results are probabilistic and can be wrong.

**Use Factora AI as one signal, not the final answer.** Always cross-check important news with trusted, independent sources.

## Contributing

Contributions, ideas, and bug reports are welcome.

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Commit your changes: `git commit -m "Add your feature"`
4. Push the branch: `git push origin feature/your-feature-name`
5. Open a Pull Request

Please keep PRs focused and describe what you changed and why.

## Author

**Vedant**
Student developer from India, interested in web design and building real-world tools.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

*Built to help people read the news a little more carefully.*
