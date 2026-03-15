# Verificador de URLs — status, tempo de resposta e disponibilidade
import concurrent.futures
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

import requests
import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TaskProgressColumn, TextColumn, TimeElapsedColumn
from rich.table import Table

from src.config import carregar_config
from src.report import salvar_relatorio

console = Console()
app = typer.Typer(help="Verificador de URLs e status de serviços")

# Limites de tempo de resposta (em ms)
LIMITE_RAPIDO = 500
LIMITE_ACEITAVEL = 1500


@dataclass
class ResultadoURL:
    """Resultado da verificação de uma URL."""
    url: str
    online: bool
    status_code: Optional[int]
    tempo_ms: Optional[float]
    redirect_url: Optional[str]
    erro: Optional[str]
    categoria: str  # "rapida", "aceitavel", "lenta", "offline"


def _normalizar_url(url: str) -> str:
    """Adiciona https:// se não houver protocolo."""
    url = url.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    return url


def _classificar_resposta(tempo_ms: Optional[float], online: bool) -> str:
    """Classifica a velocidade de resposta."""
    if not online:
        return "offline"
    if tempo_ms is None:
        return "offline"
    if tempo_ms <= LIMITE_RAPIDO:
        return "rapida"
    elif tempo_ms <= LIMITE_ACEITAVEL:
        return "aceitavel"
    return "lenta"


def verificar_url(url: str, timeout: int = 10) -> ResultadoURL:
    """
    Verifica uma URL individual.

    Args:
        url: A URL a verificar
        timeout: Tempo limite em segundos

    Returns:
        ResultadoURL com todos os dados da verificação
    """
    url_normalizada = _normalizar_url(url)

    try:
        inicio = time.perf_counter()
        resposta = requests.get(
            url_normalizada,
            timeout=timeout,
            allow_redirects=True,
            headers={"User-Agent": "dev-toolbox/1.0 URL-Checker"},
        )
        fim = time.perf_counter()
        tempo_ms = (fim - inicio) * 1000

        # Detecta redirecionamento
        redirect = None
        if resposta.url != url_normalizada:
            redirect = resposta.url

        categoria = _classificar_resposta(tempo_ms, True)

        return ResultadoURL(
            url=url_normalizada,
            online=True,
            status_code=resposta.status_code,
            tempo_ms=tempo_ms,
            redirect_url=redirect,
            erro=None,
            categoria=categoria,
        )

    except requests.exceptions.ConnectionError:
        return ResultadoURL(
            url=url_normalizada,
            online=False,
            status_code=None,
            tempo_ms=None,
            redirect_url=None,
            erro="Conexão recusada ou host não encontrado",
            categoria="offline",
        )
    except requests.exceptions.Timeout:
        return ResultadoURL(
            url=url_normalizada,
            online=False,
            status_code=None,
            tempo_ms=None,
            redirect_url=None,
            erro=f"Timeout após {timeout}s",
            categoria="offline",
        )
    except requests.exceptions.SSLError as e:
        return ResultadoURL(
            url=url_normalizada,
            online=False,
            status_code=None,
            tempo_ms=None,
            redirect_url=None,
            erro=f"Erro SSL: {str(e)[:60]}",
            categoria="offline",
        )
    except Exception as e:
        return ResultadoURL(
            url=url_normalizada,
            online=False,
            status_code=None,
            tempo_ms=None,
            redirect_url=None,
            erro=str(e)[:80],
            categoria="offline",
        )


def verificar_urls(
    urls: list[str],
    timeout: int = 10,
    max_threads: int = 10,
) -> list[ResultadoURL]:
    """
    Verifica múltiplas URLs em paralelo.

    Args:
        urls: Lista de URLs para verificar
        timeout: Timeout por requisição
        max_threads: Número de threads paralelas

    Returns:
        Lista de ResultadoURL
    """
    resultados: list[ResultadoURL] = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        tarefa = progress.add_task("[cyan]Verificando URLs...", total=len(urls))

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
            futuros = {
                executor.submit(verificar_url, url, timeout): url
                for url in urls
            }

            for futuro in concurrent.futures.as_completed(futuros):
                resultado = futuro.result()
                resultados.append(resultado)
                progress.advance(tarefa)

    # Ordena mantendo a ordem original
    ordem_original = {url: i for i, url in enumerate(_normalizar_url(u) for u in urls)}
    resultados.sort(key=lambda r: ordem_original.get(r.url, 999))

    return resultados


