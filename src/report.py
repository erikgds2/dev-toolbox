# Módulo gerador de relatórios HTML com tema escuro
import os
from datetime import datetime
from pathlib import Path
from typing import Any

from src.config import obter_diretorio_saida

# Paleta de cores do tema escuro
CORES = {
    "fundo": "#1a1a2e",
    "fundo_card": "#16213e",
    "fundo_header": "#0f3460",
    "acento": "#00d4ff",
    "acento2": "#e94560",
    "texto": "#e0e0e0",
    "texto_dim": "#9e9e9e",
    "sucesso": "#4caf50",
    "aviso": "#ff9800",
    "erro": "#f44336",
    "borda": "#2a2a4a",
}

CSS_BASE = f"""
* {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}}

body {{
    background-color: {CORES['fundo']};
    color: {CORES['texto']};
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    min-height: 100vh;
    padding: 20px;
}}

.container {{
    max-width: 1200px;
    margin: 0 auto;
}}

header {{
    background: linear-gradient(135deg, {CORES['fundo_header']}, {CORES['fundo_card']});
    border: 1px solid {CORES['acento']};
    border-radius: 12px;
    padding: 30px;
    margin-bottom: 30px;
    text-align: center;
    box-shadow: 0 0 30px rgba(0, 212, 255, 0.15);
}}

header h1 {{
    color: {CORES['acento']};
    font-size: 2.2em;
    margin-bottom: 8px;
    text-shadow: 0 0 10px rgba(0, 212, 255, 0.5);
}}

header .subtitulo {{
    color: {CORES['texto_dim']};
    font-size: 1em;
}}

header .timestamp {{
    color: {CORES['acento2']};
    font-size: 0.9em;
    margin-top: 8px;
}}

.card {{
    background-color: {CORES['fundo_card']};
    border: 1px solid {CORES['borda']};
    border-radius: 10px;
    padding: 25px;
    margin-bottom: 20px;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
}}

.card h2 {{
    color: {CORES['acento']};
    font-size: 1.3em;
    margin-bottom: 15px;
    padding-bottom: 10px;
    border-bottom: 1px solid {CORES['borda']};
}}

.estatisticas {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 15px;
    margin-bottom: 20px;
}}

.stat-item {{
    background: linear-gradient(135deg, {CORES['fundo_header']}, {CORES['fundo_card']});
    border: 1px solid {CORES['acento']};
    border-radius: 8px;
    padding: 15px;
    text-align: center;
}}

.stat-item .valor {{
    font-size: 2em;
    font-weight: bold;
    color: {CORES['acento']};
}}

.stat-item .rotulo {{
    font-size: 0.85em;
    color: {CORES['texto_dim']};
    margin-top: 5px;
}}

table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 0.9em;
}}

th {{
    background-color: {CORES['fundo_header']};
    color: {CORES['acento']};
    padding: 12px 15px;
    text-align: left;
    font-weight: 600;
    border-bottom: 2px solid {CORES['acento']};
}}

td {{
    padding: 10px 15px;
    border-bottom: 1px solid {CORES['borda']};
    color: {CORES['texto']};
}}

tr:hover td {{
    background-color: rgba(0, 212, 255, 0.05);
}}

.badge {{
    display: inline-block;
    padding: 3px 10px;
    border-radius: 12px;
    font-size: 0.8em;
    font-weight: bold;
}}

.badge-sucesso {{
    background-color: rgba(76, 175, 80, 0.2);
    color: {CORES['sucesso']};
    border: 1px solid {CORES['sucesso']};
}}

.badge-erro {{
    background-color: rgba(244, 67, 54, 0.2);
    color: {CORES['erro']};
    border: 1px solid {CORES['erro']};
}}

.badge-aviso {{
    background-color: rgba(255, 152, 0, 0.2);
    color: {CORES['aviso']};
    border: 1px solid {CORES['aviso']};
}}

footer {{
    text-align: center;
    color: {CORES['texto_dim']};
    font-size: 0.8em;
    margin-top: 30px;
    padding-top: 20px;
    border-top: 1px solid {CORES['borda']};
}}

pre {{
    background-color: {CORES['fundo']};
    border: 1px solid {CORES['borda']};
    border-radius: 6px;
    padding: 15px;
    overflow-x: auto;
    font-family: 'Courier New', monospace;
    font-size: 0.85em;
    color: {CORES['acento']};
}}

.barra-progresso {{
    background-color: {CORES['fundo']};
    border-radius: 10px;
    height: 10px;
    overflow: hidden;
    margin: 5px 0;
}}

.barra-preenchimento {{
    height: 100%;
    border-radius: 10px;
    transition: width 0.3s ease;
}}

.barra-verde {{ background-color: {CORES['sucesso']}; }}
.barra-amarela {{ background-color: {CORES['aviso']}; }}
.barra-vermelha {{ background-color: {CORES['erro']}; }}
"""


