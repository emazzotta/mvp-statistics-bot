# MVP Statistics Bot

A simple bot that collects statistics on who's been voted MVP.

## Getting Started

The file `secret.key` in `src` must contain the token of the bot.

### Docker Start

```
# From project directory
mkdir -p data
docker-compose -f setup/docker-compose.yml up -d
```

### Regular Start

```
# From project directory
setup/setup
venv/bin/python src/bot.py
```

## Commands

|Command|Action|
|---|---|
|/help|Show this text|
|/score|Display current MVP stats|
|/vote|Vote for a user (add @username after /vote)|
|/register|Register to be eligible for MVP status|

## Author

[Emanuele Mazzotta](mailto:hello@mazzotta.me?subject=MVP%20Statistics%20Bot&body=Hi%20Emanuele!%0A%0AMESSAGE_HERE%0A%0AReagards%20MYNAME_HERE)

## License

See the [LICENSE](LICENSE.md) file for license rights and limitations (MIT).
