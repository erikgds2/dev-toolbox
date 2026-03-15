# Ponto de entrada principal do dev-toolbox com menu interativo
import sys
import os

# Garante encoding UTF-8 no Windows para suporte a caracteres Unicode (Rich/emojis)
if sys.platform == "win32":
    os.environ.setdefault("PYTHONUTF8", "1")
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from pathlib import Path
from typing import Callable

import typer
from rich.align import Align
from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

# Importa ferramentas
from src.tools import (
    batch_renamer,
    duplicate_finder,
    format_converter,
    password_gen,
    system_monitor,
    url_checker,
)
from src.config import carregar_config

console = Console()
app = typer.Typer(
    name="dev-toolbox",
    help="Caixa de ferramentas para desenvolvedores e analistas — CLI com interface rica",
    add_completion=False,
)

# ─── Definição das ferramentas disponíveis ─────────────────────────────────

FERRAMENTAS: list[dict] = [
    {
        "numero": "1",
        "nome": "Monitor de Sistema",
        "icone": "🖥️",
        "descricao": "CPU, RAM e disco em tempo real",
        "cor": "cyan",
        "modulo": system_monitor,
        "funcao": system_monitor.executar,
    },
    {
        "numero": "2",
        "nome": "Gerador de Senhas",
        "icone": "🔐",
        "descricao": "Senhas seguras com score de força",
        "cor": "green",
        "modulo": password_gen,
        "funcao": password_gen.executar,
    },
    {
        "numero": "3",
        "nome": "Conversor de Formatos",
        "icone": "🔄",
        "descricao": "JSON ↔ CSV ↔ YAML ↔ XML",
        "cor": "yellow",
        "modulo": format_converter,
        "funcao": format_converter.executar,
    },
    {
        "numero": "4",
        "nome": "Verificador de URLs",
        "icone": "🌐",
        "descricao": "Status, tempo de resposta e disponibilidade",
        "cor": "blue",
        "modulo": url_checker,
        "funcao": url_checker.executar,
    },
    {
        "numero": "5",
        "nome": "Renomeador em Lote",
        "icone": "📝",
        "descricao": "Renomear com regex, prefixo e numeração",
        "cor": "magenta",
        "modulo": batch_renamer,
        "funcao": batch_renamer.executar,
    },
    {
        "numero": "6",
        "nome": "Buscador de Duplicatas",
        "icone": "🔍",
        "descricao": "Encontrar e remover duplicatas por MD5",
        "cor": "red",
        "modulo": duplicate_finder,
        "funcao": duplicate_finder.executar,
    },
]


def _exibir_banner() -> None:
    """Exibe o banner principal do dev-toolbox."""
    config = carregar_config()
    versao = config.get("version", "1.0.0")

    banner = Text()
    banner.append("  ██████╗ ███████╗██╗   ██╗\n", style="bold cyan")
    banner.append(" ██╔══██╗██╔════╝██║   ██║\n", style="bold cyan")
    banner.append(" ██║  ██║█████╗  ██║   ██║\n", style="bold blue")
    banner.append(" ██║  ██║██╔══╝  ╚██╗ ██╔╝\n", style="bold blue")
    banner.append(" ██████╔╝███████╗ ╚████╔╝ \n", style="bold cyan")
    banner.append(" ╚═════╝ ╚══════╝  ╚═══╝  \n", style="bold cyan")
    banner.append("  ████████╗ ██████╗  ██████╗ ██╗     ██████╗  ██████╗ ██╗  ██╗\n", style="bold blue")
    banner.append("     ██╔══╝██╔═══██╗██╔═══██╗██║     ██╔══██╗██╔═══██╗╚██╗██╔╝\n", style="bold blue")
    banner.append("     ██║   ██║   ██║██║   ██║██║     ██████╔╝██║   ██║ ╚███╔╝ \n", style="bold cyan")
    banner.append("     ██║   ██║   ██║██║   ██║██║     ██╔══██╗██║   ██║ ██╔██╗ \n", style="bold cyan")
    banner.append("     ██║   ╚██████╔╝╚██████╔╝███████╗██████╔╝╚██████╔╝██╔╝ ██╗\n", style="bold blue")
    banner.append("     ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝╚═════╝  ╚═════╝ ╚═╝  ╚═╝\n", style="bold blue")

    console.print(Panel(
        Align.center(banner),
        subtitle=f"[dim]v{versao} | Caixa de ferramentas para desenvolvedores[/dim]",
        border_style="cyan",
        padding=(1, 4),
    ))


def _exibir_menu() -> None:
    """Exibe o menu interativo principal."""
    tabela = Table(
        show_header=True,
        header_style="bold cyan",
        border_style="blue",
        show_lines=True,
        title="[bold cyan]Ferramentas Disponíveis[/bold cyan]",
        min_width=60,
    )

    tabela.add_column("#", style="bold white", width=4, justify="center")
    tabela.add_column("Ferramenta", style="bold", min_width=22)
    tabela.add_column("Descrição", style="dim", min_width=35)

    for ferramenta in FERRAMENTAS:
        tabela.add_row(
            f"[bold {ferramenta['cor']}]{ferramenta['numero']}[/bold {ferramenta['cor']}]",
            f"{ferramenta['icone']} [{ferramenta['cor']}]{ferramenta['nome']}[/{ferramenta['cor']}]",
            ferramenta["descricao"],
        )

    # Linha separadora antes do item sair
    tabela.add_section()
    tabela.add_row(
        "[dim]0[/dim]",
        "[dim]🚪 Sair[/dim]",
        "[dim]Encerrar o dev-toolbox[/dim]",
    )

    console.print(tabela)


