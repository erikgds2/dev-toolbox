# Changelog — dev-toolbox

Todas as mudanças notáveis neste projeto estão documentadas neste arquivo.

O formato segue [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

---

## [1.0.0] — 2026-03-15

### Adicionado

- **Menu interativo** com `rich` — interface visual para todas as ferramentas
- **Monitor de Sistema** (`system_monitor.py`)
  - Monitoramento em tempo real de CPU (por núcleo), RAM, Swap e Disco
  - Barras de progresso coloridas (verde/amarelo/vermelho)
  - Top processos por uso de CPU
  - Relatório HTML ao finalizar
- **Gerador de Senhas** (`password_gen.py`)
  - Geração criptograficamente segura com `secrets`
  - Score de força 0–100 com categorias: Fraca, Média, Forte, Muito Forte
  - Cálculo de entropia em bits
  - Configurações: comprimento, maiúsculas, minúsculas, números, símbolos
  - Exclusão de caracteres ambíguos (0, O, l, 1, |)
- **Conversor de Formatos** (`format_converter.py`)
  - Conversão bidirecional entre JSON, CSV, YAML e XML
  - Auto-detecção do formato pela extensão do arquivo
  - Suporte a conversão de diretórios inteiros
  - Prévia do conteúdo convertido no terminal
- **Verificador de URLs** (`url_checker.py`)
  - Verificação paralela com múltiplas threads configuráveis
  - Detecção de código HTTP, tempo de resposta e redirecionamentos
  - Leitura de URLs de arquivo ou argumentos
  - Classificação: rápida (< 500ms), aceitável (< 1500ms), lenta
- **Renomeador em Lote** (`batch_renamer.py`)
  - Operações: prefixo, sufixo, substituição de texto, regex, numeração
  - Modo dry-run (simulação) ativo por padrão
  - Prévia das alterações antes de aplicar
  - Filtro por extensão e busca recursiva
- **Buscador de Duplicatas** (`duplicate_finder.py`)
  - Algoritmo otimizado em dois estágios: tamanho → MD5
  - Agrupamento visual em árvore por grupo de duplicatas
  - Cálculo de espaço desperdiçado total
  - Remoção com confirmação explícita (mantém o primeiro)
- **Gerador de Relatórios HTML** (`report.py`)
  - Tema escuro: fundo `#1a1a2e`, acento `#00d4ff`, cards `#16213e`
  - Suporte a tabelas, listas, texto e badges coloridos
  - Timestamp automático e estatísticas de resumo
- **Configuração global** (`config.py`)
  - Carregamento de `config.json` com fallback para padrões
  - Criação automática do diretório de saída

### Corrigido

- Encoding UTF-8 forçado em todos os arquivos de relatório HTML
- Tratamento de erros em permissões de arquivo no buscador de duplicatas
- Conflito de nomes ao renomear arquivos com resultado idêntico
- Timeout correto ao verificar URLs com SSL inválido

### Infraestrutura

- `requirements.txt` com todas as dependências versionadas
- `.gitignore` completo para projetos Python
- README detalhado em PT-BR com exemplos de uso

---

## [0.1.0] — 2026-03-10 (Desenvolvimento Inicial)

### Adicionado

- Estrutura inicial do projeto
- Módulo de configuração base
- Esqueleto dos módulos de ferramentas
- Sistema de geração de relatórios HTML

---

[1.0.0]: https://github.com/usuario/dev-toolbox/releases/tag/v1.0.0
[0.1.0]: https://github.com/usuario/dev-toolbox/releases/tag/v0.1.0
