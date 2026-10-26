
# Relatório de Governança e Ética no Uso de IA

## 1. Objetivo

Este documento registra os riscos e controles relacionados
ao uso de Inteligência Artificial no desenvolvimento do
TaskAnalyzer durante o Bootcamp III.

A IA é utilizada como apoio ao desenvolvimento, mas suas
sugestões devem ser verificadas antes de serem integradas.

## 2. Fontes de verdade

- `CONTEXT_RULES.md`: estabelece as regras de contexto.
- `specs/task_analyzer_spec.md`: define o contrato SDD.
- `src/task_analyzer.py`: contém a implementação.
- `tests/test_harness.py`: verifica os comportamentos esperados.
- `.github/workflows/tests.yml`: automatiza os testes e
  as verificações do Docker.

## 3. Riscos e controles

### Alucinações da IA

Risco: a IA pode inventar funções, atributos, exceções ou
regras de negócio não especificadas.

Controle: comparar as sugestões com o contrato SDD e
rejeitar alterações sem justificativa contratual.

### Alterações indevidas no código

Risco: uma sugestão pode modificar a interface pública
ou alterar os resultados esperados.

Controle: revisar o código e o diff do Pull Request e
executar os testes automatizados.

### Dependências não autorizadas

Risco: a IA pode sugerir bibliotecas ou funcionalidades
desnecessárias ao projeto.

Controle: conferir as dependências e preservar o escopo
definido na especificação.

### Exposição de informações

Risco: credenciais ou informações pessoais podem ser
incluídas em prompts, logs ou arquivos públicos.

Controle: não publicar senhas, tokens ou dados pessoais
e utilizar exemplos fictícios nas demonstrações.

### Confiança excessiva nos testes

Risco: interpretar os checks aprovados como garantia
absoluta de ausência de defeitos.

Controle: combinar testes automatizados com revisão
humana e análise do contrato.

## 4. Uso responsável da IA

A implementação deve preservar as regras de contexto
e a especificação SDD. A IA pode apoiar a escrita e
a revisão do código, mas não deve decidir sozinha
quais requisitos serão implementados.

Os testes e a análise do Pull Request auxiliam a verificar
se as alterações respeitam o contrato.

## 5. Docker e integração contínua

O Docker permite executar os testes em ambiente isolado.
O GitHub Actions automatiza a execução dos testes Python,
a construção da imagem e as verificações do Docker Compose.

Essas verificações tornam o processo mais reproduzível,
mas não substituem a revisão humana.

## 6. Homologação humana

Antes da integração, devem ser conferidos:

- O contrato SDD e as regras de contexto.
- As alterações apresentadas no Pull Request.
- Os resultados dos testes automatizados.
- A construção e a execução da imagem Docker.
- A configuração e a execução do Docker Compose.

## 7. Divergências de especificação

Caso o enunciado e o contrato SDD apresentem nomes,
unidades ou regras diferentes, a divergência deve ser
confirmada com o docente e documentada.

A implementação não deve alterar silenciosamente
as regras de negócio para acomodar uma interpretação
não confirmada.

## 8. Conclusão

O uso responsável de IA combina contexto explícito,
especificação, testes automatizados, rastreabilidade
e revisão humana.

A aprovação do workflow é uma evidência técnica
importante, mas a homologação final depende da análise
crítica das alterações e dos resultados.
