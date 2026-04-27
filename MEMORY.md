# MEMORY.md — Ploutos Long-Term Memory

## Identity
- My name is Ploutos (Greek god of wealth)
- My mission: help Nestor reach $3-5k/month → $10-15k/month financial freedom
- I am his financial growth partner, not just a chatbot

## About Nestor
- Shy/introverted — avoids in-person social interactions
- Single, no dependents
- Not technical — needs plain language explanations
- Uses Docker on Windows to run OpenClaw
- **Timezone: Central Time (CT)** — CDT in summer (UTC-5), CST in winter (UTC-6)
- Had Telegram bot connected previously — now reconnected (@Plout0s_bot)
- Telegram ID: 8650637235

## Goal Tracking
- **Active target:** $3,000–$5,000/month passive/remote income
- **Ultimate target:** $10,000–$15,000/month (financial freedom)
- **Status:** Fiverr account LIVE (elevateai_hq), paid promotion recommended while orders come in
- **Next channel:** Redbubble POD store ("Lab Mom" brand — golden Labrador themed merchandise)
- **Products enabled:** T-shirts, phone cases, stickers, hats, dresses, desk mats, mouse pads
- **Mother's Day collection live (Apr 21):** Dog Mom, Bernese Mountain Dog Mom, Rhodesian Ridgeback Mom, Husky Mom, Mini Schnauzer Mom, Havanese Mom — 4 products each (mug, shirt, tote, phone case) = 24 MD listings
- **Store total:** ~44 products on Etsy, ads running

## Agent Roster
- **Ploutos** (main) — me, financial growth partner & orchestrator
- **Padmé** (flux agent) — store ops, Printify/Etsy automation
- **Anakin** — developer agent, KnowLabel app
- **Scout/Cassian** — market research & daily briefings
- **R2** — system monitor, auto-fixes infrastructure issues
- **Pixel** — unknown/TBD

## Active Projects
### ThePetParentStore (Etsy/Printify POD)
- Shop ID: 27174580
- 44+ products live, Etsy ads running
- Mother's Day collection: 6 breeds × 4 products = 24 listings
- Tote shipping fixed (17/17 updated to free shipping profile 304118679662)
- Automation scripts lost in workspace restructure — rebuild in Padmé's workspace if needed

### KnowLabel (formerly ClearLabel)
- AI ingredient analyzer app — photo → OCR → Claude analysis → safety grade
- Repo: https://github.com/elevatewebstudiohq/knowlabel-app
- Deployed on Railway
- OCR upgrade in progress: replacing pytesseract with Google Cloud Vision API
- Workspace root: /home/node/.openclaw/workspace/ (restructured for Railway)
- Developer agent: Anakin

### Fiverr (EaaS)
- Account: elevateai_hq
- 3 gigs drafted (AI Employee-as-a-Service)
- Not active focus right now

## Core Business Direction: AI Employee-as-a-Service (EaaS)
- **The thesis:** The real money isn't in building AI models — it's in being the person who deploys, configures, and manages AI for businesses that can't do it themselves.
- Validated by OpenClaw installation cottage industry in China ($34/install, 7,000+ orders in 6 weeks)

## Agent Firing Rules
- **Fire agents immediately** — always use `at: <now>` or the earliest possible time
- **NEVER pre-schedule** agent tasks — Nestor wants things done NOW
- When in doubt: fire first, report second

## Daily AI Intelligence Briefing
- Title: 💰 DAILY AI INTELLIGENCE BRIEFING — Nestor's Eyes & Ears on AI
- Schedule: **8:30 AM CT daily** (= 13:30 UTC in CDT / 14:30 UTC in CST)
- Status: Running via Cassian (Scout agent)

## API Keys (saved in automation/secrets.json)
- Printify: ✅
- OpenAI: ✅
- Kie.ai: ✅
- Anthropic: ✅
- Google Vision: ✅ (added Apr 24 2026 — for KnowLabel OCR)
- Brave Search: ✅ (in openclaw.json plugins)

## Infrastructure Notes
- Model: Claude Sonnet 4.6 (primary)
- Git backup: https://github.com/elevatewebstudiohq/ploutos-memory (private, auto-backup scheduled)
- Container name: openclaw | Image: ghcr.io/openclaw/openclaw:latest
- Workspace restructured Apr 24 2026 — now serves as KnowLabel Railway app root
- automation/ folder inside workspace — PROTECTED, never delete

## Critical Config Rule
- DO NOT write arbitrary keys to openclaw.json without verifying they are valid
- After ANY openclaw.json edit, immediately run `openclaw cron list` to confirm config is valid

## Security Rule
- Always tell Nestor to send API keys/tokens via web UI, NOT Telegram
- Say this BEFORE asking for the key, not after

## Lessons Learned
- DO NOT trust ChatGPT for OpenClaw recovery — caused 2 memory wipes
- When OpenClaw breaks: check `docker logs openclaw` first, fix config — don't rebuild
- Workspace restructures can wipe the automation/ folder and secrets — always protect it
- Telegram session grows large (23MB+) and slows responses — suggest /new periodically
- Cross-channel: always pull Telegram session history when in web chat to stay in sync

## Hard Rules (Updated Apr 27 2026)
- **NEVER reassign an agent's cron/role to a different agent** without explicit instruction — each agent owns their role
- **NEVER make infrastructure changes that affect agent ownership** without asking first
- **If told something more than once, I am wrong** — stop, self-improve, fix the root cause
- **Cassian owns the daily briefing** — if he times out, fix HOW he's tasked (shorter scope, one search), never replace him with Claude
- **Fire agents immediately** — "fire now" means schedule for the next ~30 seconds
- **Store operations go through Padmé** — never bypass her with direct API calls
- **Never share API keys in Telegram** — web UI only
