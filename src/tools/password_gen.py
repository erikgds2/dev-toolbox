# Gerador de senhas seguras com score de força
import math
import re
import secrets
import string
from dataclasses import dataclass
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from src.report import salvar_relatorio

console = Console()
app = typer.Typer(help="Gerador de senhas seguras")

# Caracteres ambíguos que podem causar confusão visual
CHARS_AMBIGUOS = set("0OIl1|")


@dataclass
class ResultadoSenha:
    """Resultado de uma senha gerada com metadados."""
    senha: str
    comprimento: int
    score: int
    nivel: str
    cor: str
    entropia: float
    tem_maiusculas: bool
    tem_minusculas: bool
    tem_numeros: bool
    tem_simbolos: bool


def calcular_score(senha: str) -> tuple[int, str, str]:
    """
    Calcula o score de força da senha de 0 a 100.

    Returns:
        Tupla (score, nivel, cor)
    """
    score = 0

    # Comprimento (até 30 pontos)
    comprimento = len(senha)
    if comprimento >= 8:
        score += 10
    if comprimento >= 12:
        score += 10
    if comprimento >= 16:
        score += 10

    # Diversidade de caracteres (até 40 pontos)
    tem_maiusculas = bool(re.search(r"[A-Z]", senha))
    tem_minusculas = bool(re.search(r"[a-z]", senha))
    tem_numeros = bool(re.search(r"\d", senha))
    tem_simbolos = bool(re.search(r"[^A-Za-z0-9]", senha))

    if tem_maiusculas:
        score += 10
    if tem_minusculas:
        score += 10
    if tem_numeros:
        score += 10
    if tem_simbolos:
        score += 10

    # Entropia estimada (até 30 pontos)
    tamanho_charset = 0
    if tem_maiusculas:
        tamanho_charset += 26
    if tem_minusculas:
        tamanho_charset += 26
    if tem_numeros:
        tamanho_charset += 10
    if tem_simbolos:
        tamanho_charset += 32

    if tamanho_charset > 0:
        entropia = comprimento * math.log2(tamanho_charset)
        if entropia >= 40:
            score += 10
        if entropia >= 60:
            score += 10
        if entropia >= 80:
            score += 10

    # Penalidades
    # Sequências óbvias
    sequencias = ["123", "abc", "qwe", "asd", "zxc", "password", "senha", "admin"]
    for seq in sequencias:
        if seq in senha.lower():
            score -= 15
            break

    # Muita repetição
    if len(set(senha)) < len(senha) * 0.4:
        score -= 10

    score = max(0, min(100, score))

    # Nível de força
    if score < 30:
        nivel = "Fraca"
        cor = "red"
    elif score < 55:
        nivel = "Média"
        cor = "yellow"
    elif score < 80:
        nivel = "Forte"
        cor = "green"
    else:
        nivel = "Muito Forte"
        cor = "bright_green"

    return score, nivel, cor


def calcular_entropia(senha: str) -> float:
    """Calcula a entropia em bits da senha."""
    tamanho_charset = 0
    if re.search(r"[A-Z]", senha):
        tamanho_charset += 26
    if re.search(r"[a-z]", senha):
        tamanho_charset += 26
    if re.search(r"\d", senha):
        tamanho_charset += 10
    if re.search(r"[^A-Za-z0-9]", senha):
        tamanho_charset += 32
    if tamanho_charset == 0:
        return 0.0
    return len(senha) * math.log2(tamanho_charset)


