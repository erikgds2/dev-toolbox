# Buscador de arquivos duplicados por hash MD5
import hashlib
import os
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TaskProgressColumn, TextColumn
from rich.table import Table
from rich.tree import Tree

from src.config import carregar_config
from src.report import salvar_relatorio

console = Console()
app = typer.Typer(help="Buscador de arquivos duplicados por hash")


@dataclass
class GrupoDuplicatas:
    """Grupo de arquivos com conteúdo idêntico."""
    hash_md5: str
    arquivos: list[Path] = field(default_factory=list)

    @property
    def tamanho_arquivo(self) -> int:
        """Retorna o tamanho do arquivo (todos são iguais)."""
        if self.arquivos and self.arquivos[0].exists():
            return self.arquivos[0].stat().st_size
        return 0

    @property
    def espaco_desperdicado(self) -> int:
        """Espaço desperdiçado pelos duplicados (contando a partir do segundo)."""
        return self.tamanho_arquivo * (len(self.arquivos) - 1)

    @property
    def quantidade_duplicatas(self) -> int:
        """Número de arquivos extras (duplicatas)."""
        return len(self.arquivos) - 1


def _formatar_bytes(num_bytes: int) -> str:
    """Converte bytes em formato legível."""
    for unidade in ["B", "KB", "MB", "GB", "TB"]:
        if num_bytes < 1024.0:
            return f"{num_bytes:.1f} {unidade}"
        num_bytes /= 1024.0
    return f"{num_bytes:.1f} PB"


def calcular_hash_md5(caminho: Path, tamanho_bloco: int = 65536) -> Optional[str]:
    """
    Calcula o hash MD5 de um arquivo.

    Args:
        caminho: Caminho do arquivo
        tamanho_bloco: Tamanho do bloco de leitura em bytes

    Returns:
        String hexadecimal do hash, ou None em caso de erro
    """
    hasher = hashlib.md5()
    try:
        with open(caminho, "rb") as f:
            while bloco := f.read(tamanho_bloco):
                hasher.update(bloco)
        return hasher.hexdigest()
    except (PermissionError, OSError, IsADirectoryError):
        return None


def encontrar_duplicatas(
    diretorio: Path,
    recursivo: bool = True,
    tamanho_minimo: int = 0,
    ignorar_extensoes: Optional[set[str]] = None,
) -> list[GrupoDuplicatas]:
    """
    Escaneia um diretório em busca de arquivos duplicados.

    Args:
        diretorio: Diretório raiz para a busca
        recursivo: Busca em subdiretórios
        tamanho_minimo: Tamanho mínimo em bytes para considerar
        ignorar_extensoes: Conjunto de extensões para ignorar

    Returns:
        Lista de GrupoDuplicatas com os arquivos duplicados
    """
    if ignorar_extensoes is None:
        ignorar_extensoes = set()

    # Coleta todos os arquivos
    if recursivo:
        todos_arquivos = [f for f in diretorio.rglob("*") if f.is_file()]
    else:
        todos_arquivos = [f for f in diretorio.iterdir() if f.is_file()]

    # Aplica filtros
    arquivos_filtrados = []
    for arquivo in todos_arquivos:
        try:
            tamanho = arquivo.stat().st_size
            ext = arquivo.suffix.lower().lstrip(".")
            if tamanho >= tamanho_minimo and ext not in ignorar_extensoes:
                arquivos_filtrados.append(arquivo)
        except OSError:
            continue

    console.print(f"[cyan]📁 Analisando {len(arquivos_filtrados)} arquivo(s)...[/cyan]")

    # Primeira passagem: agrupa por tamanho (otimização — não calcula hash de arquivos únicos)
    por_tamanho: defaultdict[int, list[Path]] = defaultdict(list)
    for arquivo in arquivos_filtrados:
        try:
            tamanho = arquivo.stat().st_size
            por_tamanho[tamanho].append(arquivo)
        except OSError:
            continue

    # Candidatos com mesmo tamanho
    candidatos = [
        arquivo
        for arquivos_mesmo_tamanho in por_tamanho.values()
        if len(arquivos_mesmo_tamanho) > 1
        for arquivo in arquivos_mesmo_tamanho
    ]

    if not candidatos:
        return []

    # Segunda passagem: calcula hash dos candidatos
    por_hash: defaultdict[str, list[Path]] = defaultdict(list)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
    ) as progress:
        tarefa = progress.add_task(
            f"[cyan]Calculando hashes de {len(candidatos)} candidatos...",
            total=len(candidatos),
        )

        for arquivo in candidatos:
            hash_md5 = calcular_hash_md5(arquivo)
            if hash_md5:
                por_hash[hash_md5].append(arquivo)
            progress.advance(tarefa)

    # Monta grupos de duplicatas
    grupos = []
    for hash_md5, arquivos in por_hash.items():
        if len(arquivos) > 1:
            grupos.append(GrupoDuplicatas(hash_md5=hash_md5, arquivos=sorted(arquivos)))

    # Ordena por espaço desperdiçado (maior primeiro)
    grupos.sort(key=lambda g: g.espaco_desperdicado, reverse=True)

    return grupos


