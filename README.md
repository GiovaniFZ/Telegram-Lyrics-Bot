# Giv's Lyrics Bot

A Telegram bot that helps you find song lyrics without leaving your chat.
Send an artist and song title to the bot, and it retrieves the lyrics from an
external lyrics API.

## Commands

| Command | Description |
| --- | --- |
| `/start` | Start interacting with the bot. |
| `/help` | Show the available commands. |
| `/lyrics` | Enter an artist name and then a song title to look up lyrics. |
| `/cancel` | Cancel an active lyrics lookup. |
| `/search <query>` | Search by query. |
| `/source` | Show the source code link. |
| `/donation` | Show ways to support the project. |

## Requirements

- Python 3.14 or newer for a local installation.
- A Telegram bot token, obtained from [BotFather](https://t.me/BotFather).
- Internet access to Telegram and the lyrics API.
- Docker, if running in a container instead of locally.

## Configuration

Copy `.env.example` to `.env` and fill in the values:

```dotenv
BOT_TOKEN=your_telegram_bot_token
SERPAPI_KEY=your_serpapi_key
USDT_KEY=your_usdt_eth_address
BTC_KEY=your_btc_address
```

| Variable | Purpose |
| --- | --- |
| `BOT_TOKEN` | Required to connect the bot to Telegram. |
| `SERPAPI_KEY` | SerpApi key for `/search`, which is currently disabled. |
| `USDT_KEY` | USDT/ETH address displayed by `/donation`. |
| `BTC_KEY` | BTC address displayed by `/donation`. |

Keep `.env` private and never commit real tokens or keys. The bot also accepts
these settings as environment variables.

## Run locally

From the project directory, create a virtual environment and install the
dependencies:

**Windows (PowerShell):**

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```

**Linux or macOS:**

```bash
python3.14 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
cp .env.example .env
```

Edit `.env`, then run:

```powershell
# Windows
.\.venv\Scripts\python.exe main.py
```

```bash
# Linux or macOS
.venv/bin/python main.py
```

Open your bot in Telegram, send `/start`, then use `/lyrics` and follow the
prompts.

## Tests

Install the development dependencies and run the tests with Python 3.14 or
newer:

```powershell
uv sync
uv run pytest
```

Tests can use `MockBotService` from `adapters.mock_bot_service` to exercise
commands without contacting Telegram. Its `messages`, `edited_messages`,
`callback_messages`, and `answered_callbacks` attributes record interactions.
`sent_messages["msg"]` and `parse_modes["parse_mode"]` contain the latest sent
message and its parse mode.

## Run with Docker

After configuring `.env`, build and start the container:

```bash
docker build -t lyrics-bot .
docker run -d --name lyrics-bot --env-file .env lyrics-bot
```

View logs or stop the container with:

```bash
docker logs -f lyrics-bot
docker stop lyrics-bot
```

The bot uses Telegram polling, so it does not need an exposed port. Avoid
running multiple polling instances with the same bot token.

## Project structure

- `main.py` configures the application and registers command handlers.
- `commands/` contains the bot commands and lyrics lookup flow.
- `services/` defines interfaces for bot, environment, and HTTP operations.
- `adapters/` provides concrete implementations of those interfaces.

## Credits

- [Lyrica](https://github.com/Wilooper/Lyrica)