def _executar_ferramenta(numero: str) -> bool:
    """
    Executa a ferramenta selecionada pelo número.

    Returns:
        False se o usuário escolheu sair, True caso contrário
    """
    if numero == "0":
        console.print("\n[bold cyan]Até logo! 👋[/bold cyan]\n")
        return False

    ferramenta = next((f for f in FERRAMENTAS if f["numero"] == numero), None)

    if not ferramenta:
        console.print(f"[red]Opção inválida: '{numero}'. Escolha entre 0 e {len(FERRAMENTAS)}.[/red]")
        return True

    console.print(f"\n[bold {ferramenta['cor']}]{ferramenta['icone']} Iniciando: {ferramenta['nome']}[/bold {ferramenta['cor']}]\n")

    try:
        ferramenta["funcao"]()
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️  Operação interrompida.[/yellow]")
    except Exception as e:
        console.print(f"\n[red]❌ Erro ao executar {ferramenta['nome']}: {e}[/red]")

    return True


@app.command(name="menu")
def menu_interativo() -> None:
    """Abre o menu interativo principal do dev-toolbox."""
    _exibir_banner()

    continuar = True
    while continuar:
        _exibir_menu()
        console.print()
        escolha = console.input("[bold white]Escolha uma ferramenta (0-6): [/bold white]").strip()
        console.print()
        continuar = _executar_ferramenta(escolha)
        if continuar:
            console.print("\n" + "─" * 60 + "\n")


@app.command(name="monitor")
def cmd_monitor(
    duracao: int = typer.Option(None, "--duracao", "-d", help="Duração em segundos"),
    relatorio: bool = typer.Option(False, "--relatorio", "-r", help="Gerar relatório HTML"),
) -> None:
    """Monitor de sistema em tempo real."""
    system_monitor.monitorar(duracao=duracao, intervalo=1.0, relatorio=relatorio)


@app.command(name="senha")
def cmd_senha(
    comprimento: int = typer.Option(16, "--comprimento", "-c"),
    quantidade: int = typer.Option(1, "--quantidade", "-q"),
    sem_simbolos: bool = typer.Option(False, "--sem-simbolos"),
    relatorio: bool = typer.Option(False, "--relatorio", "-r"),
) -> None:
    """Gera senhas seguras com score de força."""
    from src.tools.password_gen import gerar, gerar_senha, exibir_resultado, _gerar_relatorio
    resultados = []
    for i in range(quantidade):
        r = gerar_senha(comprimento=comprimento, simbolos=not sem_simbolos)
        exibir_resultado(r, i + 1)
        resultados.append(r)
    if relatorio:
        _gerar_relatorio(resultados)


@app.command(name="converter")
def cmd_converter(
    entrada: Path = typer.Argument(..., help="Arquivo de entrada"),
    para: str = typer.Option(..., "--para", "-p", help="Formato destino"),
    relatorio: bool = typer.Option(False, "--relatorio", "-r"),
) -> None:
    """Converte arquivos entre JSON, CSV, YAML e XML."""
    format_converter.converter(entrada=entrada, para=para, saida=None, preview=True, relatorio=relatorio)


@app.command(name="urls")
def cmd_urls(
    urls_arg: str = typer.Option(None, "--urls", "-u", help="URLs separadas por vírgula"),
    arquivo: Path = typer.Option(None, "--arquivo", "-f"),
    relatorio: bool = typer.Option(False, "--relatorio", "-r"),
) -> None:
    """Verifica URLs quanto a status e tempo de resposta."""
    url_checker.checar(urls_arg=urls_arg, arquivo=arquivo, timeout=10, threads=10, relatorio=relatorio)


@app.command(name="renomear")
def cmd_renomear(
    diretorio: Path = typer.Argument(...),
    prefixo: str = typer.Option("", "--prefixo", "-p"),
    sufixo: str = typer.Option("", "--sufixo", "-s"),
    numeracao: bool = typer.Option(False, "--numeracao", "-n"),
    dry_run: bool = typer.Option(True, "--dry-run/--aplicar"),
    relatorio: bool = typer.Option(False, "--relatorio", "-r"),
) -> None:
    """Renomeia arquivos em lote."""
    batch_renamer.renomear(
        diretorio=diretorio,
        prefixo=prefixo,
        sufixo=sufixo,
        substituir=None,
        regex=None,
        numeracao=numeracao,
        inicio=1,
        digitos=3,
        extensao="",
        filtro="",
        maiusculas=False,
        minusculas=False,
        recursivo=False,
        dry_run=dry_run,
        relatorio=relatorio,
    )


@app.command(name="duplicatas")
def cmd_duplicatas(
    diretorio: Path = typer.Argument(...),
    recursivo: bool = typer.Option(True, "--recursivo/--sem-recursivo"),
    deletar: bool = typer.Option(False, "--deletar", "-d"),
    relatorio: bool = typer.Option(False, "--relatorio", "-r"),
) -> None:
    """Busca e opcionalmente remove arquivos duplicados."""
    duplicate_finder.buscar(
        diretorio=diretorio,
        recursivo=recursivo,
        tamanho_minimo=0,
        ignorar="",
        deletar=deletar,
        relatorio=relatorio,
    )


@app.command(name="versao")
def cmd_versao() -> None:
    """Exibe a versão instalada do dev-toolbox."""
    config = carregar_config()
    versao = config.get("version", "desconhecida")
    console.print(f"[bold cyan]dev-toolbox[/bold cyan] v[bold]{versao}[/bold]")


def main() -> None:
    """Ponto de entrada principal."""
    # Se chamado sem argumentos, abre o menu interativo
    if len(sys.argv) == 1:
        menu_interativo()
    else:
        app()


if __name__ == "__main__":
    main()
