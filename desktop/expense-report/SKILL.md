---
name: expense-report
description: >-
  Scans Gmail for receipt and invoice emails within a date range, extracts
  merchant, amount, date, and category from each, then produces a clean expense
  table grouped by category with totals — ready to copy, paste, or save to
  Drive. Use when asked to "build my expense report", "find my receipts for
  March", "what did I spend on travel last month", "pull my work expenses",
  "compile receipts for reimbursement", or "how much did I spend on software
  this quarter".
---

# Expense Report

Every month there is a stretch of 20–30 minutes spent hunting through Gmail for receipt confirmations, opening each one, and copying amounts into a spreadsheet. Airline receipts buried in promotion tabs, hotel confirmations from two weeks ago, SaaS renewal emails that look like newsletters — it's a tedious search that happens to anyone who has to submit expenses or track spending. This skill does the hunting and the extraction, producing a clean table ready for a reimbursement form or a budget review.

## Configuration

```
date_range: last month        # "last month", "this month", "YYYY-MM", or "YYYY-MM-DD to YYYY-MM-DD"
categories: all               # "all" or comma-separated: travel, meals, software, equipment, other
currency: USD                 # ISO currency code; used to format amounts
flag_personal: true           # Flag items that look personal (subscriptions, streaming, etc.)
save_to_drive: ask            # "ask", "yes", or "no"
```

## Process

### 1. Clarify Scope

Ask the user:
1. What time period? (default: last calendar month)
2. Any categories to exclude? (default: all)
3. Work-only or all spending? (helps flag personal items)

If the user says "just go", use the defaults above.

### 2. Search Gmail for Receipts

Run multiple searches to catch the full spread of receipt formats:

- `subject:(receipt OR invoice OR "order confirmation" OR "payment confirmation")`
- `subject:("thank you for your purchase" OR "your order" OR "booking confirmation")`
- `from:(noreply OR no-reply OR billing OR receipts OR invoices)`

Apply the date range filter to each search. Collect all matching emails (deduplicate by thread and message ID).

**Volume limit:** If more than 60 emails match, report the count and ask the user whether to continue or narrow the date range.

### 3. Extract Line Items

For each receipt email, extract:

| Field | Notes |
|-------|-------|
| Date | Date on the receipt (not the email received date, when different) |
| Merchant / Vendor | The company name, not the sender email |
| Amount | The total charged amount; include currency symbol |
| Category | Classify as: Travel, Meals, Software, Equipment, Accommodation, or Other |
| Source | A short label: `Gmail: "[Subject]"` |

**Parsing notes:**
- If the email is plaintext with a dollar amount, extract it directly.
- If the email links to a PDF receipt (not inline), note the merchant and flag the amount as "PDF — verify manually".
- If multiple line items appear (e.g., itemized hotel bill), use the total only.
- If the amount is ambiguous (partial payment, refund, credit), note it in parentheses.

### 4. Classify and Deduplicate

- Merge duplicate emails for the same transaction (e.g., "Order confirmed" + "Order shipped" from the same merchant for the same amount on the same date → keep one).
- Flag items that look personal: streaming services (Netflix, Spotify), personal subscriptions, grocery stores, pharmacies, non-work merchants. Label these `⚠️ Personal?` — don't remove them; let the user decide.

### 5. Build the Expense Table

Group by category, then sort by date within each group:

```
💳 Expense Report — [Month Year]
Scanned: Gmail ([date range]) — [N] receipts found

Travel                               $XXX.XX
─────────────────────────────────────────────
Mar 04  United Airlines               $342.00   Gmail: "Your flight receipt"
Mar 08  Marriott Hotels               $198.50   Gmail: "Thank you for your stay"

Meals                                 $XX.XX
─────────────────────────────────────────────
Mar 07  Noma                           $94.30   Gmail: "Your reservation receipt"

Software                              $XX.XX
─────────────────────────────────────────────
Mar 01  Cursor                         $20.00   Gmail: "Your Cursor subscription..."
Mar 15  Vercel                         $20.00   Gmail: "Invoice #INV-2026-..."

─────────────────────────────────────────────
Total                                $674.80

⚠️  Items to review (2):
  • Mar 12  Netflix        $15.99 — looks personal
  • Mar 22  Amazon         $XX.XX — PDF receipt, verify amount manually
```

### 6. Offer to Save

After presenting the table, ask:

> Want me to save this as a Google Doc in Drive? I can also format it as a CSV-style table for pasting into a spreadsheet.

If yes: create a Google Doc titled "Expense Report — [Month Year]" in the user's Drive root (or a folder they specify). Include the full table plus a note of the search queries used.

## Guidelines

- **Show before saving.** Always present the table for review before writing anything to Drive.
- **No amounts invented.** If a receipt email doesn't contain a parseable amount, mark it as "verify manually" — don't estimate.
- **Flag, don't remove.** Personal-looking items stay in the table; the user decides what's reimbursable.
- **Admit gaps.** If Gmail returns nothing for a date range, say so — don't pad with guesses.
- **Respect the currency.** If receipts contain non-USD amounts, show them in the original currency with a note; don't convert unless asked.
- **Privacy-aware.** Show summaries in the report; avoid quoting full email body text in conversation.

## Example

**User:** "Pull my expenses for April"

```
💳 Expense Report — April 2026
Scanned: Gmail (Apr 01 – Apr 30) — 11 receipts found

Travel                               $540.50
─────────────────────────────────────────────
Apr 03  United Airlines               $342.00   Gmail: "Your receipt for flight UA447"
Apr 09  Marriott San Francisco        $198.50   Gmail: "Thank you for your stay"

Software                              $68.00
─────────────────────────────────────────────
Apr 01  Cursor                         $20.00   Gmail: "Your Cursor invoice"
Apr 01  Linear                         $18.00   Gmail: "Linear invoice — April 2026"
Apr 01  Vercel                         $20.00   Gmail: "Invoice #INV-0492"
Apr 15  Figma (seat upgrade)           $10.00   Gmail: "Figma payment confirmation"

Meals                                 $94.30
─────────────────────────────────────────────
Apr 10  Che Fico                       $94.30   Gmail: "Your OpenTable receipt"

─────────────────────────────────────────────
Total                                $702.80

⚠️  Items to review (1):
  • Apr 14  Spotify        $10.99 — looks personal

Would you like me to save this to Drive, or export it as a CSV table?
```
