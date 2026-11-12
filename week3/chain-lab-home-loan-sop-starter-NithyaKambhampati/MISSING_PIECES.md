# Missing pieces (search the code for "TODO (missing piece")

| Id | Where | What to write |
|---|---|---|
| M1 | doc_store.py: split_sections() | split the SOP text into sections at each [S#.#] heading |
| M2 | doc_store.py: search() | rank sections by overlapping words (title words count double), best first |
| M3 | injection.py: wrap_untrusted() | wrap text in tags so a closing tag inside the text cannot end the block |
| M4 | injection.py: detect_injection() | return the patterns found in the text, ignoring case |
| M5 | chain.py: verify_citation() | the section exists and the quote appears in it (ignore case and extra spaces) |
| M6 | chain.py: render_markdown() | the answer, its sources and a review note when needed |
| M7 | prompts/system_message.md, prompts/extract_template.md, CHAIN_DESIGN.md | YOUR system message, extract prompt and chain design: the main exercise |
| M8 | tests/ | tests for retrieval, injection and verification |
| M9 | stretch | tree-of-thought: for an unclear question, have the model list two readings, then pick one |
