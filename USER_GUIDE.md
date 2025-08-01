# Trading Bot User Guide & Playbook

This document provides a detailed explanation of the trading patterns and strategies implemented in this bot.

## Trading Philosophy

The bot operates on a "context-first" approach. A trade is only considered if the signal aligns with the broader market structure (regime). All signals are then scored based on a confluence of factors, and only high-scoring signals are acted upon. The core tenets are:
- Trade with the trend.
- Cut losses quickly.
- Let winners run.
- Add to winning positions on low-risk pullbacks.

---

## Pattern Playbook

### 1. Engulfing Patterns (Candlestick)

- **Description:** A powerful two-candle reversal pattern.
- **Bullish Engulfing:** A bearish candle is followed by a larger bullish candle that completely "engulfs" the prior candle's body. It signals a potential reversal from a downtrend to an uptrend.
- **Bearish Engulfing:** A bullish candle is followed by a larger bearish candle that engulfs the prior candle's body. It signals a potential reversal from an uptrend to a downtrend.
- **Bot Logic:**
    - The bot detects both bullish and bearish variations.
    - An Engulfing pattern is only considered a valid signal if it aligns with the market regime (e.g., a Bullish Engulfing will only be considered in a broader Uptrend, signaling a potential end to a small pullback).
    - The stop-loss is placed just below the low (for longs) or above the high (for shorts) of the large engulfing candle.

---

### 2. AB=CD Pattern (Geometric)

- **Description:** A "measured move" pattern consisting of four points (A, B, C, D) that exhibit price and time symmetry. It's used to identify potential trade completion points.
- **Bullish AB=CD:** The pattern starts with a low point (A), moves up to a high (B), retraces to a higher low (C), and then projects to a higher high (D). The key is that the price distance of the AB leg is roughly equal to the CD leg.
- **Bearish AB=CD:** The inverse of the bullish pattern.
- **Bot Logic:**
    - The bot identifies sequences of swing points that match the AB=CD structure.
    - **Fibonacci Requirement:** It requires the C point to be a 0.618 to 0.786 retracement of the AB leg.
    - **Symmetry:** It projects the D point based on the length of the AB leg. While the current implementation identifies the structure, a full implementation would wait for price to reach the "Potential Reversal Zone" around D and look for confirmation before entering.

---

### 3. Gartley "222" Pattern (Harmonic)

- **Description:** A more complex 5-point reversal pattern (X, A, B, C, D) based on specific Fibonacci ratios. It is used to identify high-probability reversal points.
- **Bullish Gartley:** A powerful up-move (XA) is followed by a retracement (ABCD) that forms a distinct "W" shape. The entry point is at D.
- **Bearish Gartley:** The inverse, forming an "M" shape.
- **Bot Logic:**
    - The bot searches for sequences of five swing points that match the precise Fibonacci structure of the Gartley pattern:
        1.  The **B** point must be a **~0.618** retracement of the initial **XA** leg.
        2.  The **D** point must be a **~0.786** retracement of the **XA** leg.
        3.  The final **CD** leg is typically a **1.272 to 1.618** extension of the **BC** leg.
    - The bot uses the tolerances defined in `config.yaml` to allow for minor deviations from these perfect ratios.
    - A signal is generated at the completion of the D point, with a stop-loss placed just beyond the initial X point.
