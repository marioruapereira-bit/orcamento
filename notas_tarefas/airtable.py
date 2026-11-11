"""Ligação à tabela Tarefas do Airtable: leitura e alteração do Status.

O token fica na variável de ambiente ``AIRTABLE_TOKEN``, nunca num ficheiro.

A ligação entre uma tarefa da nota e um registo do Airtable é feita pelo
campo Observações, no formato ``ancora:<id>; <caminho relativo da nota>``.
O ``<id>`` é a âncora ``^id`` da linha da nota.
"""

from __future__ import annotations

import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Callable

BASE_ID = "appeyU8suQJKs3OCm"
TABELA_ID = "tblMoR1KSuhXBOvqA"
URL_API = "https://api.airtable.com/v0"
VARIAVEL_TOKEN = "AIRTABLE_TOKEN"

CAMPO_NOME = "Nome da Tarefa"
CAMPO_ESTADO = "Status"
CAMPO_PRIORIDADE = "Prioridade"
CAMPO_TEMA = "Tema"
CAMPO_LIMITE = "Data Limite"
CAMPO_OBSERVACOES = "Observações"
CAMPO_ELVIRA = "Aguarda autorização da Dra. Elvira"

ESTADO_POR_FAZER = "Por Fazer"
ESTADO_CONCLUIDA = "Concluída"
TEMAS = ("RH", "Procurement", "Dra. Elvira", "Manutenção")
PRIORIDADES = ("Baixa", "Média", "Alta")

_ANCORA_VALIDA = re.compile(r"^[A-Za-z0-9_-]+$")
_ID_REGISTO = re.compile(r"^rec[A-Za-z0-9]{14}$")


class ErroAirtable(Exception):
    """Erro que pode ser mostrado ao utilizador."""


@dataclass(frozen=True)
class Registo:
    id: str
    nome: str
    estado: str
    prioridade: str
    tema: str
    limite: str
    observacoes: str
    aguarda: bool


def registo_de(dados: dict) -> Registo:
    campos = dados.get("fields", {})
    return Registo(
        id=dados["id"],
        nome=campos.get(CAMPO_NOME, ""),
        estado=campos.get(CAMPO_ESTADO, ""),
        prioridade=campos.get(CAMPO_PRIORIDADE, ""),
        tema=campos.get(CAMPO_TEMA, ""),
        limite=campos.get(CAMPO_LIMITE, ""),
        observacoes=campos.get(CAMPO_OBSERVACOES, ""),
        aguarda=bool(campos.get(CAMPO_ELVIRA, False)),
    )


def token() -> str:
    valor = os.environ.get(VARIAVEL_TOKEN, "").strip()
    if not valor:
        raise ErroAirtable(f"Defina a variável de ambiente {VARIAVEL_TOKEN} com o token do Airtable.")
    return valor


def _escapar(valor: str) -> str:
    return valor.replace("\\", "\\\\").replace('"', '\\"')


def formula_filtros(tema: str | None = None, prioridade: str | None = None, so_aguarda: bool = False) -> str | None:
    """Monta a fórmula do Airtable que combina os filtros. Devolve None se não houver filtros."""
    partes = []
    if tema:
        partes.append(f'{{{CAMPO_TEMA}}}="{_escapar(tema)}"')
    if prioridade:
        partes.append(f'{{{CAMPO_PRIORIDADE}}}="{_escapar(prioridade)}"')
    if so_aguarda:
        partes.append(f"{{{CAMPO_ELVIRA}}}=TRUE()")
    if not partes:
        return None
    return partes[0] if len(partes) == 1 else "AND(" + ", ".join(partes) + ")"


def formula_ancora(ancora: str) -> str:
    """Fórmula que encontra o registo cujas Observações começam pela âncora indicada."""
    if not _ANCORA_VALIDA.match(ancora):
        raise ValueError(f"Âncora inválida: {ancora!r}")
    return f'FIND("ancora:{ancora};", {{{CAMPO_OBSERVACOES}}})'


def observacoes_para(ancora: str, caminho_relativo: str) -> str:
    """Texto a guardar em Observações para ligar uma tarefa da nota ao registo."""
    if not _ANCORA_VALIDA.match(ancora):
        raise ValueError(f"Âncora inválida: {ancora!r}")
    return f"ancora:{ancora}; {caminho_relativo}"


def _pedido_http(metodo: str, url: str, corpo: dict | None, token_: str) -> dict:
    dados = json.dumps(corpo).encode("utf-8") if corpo is not None else None
    cabecalhos = {
        "Authorization": f"Bearer {token_}",
        "Content-Type": "application/json",
    }
    tentativas = 4
    for tentativa in range(tentativas):
        pedido = urllib.request.Request(url, data=dados, headers=cabecalhos, method=metodo)
        try:
            with urllib.request.urlopen(pedido, timeout=15) as resposta:
                return json.loads(resposta.read().decode("utf-8") or "{}")
        except urllib.error.HTTPError as erro:
            # O Airtable limita a cerca de 5 pedidos por segundo. Espera e tenta de novo.
            if erro.code == 429 and tentativa < tentativas - 1:
                time.sleep(1.1 * (tentativa + 1))
                continue
            mensagem = erro.read().decode("utf-8", "replace")
            raise ErroAirtable(f"O Airtable respondeu com erro {erro.code}: {mensagem[:200]}") from erro
        except urllib.error.URLError as erro:
            raise ErroAirtable(f"Sem ligação ao Airtable: {erro.reason}") from erro
    raise ErroAirtable("O Airtable continua a limitar os pedidos. Tente mais tarde.")


class Cliente:
    def __init__(self, token_: str, pedir: Callable[[str, str, dict | None], dict] | None = None):
        if not token_:
            raise ErroAirtable(f"Defina a variável de ambiente {VARIAVEL_TOKEN}.")
        self._pedir = pedir or (lambda m, u, c: _pedido_http(m, u, c, token_))
        self._url_tabela = f"{URL_API}/{BASE_ID}/{TABELA_ID}"

    def listar(self, formula: str | None = None) -> list[Registo]:
        """Lê todos os registos que cumprem a fórmula, ordenados pela data limite."""
        registos: list[Registo] = []
        offset: str | None = None
        while True:
            parametros = [
                ("pageSize", "100"),
                ("sort[0][field]", CAMPO_LIMITE),
                ("sort[0][direction]", "asc"),
            ]
            if formula:
                parametros.append(("filterByFormula", formula))
            if offset:
                parametros.append(("offset", offset))
            url = f"{self._url_tabela}?{urllib.parse.urlencode(parametros)}"
            dados = self._pedir("GET", url, None)
            registos.extend(registo_de(r) for r in dados.get("records", []))
            offset = dados.get("offset")
            if not offset:
                return registos

    def encontrar_por_ancora(self, ancora: str) -> Registo | None:
        encontrados = self.listar(formula_ancora(ancora))
        return encontrados[0] if encontrados else None

    def definir_estado(self, registo_id: str, estado: str) -> None:
        if not _ID_REGISTO.match(registo_id):
            raise ValueError(f"Id de registo inválido: {registo_id!r}")
        url = f"{self._url_tabela}/{registo_id}"
        self._pedir("PATCH", url, {"fields": {CAMPO_ESTADO: estado}})
