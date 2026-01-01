# Zenon Telegram Bot

This bot is developed to use in Zenon Network Telegram channels.

## Setting Everything Up

### Creation of Bot
- Create a Telegram Bot by typing `/newbot` to @BotFather on Telegram

### Installation

#### Option 1: Run with Python

1. Install Python3
2. Install dependencies:
   ```bash
   pip install python-telegram-bot --upgrade
   pip install python-dotenv requests
   ```
3. Configure environment:
   ```bash
   cp .env-example .env
   ```
4. Edit `.env` and set `TOKEN` to your Telegram bot token from @BotFather
5. Run the bot:
   ```bash
   python main.py
   ```

#### Option 2: Run with Docker

```bash
docker compose up -d --build
```

Set the `TOKEN` environment variable before running, or create a `.env` file.

#### Option 3: Deploy with Portainer

1. In Portainer, go to Stacks > Add stack
2. Paste the contents of `docker-compose.yml` or use the repository URL
3. Add environment variable: `TOKEN` = your bot token from @BotFather
4. Deploy the stack

### Showing Commands on Typing '/' in Telegram Chat
- Go to @BotFather on Telegram
- Use `/setcommands` command
- Send the command list below in a single message:

```
bridge - Bridge Command
buy - Buy $ZNN token
ca - Ethereum Contract Address
chart - Price Chart
decks - Investor Decks
explorers - Blockchain Explorer
forums - List of Forums
github - Github Repositories
links - Important Links
mc - Market cap of ZNN & QSR
nodes - List of Public Nodes
p2p - How to p2p swap in syrius
price - Current price of ZNN & QSR
pricechat - Price Chat
roadmap - Development Roadmap
staking - Staking & Delegating
supply - Current and max supply
trackers - Telegram Trackers
wallets - Download s y r i u s wallet
whitepaper - Download Whitepaper
```
