<p align="center">
  <h1 align="center">FinRadar</h1>
  <p align="center"><strong>AI Agent for Financial Intelligence & Startup Talent Discovery</strong></p>
</p>

<p align="center">
  <a href="#-purpose"><strong>Purpose</strong></a> •
  <a href="#-tech-stack"><strong>Tech Stack</strong></a> •
  <a href="#-features"><strong>Features</strong></a> •
  <a href="#-quick-start"><strong>Quick Start</strong></a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.11+-blue.svg" alt="Python 3.11+">
  <img src="https://img.shields.io/badge/DSPy-2.5+-green.svg" alt="DSPy">
  <img src="https://img.shields.io/badge/Prefect-3.0+-orange.svg" alt="Prefect 3">
  <img src="https://img.shields.io/badge/LlamaIndex-0.12+-purple.svg" alt="LlamaIndex">
</p>

---

## 🎯 Purpose

**FinRadar is an autonomous AI agent that:**

1. **Continuously discovers** high-potential startup teams across Crunchbase, TechCrunch, ProductHunt, and GitHub
2. **Notifies discovered teams** that they've been identified by FinRadar AI
3. **Delivers team intelligence** to you (the user) via Slack/Email
4. **Generates outreach materials** (emails, LinkedIn messages) for you to connect
5. **Facilitates career opportunities** (internships, jobs, collaborations)

### The Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                     FINRADAR AGENT LOOP                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  🔍 DISCOVER           →    📊 ASSESS        →    📤 NOTIFY     │
│  Crunchbase                 Fit Score             Team Email    │
│  TechCrunch                 Skill Match           Slack Alert   │
│  ProductHunt                Role Fit              User Inbox    │
│  GitHub Trending            Culture Match                       │
│                                                                  │
│                              ↓                                   │
│                                                                  │
│  📧 OUTREACH PREP      →    📋 DELIVER        →    🤝 CONNECT   │
│  Email Templates            Startup Profile       You contact   │
│  LinkedIn Messages          Team Details          opportunities │
│  Conversation Starters      Contact Info                        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack (Cutting-Edge 2025)

| Component | Technology | Why It's Better |
|-----------|------------|-----------------|
| **Agent Framework** | DSPy 2.5 | Declarative LLM programming, auto-optimization |
| **Type-Safe Agents** | PydanticAI | Production-grade reliability, type safety |
| **Document Processing** | LlamaIndex 0.12 | Best-in-class RAG and workflows |
| **Orchestration** | Prefect 3.x | Modern scheduling, observability, distributed |
| **Financial Data** | SEC EDGAR + yfinance | Free, official, real-time |
| **Startup Discovery** | Crunchbase + TechCrunch | Comprehensive coverage |
| **Vector Store** | Qdrant | Hybrid search, low latency |

### Why This Stack Beats LangChain

| Metric | LangChain | DSPy + PydanticAI |
|--------|-----------|-------------------|
| **Prompt Engineering** | Manual iteration | Automatic optimization |
| **Type Safety** | Runtime errors | Compile-time validation |
| **Production Reliability** | Medium | **Highest (benchmarked)** |
| **Debugging Experience** | Poor | Structured, traceable |
| **Declarative Power** | Low | High (signatures > prompts) |

---

## ✨ Features

### 🔍 Continuous Discovery
- **Multi-source aggregation**: Crunchbase, TechCrunch, ProductHunt, GitHub
- **Smart filtering**: Funding stage, industry, growth signals
- **Real-time alerts**: Slack/Email when high-fit teams found

### 📊 Intelligent Assessment
- **Fit scoring**: 0-100 based on skills, tech stack, culture
- **Role matching**: AI recommends best-fit positions
- **Gap analysis**: Identifies skill mismatches

### 📤 Dual Notification System
1. **Team Notification**: "You've been discovered by FinRadar AI"
2. **User Alert**: Slack message with profile + action buttons

### 📧 Outreach Automation
- **Personalized emails**: Generated per startup/founder
- **LinkedIn messages**: Connection request templates
- **Conversation starters**: AI-crafted talking points

### ⏰ Scheduling (Prefect)
- **Continuous discovery**: Every 6 hours
- **Weekly deep scan**: Full market analysis
- **Earnings monitoring**: Real-time alerts

---

## 🚀 Quick Start

```bash
git clone https://github.com/your-org/finradar.git
cd finradar

cp .env.example .env
# Edit .env with your keys

docker compose up -d

pip install -e ".[dev]"

finradar discover --industry "AI" --stage "Series A"
```

### Configure Your Profile

Edit `app/workflows/discovery_flow.py`:

```python
CANDIDATE_PROFILE = CandidateProfile(
    name="Your Name",
    email="your.email@example.com",
    skills=["Python", "TypeScript", "React", "Machine Learning"],
    experience_years=3,
    target_roles=["Software Engineer", "ML Engineer"],
    seeking=["Full-time", "Internship"],
)
```

### Run Discovery

```bash
finradar discover --industry "AI" --industry "Fintech" --limit 30
```

---

## 📡 Notification Flow

### To Discovered Teams

```
Subject: 🎉 [Startup Name] - You've Been Discovered by FinRadar AI!

Dear [Team Name],

Our AI agent has identified your team as a high-potential startup
in the [Industry] space. A qualified candidate using FinRadar has
expressed interest in connecting for potential opportunities.

If you're interested, they may reach out directly. No action required.

Best,
FinRadar AI
```

### To You (via Slack)

```
🎯 New Startup Discovered: [Name]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Fit Score: 85/100 | Stage: Series A
Industry: AI/ML | Location: San Francisco

Description: [Startup description...]

[📧 Send Email] [💼 LinkedIn] [🌐 Website]

Outreach status: ✅ Team notified | ✅ Email sent
```

---

## 📁 Project Structure

```
finradar/
├── app/
│   ├── agents/
│   │   ├── dspy_signatures.py    # DSPy signatures & modules
│   │   └── outreach_agent.py     # Outreach generation
│   ├── sources/
│   │   ├── financial_sources.py  # SEC, Yahoo Finance
│   │   └── startup_sources.py    # Crunchbase, TechCrunch
│   ├── processors/
│   │   └── outreach.py           # Email, Slack, LinkedIn
│   ├── workflows/
│   │   ├── discovery_flow.py     # Continuous discovery
│   │   └── scheduled_flows.py    # Prefect schedules
│   ├── api/                      # FastAPI
│   └── cli/                      # Typer CLI
├── docker-compose.yml
└── pyproject.toml
```

---

## 🎛️ Configuration

```bash
# LLM
ANTHROPIC_API_KEY=sk-...
OPENAI_API_KEY=sk-...

# Data Sources
CRUNCHBASE_API_KEY=...
SEC_USER_AGENT=FinRadar contact@your.email
ALPHA_VANTAGE_KEY=...

# Notifications
SLACK_WEBHOOK_URL=https://hooks.slack.com/...
EMAIL_SENDER=your.email@gmail.com
EMAIL_PASSWORD=your-app-password

# Scheduling
SCAN_INTERVAL_HOURS=6
DAILY_REPORT_TIME=09:00
```

---

## 🔮 Roadmap

- [ ] LinkedIn API integration for direct messaging
- [ ] Calendar scheduling for discovered teams
- [ ] Multi-language outreach (Japanese, Chinese)
- [ ] Portfolio tracking for contacted startups
- [ ] Response analytics and follow-up automation

---

## 📄 License

MIT

---

<p align="center">
  <strong>Built with DSPy + Prefect + PydanticAI</strong><br>
  <em>The most modern AI agent stack of 2025</em>
</p>
