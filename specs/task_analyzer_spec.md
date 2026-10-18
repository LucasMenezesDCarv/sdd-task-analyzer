# Especificação SDD — TaskAnalyzer

## Propósito
Calcular tempo médio de conclusão em minutos, percentual de tarefas concluídas com atraso e quantidade de tarefas consideradas, no geral e por prioridade. Processamento em memória; sem interface, persistência, banco ou serviços externos.

## Interface pública
`analisar_tarefas(tarefas: list[Tarefa]) -> RelatorioAnalise`

Tarefa: `id_tarefa: int` positivo, único e não booleano; `data_criacao: datetime`; `data_inicio: datetime | None` opcional; `data_conclusao: datetime | None`; `prazo: datetime`; `prioridade: str` (`baixa`, `media`, `alta`); `status: str` (`concluida`, `pendente`, `cancelada`). Datas devem ser objetos datetime com fuso UTC explícito e deslocamento zero. Strings de data não são convertidas.

## Validação
Rejeitar campos desconhecidos, campos obrigatórios ausentes, tipos incorretos, valores inválidos e IDs duplicados. Todas as tarefas são validadas, inclusive pendentes/canceladas. `prazo >= data_criacao`; se houver início, `data_inicio >= data_criacao`; concluídas exigem conclusão e `data_conclusao >= início de referência`; pendentes/canceladas devem omitir ou usar None em `data_conclusao`. Início após o prazo é permitido. A entrada não pode ser modificada.

## Saída
Dicionário com `geral` e `indicadores_por_prioridade`, que contém `baixa`, `media`, `alta`. Cada grupo tem `quantidade_tarefas`, `tempo_medio_conclusao_min`, `taxa_atraso_percentual`. Grupo sem concluídas: quantidade 0 e métricas None.

## Regras de cálculo
- Início de referência: `data_inicio`, ou `data_criacao` quando ausente/None.
- Duração em minutos: diferença entre conclusão e início de referência em segundos / 60.
- Atraso somente se conclusão for estritamente posterior ao prazo.
- Taxa = atrasadas / concluídas * 100.
- Calcular média geral sobre todas as tarefas concluídas, não sobre a média das prioridades.
- Arredondar apenas os resultados finais com `round(valor, 2)`.
- Sem concluídas: lançar `SemTarefasConcluidasError` com mensagem `Não há tarefas concluídas para análise`.

## Exceções
- `EntradaInvalidaError(ValueError)`: estrutura, campos, valores ou IDs inválidos.
- `DataInvalidaError(EntradaInvalidaError)`: tipo/fuso/cronologia inválidos em datas.
- `SemTarefasConcluidasError(ValueError)`: lista vazia ou nenhuma concluída.
Mensagens indicam campo, motivo e ID quando disponível.

## Cenários de aceite
CA01: dados-base geram geral 4 tarefas, média 60.00 min, atraso 25.00%; alta 2/90.00/50.00%; media 1/30.00/0.00%; baixa 1/30.00/0.00%.
CA02: conclusão anterior ao início gera DataInvalidaError.
CA03: lista vazia ou somente pendentes/canceladas gera SemTarefasConcluidasError.
CA04: somente tarefa 4; 1 tarefa, 30.00 min, 0.00%.
CA05: tarefa 1 sem início; duração desde criação, 120.00 min, 0.00%.
CA06: somente tarefa 1; alta tem 1/60.00/0.00%; media e baixa 0/None/None.
CA07: prioridade urgente gera EntradaInvalidaError.
CA08: prazo sem fuso gera DataInvalidaError.
CA09: ID duplicado gera EntradaInvalidaError.
CA10: conclusão igual ao início gera duração 0.00 e atraso 0.00%.
CA11: análise não modifica entrada.
CA12: tarefas 1, 2 e 3 geram 3 tarefas, média 70.00 min, atraso 33.33%.

## Divergência registrada para revisão humana
O enunciado da Etapa Intermediária cita `analyze_tasks`, `TaskValidationError` e métricas como `total_tarefas` e `tempo_medio_conclusao_horas`, enquanto a especificação entregue na Fase 1 define `analisar_tarefas`, três exceções específicas e métricas em minutos. Esta implementação prioriza o contrato Fase 1 para preservar CA01–CA12. A divergência deve ser confirmada com o docente antes de eventual alteração da interface.
