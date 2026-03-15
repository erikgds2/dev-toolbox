# Monitor de sistema em tempo real — CPU, RAM e disco
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

import psutil
import typer
from rich.columns import Columns
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.progress import BarColumn, Progress, TextColumn
from rich.table import Table
from rich.text import Text

from src.report import salvar_relatorio

console = Console()
app = typer.Typer(help="Monitor de sistema em tempo real")


def _cor_percentual(valor: float) -> str:
    """Retorna a cor baseada no percentual de uso."""
    if valor < 60:
        return "green"
    elif valor < 85:
        return "yellow"
    return "red"


def _barra_percentual(valor: float, largura: int = 20) -> Text:
    """Cria uma barra de progresso colorida para o terminal."""
    cor = _cor_percentual(valor)
    preenchido = int((valor / 100) * largura)
    barra = "█" * preenchido + "░" * (largura - preenchido)
    texto = Text()
    texto.append(f"[{barra}]", style=f"bold {cor}")
    texto.append(f" {valor:5.1f}%", style=cor)
    return texto


def _formatar_bytes(num_bytes: int) -> str:
    """Converte bytes em formato legível (KB, MB, GB)."""
    for unidade in ["B", "KB", "MB", "GB", "TB"]:
        if num_bytes < 1024.0:
            return f"{num_bytes:.1f} {unidade}"
        num_bytes /= 1024.0
    return f"{num_bytes:.1f} PB"


def _construir_tabela() -> Table:
    """Constrói a tabela de monitoramento em tempo real."""
    agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    # CPU
    cpu_percent = psutil.cpu_percent(interval=None)
    cpu_count = psutil.cpu_count()
    cpu_freq = psutil.cpu_freq()
    freq_str = f"{cpu_freq.current:.0f} MHz" if cpu_freq else "N/A"

    # RAM
    ram = psutil.virtual_memory()
    ram_percent = ram.percent
    ram_usado = _formatar_bytes(ram.used)
    ram_total = _formatar_bytes(ram.total)

    # Swap
    swap = psutil.swap_memory()
    swap_percent = swap.percent
    swap_usado = _formatar_bytes(swap.used)
    swap_total = _formatar_bytes(swap.total)

    # Disco
    disco = psutil.disk_usage("/")
    disco_percent = disco.percent
    disco_usado = _formatar_bytes(disco.used)
    disco_total = _formatar_bytes(disco.total)

    # Tabela principal
    tabela = Table(
        title=f"[bold cyan]🖥️  Monitor de Sistema  |  {agora}[/bold cyan]",
        border_style="blue",
        header_style="bold magenta",
        show_lines=True,
        min_width=70,
    )

    tabela.add_column("Componente", style="bold", min_width=12)
    tabela.add_column("Uso", min_width=30)
    tabela.add_column("Detalhe", min_width=20)
    tabela.add_column("Info Extra", min_width=15)

    # Linha CPU
    tabela.add_row(
        "💻 CPU",
        _barra_percentual(cpu_percent),
        f"[cyan]{cpu_count} núcleos[/cyan]",
        f"[dim]{freq_str}[/dim]",
    )

    # Linhas de cada núcleo (primeiros 4)
    try:
        percents_por_core = psutil.cpu_percent(percpu=True)
        for i, pct in enumerate(percents_por_core[:4]):
            tabela.add_row(
                f"  Core {i}",
                _barra_percentual(pct, largura=15),
                "",
                "",
            )
        if len(percents_por_core) > 4:
            tabela.add_row(f"  +{len(percents_por_core) - 4} cores...", "", "", "")
    except Exception:
        pass

    # Linha RAM
    tabela.add_row(
        "🧠 RAM",
        _barra_percentual(ram_percent),
        f"[cyan]{ram_usado} / {ram_total}[/cyan]",
        f"[dim]Livre: {_formatar_bytes(ram.available)}[/dim]",
    )

    # Linha Swap
    tabela.add_row(
        "💾 Swap",
        _barra_percentual(swap_percent),
        f"[cyan]{swap_usado} / {swap_total}[/cyan]",
        "",
    )

    # Linha Disco
    tabela.add_row(
        "📀 Disco (/)",
        _barra_percentual(disco_percent),
        f"[cyan]{disco_usado} / {disco_total}[/cyan]",
        f"[dim]Livre: {_formatar_bytes(disco.free)}[/dim]",
    )

    # Processos top
    try:
        processos = sorted(
            psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]),
            key=lambda p: p.info.get("cpu_percent") or 0,
            reverse=True,
        )[:3]

        for proc in processos:
            nome = (proc.info["name"] or "N/A")[:20]
            cpu_p = proc.info.get("cpu_percent") or 0.0
            mem_p = proc.info.get("memory_percent") or 0.0
            tabela.add_row(
                f"  PID {proc.info['pid']}",
                Text(f"{nome}", style="dim"),
                f"[yellow]CPU: {cpu_p:.1f}%[/yellow]",
                f"[blue]RAM: {mem_p:.1f}%[/blue]",
            )
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        pass

    return tabela


