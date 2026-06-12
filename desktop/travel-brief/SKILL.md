---
name: travel-brief
description: >-
  Compiles a structured trip brief from Gmail booking confirmations, Google
  Calendar events during the trip window, and live destination information
  (time zone, weather forecast, currency, and practical notes).
  Use when preparing for a trip, asking "prep me for my trip to X", "what do
  I need for my flight to Tokyo", "brief me on my Boston trip next week",
  or "what meetings do I have while I'm traveling".
---

# Travel Brief

Every trip has its context spread across four or five places: a flight confirmation buried in Gmail, a hotel booking forwarded weeks ago, meetings on the calendar that span time zones, a weather forecast you forgot to check. This skill pulls it into one brief before you pack.

## Process

### 1. Identify the Trip

If the user named a destination or timeframe, use that. Otherwise, search Google Calendar for events that look like travel (titles containing "flight", "hotel", "trip", "travel", "conference", "offsite", or a city name) in the next 30 days.

Ask at most one clarifying question if multiple trips are found or the destination is ambiguous.

Show what was resolved:
```
✈️  Trip identified: [destination]
    Dates: [departure – return]
    Source: [Calendar / user-provided]
```

If no trip is found, tell the user and offer to build a brief for a trip they describe.

### 2. Pull Booking Confirmations from Gmail

Search Gmail for booking-related emails matching the destination and date range. Look for:
- Flight confirmations (keywords: "booking confirmation", "e-ticket", "itinerary", "reservation", destination name, airline names)
- Hotel confirmations (keywords: "hotel confirmation", "check-in", "reservation", destination name)
- Car rental, train, or ferry bookings
- Conference or event registrations

For each booking found, extract and show:
```
[Type] [Carrier / Property]
  ✅ [Route or location]
  📅 [Date and time]
  🔖 Confirmation: [number]
  📧 From: [sender], [date received]
```

If Gmail is not connected, note it and continue.

### 3. Overlay Calendar Events During the Trip

Pull all Calendar events that fall within the trip's departure and return dates. Flag:
- Meetings or calls (especially multi-person events — the user may need to prepare or reschedule)
- Working blocks or focus time
- Events with video links that will need time-zone adjustment

Show them as a lightweight agenda:
```
📅 [Date, local time] — [event title]
   With: [attendees, if any]
   Note: [time zone shift if international]
```

If no events are found during the trip window, say so.

### 4. Fetch Destination Info

Web search for practical trip info about the destination:
- **Time zone** and UTC offset (relative to the user's home time zone if determinable from Calendar)
- **Weather forecast** for the trip dates — temperature range and conditions
- **Currency** (for international trips) — local currency name and approximate exchange rate
- **Practical notes** — anything immediately useful: plug adapter type, tipping norms, common transport options, relevant entry requirements

Keep this section tight — three to five bullet points. Don't pad with tourist content.

### 5. Compile the Brief

Assemble everything into a single scannable brief:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Trip Brief: [destination]
[departure date] → [return date]  ·  [N] nights
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Bookings
  ✈️  [Airline] [flight number] — [dep. time] → [arr. time], [date]
      Confirmation: [number]
  🏨  [Hotel name] — check-in [date], check-out [date]
      Confirmation: [number]

Calendar During Trip
  [Day 1]  [event], [event]
  [Day 2]  [event]
  [Day 3]  (free)

Destination
  🕐  Time zone: [zone name] (UTC[offset]) — [X hours ahead/behind you]
  🌤  Weather: [forecast summary for trip dates]
  💱  Currency: [name] ([code]) — approx. [rate] to 1 USD
  📋  Notes: [2–3 practical bullet points]

⚠️  Heads-up
  [Any unresolved items — e.g., "No hotel confirmation found. You may want to
   check your bookings." or "You have a recurring standup on Tuesday — check
   if it needs to be rescheduled."]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Then ask: **"Anything else to add before you pack?"**

### 6. Optional Follow-Up

If the user asks to go deeper:
- Show the full booking confirmation email
- Draft a "I'll be traveling" out-of-office note or Slack message
- Suggest calendar events to reschedule or mark as tentative

## Guidelines

- **Detect, don't assume** — only include booking details actually found in Gmail. If a booking type is missing, surface a heads-up rather than fabricating it.
- **Time zone translation** — for international trips, always show the local departure/arrival time and note the offset. A missed time zone is the most common travel mistake.
- **One heads-up section** — collect all flags (missing booking, conflicting meeting, tight connection) into a single block at the end, not scattered through the brief.
- **Keep destination info practical** — weather and time zone are almost always needed. Currency only matters for international. Skip tourist suggestions unless asked.
- **Don't repeat email content** — summarize bookings in a line; don't dump the full confirmation.

## Example

**User:** "Prep me for my NYC trip next week"

**Output:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Trip Brief: New York City
Mon Jun 16 → Wed Jun 18  ·  2 nights
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Bookings
  ✈️  Air Canada AC 456 — 8:10 AM → 11:35 AM, Mon Jun 16
      Confirmation: ABC123
  🏨  The Arlo Nomad — check-in Jun 16, check-out Jun 18
      Confirmation: HTL-88291
  (No car rental found)

Calendar During Trip
  Mon Jun 16  Design review (3 PM) · Dinner w/ Alex (7 PM)
  Tue Jun 17  Keynote presentation (10 AM) · Team dinner (6 PM)
  Wed Jun 18  Morning free · Flight home 2 PM

Destination
  🕐  Time zone: Eastern (UTC-4) — same as your current zone
  🌤  Weather: Partly cloudy, 72–80°F Mon–Wed; light rain possible Tuesday
  💱  USD — no exchange needed
  📋  Notes: JFK → Manhattan ~60 min by AirTrain + subway ($9) or ~45 min
      taxi ($70+). Jun 17 keynote at Javits; arrive 30 min early for badge.

⚠️  Heads-up
  • You have a recurring Wednesday standup at 9 AM — you'll be in transit
    to the airport. Consider declining or asking for async notes.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```
