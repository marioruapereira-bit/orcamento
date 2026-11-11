"""Leitura e alteração de tarefas dentro do texto de uma nota.

Uma tarefa é uma linha no formato ``- [ ] texto`` (ou ``- [x] texto``).

Opções da tarefa ficam na própria linha, no fim do texto:

- ``#elvira``: precisa de validação da Dra. Elvira.
- ``@Nome``: colega responsável. Espaços no nome são escritos como ``_``.
- ``#rh``, ``#procurement`` ou ``#geral``: área. Sem marca, a área é Geral.

Todas as funções trabalham sobre texto em memória. Alterar uma tarefa mexe
apenas nessa linha; o resto da nota fica exatamente igual.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

# Início de uma tarefa: indentação opcional, "- [", o estado, "] " e texto.
# O lookahead exige texto depois do espaço, para não contar "- [ ]" vazio.
_ESTADO = re.compile(r"^(\s*- \[)([ xX])(\]\s+(?=\S))")

# Âncora no fim da linha, por exemplo "... texto ^a1b2c3".
_ANCORA = re.compile(r"\s\^([A-Za-z0-9_-]+)$")

# Opções da tarefa, escritas como palavras separadas por espaços.
_OPCAO = re.compile(r"(?:(?<=\s)|^)(#elvira|#rh|#procurement|#geral|@[^\s#@]+)(?=\s|$)", re.IGNORECASE)

AREAS = ("RH", "Procurement", "Geral")
AREA_PREDEFINIDA = "Geral"
_ELVIRA = "#elvira"


@dataclass(frozen=True)
class Tarefa:
    linha: int  # índice da linha dentro do texto, a começar em 0
    texto: str  # texto da tarefa, sem âncora nem opções
    concluida: bool
    ancora: str | None = None
    elvira: bool = False  # precisa de validação da Dra. Elvira
    colega: str | None = None  # colega responsável
    area: str = AREA_PREDEFINIDA


def _separar(corpo: str) -> tuple[str, bool, str | None, str]:
    """Separa o texto das opções. Devolve (texto, elvira, colega, área)."""
    elvira = False
    colega: str | None = None
    area = AREA_PREDEFINIDA
    for m in _OPCAO.finditer(corpo):
        opcao = m.group(1)
        if opcao.lower() == _ELVIRA:
            elvira = True
        elif opcao.startswith("@"):
            colega = opcao[1:].replace("_", " ")  # o nome mantém as maiúsculas
        else:
            area = next(a for a in AREAS if a.lower() == opcao[1:].lower())
    texto = _OPCAO.sub("", corpo)
    texto = re.sub(r"[ \t]{2,}", " ", texto).strip()
    return texto, elvira, colega, area


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
        conteudo, elvira, colega, area = _separar(corpo)
        tarefas.append(
            Tarefa(
                linha=indice,
                texto=conteudo,
                concluida=m.group(2) in "xX",
                ancora=ancora,
                elvira=elvira,
                colega=colega,
                area=area,
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


def definir_opcoes(
    texto: str, linha: int, elvira: bool, colega: str | None, area: str
) -> str:
    """Substitui as opções de uma tarefa. O texto, o estado e a âncora ficam iguais."""
    if area not in AREAS:
        raise ValueError(f"Área desconhecida: {area}")
    linhas = texto.split("\n")
    if not 0 <= linha < len(linhas):
        raise IndexError(f"Linha {linha} fora do texto.")

    original = linhas[linha]
    m = _ESTADO.match(original)
    if not m:
        raise ValueError("A linha não é uma tarefa.")

    cabeca = original[: m.end()]
    corpo = original[m.end():].rstrip()
    ancora = ""
    fim = _ANCORA.search(corpo)
    if fim:
        ancora = corpo[fim.start():]
        corpo = corpo[: fim.start()]

    conteudo, _, _, _ = _separar(corpo)
    opcoes = []
    if elvira:
        opcoes.append(_ELVIRA)
    if colega:
        opcoes.append("@" + colega.strip().replace(" ", "_"))
    opcoes.append("#" + area.lower())

    partes = " ".join(p for p in [conteudo, " ".join(opcoes)] if p)
    linhas[linha] = cabeca + partes + ancora
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
