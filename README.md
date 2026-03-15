# 🛠️ dev-toolbox

**Caixa de ferramentas para desenvolvedores e analistas** — CLI com interface rica no terminal.

[![Python](https://img.shields.io/badge/Python-3.13+-blue?logo=python)](https://python.org)
[![Rich](https://img.shields.io/badge/Rich-13.0+-purple)](https://github.com/Textualize/rich)
[![Typer](https://img.shields.io/badge/Typer-0.9+-green)](https://typer.tiangolo.com)

---

## 📋 Sumário

- [Visão Geral](#visão-geral)
- [Ferramentas](#ferramentas)
- [Instalação](#instalação)
- [Uso](#uso)
- [Configuração](#configuração)
- [Relatórios HTML](#relatórios-html)
- [Estrutura do Projeto](#estrutura-do-projeto)

---

## Visão Geral

O **dev-toolbox** é uma coleção de utilitários de linha de comando desenvolvida em Python, com interface rica no terminal usando `rich` e `typer`. Todas as ferramentas geram relatórios HTML com tema escuro ao final da execução.

---

## Ferramentas

### 🖥️ 1. Monitor de Sistema
Monitora CPU, RAM e disco em tempo real com barras de progresso coloridas e atualização automática.

```bash
python -m src.main monitor --duracao 30 --relatorio
```

**Recursos:**
- Uso de CPU por núcleo
- RAM e Swap em uso
- Espaço em disco
- Top processos por CPU
- Cores: verde (< 60%), amarelo (< 85%), vermelho (≥ 85%)

---

### 🔐 2. Gerador de Senhas
Gera senhas criptograficamente seguras com score de força de 0 a 100.

```bash
python -m src.main senha --comprimento 20 --quantidade 5 --relatorio
```

**Recursos:**
- Comprimento configurável
- Inclusão/exclusão de maiúsculas, minúsculas, números e símbolos
- Exclusão de caracteres ambíguos (0, O, l, 1, |)
- Score de força: Fraca / Média / Forte / Muito Forte
- Cálculo de entropia em bits

---

### 🔄 3. Conversor de Formatos
Converte arquivos entre JSON, CSV, YAML e XML com auto-detecção do formato.

```bash
python -m src.main converter dados.json --para yaml
python -m src.main converter dados.csv --para xml --saida saida.xml
```

**Formatos suportados:** `json`, `csv`, `yaml` (yml), `xml`

**Recursos:**
- Auto-detecção do formato pela extensão
- Conversão de arquivos individuais ou diretórios inteiros
- Prévia do resultado no terminal
- Preservação de caracteres Unicode

---

### 🌐 4. Verificador de URLs
Verifica a disponibilidade de URLs com código HTTP e tempo de resposta.

```bash
python -m src.main urls --urls "https://google.com,https://github.com" --relatorio
python -m src.main urls --arquivo minha_lista.txt --relatorio
```

**Recursos:**
- Verificação paralela com múltiplas threads
- Código de status HTTP
- Tempo de resposta em milissegundos
- Detecção de redirecionamentos
- Classificação: rápida (< 500ms), aceitável (< 1500ms), lenta

---

### 📝 5. Renomeador em Lote
Renomeia arquivos com suporte a prefixo, sufixo, substituição de texto, regex e numeração sequencial.

```bash
# Adicionar prefixo
python -m src.main renomear ./fotos --prefixo "2024_"

# Numeração sequencial (simulação)
python -m src.main renomear ./docs --numeracao --dry-run

# Aplicar com substituição
python -m src.main renomear ./arquivos --substituir "antigo:novo" --aplicar
```

**Recursos:**
- Prefixo e sufixo
- Substituição simples de texto
- Padrões regex
- Numeração sequencial com quantidade de dígitos configurável
- Mudança de extensão
- Filtro por extensão
- Modo dry-run (simulação) por padrão

---

### 🔍 6. Buscador de Duplicatas
Encontra arquivos duplicados por hash MD5 com opção de remoção automática.

```bash
python -m src.main duplicatas ./minha_pasta --recursivo --relatorio
python -m src.main duplicatas ./downloads --deletar --relatorio
```

**Recursos:**
- Otimização em dois estágios (tamanho → MD5)
- Busca recursiva opcional
- Filtro por tamanho mínimo
- Extensões a ignorar
- Cálculo de espaço desperdiçado
- Remoção com confirmação (mantém o primeiro arquivo)

---

## Instalação

### Pré-requisitos
- Python 3.13+
- pip

### Passos

```bash
# Clone ou acesse o diretório
cd dev-toolbox

# Crie e ative o ambiente virtual
python -m venv venv
source venv/bin/activate       # Linux/macOS
venv\Scripts\activate          # Windows

# Instale as dependências
pip install -r requirements.txt
```

---

## Uso

### Menu Interativo (recomendado)

```bash
python -m src.main
```

Abre o menu interativo com todas as ferramentas listadas.

### Comandos Diretos

```bash
# Monitor de sistema
python -m src.main monitor [--duracao SEGUNDOS] [--relatorio]

# Gerador de senhas
python -m src.main senha [--comprimento N] [--quantidade N] [--sem-simbolos] [--relatorio]

# Conversor de formatos
python -m src.main converter ARQUIVO --para FORMATO [--saida ARQUIVO_SAIDA] [--relatorio]

# Verificador de URLs
python -m src.main urls --urls "url1,url2" [--arquivo ARQUIVO] [--relatorio]

# Renomeador em lote
python -m src.main renomear DIRETORIO [opções] [--aplicar] [--relatorio]

# Buscador de duplicatas
python -m src.main duplicatas DIRETORIO [--deletar] [--relatorio]
```

### Ajuda

```bash
python -m src.main --help
python -m src.main monitor --help
python -m src.main senha --help
```

---

## Configuração

O arquivo `config.json` na raiz do projeto controla as configurações globais:

```json
{
  "output_dir": "output",
  "language": "pt-BR",
  "theme": "dark",
  "version": "1.0.0",
  "auto_open_report": false,
  "max_threads": 10,
  "request_timeout": 10,
  "hash_algorithm": "md5"
}
```

| Campo | Descrição | Padrão |
|-------|-----------|--------|
| `output_dir` | Diretório para relatórios HTML | `output` |
| `max_threads` | Threads para verificação de URLs | `10` |
| `request_timeout` | Timeout HTTP em segundos | `10` |
| `hash_algorithm` | Algoritmo de hash | `md5` |

---

## Relatórios HTML

Todas as ferramentas suportam a flag `--relatorio` para gerar um relatório HTML com:

- **Tema escuro** (fundo `#1a1a2e`, acento `#00d4ff`)
- Timestamp de geração
- Resumo estatístico com cartões
- Tabelas de resultados
- Badges coloridos por status

Os relatórios são salvos em `output/` com nome no formato:
```
output/nome_ferramenta_20240115_143022.html
```

---

## Estrutura do Projeto

```
dev-toolbox/
├── src/
│   ├── __init__.py
│   ├── main.py              # Ponto de entrada com menu interativo
│   ├── report.py            # Gerador de relatórios HTML (tema escuro)
│   ├── config.py            # Carregador de configuração global
│   └── tools/
│       ├── __init__.py
│       ├── system_monitor.py    # Monitor de CPU, RAM e disco
│       ├── password_gen.py      # Gerador de senhas seguras
│       ├── format_converter.py  # Conversor JSON/CSV/YAML/XML
│       ├── url_checker.py       # Verificador de URLs
│       ├── batch_renamer.py     # Renomeador em lote
│       └── duplicate_finder.py  # Buscador de duplicatas (MD5)
├── config.json
├── requirements.txt
├── README.md
├── CHANGELOG.md
└── .gitignore
```

---

## Dependências

| Pacote | Versão | Uso |
|--------|--------|-----|
| `rich` | ≥13.0.0 | Interface do terminal |
| `typer` | ≥0.9.0 | CLI e argumentos |
| `psutil` | ≥5.9.0 | Monitor de sistema |
| `pyyaml` | ≥6.0 | Conversão YAML |
| `requests` | ≥2.31.0 | Verificação de URLs |
| `lxml` | ≥4.9.0 | Parsing XML |

---

## Licença

Projeto de uso pessoal e aprendizado. Código livre para adaptação.
