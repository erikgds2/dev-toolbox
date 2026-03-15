# Módulo de configuração global do dev-toolbox
import json
import os
from pathlib import Path
from typing import Any

# Caminho base do projeto
BASE_DIR = Path(__file__).parent.parent
CONFIG_FILE = BASE_DIR / "config.json"

# Configuração padrão
DEFAULT_CONFIG: dict[str, Any] = {
    "output_dir": "output",
    "language": "pt-BR",
    "theme": "dark",
    "version": "1.0.0",
    "auto_open_report": False,
    "max_threads": 10,
    "request_timeout": 10,
    "hash_algorithm": "md5",
}


def carregar_config() -> dict[str, Any]:
    """Carrega as configurações do arquivo config.json ou retorna padrões."""
    config = DEFAULT_CONFIG.copy()

    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                dados = json.load(f)
            config.update(dados)
        except (json.JSONDecodeError, OSError) as e:
            print(f"[Aviso] Erro ao carregar configurações: {e}. Usando padrões.")

    return config


def obter_diretorio_saida() -> Path:
    """Retorna o diretório de saída configurado, criando-o se necessário."""
    config = carregar_config()
    output_dir = Path(config.get("output_dir", "output"))

    # Se o caminho for relativo, resolve em relação à raiz do projeto
    if not output_dir.is_absolute():
        output_dir = BASE_DIR / output_dir

    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def salvar_config(nova_config: dict[str, Any]) -> bool:
    """Salva novas configurações no arquivo config.json."""
    try:
        config_atual = carregar_config()
        config_atual.update(nova_config)
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config_atual, f, indent=2, ensure_ascii=False)
        return True
    except OSError as e:
        print(f"[Erro] Não foi possível salvar configurações: {e}")
        return False


# Instância global de configuração
config = carregar_config()
