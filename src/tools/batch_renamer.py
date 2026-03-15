# Renomeador em lote com suporte a regex, prefixo, sufixo e numeração
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from src.report import salvar_relatorio

console = Console()
app = typer.Typer(help="Renomeador de arquivos em lote")


@dataclass
class OperacaoRenomear:
    """Representa uma operação de renomeação planejada."""
    original: Path
    novo_nome: str
    novo_caminho: Path
    aplicada: bool = False
    erro: Optional[str] = None


def _gerar_novo_nome(
    arquivo: Path,
    prefixo: str = "",
    sufixo: str = "",
    substituir_de: str = "",
    substituir_para: str = "",
    padrao_regex: str = "",
    substituicao_regex: str = "",
    numero: Optional[int] = None,
    inicio_numero: int = 1,
    digitos: int = 3,
    extensao: str = "",
    maiusculas: bool = False,
    minusculas: bool = False,
) -> str:
    """
    Gera o novo nome para um arquivo com base nas operações configuradas.

    Returns:
        Novo nome do arquivo (sem o diretório pai)
    """
    nome = arquivo.stem
    ext = arquivo.suffix

    # Substituição por extensão
    if extensao:
        ext = f".{extensao.lstrip('.')}"

    # Substituição simples de texto
    if substituir_de:
        nome = nome.replace(substituir_de, substituir_para)

    # Substituição por regex
    if padrao_regex:
        try:
            nome = re.sub(padrao_regex, substituicao_regex, nome)
        except re.error as e:
            raise ValueError(f"Regex inválido: {e}")

    # Caixa
    if maiusculas:
        nome = nome.upper()
    elif minusculas:
        nome = nome.lower()

    # Numeração sequencial
    if numero is not None:
        num_str = str(numero + inicio_numero - 1).zfill(digitos)
        nome = f"{num_str}_{nome}" if not prefixo else f"{prefixo}{num_str}_{nome}"
        return f"{nome}{sufixo}{ext}"

    return f"{prefixo}{nome}{sufixo}{ext}"


def planejar_renomeacao(
    diretorio: Path,
    prefixo: str = "",
    sufixo: str = "",
    substituir_de: str = "",
    substituir_para: str = "",
    padrao_regex: str = "",
    substituicao_regex: str = "",
    numeracao: bool = False,
    inicio_numero: int = 1,
    digitos: int = 3,
    extensao: str = "",
    filtro_extensao: str = "",
    maiusculas: bool = False,
    minusculas: bool = False,
    recursivo: bool = False,
) -> list[OperacaoRenomear]:
    """
    Planeja as operações de renomeação sem aplicá-las.

    Returns:
        Lista de OperacaoRenomear com o planejamento
    """
    if recursivo:
        arquivos = sorted(diretorio.rglob("*"))
    else:
        arquivos = sorted(diretorio.iterdir())

    # Filtra apenas arquivos
    arquivos = [f for f in arquivos if f.is_file()]

    # Filtra por extensão
    if filtro_extensao:
        ext_filtro = filtro_extensao.lower().lstrip(".")
        arquivos = [f for f in arquivos if f.suffix.lower().lstrip(".") == ext_filtro]

    operacoes: list[OperacaoRenomear] = []
    nomes_usados: set[str] = set()

    for i, arquivo in enumerate(arquivos):
        try:
            novo_nome = _gerar_novo_nome(
                arquivo,
                prefixo=prefixo,
                sufixo=sufixo,
                substituir_de=substituir_de,
                substituir_para=substituir_para,
                padrao_regex=padrao_regex,
                substituicao_regex=substituicao_regex,
                numero=i + 1 if numeracao else None,
                inicio_numero=inicio_numero,
                digitos=digitos,
                extensao=extensao,
                maiusculas=maiusculas,
                minusculas=minusculas,
            )

            # Resolve conflitos de nomes
            if novo_nome in nomes_usados:
                base = Path(novo_nome).stem
                ext = Path(novo_nome).suffix
                contador = 2
                while novo_nome in nomes_usados:
                    novo_nome = f"{base}_{contador}{ext}"
                    contador += 1

            nomes_usados.add(novo_nome)
            novo_caminho = arquivo.parent / novo_nome

            operacoes.append(OperacaoRenomear(
                original=arquivo,
                novo_nome=novo_nome,
                novo_caminho=novo_caminho,
            ))
        except ValueError as e:
            operacoes.append(OperacaoRenomear(
                original=arquivo,
                novo_nome=arquivo.name,
                novo_caminho=arquivo,
                erro=str(e),
            ))

    return operacoes