def gerar_senha(
    comprimento: int = 16,
    maiusculas: bool = True,
    minusculas: bool = True,
    numeros: bool = True,
    simbolos: bool = True,
    excluir_ambiguos: bool = False,
) -> ResultadoSenha:
    """
    Gera uma senha segura com as configurações especificadas.

    Args:
        comprimento: Número de caracteres da senha
        maiusculas: Incluir letras maiúsculas
        minusculas: Incluir letras minúsculas
        numeros: Incluir números
        simbolos: Incluir símbolos especiais
        excluir_ambiguos: Excluir caracteres visualmente ambíguos

    Returns:
        ResultadoSenha com a senha e seus metadados
    """
    if not any([maiusculas, minusculas, numeros, simbolos]):
        raise ValueError("Pelo menos um tipo de caractere deve ser selecionado.")

    charset = ""
    obrigatorios: list[str] = []

    if maiusculas:
        chars = string.ascii_uppercase
        if excluir_ambiguos:
            chars = "".join(c for c in chars if c not in CHARS_AMBIGUOS)
        charset += chars
        obrigatorios.append(secrets.choice(chars))

    if minusculas:
        chars = string.ascii_lowercase
        if excluir_ambiguos:
            chars = "".join(c for c in chars if c not in CHARS_AMBIGUOS)
        charset += chars
        obrigatorios.append(secrets.choice(chars))

    if numeros:
        chars = string.digits
        if excluir_ambiguos:
            chars = "".join(c for c in chars if c not in CHARS_AMBIGUOS)
        charset += chars
        obrigatorios.append(secrets.choice(chars))

    if simbolos:
        chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        charset += chars
        obrigatorios.append(secrets.choice(chars))

    # Preenche o restante aleatoriamente
    restante = comprimento - len(obrigatorios)
    senha_lista = obrigatorios + [secrets.choice(charset) for _ in range(restante)]

    # Embaralha com algoritmo criptograficamente seguro
    for i in range(len(senha_lista) - 1, 0, -1):
        j = secrets.randbelow(i + 1)
        senha_lista[i], senha_lista[j] = senha_lista[j], senha_lista[i]

    senha = "".join(senha_lista)
    score, nivel, cor = calcular_score(senha)
    entropia = calcular_entropia(senha)

    return ResultadoSenha(
        senha=senha,
        comprimento=len(senha),
        score=score,
        nivel=nivel,
        cor=cor,
        entropia=entropia,
        tem_maiusculas=bool(re.search(r"[A-Z]", senha)),
        tem_minusculas=bool(re.search(r"[a-z]", senha)),
        tem_numeros=bool(re.search(r"\d", senha)),
        tem_simbolos=bool(re.search(r"[^A-Za-z0-9]", senha)),
    )


def exibir_resultado(resultado: ResultadoSenha, numero: int = 1) -> None:
    """Exibe uma senha gerada no terminal com formatação rica."""
    # Barra de força
    largura_barra = 30
    preenchido = int((resultado.score / 100) * largura_barra)
    barra = "█" * preenchido + "░" * (largura_barra - preenchido)

    texto = Text()
    texto.append(f"  Senha {numero}: ", style="bold white")
    texto.append(resultado.senha, style=f"bold {resultado.cor}")
    texto.append(f"\n  Força: ", style="white")
    texto.append(f"[{barra}]", style=f"bold {resultado.cor}")
    texto.append(f" {resultado.score}/100 — {resultado.nivel}", style=resultado.cor)
    texto.append(f"\n  Entropia: {resultado.entropia:.1f} bits", style="dim")
    texto.append(f"  |  Comprimento: {resultado.comprimento} chars", style="dim")

    console.print(Panel(texto, border_style=resultado.cor))


