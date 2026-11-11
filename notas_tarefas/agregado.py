"""Tarefas de todas as notas numa só lista, com filtros.

Os filtros funcionam só com os dados das notas locais.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from . import notas
from .tarefas import Tarefa, extrair_tarefas

ESTADOS = ("Todas", "Por fazer", "Concluídas")


@dataclass(frozen=True)
class TarefaDeNota:
    tarefa: Tarefa
    caminho: Path  # ficheiro da nota
    nota: str  # nome da nota, sem extensão
    pasta: str  # pasta relativa à pasta de notas; "" se estiver na raiz


def recolher(raiz: Path, sobrepor: dict[Path, str] | None = None) -> list[TarefaDeNota]:
    """Lê todas as notas de ``raiz`` e devolve as tarefas de cada uma.

    ``sobrepor`` permite usar o texto em memória de uma nota (por exemplo,
    a nota aberta com alterações por guardar) em vez do conteúdo do disco.
    """
    sobrepor = sobrepor or {}
    resultado: list[TarefaDeNota] = []

    for entrada in notas.listar_arvore(raiz):
        if entrada.pasta:
            continue
        texto = sobrepor.get(entrada.caminho)
        if texto is None:
            try:
                texto = notas.ler_nota(entrada.caminho).replace("\r\n", "\n")
            except OSError:
                continue

        pasta = entrada.caminho.parent.relative_to(raiz).as_posix()
        pasta = "" if pasta == "." else pasta
        for tarefa in extrair_tarefas(texto):
            resultado.append(TarefaDeNota(tarefa, entrada.caminho, entrada.nome, pasta))
    return resultado


def pastas_disponiveis(lista: list[TarefaDeNota]) -> list[str]:
    """Pastas com tarefas, ordenadas, sem contar a raiz."""
    return sorted({item.pasta for item in lista if item.pasta}, key=str.lower)


def filtrar(
    lista: list[TarefaDeNota],
    estado: str = "Todas",
    pasta: str | None = None,
    pesquisa: str = "",
) -> list[TarefaDeNota]:
    """Aplica os filtros em conjunto.

    - ``estado``: "Todas", "Por fazer" ou "Concluídas".
    - ``pasta``: None para todas as pastas, "" para só a raiz, ou o nome de uma pasta.
    - ``pesquisa``: texto que tem de aparecer na tarefa ou no nome da nota.
    """
    termo = pesquisa.strip().casefold()
    resultado = []
    for item in lista:
        if estado == "Por fazer" and item.tarefa.concluida:
            continue
        if estado == "Concluídas" and not item.tarefa.concluida:
            continue
        if pasta is not None and item.pasta != pasta:
            continue
        if termo and termo not in item.tarefa.texto.casefold() and termo not in item.nota.casefold():
            continue
        resultado.append(item)
    return resultado
