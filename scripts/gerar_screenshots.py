"""
Gera screenshots SVG do dev-toolbox para o README.
Execute: python scripts/gerar_screenshots.py
"""
import math
import sys
from pathlib import Path

from rich.align import Align
from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

SCREENSHOTS_DIR = Path("docs/screenshots")
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

# Redireciona output pra nulo durante gravacao (evita erro de encoding no Windows)
import io as _io
_null = open(_io.StringIO.__module__ and "nul" if __import__("sys").platform == "win32" else "/dev/null", "w", encoding="utf-8", errors="replace")


def nova_console(width: int = 80) -> Console:
    """Cria console que grava sem imprimir no stdout (compativel com Windows)."""
    return Console(record=True, width=width, file=_null, force_terminal=True)


def salvar(console: Console, nome: str) -> None:
    caminho = SCREENSHOTS_DIR / f"{nome}.svg"
    console.save_svg(str(caminho), title=f"dev-toolbox — {nome}")
    print(f"  OK: {caminho}")


# ─── 1. Menu principal ────────────────────────────────────────────────────────

def screenshot_menu() -> None:
    console = nova_console(80)

    banner = Text()
    banner.append("  ██████╗ ███████╗██╗   ██╗\n", style="bold cyan")
    banner.append(" ██╔══██╗██╔════╝██║   ██║\n", style="bold cyan")
    banner.append(" ██║  ██║█████╗  ██║   ██║\n", style="bold blue")
    banner.append(" ██║  ██║██╔══╝  ╚██╗ ██╔╝\n", style="bold blue")
    banner.append(" ██████╔╝███████╗ ╚████╔╝ \n", style="bold cyan")
    banner.append(" ╚═════╝ ╚══════╝  ╚═══╝  \n", style="bold cyan")
    banner.append("  TOOLBOX — Caixa de ferramentas CLI\n", style="bold blue")

    console.print(Panel(Align.center(banner), subtitle="[dim]v1.0.0[/dim]", border_style="cyan", padding=(1, 4)))

    tabela = Table(
        show_header=True, header_style="bold cyan",
        border_style="blue", show_lines=True,
        title="[bold cyan]Ferramentas Disponíveis[/bold cyan]", min_width=60,
    )
    tabela.add_column("#", style="bold white", width=4, justify="center")
    tabela.add_column("Ferramenta", style="bold", min_width=22)
    tabela.add_column("Descrição", style="dim", min_width=35)

    ferramentas = [
        ("1", "cyan",    "🖥️",  "Monitor de Sistema",    "CPU, RAM e disco em tempo real"),
        ("2", "green",   "🔐", "Gerador de Senhas",     "Senhas seguras com score de força"),
        ("3", "yellow",  "🔄", "Conversor de Formatos", "JSON ↔ CSV ↔ YAML ↔ XML"),
        ("4", "blue",    "🌐", "Verificador de URLs",   "Status, tempo de resposta e disponibilidade"),
        ("5", "magenta", "📝", "Renomeador em Lote",    "Renomear com regex, prefixo e numeração"),
        ("6", "red",     "🔍", "Buscador de Duplicatas","Encontrar e remover duplicatas por MD5"),
    ]

    for num, cor, icone, nome, desc in ferramentas:
        tabela.add_row(
            f"[bold {cor}]{num}[/bold {cor}]",
            f"{icone} [{cor}]{nome}[/{cor}]",
            desc,
        )

    tabela.add_section()
    tabela.add_row("[dim]0[/dim]", "[dim]🚪 Sair[/dim]", "[dim]Encerrar o dev-toolbox[/dim]")
    console.print(tabela)
    console.print()
    console.print("[bold white]Escolha uma ferramenta (0-6): [/bold white][bold cyan]_[/bold cyan]")

    salvar(console, "menu_principal")


# ─── 2. Gerador de senhas ─────────────────────────────────────────────────────

