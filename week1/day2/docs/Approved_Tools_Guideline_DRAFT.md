# Approved AI tools - team guideline (DRAFT)

This is a draft from the GenAI Ops training. It isn't policy until Information Security and Legal have reviewed it.
If it disagrees with an official policy, the official policy wins.

It covers the AI tools we use day to day: Claude Code with the organisation's key, chat apps on a personal account
(Claude.ai, ChatGPT, Gemini on free or personal plans), and chat tools under an enterprise agreement.

Main rule: work out what kind of data it is first, then pick the tool.

| Data | Example | Claude Code (org key) | Personal chat account | Enterprise chat |
|---|---|---|---|---|
| Public | A published web page, a public regulation, open-source code | Allowed | Allowed | Allowed |
| Internal | Meeting notes with no personal data, process descriptions, ordinary code | Allowed, but only open the folders you need, and never paste secrets | Not allowed | Ask Security |
| Confidential / personal | Customer names and orders, account numbers, employee records, client contract terms | Ask Security | Not allowed | Ask Security |

Why:
- Public data has nothing to leak, but you still need to check the answers are right.
- Personal accounts are under consumer terms. Chats can be stored and, depending on a setting we can't control,
  used for training. That's why internal data isn't allowed there. With confidential data it could also break
  data-protection law or a client contract, and redaction tools often miss names and free text.
- Enterprise plans are usually fine for internal data once we've confirmed the contract says no training on our
  data and gives a retention period. We need to check that for our actual contract, though.
- For confidential data with Claude Code or an enterprise tool, we need a data-protection review for the use case,
  the data cut down or redacted first, a check on where the data is stored (for example EEA-only), and sign-off
  from the data owner. Also nothing the client contract says can't go to a third party.

Whatever the tool:
1. Use made-up or public examples when you're learning or testing prompts.
2. Never paste API keys, passwords, connection strings or `.env` contents into a chat.
3. Treat every answer as a draft, and check numbers and quotes against the source before anyone acts on them.
4. On any personal account, check the "use my data to improve the model" setting and note whether the account is
   personal or enterprise.
5. If you're not sure which kind of data it is, assume the more sensitive one and ask.

Questions for Security and Legal:
- Which enterprise agreements do we actually have, and what do they say about retention and training?
- Can the org key ever be used on client data, and under which contracts?
- Is there an approved redaction tool?
- Who signs off new tools?

Based on the lab's `data/approved_tools.json`. Draft v0.1.
