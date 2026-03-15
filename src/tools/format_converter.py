# Conversor de formatos: JSON ↔ CSV ↔ YAML ↔ XML
import csv
import io
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Optional

import typer
import yaml
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table

from src.report import salvar_relatorio

console = Console()
app = typer.Typer(help="Conversor de formatos JSON, CSV, YAML e XML")

FORMATOS_SUPORTADOS = {"json", "csv", "yaml", "yml", "xml"}


def detectar_formato(caminho: Path) -> str:
    """Detecta o formato de um arquivo pela extensão."""
    ext = caminho.suffix.lower().lstrip(".")
    if ext == "yml":
        ext = "yaml"
    if ext not in FORMATOS_SUPORTADOS - {"yml"}:
        raise ValueError(f"Formato não suportado: '{ext}'. Use: {', '.join(FORMATOS_SUPORTADOS)}")
    return ext


# ─── Leitores ────────────────────────────────────────────────────────────────

def ler_json(conteudo: str) -> Any:
    """Lê e parseia conteúdo JSON."""
    return json.loads(conteudo)


def ler_csv(conteudo: str) -> list[dict[str, str]]:
    """Lê e parseia conteúdo CSV em lista de dicionários."""
    reader = csv.DictReader(io.StringIO(conteudo))
    return list(reader)


def ler_yaml(conteudo: str) -> Any:
    """Lê e parseia conteúdo YAML."""
    return yaml.safe_load(conteudo)


def ler_xml(conteudo: str) -> list[dict[str, str]]:
    """Lê e parseia conteúdo XML em lista de dicionários."""
    raiz = ET.fromstring(conteudo)
    resultado = []
    for filho in raiz:
        item: dict[str, str] = {}
        # Atributos do elemento
        item.update(filho.attrib)
        # Sub-elementos
        for sub in filho:
            item[sub.tag] = sub.text or ""
        # Texto direto
        if filho.text and filho.text.strip():
            item["_texto"] = filho.text.strip()
        resultado.append(item)
    return resultado


def ler_arquivo(caminho: Path) -> tuple[Any, str]:
    """Lê um arquivo e retorna (dados, formato)."""
    conteudo = caminho.read_text(encoding="utf-8")
    formato = detectar_formato(caminho)

    leitores = {
        "json": ler_json,
        "csv": ler_csv,
        "yaml": ler_yaml,
        "xml": ler_xml,
    }
    return leitores[formato](conteudo), formato


# ─── Escritores ──────────────────────────────────────────────────────────────

def escrever_json(dados: Any) -> str:
    """Converte dados para JSON."""
    return json.dumps(dados, indent=2, ensure_ascii=False)