def exibir_resultados(resultados: list[ResultadoURL]) -> None:
    """Exibe os resultados da verificação em uma tabela colorida."""
    tabela = Table(
        title="[bold cyan]Resultados da Verificação de URLs[/bold cyan]",
        border_style="blue",
        header_style="bold magenta",
        show_lines=True,
    )

    tabela.add_column("URL", style="cyan", max_width=50)
    tabela.add_column("Status", justify="center")
    tabela.add_column("Código", justify="center")
    tabela.add_column("Tempo (ms)", justify="right")
    tabela.add_column("Info", style="dim")

    for r in resultados:
        # Status visual
        if r.online and r.status_code and r.status_code < 400:
            status_txt = "[green]✅ Online[/green]"
        elif r.online and r.status_code and r.status_code >= 400:
            status_txt = "[yellow]⚠️ Erro HTTP[/yellow]"
        else:
            status_txt = "[red]❌ Offline[/red]"

        # Código HTTP
        if r.status_code:
            if r.status_code < 300:
                codigo = f"[green]{r.status_code}[/green]"
            elif r.status_code < 400:
                codigo = f"[cyan]{r.status_code}[/cyan]"
            elif r.status_code < 500:
                codigo = f"[yellow]{r.status_code}[/yellow]"
            else:
                codigo = f"[red]{r.status_code}[/red]"
        else:
            codigo = "[dim]N/A[/dim]"

        # Tempo de resposta
        if r.tempo_ms is not None:
            if r.tempo_ms <= LIMITE_RAPIDO:
                tempo = f"[green]{r.tempo_ms:.0f}[/green]"
            elif r.tempo_ms <= LIMITE_ACEITAVEL:
                tempo = f"[yellow]{r.tempo_ms:.0f}[/yellow]"
            else:
                tempo = f"[red]{r.tempo_ms:.0f}[/red]"
        else:
            tempo = "[dim]N/A[/dim]"

        # Info extra
        info = r.erro or ""
        if r.redirect_url:
            info = f"→ {r.redirect_url[:40]}"

        tabela.add_row(r.url[:50], status_txt, codigo, tempo, info)

    console.print(tabela)

    # Resumo
    online = sum(1 for r in resultados if r.online and (r.status_code or 0) < 400)
    offline = sum(1 for r in resultados if not r.online)
    erros_http = len(resultados) - online - offline

    console.print(
        f"\n[bold]Resumo:[/bold] "
        f"[green]{online} online[/green] | "
        f"[yellow]{erros_http} erros HTTP[/yellow] | "
        f"[red]{offline} offline[/red] | "
        f"Total: {len(resultados)}"
    )


@app.command()
def checar(
    urls_arg: Optional[str] = typer.Option(None, "--urls", "-u", help="URLs separadas por vírgula"),
    arquivo: Optional[Path] = typer.Option(None, "--arquivo", "-f", help="Arquivo com URLs (uma por linha)"),
    timeout: int = typer.Option(10, "--timeout", "-t", help="Timeout por URL em segundos"),
    threads: int = typer.Option(10, "--threads", help="Número de threads paralelas"),
    relatorio: bool = typer.Option(False, "--relatorio", "-r", help="Gerar relatório HTML"),
) -> None:
    """Verifica se URLs estão online, com código de status e tempo de resposta."""
    console.print(Panel(
        "[bold cyan]🌐 Verificador de URLs[/bold cyan]",
        border_style="cyan",
    ))

    urls: list[str] = []

    if arquivo and arquivo.exists():
        linhas = arquivo.read_text(encoding="utf-8").splitlines()
        urls = [l.strip() for l in linhas if l.strip() and not l.startswith("#")]
        console.print(f"[cyan]📄 Carregadas {len(urls)} URLs do arquivo[/cyan]")
    elif urls_arg:
        urls = [u.strip() for u in urls_arg.split(",") if u.strip()]
    else:
        console.print("[red]Forneça URLs via --urls ou --arquivo[/red]")
        raise typer.Exit(1)

    if not urls:
        console.print("[yellow]Nenhuma URL para verificar.[/yellow]")
        raise typer.Exit(0)

    console.print(f"[dim]Verificando {len(urls)} URL(s) com {threads} threads...[/dim]\n")
    resultados = verificar_urls(urls, timeout=timeout, max_threads=threads)
    exibir_resultados(resultados)

    if relatorio:
        _gerar_relatorio(resultados)