def exibir_grupos(grupos: list[GrupoDuplicatas]) -> None:
    """Exibe os grupos de duplicatas com detalhes."""
    if not grupos:
        console.print(Panel(
            "[green]✅ Nenhum arquivo duplicado encontrado![/green]",
            border_style="green",
        ))
        return

    total_duplicatas = sum(g.quantidade_duplicatas for g in grupos)
    espaco_total = sum(g.espaco_desperdicado for g in grupos)

    console.print(Panel(
        f"[bold red]⚠️  {len(grupos)} grupo(s) de duplicatas encontrado(s)[/bold red]\n"
        f"[yellow]{total_duplicatas} arquivo(s) duplicado(s)[/yellow]\n"
        f"[red]Espaço desperdiçado: {_formatar_bytes(espaco_total)}[/red]",
        border_style="red",
    ))

    for i, grupo in enumerate(grupos, 1):
        arvore = Tree(
            f"[bold cyan]Grupo {i}[/bold cyan] — "
            f"[dim]{grupo.hash_md5[:16]}...[/dim] — "
            f"[yellow]{_formatar_bytes(grupo.tamanho_arquivo)} cada[/yellow] — "
            f"[red]Desperdiçando: {_formatar_bytes(grupo.espaco_desperdicado)}[/red]"
        )

        for j, arquivo in enumerate(grupo.arquivos):
            icone = "📌" if j == 0 else "📋"
            label = " [dim](original)[/dim]" if j == 0 else " [yellow](duplicata)[/yellow]"
            arvore.add(f"{icone} {arquivo}{label}")

        console.print(arvore)
        console.print()


def deletar_duplicatas(
    grupos: list[GrupoDuplicatas],
    confirmar: bool = True,
) -> tuple[int, int]:
    """
    Remove os arquivos duplicados, mantendo o primeiro de cada grupo.

    Returns:
        Tupla (arquivos_removidos, bytes_liberados)
    """
    arquivos_removidos = 0
    bytes_liberados = 0

    if confirmar:
        resposta = console.input(
            f"\n[bold red]⚠️  Tem certeza que deseja deletar as duplicatas? "
            f"(digite 'CONFIRMAR' para prosseguir): [/bold red]"
        ).strip()
        if resposta != "CONFIRMAR":
            console.print("[yellow]Operação cancelada.[/yellow]")
            return 0, 0

    for grupo in grupos:
        # Mantém o primeiro arquivo, deleta os outros
        for arquivo in grupo.arquivos[1:]:
            try:
                tamanho = arquivo.stat().st_size
                arquivo.unlink()
                arquivos_removidos += 1
                bytes_liberados += tamanho
                console.print(f"[red]🗑️  Removido: {arquivo}[/red]")
            except OSError as e:
                console.print(f"[yellow]⚠️  Não foi possível remover {arquivo}: {e}[/yellow]")

    return arquivos_removidos, bytes_liberados


