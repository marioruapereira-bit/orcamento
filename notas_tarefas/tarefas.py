"""Leitura e alteração de tarefas dentro do texto de uma nota.

Uma tarefa é uma linha no formato ``- [ ] texto`` (ou ``- [x] texto``).

Todas as funções trabalham sobre texto em memória. Alterar uma tarefa mexe
apenas no carácter do estado; o resto da linha e o resto da nota ficam
exatamente iguais.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

# Início de uma tarefa: indentação opcional, "- [", o estado, "] " e texto.
# O lookahead exige texto depois do espaço, para não contar "- [ ]" vazio.
_ESTADO = re.compile(r"^(\s*- \[)([ xX])(\]\s+(?=\S))")

# Âncora no fim da linha, por exemplo "... texto ^a1b2c3".
_ANCORA = re.compile(r"\s\^([A-Za-z0-9_-]+)$")


@dataclass(frozen=True)
class Tarefa:
    linha: int  # índice da linha dentro do texto, a começar em 0
    texto: str  # texto da tarefa, sem a âncora
    concluida: bool
    ancora: str | None = None


def extrair_tarefas(texto: str) -> list[Tarefa]:
    """Devolve as tarefas do texto, pela ordem em que aparecem."""
    tarefas: list[Tarefa] = []
    for indice, linha in enumerate(texto.split("\n")):
        m = _ESTADO.match(linha)
        if not m:
            continue
        corpo = linha[m.end():].rstrip()
        ancora = None
        fim = _ANCORA.search(corpo)
        if fim:
            ancora = fim.group(1)
            corpo = corpo[: fim.start()]
        tarefas.append(
            Tarefa(
                linha=indice,
                texto=corpo.strip(),
                concluida=m.group(2) in "xX",
                ancora=ancora,
            )
        )
    return tarefas


def alternar_tarefa(texto: str, linha: int) -> str:
    """Muda o estado da tarefa na linha indicada: ``[ ]`` <-> ``[x]``.

    Só o carácter do estado muda. Qualquer outra linha fica igual.
    Levanta ``IndexError`` se a linha não existir e ``ValueError`` se a
    linha não for uma tarefa.
    """
    linhas = texto.split("\n")
    if not 0 <= linha < len(linhas):
        raise IndexError(f"Linha {linha} fora do texto.")

    original = linhas[linha]
    m = _ESTADO.match(original)
    if not m:
        raise ValueError("A linha não é uma tarefa.")

    novo_estado = " " if m.group(2) in "xX" else "x"
    inicio, fim = m.start(2), m.end(2)
    linhas[linha] = original[:inicio] + novo_estado + original[fim:]
    return "\n".join(linhas)


def acrescentar_tarefa(texto: str, descricao: str) -> str:
    """Acrescenta uma tarefa aberta no fim do texto: ``- [ ] descricao``.

    Levanta ``ValueError`` se a descrição estiver vazia ou tiver mais do que uma linha.
    """
    descricao = descricao.strip()
    if not descricao or "\n" in descricao or "\r" in descricao:
        raise ValueError("A tarefa tem de ter texto e ocupar uma só linha.")
    linha = f"- [ ] {descricao}"
    if not texto:
        return linha
    separador = "" if texto.endswith("\n") else "\n"
    return texto + separador + linha
