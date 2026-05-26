from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    print("Install python-dotenv")
    print("pip install python-dotenv")
    sys.exit(1)

try:
    from google import genai
except ImportError:
    print("Install google-genai")
    print("pip install google-genai")
    sys.exit(1)

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.markdown import Markdown
    from rich.syntax import Syntax
except ImportError:
    print("Install rich")
    print("pip install rich")
    sys.exit(1)

try:
    from prompt_toolkit import prompt
    from prompt_toolkit.history import InMemoryHistory
except ImportError:
    print("Install prompt_toolkit")
    print("pip install prompt_toolkit")
    sys.exit(1)


# =========================================================
# LOAD ENV
# =========================================================

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    print("GEMINI_API_KEY missing in .env")
    sys.exit(1)

MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")


# =========================================================
# RICH CONSOLE
# =========================================================

console = Console()


# =========================================================
# CHAT STORAGE
# =========================================================

CHAT_DIR = Path("chat_sessions")
CHAT_DIR.mkdir(exist_ok=True)

CURRENT_SESSION = (
    CHAT_DIR /
    f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
)

history = []


# =========================================================
# SYSTEM PROMPTS
# =========================================================

MODES = {
    "default": """
You are a helpful AI assistant.
Give clear and concise responses.
""",

    "coder": """
You are an expert software engineer.
Provide optimized code with explanations.
""",

    "teacher": """
You are an expert teacher.
Explain concepts step by step.
""",

    "research": """
You are a research assistant.
Provide detailed technical explanations.
"""
}

current_mode = "default"


# =========================================================
# GEMINI CLIENT
# =========================================================

client = genai.Client(api_key=API_KEY)

chat = client.chats.create(
    model=MODEL_NAME
)


# =========================================================
# SAVE HISTORY
# =========================================================

def save_chat():
    with open(CURRENT_SESSION, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)


# =========================================================
# LOAD SESSION
# =========================================================

def load_session(path):
    global history

    with open(path, "r", encoding="utf-8") as f:
        history = json.load(f)

    console.print(
        f"[green]Loaded session:[/green] {path}"
    )


# =========================================================
# CLEAR SCREEN
# =========================================================

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


# =========================================================
# HELP MENU
# =========================================================

def show_help():
    help_text = """
[bold cyan]Available Commands[/bold cyan]

/help               Show commands
/clear              Clear terminal
/history            Show chat history
/save               Save current session
/sessions           Show saved sessions
/load               Load session
/mode               Change assistant mode
/tokens             Show token estimate
/exit               Exit chatbot

[bold yellow]Modes[/bold yellow]

default
coder
teacher
research
"""

    console.print(Panel(help_text))


# =========================================================
# SHOW HISTORY
# =========================================================

def show_history():
    if not history:
        console.print("[yellow]No history available.[/yellow]")
        return

    for item in history:
        role = item["role"]
        content = item["content"]

        color = "cyan" if role == "user" else "green"

        console.print(
            f"[bold {color}]{role.upper()}:[/bold {color}]"
        )

        console.print(Markdown(content))
        console.print()


# =========================================================
# TOKEN ESTIMATE
# =========================================================

def estimate_tokens():
    total_chars = sum(
        len(item["content"])
        for item in history
    )

    estimated_tokens = total_chars // 4

    console.print(
        Panel(
            f"Estimated Tokens: {estimated_tokens}",
            title="Token Usage"
        )
    )



def list_sessions():
    files = list(CHAT_DIR.glob("*.json"))

    if not files:
        console.print("[yellow]No sessions found.[/yellow]")
        return

    console.print(
        Panel(
            "\n".join(str(f) for f in files),
            title="Saved Sessions"
        )
    )


# =========================================================
# CHANGE MODE
# =========================================================

def change_mode():
    global current_mode

    console.print("\nAvailable modes:")

    for mode in MODES:
        console.print(f"- {mode}")

    selected = input("\nEnter mode: ").strip()

    if selected in MODES:
        current_mode = selected

        console.print(
            f"[green]Mode changed to:[/green] {selected}"
        )
    else:
        console.print("[red]Invalid mode[/red]")


# =========================================================
# STREAM RESPONSE
# =========================================================

def stream_response(user_text):
    global history

    full_prompt = MODES[current_mode] + "\n\n"

    for item in history[-10:]:
        full_prompt += (
            f"{item['role']}: "
            f"{item['content']}\n"
        )

    full_prompt += f"user: {user_text}"

    retries = 3

    for attempt in range(retries):
        try:
            start_time = time.time()

            response_stream = chat.send_message_stream(
                full_prompt
            )

            console.print(
                "\n[bold green]Gemini:[/bold green] ",
                end=""
            )

            final_text = ""

            for chunk in response_stream:

                chunk_text = getattr(
                    chunk,
                    "text",
                    ""
                )

                final_text += chunk_text

                print(
                    chunk_text,
                    end="",
                    flush=True
                )

            elapsed = round(
                time.time() - start_time,
                2
            )

            print()

            console.print(
                f"\n[dim]Response time: {elapsed}s[/dim]"
            )

            history.append({
                "role": "user",
                "content": user_text,
                "time": str(datetime.now())
            })

            history.append({
                "role": "assistant",
                "content": final_text,
                "time": str(datetime.now())
            })

            save_chat()

            return

        except Exception as exc:

            console.print(
                f"\n[red]Error:[/red] {exc}"
            )

            if attempt < retries - 1:
                console.print(
                    "[yellow]Retrying in 5 seconds...[/yellow]"
                )

                time.sleep(5)

            else:
                console.print(
                    "[bold red]Failed after retries.[/bold red]"
                )


# =========================================================
# MAIN
# =========================================================

def main():

    clear_screen()

    console.print(
        Panel.fit(
            f"""
[bold green]Terminal Gemini Chatbot[/bold green]

Model : {MODEL_NAME}
Mode  : {current_mode}

Type /help for commands.
""",
            border_style="green"
        )
    )

    session_history = InMemoryHistory()

    while True:

        try:
            user_text = prompt(
                "\nYou: ",
                history=session_history,
                multiline=False
            ).strip()

        except (KeyboardInterrupt, EOFError):
            console.print(
                "\n[bold red]Exiting chatbot...[/bold red]"
            )
            break

        if not user_text:
            continue

        # =================================================
        # COMMANDS
        # =================================================

        if user_text == "/help":
            show_help()
            continue

        elif user_text == "/clear":
            clear_screen()
            continue

        elif user_text == "/history":
            show_history()
            continue

        elif user_text == "/save":
            save_chat()

            console.print(
                "[green]Session saved.[/green]"
            )
            continue

        elif user_text == "/sessions":
            list_sessions()
            continue

        elif user_text == "/load":

            list_sessions()

            path = input(
                "\nEnter session path: "
            ).strip()

            if os.path.exists(path):
                load_session(path)
            else:
                console.print(
                    "[red]File not found[/red]"
                )

            continue

        elif user_text == "/mode":
            change_mode()
            continue

        elif user_text == "/tokens":
            estimate_tokens()
            continue

        elif user_text in {"/exit", "exit", "quit"}:
            console.print(
                "[bold red]Goodbye![/bold red]"
            )
            break

        # =================================================
        # CHAT RESPONSE
        # =================================================

        stream_response(user_text)


# =========================================================
# START
# =========================================================

if __name__ == "__main__":
    main()