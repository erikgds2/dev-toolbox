# Como contribuir com o dev-toolbox

Obrigado pelo interesse em contribuir! Antes de abrir uma PR, leia as orientações abaixo.

## Configurando o ambiente

```bash
git clone https://github.com/erikgds2/dev-toolbox
cd dev-toolbox
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

## Estrutura do projeto

Cada ferramenta fica em `src/tools/` como um módulo independente. Para adicionar uma nova ferramenta:

1. Crie o arquivo `src/tools/minha_ferramenta.py`
2. Exporte as funções `executar()` e opcionalmente um `app` typer
3. Registre no `FERRAMENTAS` em `src/main.py`

## Padrões de código

- Python 3.13+, type hints em tudo
- Mensagens, comentários e strings em PT-BR
- Funções públicas com docstring
- Sem print() — use `rich.console.Console`
- Teste manualmente antes de abrir PR

## Commits

Use prefixos convencionais em português:
- `feat:` nova funcionalidade
- `fix:` correção de bug
- `docs:` documentação
- `refactor:` refatoração sem mudança de comportamento
- `chore:` tarefas de manutenção

## Abrindo uma PR

- Descreva o que muda e por quê
- Se for bug, descreva como reproduzir
- Screenshots do terminal são bem-vindas
