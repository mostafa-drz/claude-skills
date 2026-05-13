# Emotion frameworks reference

This file is loaded by the main workflow when applying sentiment / emotion analysis. Each framework section gives the model the exact taxonomy and decision rules to use, plus a short justification.

---

## 1. Plutchik's Wheel of Emotions (1980)

**Eight primary emotions**, arranged in opposing pairs:

| Emotion       | Opposite      | Linguistic markers (English)                              |
|---------------|---------------|-----------------------------------------------------------|
| Joy           | Sadness       | "great", "love", "amazing", "yes!", excited punctuation   |
| Trust         | Disgust       | "thanks", "appreciate", "agree", reassurance language     |
| Fear          | Anger         | "worried", "afraid", "what if", hedging modals            |
| Surprise      | Anticipation  | "wait", "didn't expect", "huh", exclamatives              |
| Sadness       | Joy           | "tired", "down", "ugh", flat affect, low energy markers   |
| Disgust       | Trust         | "gross", "awful", "hate", strong rejection language       |
| Anger         | Fear          | "frustrated", "stupid", "wtf", caps, repeated punctuation |
| Anticipation  | Surprise      | "looking forward", "planning", future-tense + agency      |

**Intensity gradients** (Plutchik called these dyads): each primary has a milder and stronger form, e.g. _serenity → joy → ecstasy_. The skill records the primary; intensity comes from the Russell arousal axis (below).

**Decision rule**: tag a user message with **0-2 primary emotions**. If neither tag has strong evidence, leave empty (tone-neutral). Never assign all 8 — that's noise.

**Why this framework**: Plutchik's wheel is the most widely-used emotion model in computational sentiment work because it gives discrete categories that pair naturally with linguistic markers. It's used in NRC Emotion Lexicon (Mohammad & Turney, 2013), which is the de facto standard in NLP emotion tagging.

---

## 2. Ekman's Basic Emotions (1992)

Six universal emotions argued to be cross-culturally recognised:

- Happiness
- Sadness
- Fear
- Anger
- Surprise
- Disgust

Ekman's set overlaps Plutchik's but drops Trust and Anticipation. Useful when:
- The conversation is short and you want a coarser tag
- The user preference is `framework: ekman`
- You're producing the "dominant emotion" line in the at-a-glance section — six is easier for humans to parse than eight.

**Why this framework**: Ekman's facial-expression studies (1971, 1992) are the foundational empirical case for universal emotion categories. Even with later challenges (Barrett, 2017, _How Emotions Are Made_), Ekman remains the canonical reference and is widely understood.

---

## 3. Russell's Circumplex Model of Affect (1980)

A **dimensional** rather than categorical model. Every affective state is a point on two axes:

- **Valence** — pleasant (+1) ↔ unpleasant (−1)
- **Arousal** — activated (+1) ↔ calm (0)

This produces four quadrants:

| Quadrant | Valence | Arousal | Example states           | Suggested HTML colour swatch |
|----------|---------|---------|--------------------------|------------------------------|
| Q1       | +       | +       | excited, enthusiastic    | warm gold `#d4a04a`          |
| Q2       | −       | +       | tense, frustrated, angry | desaturated rose `#c66b6b`   |
| Q3       | −       | −       | tired, bored, low        | dusty indigo `#6b6b8a`       |
| Q4       | +       | −       | calm, content, focused   | sage green `#7a9580`         |

**Decision rule**: every analysed user message gets a `(valence, arousal)` pair in `[-1, 1] × [0, 1]`. Aggregate by mean.

The **dominant quadrant** for the report is the quadrant where the centroid of all message points falls. Use this to pick the at-a-glance swatch colour.

**Why this framework**: Russell's circumplex is the dominant dimensional model in affective science. It explains why "tired" and "frustrated" — both negative — feel completely different (arousal axis), and why categorical tags miss that. The valence/arousal pair is also what most affective-computing systems output today (Russell, 1980; Posner, Russell, & Peterson, 2005).

---

## 4. Pennebaker-style linguistic markers (LIWC, 2003–2015)

The skill applies a lightweight LIWC-inspired analysis. The model counts (or estimates ratios for) these categories across the window:

| Category              | What it suggests                                              | Reference                        |
|-----------------------|---------------------------------------------------------------|----------------------------------|
| 1st-person singular   | Self-focus; rising trend correlates with rumination / sadness | Pennebaker (2003), Rude et al. (2004) |
| Negative-emotion words| Distress, frustration, anxiety                                | Tausczik & Pennebaker (2010)     |
| Positive-emotion words| Engagement, gratitude, satisfaction                           | Tausczik & Pennebaker (2010)     |
| Cognitive complexity  | "because", "however", "although" — flexible thinking          | Pennebaker (2003)                |
| Certainty markers     | "never", "always", "must" — rigid thinking, often anxious     | Pennebaker (2003)                |
| Social references     | "we", "they", names — connection vs isolation                 | Tausczik & Pennebaker (2010)     |
| Temporal focus        | Past / present / future verb tense ratio                      | Pennebaker (2011)                |

**Decision rule for flagging**: only flag a marker shift if it differs **≥50% from baseline** (learned from prior sessions). Never flag on the first session — there's no baseline yet.

**Important caveat to include in reports**: linguistic markers are correlational, not diagnostic. A high 1st-person count in a debugging session doesn't mean depression — it might mean the user is the only one debugging. Context matters.

---

## 5. Supporting frameworks (cited but not used as primary)

- **Csikszentmihalyi's Flow (1990)** — productive struggle vs. distress. Used to reframe frustration patterns that show high engagement (long messages, complex problem-solving) rather than withdrawal.
- **Fredrickson's Broaden-and-Build (2001)** — positive emotions broaden cognition and build resources. Used in the "Bright spots" section to explain _why_ that section matters.
- **Walker's sleep research (_Why We Sleep_, 2017)** — invoked when late-night sessions correlate with negative-valence drops.
- **Barrett's Theory of Constructed Emotion (2017)** — invoked in the caveats section to remind the reader that emotion categories themselves are constructed, not discovered. This is the honest counterweight to Ekman.

---

## Decision priority

When `framework: combined` (the default):

1. Use **Russell** for the at-a-glance quadrant + sparkline (it's the most informative single number).
2. Use **Plutchik** for the "Dominant emotions" section (richer categorical labels).
3. Use **Pennebaker** for the "Patterns" section (linguistic shifts over time).
4. Use **Ekman** as a fallback simplification when summarising for the user verbally.

When `framework: <single>`, use only that one across all sections.
