# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Telegram bot for Zenon Network community channels. Provides informational commands about ZNN/QSR tokens, network resources, pricing, and ecosystem links.

## Running the Bot

```bash
# Install dependencies
pip install python-telegram-bot --upgrade
pip install python-dotenv requests

# Configure environment
cp .env-example .env
# Edit .env and set TOKEN to your Telegram bot token from @BotFather

# Run
python main.py
```

### Docker

```bash
# Build and run with Docker Compose
docker compose up -d --build

# View logs
docker compose logs -f
```

## Architecture

Single-file bot (`main.py`) using `python-telegram-bot` library with async handlers:

- **Command handlers**: Each `/command` maps to an async function that returns formatted Markdown text
- **Chat member tracking**: `track_chats()` monitors bot membership in groups/channels/private chats
- **External APIs**:
  - `https://api.zenon.info/price` - ZNN/QSR/BTC/ETH prices
  - `https://zenonhub.io/api/nom/token/get-by-owner` - Token supply data

## Adding New Commands

1. Create async handler function following existing pattern:
```python
async def mycommand(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = """..."""
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
```

2. Register in `main()`:
```python
application.add_handler(CommandHandler("mycommand", mycommand))
```

3. Update bot commands in @BotFather using `/set_commands`

## Key Patterns

- All responses use Markdown formatting with `disable_web_page_preview=True`
- URLs stored in lists, referenced by index in formatted strings
- Token amounts from API have 8 decimal places (divide by 10^8 or slice `[:-8]`)