def screenshot_senha() -> None:
    console = nova_console(72)

    console.print(Panel("[bold cyan]🔐 Gerador de Senhas Seguras[/bold cyan]", border_style="cyan"))

    senhas = [
        ("T@k9#mXvQ2$Lp7Wz", 92, "Muito Forte", "bright_green", 103.4),
        ("hN3!vR8@qP5#mK1$", 88, "Muito Forte", "bright_green",  98.7),
        ("Xw7!nQ2@mP9#kL4$", 85, "Muito Forte", "bright_green",  96.2),
    ]

    for i, (senha, score, nivel, cor, entropia) in enumerate(senhas, 1):
        largura_barra = 40
        preenchido = int((score / 100) * largura_barra)
        barra = "█" * preenchido + "░" * (largura_barra - preenchido)

        texto = Text()
        texto.append(f"  Senha {i}: ", style="bold white")
        texto.append(senha, style=f"bold {cor}")
        texto.append(f"\n  Força: ", style="white")
        texto.append(f"[{barra}]", style=f"bold {cor}")
        texto.append(f" {score}/100 — {nivel}", style=cor)
        texto.append(f"\n  Entropia: {entropia:.1f} bits", style="dim")
        texto.append(f"  |  Comprimento: {len(senha)} chars", style="dim")
        console.print(Panel(texto, border_style=cor))

    salvar(console, "gerador_senhas")


# ─── 3. Verificador de URLs ───────────────────────────────────────────────────

def screenshot_urls() -> None:
    console = nova_console(80)

    console.print(Panel("[bold blue]🌐 Verificador de URLs[/bold blue]", border_style="blue"))

    tabela = Table(
        show_header=True, header_style="bold blue",
        border_style="blue", show_lines=True,
        title="[bold]Resultados da Verificação[/bold]",
    )
    tabela.add_column("URL", style="white", min_width=32)
    tabela.add_column("Status", justify="center", width=8)
    tabela.add_column("Tempo", justify="right", width=10)
    tabela.add_column("Situação", justify="center", width=14)

    dados = [
        ("https://www.google.com",  "200", "142 ms",  "online",  "green",   "✅ Online"),
        ("https://www.github.com",  "200", "198 ms",  "online",  "green",   "✅ Online"),
        ("https://www.python.org",  "200", "231 ms",  "online",  "green",   "✅ Online"),
        ("https://httpbin.org/status/404", "404", "89 ms",  "aviso", "yellow",  "⚠️  Erro 404"),
        ("https://site-inexistente.xyz",   "—",  "—",      "offline","red",     "❌ Offline"),
        ("https://httpbin.org/delay/2",    "200", "2041 ms","lenta", "yellow",  "🐢 Lenta"),
    ]

    for url, status, tempo, _, cor, situacao in dados:
        tabela.add_row(url, f"[{cor}]{status}[/{cor}]", f"[dim]{tempo}[/dim]", f"[{cor}]{situacao}[/{cor}]")

    console.print(tabela)
    console.print()
    console.print("[bold]Resumo:[/bold] 6 URLs verificadas  |  [green]3 online[/green]  |  [yellow]2 avisos[/yellow]  |  [red]1 offline[/red]")

    salvar(console, "url_checker")


# ─── 4. Monitor de sistema ────────────────────────────────────────────────────

