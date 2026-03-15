# =============================================================================
# dev-toolbox — Makefile interativo
# Uso: make <comando>
# Requer: Git Bash (Windows) ou terminal Linux/macOS
# Windows sem Git Bash: instale via https://gitforwindows.org
# =============================================================================

PYTHON = python
MODULE = src.main

.DEFAULT_GOAL := help

# -----------------------------------------------------------------------------
# Ajuda
# -----------------------------------------------------------------------------
.PHONY: help
help: ## Mostra todos os comandos disponíveis
	@echo ""
	@echo "  ██████╗ ███████╗██╗   ██╗    ████████╗ ██████╗  ██████╗ ██╗     ██████╗  ██████╗ ██╗  ██╗"
	@echo "  ██╔══██╗██╔════╝██║   ██║       ██╔══╝██╔═══██╗██╔═══██╗██║     ██╔══██╗██╔═══██╗╚██╗██╔╝"
	@echo "  ██║  ██║█████╗  ██║   ██║       ██║   ██║   ██║██║   ██║██║     ██████╔╝██║   ██║ ╚███╔╝ "
	@echo "  ██║  ██║██╔══╝  ╚██╗ ██╔╝       ██║   ██║   ██║██║   ██║██║     ██╔══██╗██║   ██║ ██╔██╗ "
	@echo "  ██████╔╝███████╗ ╚████╔╝        ██║   ╚██████╔╝╚██████╔╝███████╗██████╔╝╚██████╔╝██╔╝ ██╗"
	@echo "  ╚═════╝ ╚══════╝  ╚═══╝         ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝╚═════╝  ╚═════╝ ╚═╝  ╚═╝"
	@echo ""
	@echo "  Caixa de ferramentas para desenvolvedores — v1.0.0"
	@echo ""
	@echo "  Comandos disponíveis:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "    \033[36m%-18s\033[0m %s\n", $$1, $$2}'
	@echo ""

# -----------------------------------------------------------------------------
# Setup
# -----------------------------------------------------------------------------
.PHONY: install
install: ## Instala todas as dependências do projeto
	@echo ""
	@echo "  Instalando dependências..."
	@pip install -r requirements.txt
	@echo ""
	@echo "  Pronto! Execute 'make menu' para começar."
	@echo ""

# -----------------------------------------------------------------------------
# Menu interativo completo
# -----------------------------------------------------------------------------
.PHONY: menu
menu: ## Abre o menu interativo com todas as ferramentas
	@$(PYTHON) -m $(MODULE)

# -----------------------------------------------------------------------------
# Ferramentas individuais — com perguntas interativas
# -----------------------------------------------------------------------------

.PHONY: monitor
monitor: ## Monitor de CPU, RAM e disco em tempo real
	@echo ""
	@echo "  🖥️  Monitor de Sistema"
	@echo "  ─────────────────────────────────────────"
	@read -p "  ⏱  Por quantos segundos monitorar? (Enter = rodar até Ctrl+C): " t; \
	read -p "  📊 Gerar relatório HTML ao final? (s/N): " r; \
	echo ""; \
	cmd="$(PYTHON) -m $(MODULE) monitor"; \
	[ -n "$$t" ] && cmd="$$cmd --duracao $$t"; \
	[ "$$r" = "s" ] || [ "$$r" = "S" ] && cmd="$$cmd --relatorio"; \
	$$cmd

.PHONY: senha
senha: ## Gera senhas seguras com score de força
	@echo ""
	@echo "  🔐 Gerador de Senhas Seguras"
	@echo "  ─────────────────────────────────────────"
	@read -p "  📏 Comprimento da senha (Enter = 16): " c; \
	read -p "  🔢 Quantas senhas gerar? (Enter = 1): " q; \
	read -p "  🚫 Remover símbolos especiais? (s/N): " ns; \
	read -p "  👁  Excluir caracteres ambíguos (0,O,l,1)? (s/N): " amb; \
	read -p "  📊 Gerar relatório HTML? (s/N): " r; \
	echo ""; \
	cmd="$(PYTHON) -m $(MODULE) senha"; \
	[ -n "$$c" ] && cmd="$$cmd --comprimento $$c"; \
	[ -n "$$q" ] && cmd="$$cmd --quantidade $$q"; \
	[ "$$ns" = "s" ] || [ "$$ns" = "S" ] && cmd="$$cmd --sem-simbolos"; \
	[ "$$r" = "s" ] || [ "$$r" = "S" ] && cmd="$$cmd --relatorio"; \
	$$cmd

.PHONY: urls
urls: ## Verifica se URLs estão online (status, tempo de resposta)
	@echo ""
	@echo "  🌐 Verificador de URLs"
	@echo "  ─────────────────────────────────────────"
	@echo "  Como você quer informar as URLs?"
	@echo "    1) Arquivo de texto (uma URL por linha)"
	@echo "    2) Digitar manualmente"
	@echo ""
	@read -p "  Escolha (1 ou 2): " op; \
	echo ""; \
	if [ "$$op" = "1" ]; then \
		read -p "  📂 Caminho do arquivo: " f; \
		read -p "  📊 Gerar relatório HTML? (s/N): " r; \
		echo ""; \
		cmd="$(PYTHON) -m $(MODULE) urls --arquivo $$f"; \
		[ "$$r" = "s" ] || [ "$$r" = "S" ] && cmd="$$cmd --relatorio"; \
		$$cmd; \
	else \
		read -p "  🌐 URLs separadas por vírgula: " u; \
		read -p "  📊 Gerar relatório HTML? (s/N): " r; \
		echo ""; \
		cmd="$(PYTHON) -m $(MODULE) urls --urls \"$$u\""; \
		[ "$$r" = "s" ] || [ "$$r" = "S" ] && cmd="$$cmd --relatorio"; \
		$$cmd; \
	fi

.PHONY: converter
converter: ## Converte arquivos entre JSON, CSV, YAML e XML
	@echo ""
	@echo "  🔄 Conversor de Formatos"
	@echo "  ─────────────────────────────────────────"
	@echo "  Formatos suportados: json  csv  yaml  xml"
	@echo ""
	@read -p "  📂 Caminho do arquivo de entrada: " f; \
	read -p "  🔄 Converter para qual formato?: " p; \
	read -p "  📊 Gerar relatório HTML? (s/N): " r; \
	echo ""; \
	cmd="$(PYTHON) -m $(MODULE) converter $$f --para $$p"; \
	[ "$$r" = "s" ] || [ "$$r" = "S" ] && cmd="$$cmd --relatorio"; \
	$$cmd

.PHONY: renomear
renomear: ## Renomeia arquivos em lote com regex, prefixo e numeração
	@echo ""
	@echo "  📝 Renomeador em Lote"
	@echo "  ─────────────────────────────────────────"
	@read -p "  📁 Pasta com os arquivos: " d; \
	read -p "  ➕ Prefixo para adicionar (Enter = nenhum): " p; \
	read -p "  ➕ Sufixo para adicionar (Enter = nenhum): " s; \
	read -p "  🔢 Adicionar numeração automática? (s/N): " n; \
	read -p "  📊 Gerar relatório HTML? (s/N): " r; \
	echo ""; \
	echo "  Mostrando preview das alterações..."; \
	echo ""; \
	cmd="$(PYTHON) -m $(MODULE) renomear $$d --dry-run"; \
	[ -n "$$p" ] && cmd="$$cmd --prefixo $$p"; \
	[ -n "$$s" ] && cmd="$$cmd --sufixo $$s"; \
	[ "$$n" = "s" ] || [ "$$n" = "S" ] && cmd="$$cmd --numeracao"; \
	[ "$$r" = "s" ] || [ "$$r" = "S" ] && cmd="$$cmd --relatorio"; \
	$$cmd; \
	echo ""; \
	read -p "  ✅ Aplicar as renomeações? (s/N): " aplicar; \
	if [ "$$aplicar" = "s" ] || [ "$$aplicar" = "S" ]; then \
		cmd="$(PYTHON) -m $(MODULE) renomear $$d --aplicar"; \
		[ -n "$$p" ] && cmd="$$cmd --prefixo $$p"; \
		[ -n "$$s" ] && cmd="$$cmd --sufixo $$s"; \
		[ "$$n" = "s" ] || [ "$$n" = "S" ] && cmd="$$cmd --numeracao"; \
		[ "$$r" = "s" ] || [ "$$r" = "S" ] && cmd="$$cmd --relatorio"; \
		$$cmd; \
	else \
		echo "  Operação cancelada."; \
	fi

.PHONY: duplicatas
duplicatas: ## Encontra (e opcionalmente remove) arquivos duplicados
	@echo ""
	@echo "  🔍 Buscador de Duplicatas"
	@echo "  ─────────────────────────────────────────"
	@read -p "  📁 Pasta para escanear: " d; \
	read -p "  🔍 Busca recursiva em subpastas? (S/n): " rec; \
	read -p "  📊 Gerar relatório HTML? (s/N): " r; \
	echo ""; \
	cmd="$(PYTHON) -m $(MODULE) duplicatas $$d"; \
	[ "$$rec" = "n" ] || [ "$$rec" = "N" ] && cmd="$$cmd --sem-recursivo"; \
	[ "$$r" = "s" ] || [ "$$r" = "S" ] && cmd="$$cmd --relatorio"; \
	$$cmd; \
	echo ""; \
	read -p "  🗑  Deseja deletar os duplicatas encontrados? (s/N): " del; \
	if [ "$$del" = "s" ] || [ "$$del" = "S" ]; then \
		cmd="$(PYTHON) -m $(MODULE) duplicatas $$d --deletar"; \
		[ "$$rec" = "n" ] || [ "$$rec" = "N" ] && cmd="$$cmd --sem-recursivo"; \
		$$cmd; \
	fi

# -----------------------------------------------------------------------------
# Utilitários
# -----------------------------------------------------------------------------
.PHONY: versao
versao: ## Exibe a versão instalada do dev-toolbox
	@$(PYTHON) -m $(MODULE) versao

.PHONY: demo
demo: ## Gera screenshots de demonstração do CLI
	@echo "  Gerando screenshots..."
	@$(PYTHON) scripts/gerar_screenshots.py
	@echo "  Screenshots salvas em docs/screenshots/"

.PHONY: clean
clean: ## Remove relatórios gerados (pasta output/)
	@echo ""
	@read -p "  🗑  Remover todos os relatórios em output/? (s/N): " c; \
	if [ "$$c" = "s" ] || [ "$$c" = "S" ]; then \
		rm -rf output/ && echo "  ✅ Pasta output/ removida."; \
	else \
		echo "  Operação cancelada."; \
	fi
	@echo ""
