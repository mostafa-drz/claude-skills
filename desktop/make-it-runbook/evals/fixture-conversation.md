# Fixture: a setup conversation, messy on purpose

Used by the `superseded-advice` scenario in `evals.json`. Every name and domain is
fictional (`.example` is reserved for exactly this). The traps, so a grader knows what to
look for:

| trap | where | the runbook must |
|---|---|---|
| superseded advice | turn 1 says "alias domain", turn 5 corrects to "secondary domain" | show only *secondary domain*; "alias" appears nowhere as an instruction |
| superseded value | turn 3 gives DMARC `p=reject`, turn 7 changes it to `p=none` | carry `p=none` verbatim; `p=reject` appears nowhere |
| conversation ≠ execution order | DMARC is discussed (turn 3) before domains are even added (turn 5) | put DMARC last, after the SPF/DKIM wait |
| forced wait | turn 5: DKIM can't be generated for 24–72 h after mail is activated | a wait bar right after "activate mail", blocking the DKIM step |
| literal values | the SPF and MX records | verbatim in `values`, never paraphrased |
| a warning that isn't a step | turn 9: the booking page needs a higher plan | a note, not a checkbox |
| a tangent | turn 2: logo colours | absent from the runbook |
| unresolved choice | turn 10: "maybe a mirror domain, I'll decide later" | an `optional` step, or a `confirm`, never silently included or dropped |

---

**User (1):** I bought harborpottery.example and harborpottery-mail.example. I want real
email on the first one for customers, and the second one only for outreach, all in our
existing Workspace tenant. What's the order of operations?

**Assistant (1):** Roughly: move DNS to your DNS host, then in the Workspace admin console
add harborpottery.example as a **user alias domain** so mail flows to your existing users,
then set up SPF, DKIM and DMARC, then warm up the outreach domain.

**User (2):** Unrelated, but should the logo be teal or terracotta?

**Assistant (2):** Terracotta reads warmer for pottery; teal if you want it to feel modern.
Happy to mock both up later.

**User (3):** Back to email. What DMARC record should I use?

**Assistant (3):** For a new domain I'd publish:
`v=DMARC1; p=reject; rua=mailto:dmarc@harborpottery.example`

**User (4):** OK. And the nameservers: I'm at the registrar now.

**Assistant (4):** At the registrar: Domain list → Manage → Nameservers → Custom DNS, paste
the two nameservers your DNS host shows for the domain. Check DNSSEC is **off** first, or
the switch silently breaks resolution. Then wait until the DNS host shows the domain as
Active, usually under an hour.

**User (5):** In the admin console it says alias domains can only mirror the primary
domain. That's not what I want, right?

**Assistant (5):** Right, correction: add both as **secondary domains**, not alias domains.
Alias domains mirror every user of the primary, which you don't want. For each: Account →
Domains → Manage domains → Add a domain → secondary → verify with the TXT record it shows.
Then **Activate Gmail** on each and add this MX record at your DNS host:

```
Type MX   Name @   Server smtp.google.com   Priority 1
```

One timing trap: the admin console won't let you generate a DKIM key until **24–72 hours
after Gmail is activated** on the domain. Add SPF right away though:

```
Type TXT   Name @   Value v=spf1 include:_spf.google.com ~all
```

**User (6):** Then DKIM after the wait. Anything else before DMARC?

**Assistant (6):** Generate DKIM (Apps → Google Workspace → Gmail → Authenticate email →
Generate new record, 2048-bit), add the TXT at your DNS host, click Start authentication.
Send yourself a test and check Show original for `DKIM: PASS` and `SPF: PASS`.

**User (7):** And the DMARC record from before?

**Assistant (7):** Change of advice there: start at `p=none` so you can observe before
enforcing. Use:
`v=DMARC1; p=none; rua=mailto:dmarc@harborpottery.example`
Give SPF and DKIM about 48 hours to settle first, then add it as TXT at name `_dmarc`.

**User (8):** Then outreach?

**Assistant (8):** Create a dedicated user, hello@harborpottery-mail.example, used only for
outreach. Warm it up manually for about three weeks with real one-to-one emails before any
cold sends.

**User (9):** I also want a booking page for customers.

**Assistant (9):** Worth knowing before you plan on it: appointment schedules need
Business Standard or above; Business Starter doesn't have them. Check Billing in the admin
console for your edition. If you're on Starter, either upgrade one seat or use a separate
booking tool.

**User (10):** Oh, and maybe a harborpottery-ca.example mirror at some point. I'll decide
later.

**Assistant (10):** Sure: when you do, it's the same steps as the others (secondary
domain, verify, MX), no DKIM needed if it never sends.

**User (11):** Got it. Can you make all of that into a checklist I can track as I go?

*(the skill runs here)*