def gerar_html(
    titulo_ferramenta: str,
    descricao: str,
    secoes: list[dict[str, Any]],
    estatisticas: dict[str, Any] | None = None,
) -> str:
    """
    Gera o HTML completo do relatório.

    Args:
        titulo_ferramenta: Nome da ferramenta
        descricao: Descrição do relatório
        secoes: Lista de seções com título, tipo e dados
        estatisticas: Dicionário com métricas resumidas

    Returns:
        String com o HTML completo
    """
    agora = datetime.now().strftime("%d/%m/%Y às %H:%M:%S")

    html_estatisticas = ""
    if estatisticas:
        itens_stat = ""
        for rotulo, valor in estatisticas.items():
            itens_stat += f"""
            <div class="stat-item">
                <div class="valor">{valor}</div>
                <div class="rotulo">{rotulo}</div>
            </div>"""
        html_estatisticas = f"""
        <div class="card">
            <h2>Resumo</h2>
            <div class="estatisticas">{itens_stat}
            </div>
        </div>"""

    html_secoes = ""
    for secao in secoes:
        tipo = secao.get("tipo", "tabela")
        titulo_secao = secao.get("titulo", "Resultados")

        if tipo == "tabela":
            html_secoes += _renderizar_tabela(titulo_secao, secao)
        elif tipo == "texto":
            html_secoes += _renderizar_texto(titulo_secao, secao)
        elif tipo == "lista":
            html_secoes += _renderizar_lista(titulo_secao, secao)

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>dev-toolbox | {titulo_ferramenta}</title>
    <style>
{CSS_BASE}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🛠️ dev-toolbox</h1>
            <div class="subtitulo">{titulo_ferramenta} — {descricao}</div>
            <div class="timestamp">Gerado em: {agora}</div>
        </header>

        {html_estatisticas}

        {html_secoes}

        <footer>
            <p>Gerado automaticamente pelo <strong>dev-toolbox v1.0.0</strong></p>
        </footer>
    </div>
</body>
</html>"""


def _renderizar_tabela(titulo: str, secao: dict[str, Any]) -> str:
    """Renderiza uma seção de tabela HTML."""
    colunas = secao.get("colunas", [])
    linhas = secao.get("linhas", [])

    if not colunas or not linhas:
        return ""

    cabecalho = "".join(f"<th>{col}</th>" for col in colunas)

    linhas_html = ""
    for linha in linhas:
        celulas = ""
        for i, celula in enumerate(linha):
            # Verifica se é um badge
            if isinstance(celula, dict) and "badge" in celula:
                tipo_badge = celula.get("tipo", "sucesso")
                celulas += f'<td><span class="badge badge-{tipo_badge}">{celula["badge"]}</span></td>'
            else:
                celulas += f"<td>{celula}</td>"
        linhas_html += f"<tr>{celulas}</tr>"

    return f"""
        <div class="card">
            <h2>{titulo}</h2>
            <table>
                <thead><tr>{cabecalho}</tr></thead>
                <tbody>{linhas_html}</tbody>
            </table>
        </div>"""


def _renderizar_texto(titulo: str, secao: dict[str, Any]) -> str:
    """Renderiza uma seção de texto/código."""
    conteudo = secao.get("conteudo", "")
    return f"""
        <div class="card">
            <h2>{titulo}</h2>
            <pre>{conteudo}</pre>
        </div>"""


def _renderizar_lista(titulo: str, secao: dict[str, Any]) -> str:
    """Renderiza uma seção de lista."""
    itens = secao.get("itens", [])
    itens_html = "".join(f"<li style='padding: 5px 0; color: #e0e0e0;'>{item}</li>" for item in itens)
    return f"""
        <div class="card">
            <h2>{titulo}</h2>
            <ul style="list-style: none; padding-left: 10px;">{itens_html}</ul>
        </div>"""


def salvar_relatorio(
    nome_arquivo: str,
    titulo_ferramenta: str,
    descricao: str,
    secoes: list[dict[str, Any]],
    estatisticas: dict[str, Any] | None = None,
) -> Path:
    """
    Gera e salva o relatório HTML no diretório de saída.

    Args:
        nome_arquivo: Nome do arquivo (sem extensão)
        titulo_ferramenta: Nome da ferramenta
        descricao: Descrição do relatório
        secoes: Seções de conteúdo
        estatisticas: Métricas de resumo

    Returns:
        Caminho completo do arquivo salvo
    """
    html = gerar_html(titulo_ferramenta, descricao, secoes, estatisticas)

    diretorio = obter_diretorio_saida()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_completo = f"{nome_arquivo}_{timestamp}.html"
    caminho = diretorio / nome_completo

    with open(caminho, "w", encoding="utf-8", errors="replace") as f:
        f.write(html)

    return caminho
