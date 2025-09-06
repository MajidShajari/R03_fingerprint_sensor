from rich.console import Console
from rich.prompt import Prompt

from src.config import ENCRYPTED_PATH
from src.features.encrypt import Encrypt
from src.features.enroll import Enroll

console = Console()


def main():
    while True:
        console.rule("[bold blue]Fingerprint Recognition System and Encryption Tool[/bold blue]")
        console.print("\ne: Enroll Finger\ni: Identify Finger \nq: Quit\n", style="bold green")
        command = Prompt.ask("Enter your command", choices=["e", "i", "q"])
        if command == "e":
            console.clear()
            try:
                enroll = Enroll()
                console.print("[bold yellow]Enroll Finger Option[/bold yellow]")
                console.print(
                    "r: Get Raw Fingerprint Data\ne: Enroll Fingerprint and Encrypt Data\n", style="bold green"
                )
                sub_command = Prompt.ask("Enter your command", choices=["r", "e"])
                if sub_command == "e":
                    enroll.get_raw()
                    console.print("[bold green]Fingerprint data captured successfully![/bold green]")
            except Exception as e:
                console.print(f"[bold red]Error:[/bold red] {e}")
        if command == "q":
            raise SystemExit


if __name__ == "__main__":
    main()