def _gerar_relatorio(resultados: list[ResultadoURL]) -> None:
    """Gera relatório HTML dos resultados."""
    online = sum(1 for r in resultados if r.online and (r.status_code or 0) < 400)
    offline = sum(1 for r in resultados if not r.online)
    tempos = [r.tempo_ms for r in resultados if r.tempo_ms is not None]
    media_tempo = sum(tempos) / len(tempos) if tempos else 0

    estatisticas = {
        "Total de URLs": str(len(resultados)),
        "Online": str(online),
        "Offline": str(offline),
        "Erros HTTP": str(len(resultados) - online - offline),
        "Tempo Médio": f"{media_tempo:.0f} ms",
    }

    linhas = []
    for r in resultados:
        badge_status = {"badge": "Online", "tipo": "sucesso"} if (r.online and (r.status_code or 0) < 400) \
            else {"badge": "Offline", "tipo": "erro"}
        linhas.append([
            r.url,
            badge_status,
            str(r.status_code) if r.status_code else "N/A",
            f"{r.tempo_ms:.0f} ms" if r.tempo_ms else "N/A",
            r.redirect_url or r.erro or "",
        ])

    secoes = [
        {
            "tipo": "tabela",
            "titulo": "Resultados da Verificação",
            "colunas": ["URL", "Status", "Código HTTP", "Tempo Resposta", "Info"],
            "linhas": linhas,
        }
    ]

    caminho = salvar_relatorio(
        "verificador_urls",
        "Verificador de URLs",
        f"Verificação de {len(resultados)} URL(s)",
        secoes,
        estatisticas,
    )
    console.print(f"\n[green]✅ Relatório salvo em: {caminho}[/green]")


def executar() -> None:
    """Ponto de entrada interativo para o verificador de URLs."""
    console.print(Panel(
        "[bold cyan]🌐 Verificador de URLs[/bold cyan]\n"
        "[dim]Verifique status e tempo de resposta de URLs[/dim]",
        border_style="cyan",
    ))

    console.print("[dim]Digite as URLs separadas por vírgula ou o caminho de um arquivo:[/dim]")
    entrada = console.input("[bold]URLs ou arquivo: [/bold]").strip()

    urls: list[str] = []
    p = Path(entrada)

    if p.exists() and p.is_file():
        linhas = p.read_text(encoding="utf-8").splitlines()
        urls = [l.strip() for l in linhas if l.strip() and not l.startswith("#")]
        console.print(f"[cyan]Carregadas {len(urls)} URLs do arquivo[/cyan]")
    else:
        urls = [u.strip() for u in entrada.split(",") if u.strip()]

    if not urls:
        console.print("[yellow]Nenhuma URL fornecida.[/yellow]")
        return

    config = carregar_config()
    timeout = config.get("request_timeout", 10)
    max_threads = config.get("max_threads", 10)

    gerar_rel = console.input("[bold]Gerar relatório HTML? (s/N): [/bold]").strip().lower() == "s"

    resultados = verificar_urls(urls, timeout=timeout, max_threads=max_threads)
    exibir_resultados(resultados)

    if gerar_rel:
        _gerar_relatorio(resultados)


if __name__ == "__main__":
    app()