@app.command()
def gerar(
    comprimento: int = typer.Option(16, "--comprimento", "-c", help="Comprimento da senha"),
    quantidade: int = typer.Option(1, "--quantidade", "-q", help="Quantidade de senhas"),
    sem_maiusculas: bool = typer.Option(False, "--sem-maiusculas", help="Excluir letras maiúsculas"),
    sem_minusculas: bool = typer.Option(False, "--sem-minusculas", help="Excluir letras minúsculas"),
    sem_numeros: bool = typer.Option(False, "--sem-numeros", help="Excluir números"),
    sem_simbolos: bool = typer.Option(False, "--sem-simbolos", help="Excluir símbolos"),
    excluir_ambiguos: bool = typer.Option(False, "--excluir-ambiguos", "-a", help="Excluir caracteres ambíguos"),
    relatorio: bool = typer.Option(False, "--relatorio", "-r", help="Gerar relatório HTML"),
) -> None:
    """Gera senhas seguras com score de força e configurações personalizáveis."""
    console.print(Panel(
        "[bold cyan]🔐 Gerador de Senhas Seguras[/bold cyan]",
        border_style="cyan",
    ))

    resultados: list[ResultadoSenha] = []

    for i in range(quantidade):
        try:
            resultado = gerar_senha(
                comprimento=comprimento,
                maiusculas=not sem_maiusculas,
                minusculas=not sem_minusculas,
                numeros=not sem_numeros,
                simbolos=not sem_simbolos,
                excluir_ambiguos=excluir_ambiguos,
            )
            exibir_resultado(resultado, i + 1)
            resultados.append(resultado)
        except ValueError as e:
            console.print(f"[red]Erro: {e}[/red]")
            return

    if relatorio:
        _gerar_relatorio(resultados)


def _gerar_relatorio(resultados: list[ResultadoSenha]) -> None:
    """Gera relatório HTML com as senhas geradas."""
    scores = [r.score for r in resultados]
    media_score = sum(scores) / len(scores) if scores else 0

    estatisticas = {
        "Total Geradas": str(len(resultados)),
        "Score Médio": f"{media_score:.0f}/100",
        "Score Máximo": f"{max(scores)}/100" if scores else "N/A",
        "Score Mínimo": f"{min(scores)}/100" if scores else "N/A",
        "Comprimento": str(resultados[0].comprimento if resultados else 0),
    }

    linhas = []
    for i, r in enumerate(resultados, 1):
        linhas.append([
            str(i),
            r.senha,
            f"{r.score}/100",
            r.nivel,
            f"{r.entropia:.1f} bits",
            str(r.comprimento),
        ])

    secoes = [
        {
            "tipo": "tabela",
            "titulo": "Senhas Geradas",
            "colunas": ["#", "Senha", "Score", "Nível", "Entropia", "Comprimento"],
            "linhas": linhas,
        },
    ]

    caminho = salvar_relatorio(
        "gerador_senhas",
        "Gerador de Senhas Seguras",
        f"{len(resultados)} senha(s) gerada(s)",
        secoes,
        estatisticas,
    )
    console.print(f"\n[green]✅ Relatório salvo em: {caminho}[/green]")


def executar() -> None:
    """Ponto de entrada interativo para o gerador de senhas."""
    console.print(Panel(
        "[bold cyan]🔐 Gerador de Senhas Seguras[/bold cyan]\n"
        "[dim]Gere senhas com score de força personalizado[/dim]",
        border_style="cyan",
    ))

    comprimento_str = console.input("[bold]Comprimento da senha (padrão 16): [/bold]").strip()
    comprimento = int(comprimento_str) if comprimento_str.isdigit() else 16

    quantidade_str = console.input("[bold]Quantidade de senhas (padrão 1): [/bold]").strip()
    quantidade = int(quantidade_str) if quantidade_str.isdigit() else 1

    sem_simbolos = console.input("[bold]Incluir símbolos? (S/n): [/bold]").strip().lower() == "n"
    excluir_amb = console.input("[bold]Excluir caracteres ambíguos? (s/N): [/bold]").strip().lower() == "s"
    gerar_rel = console.input("[bold]Gerar relatório HTML? (s/N): [/bold]").strip().lower() == "s"

    resultados: list[ResultadoSenha] = []
    for i in range(quantidade):
        resultado = gerar_senha(
            comprimento=comprimento,
            simbolos=not sem_simbolos,
            excluir_ambiguos=excluir_amb,
        )
        exibir_resultado(resultado, i + 1)
        resultados.append(resultado)

    if gerar_rel and resultados:
        _gerar_relatorio(resultados)


if __name__ == "__main__":
    app()
