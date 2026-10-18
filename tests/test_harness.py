"""Test Harness dos cenários de aceite CA01–CA12 e validações complementares."""

from copy import deepcopy
from datetime import datetime, timezone
import pytest

from src.task_analyzer import (
    analisar_tarefas,
    EntradaInvalidaError,
    DataInvalidaError,
    SemTarefasConcluidasError,
)

UTC = timezone.utc


def dt(hora: int, minuto: int = 0) -> datetime:
    """Cria horário UTC no dia de referência dos cenários."""
    return datetime(2026, 9, 1, hora, minuto, tzinfo=UTC)


@pytest.fixture
def tarefas_ca01() -> list[dict]:
    """Fornece os seis registros definidos no cenário CA01."""
    return [
        {"id_tarefa": 1, "data_criacao": dt(8), "data_inicio": dt(9),
         "prazo": dt(10, 30), "data_conclusao": dt(10), "prioridade": "alta", "status": "concluida"},
        {"id_tarefa": 2, "data_criacao": dt(8), "data_inicio": dt(9),
         "prazo": dt(10, 30), "data_conclusao": dt(11), "prioridade": "alta", "status": "concluida"},
        {"id_tarefa": 3, "data_criacao": dt(8), "data_inicio": dt(9),
         "prazo": dt(10), "data_conclusao": dt(9, 30), "prioridade": "media", "status": "concluida"},
        {"id_tarefa": 4, "data_criacao": dt(8), "data_inicio": dt(9),
         "prazo": dt(9, 30), "data_conclusao": dt(9, 30), "prioridade": "baixa", "status": "concluida"},
        {"id_tarefa": 5, "data_criacao": dt(8), "data_inicio": None,
         "prazo": dt(12), "data_conclusao": None, "prioridade": "media", "status": "pendente"},
        {"id_tarefa": 6, "data_criacao": dt(8), "data_inicio": None,
         "prazo": dt(12), "data_conclusao": None, "prioridade": "baixa", "status": "cancelada"},
    ]


def test_CA01_analise_bem_sucedida(tarefas_ca01: list[dict]) -> None:
    relatorio = analisar_tarefas(tarefas_ca01)
    assert relatorio["geral"] == {
        "quantidade_tarefas": 4,
        "tempo_medio_conclusao_min": 60.0,
        "taxa_atraso_percentual": 25.0,
    }
    assert relatorio["indicadores_por_prioridade"]["alta"]["quantidade_tarefas"] == 2
    assert relatorio["indicadores_por_prioridade"]["alta"]["tempo_medio_conclusao_min"] == 90.0
    assert relatorio["indicadores_por_prioridade"]["alta"]["taxa_atraso_percentual"] == 50.0
    assert relatorio["indicadores_por_prioridade"]["media"]["tempo_medio_conclusao_min"] == 30.0
    assert relatorio["indicadores_por_prioridade"]["baixa"]["taxa_atraso_percentual"] == 0.0


def test_CA02_conclusao_anterior_ao_inicio(tarefas_ca01: list[dict]) -> None:
    tarefa = deepcopy(tarefas_ca01[0])
    tarefa["data_conclusao"] = dt(8, 30)
    with pytest.raises(DataInvalidaError, match="data_conclusao.*anterior ao início"):
        analisar_tarefas([tarefa])


def test_CA03_ausencia_de_concluidas(tarefas_ca01: list[dict]) -> None:
    with pytest.raises(SemTarefasConcluidasError, match="Não há tarefas concluídas para análise"):
        analisar_tarefas([])
    with pytest.raises(SemTarefasConcluidasError):
        analisar_tarefas(tarefas_ca01[4:])


def test_CA04_prazo_exato(tarefas_ca01: list[dict]) -> None:
    resultado = analisar_tarefas([tarefas_ca01[3]])["geral"]
    assert resultado["quantidade_tarefas"] == 1
    assert resultado["tempo_medio_conclusao_min"] == 30.0
    assert resultado["taxa_atraso_percentual"] == 0.0


def test_CA05_inicio_ausente(tarefas_ca01: list[dict]) -> None:
    tarefa = deepcopy(tarefas_ca01[0])
    tarefa.pop("data_inicio")
    resultado = analisar_tarefas([tarefa])["geral"]
    assert resultado["tempo_medio_conclusao_min"] == 120.0
    assert resultado["taxa_atraso_percentual"] == 0.0


def test_CA06_grupos_vazios(tarefas_ca01: list[dict]) -> None:
    relatorio = analisar_tarefas([tarefas_ca01[0]])
    assert relatorio["geral"]["tempo_medio_conclusao_min"] == 60.0
    assert relatorio["indicadores_por_prioridade"]["media"] == {
        "quantidade_tarefas": 0,
        "tempo_medio_conclusao_min": None,
        "taxa_atraso_percentual": None,
    }
    assert relatorio["indicadores_por_prioridade"]["baixa"]["quantidade_tarefas"] == 0


