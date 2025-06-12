# TLDR Bot

A Discord bot written in Python that summarizes recent chat messages using either OpenAI or Google's Gemini APIs. The bot is controlled via slash commands and supports multiple summary styles.

## Features

* Uses slash command: `/tldr {number} {style}`
* Summarizes recent messages in a channel
* Supports multiple output styles: `normal`, `list`, `pirate`, `cowboy`, `dramatised`
* Can switch between OpenAI and Google Gemini as the language model provider
* Guild-specific command syncing for faster development

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/JHAhmed/TLDR-bot.git
cd TLDR-bot
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Create a `.env` file

```env
BOT_TOKEN=your_discord_bot_token
GEMINI_API_KEY=your_google_gemini_api_key
OPENAI_API_KEY=your_openai_api_key
GUILD_ID=your_test_server_id # Optional
```

Only one of the API keys is used depending on the provider selected.

### 4. Run the bot

```bash
python bot.py
```
