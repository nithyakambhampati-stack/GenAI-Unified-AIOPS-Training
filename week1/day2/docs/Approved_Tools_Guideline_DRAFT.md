# Approved AI tools - team guideline (DRAFT)

> **DRAFT for review.** This page is a proposal from the GenAI Ops training. It is **not** policy until our
> organisation's Information Security and Legal teams have reviewed and confirmed it. Where this draft and an
> official policy disagree, the official policy wins.

**Scope.** Generative-AI tools used for day-to-day work: Claude Code with the organisation-issued key, consumer chat
apps on a personal account (Claude.ai, ChatGPT, Gemini free or personal plans), and chat tools under an enterprise
agreement. **Rule of thumb:** classify the data *before* you choose the tool, not after.

| Data class | Example | Claude Code with organisation key | Consumer chat (personal account) | Enterprise plan chat |
|---|---|---|---|---|
| **Public** | A published web page, a public regulation, open-source code | **Allowed.** Public data carries no confidentiality risk; normal care about accuracy still applies. | **Allowed.** Nothing is disclosed that is not already public; still verify the answer before using it. | **Allowed.** Same as the other columns; the enterprise plan adds no restriction for public data. |
| **Internal** | Meeting notes without personal data, an internal process description, non-sensitive code | **Allowed.** The key is organisation-managed, but use only the repositories and folders you need and never paste secrets or credentials. | **Not allowed.** Personal accounts sit under consumer terms; chats may be stored and, depending on a setting the organisation cannot control, used to improve models. | **Ask security.** Usually acceptable once the agreement confirms no training on our data and an agreed retention period, but that must be checked for our specific contract. |
| **Confidential / personal** | Customer names and order history, account numbers, employee records, contract terms with a client | **Ask security.** Only with a documented data-protection review for the use case, data minimised or redacted first, and nothing that the client contract forbids sending to a third party. | **Not allowed.** Personal data in a personal account is outside our control and may breach data-protection law and client contracts; redaction tools miss names and free text. | **Ask security.** Even under enterprise terms, personal and client-confidential data needs a lawful basis, data-location checks (for example EEA-only clauses) and the data owner's approval. |

**Always, whatever the tool**

1. Use synthetic or public examples when you are learning or testing prompts.
2. Never paste API keys, passwords, connection strings or `.env` contents into any chat.
3. Treat every answer as a draft: check figures and quotes against the source before anyone acts on them.
4. Check the "use my data to improve the model" setting on any personal account you use for public data, and record
   whether an account is personal or enterprise.
5. If you are unsure which class the data is in, treat it as the higher class and ask.

**Open questions for Security and Legal:** which enterprise agreements we actually hold and their retention and
training terms; whether the organisation key may ever process client data, and under which contracts; the approved
redaction tool, if any; and who signs off new tools.

*Prepared from `data/approved_tools.json` (lab example list). Draft version 0.1.*
