"""Análise determinística de tarefas conforme o contrato SDD TaskAnalyzer."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import NotRequired, TypedDict

logger = logging.getLogger(__name__)
PRIORIDADES = ("baixa", "media", "alta")
STATUS_VALIDOS = ("concluida", "pendente", "cancelada")
CAMPOS_OBRIGATORIOS = {
    "id_tarefa", "data_criacao", "data_conclusao", "prazo",
    "prioridade", "status",
}
CAMPOS_PERMITIDOS = CAMPOS_OBRIGATORIOS | {"data_inicio"}


class Tarefa(TypedDict):
    """Estrutura pública de uma tarefa."""

    id_tarefa: int
    data_criacao: datetime
    data_conclusao: datetime | None
    prazo: datetime
    prioridade: str
    status: str
    data_inicio: NotRequired[datetime | None]


class Metricas(TypedDict):
    """Métricas calculadas para um grupo de tarefas."""

    quantidade_tarefas: int
    tempo_medio_conclusao_min: float | None
    taxa_atraso_percentual: float | None


class RelatorioAnalise(TypedDict):
    """Relatório geral e agrupado por prioridade."""

    geral: Metricas
    indicadores_por_prioridade: dict[str, Metricas]


class EntradaInvalidaError(ValueError):
    """Entrada de tarefas incompatível com o contrato."""


class DataInvalidaError(EntradaInvalidaError):
    """Data, fuso horário ou cronologia incompatível com o contrato."""


class SemTarefasConcluidasError(ValueError):
    """Não existem tarefas concluídas para analisar."""


def _erro_data(tarefa_id: object, campo: str, motivo: str) -> DataInvalidaError:
    """Cria uma exceção de data com contexto útil."""
    identificacao = f"Tarefa {tarefa_id}: " if tarefa_id is not None else ""
    return DataInvalidaError(f"{identificacao}{campo}: {motivo}")


def _validar_datetime(
    valor: object, campo: str, tarefa_id: object, obrigatorio: bool = True
) -> None:
    """Valida tipo datetime e fuso UTC explícito."""
    if valor is None and not obrigatorio:
        return
    if not isinstance(valor, datetime):
        raise _erro_data(tarefa_id, campo, "deve ser um objeto datetime")
    if valor.tzinfo is None or valor.utcoffset() is None:
        raise _erro_data(tarefa_id, campo, "deve possuir fuso horário UTC")
    if valor.utcoffset() != timedelta(0):
        raise _erro_data(tarefa_id, campo, "o deslocamento deve ser UTC (+00:00)")


def _validar_tarefa(tarefa: object, ids: set[int]) -> Tarefa:
    """Valida a estrutura, os valores e a cronologia de uma tarefa.

    Args:
        tarefa: Registro a validar.
        ids: Identificadores já encontrados na lista.

    Returns:
        A tarefa validada, sem modificá-la.

    Raises:
        EntradaInvalidaError: Quando a estrutura ou os valores são inválidos.
        DataInvalidaError: Quando datas ou cronologia são inválidas.
    """
    if not isinstance(tarefa, dict):
        raise EntradaInvalidaError("Cada tarefa deve ser um dicionário")
    tarefa_id = tarefa.get("id_tarefa")
    desconhecidos = set(tarefa) - CAMPOS_PERMITIDOS
    if desconhecidos:
        campo = sorted(desconhecidos)[0]
        raise EntradaInvalidaError(f"Tarefa {tarefa_id}: campo desconhecido '{campo}'")
    ausentes = CAMPOS_OBRIGATORIOS - set(tarefa)
    if ausentes:
        campo = sorted(ausentes)[0]
        raise EntradaInvalidaError(f"Tarefa {tarefa_id}: campo obrigatório ausente '{campo}'")

    if isinstance(tarefa_id, bool) or not isinstance(tarefa_id, int) or tarefa_id <= 0:
        raise EntradaInvalidaError(
            f"Tarefa {tarefa_id}: id_tarefa deve ser inteiro maior que zero"
        )
    if tarefa_id in ids:
        raise EntradaInvalidaError(f"Tarefa {tarefa_id}: id_tarefa duplicado")
    ids.add(tarefa_id)

    for campo in ("data_criacao", "prazo"):
        _validar_datetime(tarefa[campo], campo, tarefa_id)
    _validar_datetime(tarefa.get("data_inicio"), "data_inicio", tarefa_id, False)
    _validar_datetime(tarefa["data_conclusao"], "data_conclusao", tarefa_id, False)

    prioridade = tarefa["prioridade"]
    if not isinstance(prioridade, str) or prioridade not in PRIORIDADES:
        raise EntradaInvalidaError(
            f"Tarefa {tarefa_id}: prioridade deve ser baixa, media ou alta"
        )
    status = tarefa["status"]
    if not isinstance(status, str) or status not in STATUS_VALIDOS:
        raise EntradaInvalidaError(
            f"Tarefa {tarefa_id}: status deve ser concluida, pendente ou cancelada"
        )

    criacao = tarefa["data_criacao"]
    prazo = tarefa["prazo"]
    inicio = tarefa.get("data_inicio")
    conclusao = tarefa["data_conclusao"]
    if prazo < criacao:
        raise _erro_data(tarefa_id, "prazo", "anterior à data_criacao")
    if inicio is not None and inicio < criacao:
        raise _erro_data(tarefa_id, "data_inicio", "anterior à data_criacao")
    if status == "concluida":
        if conclusao is None:
            raise _erro_data(tarefa_id, "data_conclusao", "obrigatória para tarefa concluida")
        referencia = inicio if inicio is not None else criacao
        if conclusao < referencia:
            raise _erro_data(
                tarefa_id, "data_conclusao", "anterior ao início de referência"
            )
    elif conclusao is not None:
        raise _erro_data(
            tarefa_id, "data_conclusao", "deve estar ausente ou ser None para tarefa não concluída"
        )

    logger.info("evento=tarefa_validada id_tarefa=%s", tarefa_id)
    return tarefa  # type: ignore[return-value]


def _calcular_metricas(tarefas: list[Tarefa]) -> Metricas:
    """Calcula métricas de uma lista já filtrada de tarefas concluídas."""
    quantidade = len(tarefas)
    if quantidade == 0:
        return {
            "quantidade_tarefas": 0,
            "tempo_medio_conclusao_min": None,
            "taxa_atraso_percentual": None,
        }

    duracoes: list[float] = []
    atrasadas = 0
    for tarefa in tarefas:
        referencia = tarefa.get("data_inicio") or tarefa["data_criacao"]
        conclusao = tarefa["data_conclusao"]
        assert conclusao is not None
        duracoes.append((conclusao - referencia).total_seconds() / 60)
        if conclusao > tarefa["prazo"]:
            atrasadas += 1

    return {
        "quantidade_tarefas": quantidade,
        "tempo_medio_conclusao_min": round(sum(duracoes) / quantidade, 2),
        "taxa_atraso_percentual": round(atrasadas / quantidade * 100, 2),
    }


def analisar_tarefas(tarefas: list[Tarefa]) -> RelatorioAnalise:
    """Valida tarefas e calcula métricas gerais e por prioridade.

    Args:
        tarefas: Lista de dicionários conforme o contrato Tarefa.

    Returns:
        Relatório com métricas gerais e por prioridade.

    Raises:
        EntradaInvalidaError: Para estrutura, campos, valores ou IDs inválidos.
        DataInvalidaError: Para datas, fusos ou cronologia inválidos.
        SemTarefasConcluidasError: Quando não há tarefas concluídas.
    """
    if not isinstance(tarefas, list):
        raise EntradaInvalidaError("A entrada deve ser uma lista de tarefas")

    ids: set[int] = set()
    validadas: list[Tarefa] = []
    for tarefa in tarefas:
        validadas.append(_validar_tarefa(tarefa, ids))

    concluidas = [tarefa for tarefa in validadas if tarefa["status"] == "concluida"]
    if not concluidas:
        logger.warning("evento=analise_sem_tarefas_concluidas")
        raise SemTarefasConcluidasError("Não há tarefas concluídas para análise")

    por_prioridade = {
        prioridade: _calcular_metricas(
            [tarefa for tarefa in concluidas if tarefa["prioridade"] == prioridade]
        )
        for prioridade in PRIORIDADES
    }
    logger.info("evento=analise_concluida quantidade_tarefas=%s", len(concluidas))
    return {
        "geral": _calcular_metricas(concluidas),
        "indicadores_por_prioridade": por_prioridade,
    }