def escrever_csv(dados: Any) -> str:
    """Converte dados para CSV."""
    if not dados:
        return ""

    # Normaliza para lista de dicionários
    if isinstance(dados, dict):
        dados = [dados]
    elif not isinstance(dados, list):
        dados = [{"valor": str(dados)}]

    if not isinstance(dados[0], dict):
        dados = [{"valor": str(item)} for item in dados]

    saida = io.StringIO()
    campos = list(dados[0].keys())
    writer = csv.DictWriter(saida, fieldnames=campos, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(dados)
    return saida.getvalue()


def escrever_yaml(dados: Any) -> str:
    """Converte dados para YAML."""
    return yaml.dump(dados, allow_unicode=True, default_flow_style=False, sort_keys=False)


def escrever_xml(dados: Any) -> str:
    """Converte dados para XML."""
    if isinstance(dados, dict):
        dados = [dados]
    elif not isinstance(dados, list):
        dados = [{"valor": str(dados)}]

    raiz = ET.Element("dados")

    for item in dados:
        if isinstance(item, dict):
            filho = ET.SubElement(raiz, "item")
            for chave, valor in item.items():
                chave_limpa = str(chave).replace(" ", "_").replace("-", "_")
                sub = ET.SubElement(filho, chave_limpa)
                sub.text = str(valor) if valor is not None else ""
        else:
            filho = ET.SubElement(raiz, "item")
            filho.text = str(item)

    ET.indent(raiz, space="  ")
    return ET.tostring(raiz, encoding="unicode", xml_declaration=False)


def converter_conteudo(dados: Any, formato_saida: str) -> str:
    """Converte dados para o formato de saída desejado."""
    escritores = {
        "json": escrever_json,
        "csv": escrever_csv,
        "yaml": escrever_yaml,
        "xml": escrever_xml,
    }
    if formato_saida not in escritores:
        raise ValueError(f"Formato de saída não suportado: '{formato_saida}'")
    return escritores[formato_saida](dados)


def converter_arquivo(
    entrada: Path,
    formato_saida: str,
    saida: Optional[Path] = None,
) -> tuple[Path, str, str]:
    """
    Converte um arquivo para o formato especificado.

    Returns:
        Tupla (caminho_saida, formato_entrada, formato_saida)
    """
    dados, formato_entrada = ler_arquivo(entrada)
    conteudo_convertido = converter_conteudo(dados, formato_saida)

    if saida is None:
        ext_saida = "yml" if formato_saida == "yaml" else formato_saida
        saida = entrada.with_suffix(f".{ext_saida}")

    saida.write_text(conteudo_convertido, encoding="utf-8", errors="replace")
    return saida, formato_entrada, formato_saida


# ─── CLI ─────────────────────────────────────────────────────────────────────

@app.command()
def converter(
    entrada: Path = typer.Argument(..., help="Arquivo ou diretório de entrada"),
    para: str = typer.Option(..., "--para", "-p", help="Formato de saída: json, csv, yaml, xml"),
    saida: Optional[Path] = typer.Option(None, "--saida", "-o", help="Arquivo de saída (opcional)"),
    preview: bool = typer.Option(True, "--preview/--sem-preview", help="Mostrar prévia do resultado"),
    relatorio: bool = typer.Option(False, "--relatorio", "-r", help="Gerar relatório HTML"),
) -> None:
    """Converte arquivos entre os formatos JSON, CSV, YAML e XML."""
    console.print(Panel(
        "[bold cyan]🔄 Conversor de Formatos[/bold cyan]",
        border_style="cyan",
    ))

    formato_saida = para.lower().strip(".")
    if formato_saida == "yml":
        formato_saida = "yaml"

    arquivos_processados: list[dict[str, Any]] = []

    if entrada.is_dir():
        # Converter múltiplos arquivos
        arquivos = [
            f for f in entrada.iterdir()
            if f.is_file() and f.suffix.lower().lstrip(".") in FORMATOS_SUPORTADOS
        ]
        console.print(f"[cyan]📁 Encontrados {len(arquivos)} arquivos para converter[/cyan]")
    else:
        arquivos = [entrada]

    tabela = Table(
        title="Resultados da Conversão",
        border_style="blue",
        header_style="bold magenta",
    )
    tabela.add_column("Arquivo", style="cyan")
    tabela.add_column("De", style="yellow")
    tabela.add_column("Para", style="green")
    tabela.add_column("Saída", style="dim")
    tabela.add_column("Status")

    for arquivo in arquivos:
        try:
            caminho_saida, fmt_entrada, fmt_saida = converter_arquivo(
                arquivo, formato_saida, saida if len(arquivos) == 1 else None
            )
            tabela.add_row(
                arquivo.name,
                fmt_entrada.upper(),
                fmt_saida.upper(),
                str(caminho_saida),
                "[green]✅ OK[/green]",
            )
            arquivos_processados.append({
                "arquivo": arquivo.name,
                "de": fmt_entrada.upper(),
                "para": fmt_saida.upper(),
                "saida": str(caminho_saida),
                "status": "Sucesso",
            })

            if preview and len(arquivos) == 1:
                conteudo = caminho_saida.read_text(encoding="utf-8")
                linhas_preview = conteudo[:1000]
                if len(conteudo) > 1000:
                    linhas_preview += "\n... (truncado)"

                linguagem_map = {
                    "json": "json",
                    "yaml": "yaml",
                    "xml": "xml",
                    "csv": "text",
                }
                lang = linguagem_map.get(fmt_saida, "text")
                console.print(Panel(
                    Syntax(linhas_preview, lang, theme="monokai", line_numbers=True),
                    title=f"Prévia: {caminho_saida.name}",
                    border_style="green",
                ))

        except Exception as e:
            tabela.add_row(
                arquivo.name, "?", formato_saida.upper(), "N/A",
                f"[red]❌ {str(e)[:40]}[/red]",
            )
            arquivos_processados.append({
                "arquivo": arquivo.name,
                "de": "?",
                "para": formato_saida.upper(),
                "saida": "N/A",
                "status": f"Erro: {e}",
            })

    console.print(tabela)

    if relatorio:
        _gerar_relatorio(arquivos_processados, formato_saida)


def _gerar_relatorio(arquivos: list[dict[str, Any]], formato_saida: str) -> None:
    """Gera relatório HTML da conversão."""
    total = len(arquivos)
    sucesso = sum(1 for a in arquivos if a["status"] == "Sucesso")

    estatisticas = {
        "Total de Arquivos": str(total),
        "Convertidos": str(sucesso),
        "Erros": str(total - sucesso),
        "Formato Destino": formato_saida.upper(),
    }

    linhas = [
        [a["arquivo"], a["de"], a["para"], a["saida"], a["status"]]
        for a in arquivos
    ]

    secoes = [
        {
            "tipo": "tabela",
            "titulo": "Arquivos Convertidos",
            "colunas": ["Arquivo", "De", "Para", "Saída", "Status"],
            "linhas": linhas,
        }
    ]

    caminho = salvar_relatorio(
        "conversor_formatos",
        "Conversor de Formatos",
        f"Conversão de {total} arquivo(s) para {formato_saida.upper()}",
        secoes,
        estatisticas,
    )
    console.print(f"\n[green]✅ Relatório salvo em: {caminho}[/green]")


def executar() -> None:
    """Ponto de entrada interativo para o conversor de formatos."""
    console.print(Panel(
        "[bold cyan]🔄 Conversor de Formatos[/bold cyan]\n"
        "[dim]Converta entre JSON, CSV, YAML e XML[/dim]",
        border_style="cyan",
    ))

    entrada_str = console.input("[bold]Caminho do arquivo de entrada: [/bold]").strip()
    entrada = Path(entrada_str)

    if not entrada.exists():
        console.print(f"[red]Arquivo não encontrado: {entrada}[/red]")
        return

    formatos = ", ".join(sorted(FORMATOS_SUPORTADOS - {"yml"}))
    para = console.input(f"[bold]Formato de saída ({formatos}): [/bold]").strip().lower()
    gerar_rel = console.input("[bold]Gerar relatório HTML? (s/N): [/bold]").strip().lower() == "s"

    try:
        caminho_saida, fmt_entrada, fmt_saida = converter_arquivo(entrada, para)
        console.print(f"\n[green]✅ Convertido: {fmt_entrada.upper()} → {fmt_saida.upper()}[/green]")
        console.print(f"[cyan]Salvo em: {caminho_saida}[/cyan]")

        if gerar_rel:
            _gerar_relatorio(
                [{"arquivo": entrada.name, "de": fmt_entrada.upper(), "para": fmt_saida.upper(),
                  "saida": str(caminho_saida), "status": "Sucesso"}],
                fmt_saida,
            )
    except Exception as e:
        console.print(f"[red]Erro na conversão: {e}[/red]")


if __name__ == "__main__":
    app()