def test_CA07_prioridade_invalida(tarefas_ca01: list[dict]) -> None:
    tarefa = deepcopy(tarefas_ca01[0])
    tarefa["prioridade"] = "urgente"
    with pytest.raises(EntradaInvalidaError, match="prioridade"):
        analisar_tarefas([tarefa])


def test_CA08_fuso_utc_obrigatorio(tarefas_ca01: list[dict]) -> None:
    tarefa = deepcopy(tarefas_ca01[0])
    tarefa["prazo"] = datetime(2026, 9, 1, 10, 30)
    with pytest.raises(DataInvalidaError, match="prazo.*fuso horário UTC"):
        analisar_tarefas([tarefa])


def test_CA09_identificador_repetido(tarefas_ca01: list[dict]) -> None:
    with pytest.raises(EntradaInvalidaError, match="id_tarefa duplicado"):
        analisar_tarefas([tarefas_ca01[0], deepcopy(tarefas_ca01[0])])


def test_CA10_duracao_zero(tarefas_ca01: list[dict]) -> None:
    tarefa = deepcopy(tarefas_ca01[0])
    tarefa["data_conclusao"] = tarefa["data_inicio"]
    resultado = analisar_tarefas([tarefa])["geral"]
    assert resultado["tempo_medio_conclusao_min"] == 0.0
    assert resultado["taxa_atraso_percentual"] == 0.0


def test_CA11_nao_modificar_entrada(tarefas_ca01: list[dict]) -> None:
    original = deepcopy(tarefas_ca01)
    analisar_tarefas(tarefas_ca01)
    assert tarefas_ca01 == original


def test_CA12_arredondamento(tarefas_ca01: list[dict]) -> None:
    resultado = analisar_tarefas(tarefas_ca01[:3])["geral"]
    assert resultado["quantidade_tarefas"] == 3
    assert resultado["tempo_medio_conclusao_min"] == pytest.approx(70.0)
    assert resultado["taxa_atraso_percentual"] == pytest.approx(33.33)


@pytest.mark.parametrize("campo", ["data_criacao", "prazo"])
def test_datas_obrigatorias_sem_fuso_sao_rejeitadas(
    tarefas_ca01: list[dict], campo: str
) -> None:
    tarefa = deepcopy(tarefas_ca01[0])
    tarefa[campo] = datetime(2026, 9, 1, 8)
    with pytest.raises(DataInvalidaError):
        analisar_tarefas([tarefa])


def test_campo_obrigatorio_ausente(tarefas_ca01: list[dict]) -> None:
    tarefa = deepcopy(tarefas_ca01[0])
    del tarefa["prioridade"]
    with pytest.raises(EntradaInvalidaError, match="campo obrigatório ausente"):
        analisar_tarefas([tarefa])


def test_campo_desconhecido_rejeitado(tarefas_ca01: list[dict]) -> None:
    tarefa = deepcopy(tarefas_ca01[0])
    tarefa["observacao"] = "não permitido"
    with pytest.raises(EntradaInvalidaError, match="campo desconhecido"):
        analisar_tarefas([tarefa])


def test_id_booleano_rejeitado(tarefas_ca01: list[dict]) -> None:
    tarefa = deepcopy(tarefas_ca01[0])
    tarefa["id_tarefa"] = True
    with pytest.raises(EntradaInvalidaError, match="id_tarefa"):
        analisar_tarefas([tarefa])


def test_prazo_anterior_a_criacao(tarefas_ca01: list[dict]) -> None:
    tarefa = deepcopy(tarefas_ca01[0])
    tarefa["prazo"] = dt(7)
    with pytest.raises(DataInvalidaError, match="prazo.*anterior"):
        analisar_tarefas([tarefa])


def test_data_inicio_anterior_a_criacao(tarefas_ca01: list[dict]) -> None:
    tarefa = deepcopy(tarefas_ca01[0])
    tarefa["data_inicio"] = dt(7)
    with pytest.raises(DataInvalidaError, match="data_inicio.*anterior"):
        analisar_tarefas([tarefa])


def test_status_invalido(tarefas_ca01: list[dict]) -> None:
    tarefa = deepcopy(tarefas_ca01[0])
    tarefa["status"] = "finalizada"
    with pytest.raises(EntradaInvalidaError, match="status"):
        analisar_tarefas([tarefa])


def test_pendente_nao_pode_ter_conclusao(tarefas_ca01: list[dict]) -> None:
    tarefa = deepcopy(tarefas_ca01[4])
    tarefa["data_conclusao"] = dt(9)
    with pytest.raises(DataInvalidaError, match="data_conclusao"):
        analisar_tarefas([tarefa])


def test_lista_de_tipo_invalido() -> None:
    with pytest.raises(EntradaInvalidaError, match="lista"):
        analisar_tarefas("não é uma lista")  # type: ignore[arg-type]
