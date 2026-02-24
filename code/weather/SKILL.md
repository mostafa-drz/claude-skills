---
name: weather
description: >-
  Checks the current weather for the user's location using live online data.
  Asks for location on first use and saves it for future runs.
  Use when the user wants a quick weather check or forecast.
argument-hint: "[city name]"
context: fork
allowed-tools:
  - AskUserQuestion
  - Bash
  - WebFetch
  - WebSearch
  - Read
  - Write
  - Edit
---

# Weather

Check the current weather for your location using live data from Open-Meteo (free, no API key needed).

## Preferences

_Read `~/.claude/skills/weather/preferences.md` using the Read tool. If not found, no preferences are set._

## Command routing

Check `$ARGUMENTS`:

- **`help`** → display help then stop
- **`config`** → interactive setup then stop
- **`reset`** → delete `~/.claude/skills/weather/preferences.md`, confirm, stop
- **anything else** (including empty) → run the skill

### Help

```
Weather — Check current weather for your location

Usage:
  /weather                     Show weather for saved location
  /weather Berlin              Show weather for Berlin
  /weather config              Set your default location
  /weather reset               Clear saved location
  /weather help                This help

Examples:
  /weather                     Uses your saved city
  /weather "New York"          One-off check for New York
  /weather Tokyo               One-off check for Tokyo

Current preferences:
  (shown above under Preferences)
```

### Config

Use **AskUserQuestion**:

**Q1** — "What city are you in?" (text input via Other)
- Options: suggest common cities as quick picks, plus Other for custom input

**Q2** — "Temperature unit?"
- Celsius (default)
- Fahrenheit

Save to `~/.claude/skills/weather/preferences.md`.

### Reset

Delete `~/.claude/skills/weather/preferences.md` and confirm: "Preferences cleared. Using defaults."

## First-time detection

If no preferences file exists and no city argument was provided:

1. Use **AskUserQuestion** to ask: "Where are you located? (city name)"
2. After getting weather, offer to save the location

## Steps

### 1. Determine location

- If `$ARGUMENTS` contains a city name (not help/config/reset) → use that city
- Else if preferences has a saved city → use that
- Else → ask via **AskUserQuestion**: "What city should I check the weather for?"

### 2. Geocode the city

Use **WebFetch** to call the Open-Meteo geocoding API:

```
https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json
```

Extract `latitude`, `longitude`, and `name` (resolved city name) from the first result.

If no results found, tell the user and ask for a different city.

### 3. Fetch current weather

Use **WebFetch** to call the Open-Meteo forecast API:

```
https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m,wind_direction_10m&temperature_unit={celsius|fahrenheit}&wind_speed_unit=kmh&timezone=auto
```

### 4. Display weather

Show a fun, concise weather card:

```
{weather emoji} Weather in {City}

  Temperature:  {temp}°{C/F} (feels like {apparent}°)
  Conditions:   {description from weather code}
  Humidity:     {humidity}%
  Wind:         {speed} km/h {direction}

  {fun one-liner comment about the weather}
```

**Weather code mapping** (WMO codes):
- 0: Clear sky
- 1-3: Partly cloudy
- 45, 48: Foggy
- 51-55: Drizzle
- 61-65: Rain
- 66-67: Freezing rain
- 71-77: Snow
- 80-82: Rain showers
- 85-86: Snow showers
- 95-99: Thunderstorm

**Emoji mapping:**
- Clear → sun
- Cloudy → cloud
- Rain/Drizzle → rain
- Snow → snowflake
- Thunderstorm → lightning
- Fog → fog

### 5. Offer to save (first-time only)

If no preferences existed and no city argument was given, ask:

> Save {City} as your default location?

If yes, write preferences file.

## Principles

- **Always live data** — never cache or guess weather; always fetch fresh from the API.
- **Fun and concise** — keep it light. One screen, one glance. Add a witty comment about the conditions.
- **Fail gracefully** — if the API is down or city not found, say so clearly and suggest alternatives.
- **Respect saved preferences** — once configured, just show the weather with zero friction.
