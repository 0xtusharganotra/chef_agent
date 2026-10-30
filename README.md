# Personal Chef Agent

A terminal chat assistant built with LangChain, Google Gemini, and LangGraph. It streams response text as it arrives, remembers the current conversation, and can search the web through Tavily.

## Requirements

- Python 3.12 or newer
- uv for dependency management
- A Google Gemini API key with access to the configured model
- A Tavily API key

## Setup

Run these commands from the `personal_chef_agent` directory:

```powershell
uv sync --locked
```

Create a `.env` file in that directory with your own API keys:

```dotenv
GOOGLE_API_KEY=your_google_api_key
TAVILY_API_KEY=your_tavily_api_key
```

Both keys are required by the current startup code. `.env` is excluded from Git; keep actual keys out of source files and commits.

## Run

```powershell
uv run agent.py
```

Type a message at the `YOU` prompt. For example:

```text
Suggest a vegetarian dinner with rice and chickpeas.
Search the web for a quick chickpea curry recipe.
```

The entry point is `agent.py`. `main.py` is a placeholder script.

## Commands

| Command            | Action                                               |
| ------------------ | ---------------------------------------------------- |
| `/help`            | Show available commands.                             |
| `/clear`           | Clear the display while keeping conversation memory. |
| `/reset`           | Start a fresh conversation.                          |
| `/exit` or `/quit` | Exit the application.                                |

`Ctrl+C` also ends the session. Conversation memory is stored in the running process and is not saved between launches.

## Tools and streaming

- `search_internet`: searches Tavily and returns a summary, source URLs, and snippets.
- `get_weather`: a demonstration tool that always reports sunny weather; it does not retrieve actual weather data.

LangChain's `agent.stream(..., stream_mode="messages")` yields model chunks. The app prints text blocks immediately with `flush=True`, without repeatedly redrawing the full answer. Tool arguments and raw tool results are not printed by the streaming loop.

## Configuration

The model settings are defined in `agent.py`:

| Setting               | Current value           |
| --------------------- | ----------------------- |
| Model                 | `gemini-3.5-flash-lite` |
| Provider              | `google_genai`          |
| Request timeout       | 60 seconds              |
| Maximum output tokens | 2,048                   |

If the configured model is unavailable to your API key, change `MODEL_NAME` to a model you can access, then restart the application.

## Project files

```text
personal_chef_agent/
  agent.py          # Agent, tools, streaming, and terminal chat loop
  main.py           # Placeholder script
  pyproject.toml    # Python requirements and dependencies
  uv.lock           # Locked dependency versions
  .python-version   # Local Python version selection
  .gitignore        # Secrets, environments, caches, and generated files
  README.md
```