def exibir_preview(operacoes: list[OperacaoRenomear]) -> None:
    """Exibe uma prévia das operações de renomeação planejadas."""
    tabela = Table(
        title="[bold cyan]Prévia das Renomeações[/bold cyan]",
        border_style="blue",
        header_style="bold magenta",
        show_lines=True,
    )
    tabela.add_column("#", style="dim", width=4)
    tabela.add_column("Nome Original", style="yellow", max_width=45, no_wrap=True)
    tabela.add_column("Novo Nome", style="green", max_width=45, no_wrap=True)
    tabela.add_column("Status")

    alteracoes = 0
    for i, op in enumerate(operacoes, 1):
        if op.erro:
            status = f"[red]❌ Erro: {op.erro[:30]}[/red]"
            novo = f"[red]{op.novo_nome}[/red]"
        elif op.original.name == op.novo_nome:
            status = "[dim]Sem alteração[/dim]"
            novo = f"[dim]{op.novo_nome}[/dim]"
        else:
            status = "[green]✅ Renomear[/green]"
            novo = f"[bold green]{op.novo_nome}[/bold green]"
            alteracoes += 1

        tabela.add_row(str(i), op.original.name, novo, status)

    console.print(tabela)
    console.print(f"\n[bold]Total: {len(operacoes)} arquivo(s) | {alteracoes} serão renomeados[/bold]")


def aplicar_renomeacao(operacoes: list[OperacaoRenomear]) -> list[OperacaoRenomear]:
    """Aplica as operações de renomeação planejadas."""
    for op in operacoes:
        if op.erro or op.original.name == op.novo_nome:
            continue
        try:
            op.original.rename(op.novo_caminho)
            op.aplicada = True
        except OSError as e:
            op.erro = str(e)

    return operacoes


@app.command()
def renomear(
    diretorio: Path = typer.Argument(..., help="Diretório com os arquivos"),
    prefixo: str = typer.Option("", "--prefixo", "-p", help="Adicionar prefixo"),
    sufixo: str = typer.Option("", "--sufixo", "-s", help="Adicionar sufixo ao nome"),
    substituir: Optional[str] = typer.Option(None, "--substituir", help="Texto a substituir (formato: 'de:para')"),
    regex: Optional[str] = typer.Option(None, "--regex", help="Padrão regex (formato: 'padrão:substituição')"),
    numeracao: bool = typer.Option(False, "--numeracao", "-n", help="Adicionar numeração sequencial"),
    inicio: int = typer.Option(1, "--inicio", help="Número inicial para numeração"),
    digitos: int = typer.Option(3, "--digitos", help="Dígitos na numeração (ex: 3 = 001)"),
    extensao: str = typer.Option("", "--extensao", "-e", help="Mudar extensão dos arquivos"),
    filtro: str = typer.Option("", "--filtro", "-f", help="Filtrar por extensão"),
    maiusculas: bool = typer.Option(False, "--maiusculas", help="Converter para maiúsculas"),
    minusculas: bool = typer.Option(False, "--minusculas", help="Converter para minúsculas"),
    recursivo: bool = typer.Option(False, "--recursivo", "-r", help="Busca recursiva"),
    dry_run: bool = typer.Option(True, "--dry-run/--aplicar", help="Apenas simular (padrão: True)"),
    relatorio: bool = typer.Option(False, "--relatorio", help="Gerar relatório HTML"),
) -> None:
    """Renomeia arquivos em lote com suporte a prefixo, sufixo, regex e numeração."""
    console.print(Panel(
        "[bold cyan]📝 Renomeador em Lote[/bold cyan]",
        border_style="cyan",
    ))

    if not diretorio.exists() or not diretorio.is_dir():
        console.print(f"[red]Diretório inválido: {diretorio}[/red]")
        raise typer.Exit(1)

    # Parse de substituição
    subst_de = subst_para = ""
    if substituir:
        partes = substituir.split(":", 1)
        if len(partes) == 2:
            subst_de, subst_para = partes

    # Parse de regex
    regex_padrao = regex_subst = ""
    if regex:
        partes = regex.split(":", 1)
        if len(partes) == 2:
            regex_padrao, regex_subst = partes
        else:
            regex_padrao = partes[0]

    operacoes = planejar_renomeacao(
        diretorio,
        prefixo=prefixo,
        sufixo=sufixo,
        substituir_de=subst_de,
        substituir_para=subst_para,
        padrao_regex=regex_padrao,
        substituicao_regex=regex_subst,
        numeracao=numeracao,
        inicio_numero=inicio,
        digitos=digitos,
        extensao=extensao,
        filtro_extensao=filtro,
        maiusculas=maiusculas,
        minusculas=minusculas,
        recursivo=recursivo,
    )

    if not operacoes:
        console.print("[yellow]Nenhum arquivo encontrado para renomear.[/yellow]")
        raise typer.Exit(0)

    exibir_preview(operacoes)

    if dry_run:
        console.print("\n[yellow]⚠️  Modo DRY-RUN: nenhum arquivo foi alterado.[/yellow]")
        console.print("[dim]Use --aplicar para aplicar as alterações.[/dim]")
    else:
        confirmar = console.input("\n[bold yellow]Confirmar renomeação? (s/N): [/bold yellow]").strip().lower()
        if confirmar == "s":
            operacoes = aplicar_renomeacao(operacoes)
            aplicadas = sum(1 for op in operacoes if op.aplicada)
            erros = sum(1 for op in operacoes if op.erro)
            console.print(f"\n[green]✅ {aplicadas} arquivo(s) renomeados com sucesso.[/green]")
            if erros:
                console.print(f"[red]❌ {erros} erro(s) durante a renomeação.[/red]")
        else:
            console.print("[yellow]Operação cancelada.[/yellow]")

    if relatorio:
        _gerar_relatorio(operacoes, dry_run)