def monitorar(
    duracao: Optional[int] = typer.Option(None, "--duracao", "-d", help="Duração em segundos (padrão: ilimitado)"),
    intervalo: float = typer.Option(1.0, "--intervalo", "-i", help="Intervalo de atualização em segundos"),
    relatorio: bool = typer.Option(False, "--relatorio", "-r", help="Gerar relatório HTML ao finalizar"),
) -> None:
    """Monitora CPU, RAM e disco em tempo real com atualização automática."""
    console.print(Panel(
        "[bold cyan]Monitor de Sistema Iniciado[/bold cyan]\n"
        "[dim]Pressione Ctrl+C para parar[/dim]",
        border_style="cyan",
    ))

    historico_cpu: list[float] = []
    historico_ram: list[float] = []
    inicio = time.time()

    # Inicializa coleta de CPU (primeira leitura é sempre 0)
    psutil.cpu_percent(interval=None)

    try:
        with Live(console=console, refresh_per_second=1, screen=False) as live:
            while True:
                if duracao and (time.time() - inicio) >= duracao:
                    break

                tabela = _construir_tabela()
                live.update(tabela)

                # Registra histórico
                historico_cpu.append(psutil.cpu_percent(interval=None))
                historico_ram.append(psutil.virtual_memory().percent)

                time.sleep(intervalo)

    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️  Monitoramento interrompido pelo usuário.[/yellow]")

    tempo_total = time.time() - inicio
    console.print(f"[dim]Tempo monitorado: {tempo_total:.0f} segundos[/dim]")

    if relatorio and historico_cpu:
        _gerar_relatorio(historico_cpu, historico_ram, tempo_total)


def _gerar_relatorio(
    historico_cpu: list[float],
    historico_ram: list[float],
    tempo_total: float,
) -> None:
    """Gera relatório HTML com o resumo do monitoramento."""
    media_cpu = sum(historico_cpu) / len(historico_cpu)
    max_cpu = max(historico_cpu)
    media_ram = sum(historico_ram) / len(historico_ram)
    max_ram = max(historico_ram)

    disco = psutil.disk_usage("/")
    ram = psutil.virtual_memory()

    estatisticas = {
        "CPU Média": f"{media_cpu:.1f}%",
        "CPU Máxima": f"{max_cpu:.1f}%",
        "RAM Média": f"{media_ram:.1f}%",
        "RAM Máxima": f"{max_ram:.1f}%",
        "Tempo Monitorado": f"{tempo_total:.0f}s",
        "Amostras": str(len(historico_cpu)),
    }

    linhas_cpu = [
        [f"Amostra {i+1}", f"{v:.1f}%"] for i, v in enumerate(historico_cpu[-20:])
    ]

    secoes = [
        {
            "tipo": "tabela",
            "titulo": "Histórico de CPU (últimas 20 amostras)",
            "colunas": ["Amostra", "Uso CPU"],
            "linhas": linhas_cpu,
        },
        {
            "tipo": "tabela",
            "titulo": "Estado do Sistema ao Finalizar",
            "colunas": ["Componente", "Uso", "Total"],
            "linhas": [
                ["RAM", f"{ram.percent:.1f}%", _formatar_bytes(ram.total)],
                ["Disco (/)", f"{disco.percent:.1f}%", _formatar_bytes(disco.total)],
            ],
        },
    ]

    caminho = salvar_relatorio(
        "monitor_sistema",
        "Monitor de Sistema",
        "Relatório de monitoramento de CPU, RAM e Disco",
        secoes,
        estatisticas,
    )
    console.print(f"\n[green]✅ Relatório salvo em: {caminho}[/green]")


def executar() -> None:
    """Ponto de entrada interativo para o monitor de sistema."""
    console.print(Panel(
        "[bold cyan]Monitor de Sistema[/bold cyan]\n"
        "[dim]Monitoramento em tempo real de CPU, RAM e Disco[/dim]",
        border_style="cyan",
    ))

    duracao_str = console.input("[bold]Duração em segundos (Enter para ilimitado): [/bold]").strip()
    duracao = int(duracao_str) if duracao_str.isdigit() else None

    gerar_rel = console.input("[bold]Gerar relatório HTML ao finalizar? (s/N): [/bold]").strip().lower() == "s"

    monitorar(duracao=duracao, relatorio=gerar_rel)


if __name__ == "__main__":
    app()
