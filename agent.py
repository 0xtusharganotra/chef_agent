
import os
import uuid

from dotenv import load_dotenv

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.align import Align
from rich.text import Text
from rich.rule import Rule

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from tavily import TavilyClient

# ─────────── CONFIGURATION ───────────

load_dotenv()

console = Console()
MODEL_NAME = "gemini-3.5-flash-lite"
AGENT_NAME = "CHEF AGENT"
tavily_client = TavilyClient(
    api_key=os.environ["TAVILY_API_KEY"]
)


if not os.getenv("GOOGLE_API_KEY"):
    console.print("[bold red]GOOGLE_API_KEY is missing![/]")
    raise SystemExit(1)


# ─────────── TOOLS ───────────

@tool
def get_weather(city: str) -> str:
    """Get the weather for a given city."""
    return f"It's always sunny in {city}!"


@tool
def search_internet(query: str) -> str:
    """Search the live internet for current information,
    news, recent events, and factual questions.
    """
    response = tavily_client.search(
        query=query,
        search_depth="basic",
        max_results=5,
        include_answer=True,
    )

    results = []

    if response.get("answer"):
        results.append(
            f"Search summary: {response['answer']}"
        ) 

    for item in response.get("results", []):
        results.append(
            f"Title: {item.get('title', '')}\n"
            f"URL: {item.get('url', '')}\n"
            f"Content: {item.get('content', '')}"
        )

    return "\n\n".join(results) or "No results found."

# ─────────── MODEL ───────────

model = init_chat_model(
    MODEL_NAME,
    model_provider="google_genai",
    timeout=60,
    max_tokens=2048,
)

checkpointer = InMemorySaver()

agent = create_agent(
    model=model,
    tools=[get_weather, search_internet],
    system_prompt=(
        "You are Chef Agent, a friendly and helpful AI assistant. "
        "Give clear answers and use tools when appropriate."
    ),
    checkpointer=checkpointer,
)


# ─────────── TERMINAL UI ───────────

def show_banner():
    console.clear()

    banner = Text(justify="center")
    banner.append("✦ CHEF AGENT ✦\n", style="bold bright_cyan")
    banner.append(
        "Your Intelligent AI Assistant\n\n",
        style="white",
    )
    banner.append("● ONLINE", style="bold green")
    banner.append("    |    ", style="dim")

    console.print(
        Panel(
            Align.center(banner),
            border_style="bright_blue",
            padding=(1, 4),
            title="[bold cyan]LANGCHAIN × GEMINI[/]",
            subtitle="[dim]Powered by LangGraph[/]",
        )
    )

    console.print(
        "\n[dim]Commands:[/] "
        "[cyan]/help[/]  "
        "[cyan]/clear[/]  "
        "[cyan]/reset[/]  "
        "[cyan]/exit[/]\n"
    )


def show_help():
    console.print(
        Panel(
            "[cyan]/help[/]  - Show commands\n"
            "[cyan]/clear[/] - Clear terminal screen\n"
            "[cyan]/reset[/] - Start a fresh conversation\n"
            "[cyan]/exit[/]  - Exit the application",
            title="Available Commands",
            border_style="yellow",
        )
    )


def stream_answer(user_input: str, config: dict):
    console.print(f"\n[bold green]{AGENT_NAME}[/]")
    has_text = False
    try:
        for chunk, metadata in agent.stream(
            {"messages": [{"role": "user", "content": user_input}]},
            config=config,
            stream_mode="messages",
        ):
            if metadata.get("langgraph_node") != "model":
                continue
            for block in chunk.content_blocks:
                if block.get("type") == "text" and block.get("text"):
                    print(block["text"], end="", flush=True)
                    has_text = True
        if not has_text:
            print("No text response returned.", end="")
    finally:
        print()


# ─────────── CHAT LOOP ───────────

def main():
    
    thread_id = str(uuid.uuid4())

    show_banner()

    while True:
        try:
            user_input = Prompt.ask(
                "\n[bold bright_blue]❯ YOU[/]"
            ).strip()

            if not user_input:
                continue

            command = user_input.lower()

            if command in ("/exit", "/quit"):
                console.print(
                    "\n[bold cyan]Goodbye! See you soon ✦[/]\n"
                )
                break

            if command == "/help":
                show_help()
                continue

            if command == "/clear":
                show_banner()
                continue

            if command == "/reset":
                thread_id = str(uuid.uuid4())
                console.print(
                    "[green]✓ New conversation started.[/]"
                )
                continue

            config = {
                "configurable": {
                    "thread_id": thread_id
                }
            }

            stream_answer(user_input, config)
            console.print(
                Rule(style="dim bright_black")
            )

        except (KeyboardInterrupt, EOFError):
            console.print(
                "\n[bold cyan]Session ended. Goodbye![/]"
            )
            break

        except Exception as error:
            console.print(
                Panel(
                    str(error),
                    title="[bold red]Agent Error[/]",
                    border_style="red",
                )
            )

if __name__ == "__main__":
    main()
