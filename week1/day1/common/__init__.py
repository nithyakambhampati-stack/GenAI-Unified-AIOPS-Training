"""
common - shared helpers used by every solution in this lab.

* config.py : reads the .env file and exposes model IDs and settings
* llm.py    : one thin wrapper around the Anthropic SDK (plain calls, tool-use loop,
              token counting, JSON extraction)

Keeping these in one place means each solution script stays short and focused on the
concept it teaches, not on API plumbing.
"""
