# MVP Statistics Bot

A simple bot that collects statistics on who's been voted MVP.

## Getting Started

The file `secret.key` in `src` must contain the token of the bot.

### Docker Start

```
# From project directory
mkdir -p data
docker-compose up -d
```

### Regular Start

```
# From project directory
./setup.sh
venv/bin/python src/bot.py
```

## Commands

|Command|Action|
|---|---|
|/help|Show this text|
|/score|Display current MVP stats|
|/vote|Vote for a user (add @username after /vote)|
|/meme|Generate meme for current MVP|
|/register|Register to be eligible for MVP status|

## Author

[Emanuele Mazzotta](mailto:hello@mazzotta.me)
