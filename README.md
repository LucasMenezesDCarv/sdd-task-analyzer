# TaskAnalyzer — Bootcamp III

Implementação em Python do contrato SDD TaskAnalyzer da Fase 1, com validação estrita e métricas determinísticas.

## Requisitos
- Python 3.11+
- pytest para testes

## Instalação e execução
Na raiz do projeto:

```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# Linux/macOS:
# source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest tests/test_harness.py -v
```

## Estrutura
```text
sdd-task-analyzer/
├── .gitignore
├── CONTEXT_RULES.md
├── README.md
├── requirements.txt
├── specs/
│   └── task_analyzer_spec.md
├── src/
│   ├── __init__.py
│   └── task_analyzer.py
└── tests/
    └── test_harness.py
```

## Interface
A função pública é `analisar_tarefas(tarefas)`. As exceções são `EntradaInvalidaError`, `DataInvalidaError` e `SemTarefasConcluidasError`. Veja `specs/task_analyzer_spec.md`.

## Governança e homologação
A implementação foi preparada com apoio de IA e os testes são independentes da lógica de cálculo. Antes de aprovar/mesclar, o estudante deve revisar o código, executar os testes no seu ambiente, inspecionar logs e confirmar os critérios CA01–CA12.

**Atenção:** o enunciado da Fase 2 contém nomes de interface e métricas diferentes da Fase 1. A divergência está registrada na especificação; confirme com o docente se deve prevalecer o contrato já entregue ou a interface citada no enunciado da Fase 2.

## GitHub
Fluxo sugerido: `main` para versões aprovadas, `develop` para integração e `feature/*` para mudanças isoladas. Abrir PR da branch de funcionalidade para `main`, descrever alterações, testes executados, evidências e revisão humana. Não afirmar revisão independente quando o trabalho for individual.


## Fase 3 — CI/CD e Docker

O projeto utiliza GitHub Actions para executar os testes
automatizados e verificar a construção e execução da
imagem Docker.

### Construir a imagem

```bash
docker compose build
```

### Executar os testes no contêiner

```bash
docker compose run --rm test-harness
```

### Validar a configuração

```bash
docker compose config
```

### Governança de IA

O arquivo `RELATORIO_GOVERNANCA_ETICA_IA.md` documenta
os riscos, os controles e a revisão humana relacionados
ao desenvolvimento assistido por Inteligência Artificial.

### Integração contínua

Consulte as execuções do projeto:

https://github.com/LucasMenezesDCarv/sdd-task-analyzer/actions
