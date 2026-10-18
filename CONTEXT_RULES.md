# CONTEXT_RULES — TaskAnalyzer

## Contrato e governança
- `specs/task_analyzer_spec.md` é o contrato de negócio autoritativo.
- Não mudar campos, assinaturas públicas, fórmulas ou cenários sem decisão humana registrada.
- Em caso de conflito entre enunciados, registrar a divergência e solicitar decisão humana; não inventar equivalências silenciosamente.

## Regras obrigatórias
- Python 3.11 ou superior; type hints em parâmetros, retornos e estruturas.
- Seguir PEP 8 e Single Responsibility Principle.
- Usar Google style docstrings com Args, Returns e Raises quando aplicável.
- Separar validação, seleção e cálculo.
- Usar exceções específicas do contrato; não capturar exceções genéricas para esconder erros.
- Usar `logging` da biblioteca padrão para eventos, sem registrar registros completos nem gravar logs em arquivo.
- Processar somente em memória, com resultados determinísticos e sem modificar a entrada.
- Não usar o relógio atual para avaliar tarefas pendentes.
- Dependências de produção: somente biblioteca padrão. `pytest` é permitido para testes.
- Não persistir tarefas/resultados, usar serviços externos, inserir segredos ou adicionar funcionalidades fora do escopo.
- Não alterar testes esperados para fazer a implementação passar.
- Revisão e aprovação finais são responsabilidade humana.