@app.command()
def buscar(
    diretorio: Path = typer.Argument(..., help="Diretório para escanear"),
    recursivo: bool = typer.Option(True, "--recursivo/--sem-recursivo", help="Busca recursiva"),
    tamanho_minimo: int = typer.Option(0, "--tamanho-minimo", help="Tamanho mínimo em bytes"),
    ignorar: str = typer.Option("", "--ignorar", help="Extensões a ignorar (ex: 'tmp,log')"),
    deletar: bool = typer.Option(False, "--deletar", "-d", help="Deletar duplicatas (mantém o primeiro)"),
    relatorio: bool = typer.Option(False, "--relatorio", "-r", help="Gerar relatório HTML"),
) -> None:
    """Encontra arquivos duplicados por hash MD5 e opcionalmente os remove."""
    console.print(Panel(
        "[bold cyan]🔍 Buscador de Duplicatas[/bold cyan]",
        border_style="cyan",
    ))

    if not diretorio.exists() or not diretorio.is_dir():
        console.print(f"[red]Diretório inválido: {diretorio}[/red]")
        raise typer.Exit(1)

    extensoes_ignorar = {e.strip().lower() for e in ignorar.split(",") if e.strip()} if ignorar else set()

    grupos = encontrar_duplicatas(
        diretorio,
        recursivo=recursivo,
        tamanho_minimo=tamanho_minimo,
        ignorar_extensoes=extensoes_ignorar,
    )

    exibir_grupos(grupos)

    removidos = liberados = 0
    if deletar and grupos:
        removidos, liberados = deletar_duplicatas(grupos)
        if removidos > 0:
            console.print(f"\n[green]✅ {removidos} arquivo(s) removidos, {_formatar_bytes(liberados)} liberados.[/green]")

    if relatorio:
        _gerar_relatorio(grupos, removidos, liberados)


def _gerar_relatorio(
    grupos: list[GrupoDuplicatas],
    removidos: int = 0,
    liberados: int = 0,
) -> None:
    """Gera relatório HTML dos duplicados encontrados."""
    total_grupos = len(grupos)
    total_duplicatas = sum(g.quantidade_duplicatas for g in grupos)
    espaco_desperdicado = sum(g.espaco_desperdicado for g in grupos)

    estatisticas = {
        "Grupos de Duplicatas": str(total_grupos),
        "Arquivos Duplicados": str(total_duplicatas),
        "Espaço Desperdiçado": _formatar_bytes(espaco_desperdicado),
        "Arquivos Removidos": str(removidos),
        "Espaço Liberado": _formatar_bytes(liberados) if liberados else "N/A",
    }

    linhas = []
    for i, grupo in enumerate(grupos, 1):
        for j, arquivo in enumerate(grupo.arquivos):
            tipo = "Original" if j == 0 else "Duplicata"
            linhas.append([
                str(i),
                arquivo.name,
                str(arquivo.parent),
                _formatar_bytes(grupo.tamanho_arquivo),
                tipo,
                grupo.hash_md5[:16] + "...",
            ])

    secoes = [
        {
            "tipo": "tabela",
            "titulo": "Arquivos Duplicados",
            "colunas": ["Grupo", "Arquivo", "Diretório", "Tamanho", "Tipo", "Hash MD5"],
            "linhas": linhas,
        }
    ]

    caminho = salvar_relatorio(
        "duplicatas",
        "Buscador de Duplicatas",
        f"{total_grupos} grupo(s) de duplicatas encontrado(s)",
        secoes,
        estatisticas,
    )
    console.print(f"\n[green]✅ Relatório salvo em: {caminho}[/green]")


def executar() -> None:
    """Ponto de entrada interativo para o buscador de duplicatas."""
    console.print(Panel(
        "[bold cyan]🔍 Buscador de Duplicatas[/bold cyan]\n"
        "[dim]Encontre e remova arquivos duplicados por hash MD5[/dim]",
        border_style="cyan",
    ))

    diretorio_str = console.input("[bold]Diretório para escanear: [/bold]").strip()
    diretorio = Path(diretorio_str)

    if not diretorio.exists() or not diretorio.is_dir():
        console.print(f"[red]Diretório inválido: {diretorio}[/red]")
        return

    recursivo = console.input("[bold]Busca recursiva? (S/n): [/bold]").strip().lower() != "n"
    gerar_rel = console.input("[bold]Gerar relatório HTML? (s/N): [/bold]").strip().lower() == "s"

    grupos = encontrar_duplicatas(diretorio, recursivo=recursivo)
    exibir_grupos(grupos)

    removidos = liberados = 0
    if grupos:
        deletar = console.input("[bold red]Deletar duplicatas? (s/N): [/bold red]").strip().lower() == "s"
        if deletar:
            removidos, liberados = deletar_duplicatas(grupos)
            if removidos > 0:
                console.print(
                    f"\n[green]✅ {removidos} arquivo(s) removidos, {_formatar_bytes(liberados)} liberados.[/green]"
                )

    if gerar_rel:
        _gerar_relatorio(grupos, removidos, liberados)


if __name__ == "__main__":
    app()
