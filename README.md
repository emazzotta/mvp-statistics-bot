# MVP Statistics Bot

A simple bot that collects statistics on who's been voted MVP.

## Commands

|Command|Action|
|---|---|
|/help|Show this text|
|/score|Display current MVP stats|
|/vote|Vote for a user (add @username after /vote)|
|/meme|Generate meme for current MVP|
|/register|Register to be eligible for MVP status|

## Getting Started

### Start

```
echo "BOT_SECRET_TOKEN" > src/secret.key
mkdir -p data
docker-compose up -d
```

## Author

[Emanuele Mazzotta](mailto:hello@mazzotta.me)