def screenshot_monitor() -> None:
    console = nova_console(72)

    def barra(valor: float, largura: int = 20) -> Text:
        cor = "green" if valor < 60 else ("yellow" if valor < 85 else "bold red")
        preenchido = int((valor / 100) * largura)
        b = "█" * preenchido + "░" * (largura - preenchido)
        t = Text()
        t.append(f"[{b}]", style=f"bold {cor}")
        t.append(f" {valor:5.1f}%", style=cor)
        return t

    # CPU
    cpu_text = Text()
    cpu_text.append("CPU Global      ", style="bold white")
    cpu_text.append_text(barra(43.2))
    cpu_text.append("\n")
    for i, uso in enumerate([38.1, 51.4, 42.7, 40.0]):
        cpu_text.append(f"  Núcleo {i+1}      ", style="dim")
        cpu_text.append_text(barra(uso, 16))
        cpu_text.append("\n")

    cpu_panel = Panel(cpu_text, title="[bold cyan]🖥️ CPU[/bold cyan]", border_style="cyan")

    # RAM
    ram_text = Text()
    ram_text.append("Usada    ", style="bold white")
    ram_text.append_text(barra(67.3))
    ram_text.append("\n")
    ram_text.append("11.2 GB / 16.0 GB disponíveis", style="dim")
    ram_panel = Panel(ram_text, title="[bold green]🧠 RAM[/bold green]", border_style="green")

    # Disco
    disco_text = Text()
    disco_text.append("C:\\       ", style="bold white")
    disco_text.append_text(barra(54.8))
    disco_text.append("\n")
    disco_text.append("230 GB / 512 GB livres", style="dim")
    disco_panel = Panel(disco_text, title="[bold yellow]💾 Disco[/bold yellow]", border_style="yellow")

    console.print(Panel("[bold cyan]🖥️ Monitor de Sistema[/bold cyan] [dim]— atualiza a cada 1s[/dim]", border_style="cyan"))
    console.print(Columns([cpu_panel, ram_panel]))
    console.print(disco_panel)

    salvar(console, "monitor_sistema")


# ─── 5. Makefile help ─────────────────────────────────────────────────────────

def screenshot_makefile() -> None:
    console = nova_console(72)

    console.print()
    banner_lines = [
        ("  ██████╗ ███████╗██╗   ██╗    ████████╗ ██████╗  ██████╗ ██╗     ██████╗  ██████╗ ██╗  ██╗", "bold cyan"),
        ("  ██╔══██╗██╔════╝██║   ██║       ██╔══╝██╔═══██╗██╔═══██╗██║     ██╔══██╗██╔═══██╗╚██╗██╔╝", "bold cyan"),
        ("  ██║  ██║█████╗  ██║   ██║       ██║   ██║   ██║██║   ██║██║     ██████╔╝██║   ██║ ╚███╔╝ ", "bold blue"),
        ("  ╚═════╝ ╚══════╝  ╚═══╝         ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝╚═════╝  ╚═════╝ ╚═╝  ╚═╝", "bold blue"),
    ]
    for line, style in banner_lines:
        console.print(line, style=style)

    console.print()
    console.print("  Caixa de ferramentas para desenvolvedores — v1.0.0", style="dim")
    console.print()
    console.print("  Comandos disponíveis:", style="bold white")
    console.print()

    comandos = [
        ("install",    "Instala todas as dependências do projeto"),
        ("menu",       "Abre o menu interativo com todas as ferramentas"),
        ("monitor",    "Monitor de CPU, RAM e disco em tempo real"),
        ("senha",      "Gera senhas seguras com score de força"),
        ("urls",       "Verifica se URLs estão online (status, tempo de resposta)"),
        ("converter",  "Converte arquivos entre JSON, CSV, YAML e XML"),
        ("renomear",   "Renomeia arquivos em lote com regex, prefixo e numeração"),
        ("duplicatas", "Encontra (e opcionalmente remove) arquivos duplicados"),
        ("clean",      "Remove relatórios gerados (pasta output/)"),
        ("demo",       "Gera screenshots de demonstração do CLI"),
    ]

    for cmd, desc in comandos:
        console.print(f"    [cyan]{cmd:<18}[/cyan] {desc}")

    console.print()

    salvar(console, "make_help")


# ─── main ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # força UTF-8 no stdout do Windows (evita UnicodeEncodeError com emojis)
    import io as _io2, sys as _sys
    if hasattr(_sys.stdout, "buffer"):
        _sys.stdout = _io2.TextIOWrapper(_sys.stdout.buffer, encoding="utf-8", errors="replace")
    print("\n  Gerando screenshots do dev-toolbox...\n")
    screenshot_menu()
    screenshot_senha()
    screenshot_urls()
    screenshot_monitor()
    screenshot_makefile()
    print(f"\n  Todas as screenshots salvas em {SCREENSHOTS_DIR}/\n")
