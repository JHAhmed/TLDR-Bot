# TLDR Bot
A discord bot built on Python that summarizes conversations in your server using a given LLM.
Bring your own BOT_TOKEN and {PROVIDER}_API_KEY in an `.env` (or heck, plug them directly into the code!)
This bot supports slash commands, use `/tldr {number} {style}` to TL;DR a number of messages in different styles!

- Exclude messages from users and bots by adding their user IDs to `exclude_list`

Roadmap:
- Add support for more providers' models
- More styles?