def _gerar_relatorio(operacoes: list[OperacaoRenomear], dry_run: bool) -> None:
    """Gera relatório HTML do processo de renomeação."""
    total = len(operacoes)
    alteracoes = sum(1 for op in operacoes if op.original.name != op.novo_nome and not op.erro)
    aplicadas = sum(1 for op in operacoes if op.aplicada)
    erros = sum(1 for op in operacoes if op.erro)

    estatisticas = {
        "Total de Arquivos": str(total),
        "Com Alteração": str(alteracoes),
        "Aplicadas": str(aplicadas) if not dry_run else "N/A (dry-run)",
        "Erros": str(erros),
        "Modo": "Simulação (dry-run)" if dry_run else "Aplicado",
    }

    linhas = []
    for op in operacoes:
        if op.erro:
            status = {"badge": "Erro", "tipo": "erro"}
        elif op.aplicada:
            status = {"badge": "Renomeado", "tipo": "sucesso"}
        elif op.original.name == op.novo_nome:
            status = {"badge": "Sem mudança", "tipo": "aviso"}
        else:
            status = {"badge": "Planejado", "tipo": "aviso"}

        linhas.append([
            op.original.name,
            op.novo_nome,
            str(op.original.parent),
            status,
            op.erro or "",
        ])

    secoes = [
        {
            "tipo": "tabela",
            "titulo": "Operações de Renomeação",
            "colunas": ["Nome Original", "Novo Nome", "Diretório", "Status", "Erro"],
            "linhas": linhas,
        }
    ]

    caminho = salvar_relatorio(
        "renomeador_lote",
        "Renomeador em Lote",
        f"Processamento de {total} arquivo(s)",
        secoes,
        estatisticas,
    )
    console.print(f"\n[green]✅ Relatório salvo em: {caminho}[/green]")


def executar() -> None:
    """Ponto de entrada interativo para o renomeador em lote."""
    console.print(Panel(
        "[bold cyan]📝 Renomeador em Lote[/bold cyan]\n"
        "[dim]Renomeie arquivos com prefixo, sufixo, regex e numeração[/dim]",
        border_style="cyan",
    ))

    diretorio_str = console.input("[bold]Diretório com os arquivos: [/bold]").strip()
    diretorio = Path(diretorio_str)

    if not diretorio.exists() or not diretorio.is_dir():
        console.print(f"[red]Diretório inválido: {diretorio}[/red]")
        return

    prefixo = console.input("[bold]Prefixo (Enter para pular): [/bold]").strip()
    sufixo = console.input("[bold]Sufixo no nome (Enter para pular): [/bold]").strip()
    substituir_str = console.input("[bold]Substituir texto (formato 'de:para', Enter para pular): [/bold]").strip()
    numeracao = console.input("[bold]Numeração sequencial? (s/N): [/bold]").strip().lower() == "s"
    filtro = console.input("[bold]Filtrar por extensão (Enter para todos): [/bold]").strip()
    dry_run = console.input("[bold]Modo simulação (dry-run)? (S/n): [/bold]").strip().lower() != "n"
    gerar_rel = console.input("[bold]Gerar relatório HTML? (s/N): [/bold]").strip().lower() == "s"

    subst_de = subst_para = ""
    if substituir_str and ":" in substituir_str:
        partes = substituir_str.split(":", 1)
        subst_de, subst_para = partes

    operacoes = planejar_renomeacao(
        diretorio,
        prefixo=prefixo,
        sufixo=sufixo,
        substituir_de=subst_de,
        substituir_para=subst_para,
        numeracao=numeracao,
        filtro_extensao=filtro,
    )

    if not operacoes:
        console.print("[yellow]Nenhum arquivo encontrado.[/yellow]")
        return

    exibir_preview(operacoes)

    if not dry_run:
        confirmar = console.input("\n[bold yellow]Confirmar renomeação? (s/N): [/bold yellow]").strip().lower()
        if confirmar == "s":
            operacoes = aplicar_renomeacao(operacoes)
            aplicadas = sum(1 for op in operacoes if op.aplicada)
            console.print(f"\n[green]✅ {aplicadas} arquivo(s) renomeados.[/green]")
    else:
        console.print("\n[yellow]⚠️  Modo simulação: nenhum arquivo alterado.[/yellow]")

    if gerar_rel:
        _gerar_relatorio(operacoes, dry_run)


if __name__ == "__main__":
    app()
