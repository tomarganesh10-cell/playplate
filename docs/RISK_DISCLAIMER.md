# Risk Disclaimer

**Read this in full before using Trading Playplate with any real capital.**

## No guarantee of profit

Trading Playplate is a software tool for technical analysis, signal generation,
and order management. It does **not** and **cannot** guarantee any profit. Any
statement, score, "confidence" value, backtest, or AI-generated explanation
produced by this system is **analysis, not advice, and not a prediction**.

- Markets are uncertain. You can lose some or all of your capital.
- Past performance — including backtested or paper-traded performance — is
  **not** indicative of future results.
- Backtests are hypothetical, computed on historical data, and subject to
  survivorship bias, look-ahead risk, slippage assumptions, and overfitting.

## Not investment advice

Nothing produced by this software constitutes investment, financial, legal, or
tax advice, or a solicitation or recommendation to buy or sell any security.
Consult a SEBI-registered investment adviser before trading.

## Your responsibility

- You are solely responsible for every order placed in a live brokerage account.
- You are responsible for complying with all applicable laws, exchange rules,
  and your broker's terms (including Zerodha's API terms).
- The authors and contributors accept **no liability** for any loss or damage
  arising from the use of this software.

## Safety design (and its limits)

The platform is engineered to be conservative:

- **Paper trading is the default.** Live order routing is disabled unless
  `TRADING_MODE=live` **and** `ALLOW_LIVE_TRADING=true`.
- Every live order additionally requires an explicit per-order confirmation token.
- A risk manager enforces position sizing, exposure caps, a daily-loss limit,
  and a drawdown limit, backed by a circuit breaker that halts new entries.

These controls reduce, but do **not** eliminate, risk. Software has bugs;
networks fail; markets gap. Use only risk capital you can afford to lose, and
start in paper mode.

## Software warranty

This software is provided "AS IS", without warranty of any kind, express or
implied, including but not limited to the warranties of merchantability,
fitness for a particular purpose, and non-infringement.
