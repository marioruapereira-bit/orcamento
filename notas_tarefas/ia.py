"""Estruturação de notas com o Gemini.

Se o Gemini não responder, ou se a nota for privada, o texto escrito é
guardado tal como está, como nota nova. Nada se perde.

A chave fica na variável de ambiente ``GOOGLE_API_KEY``. O modelo pode ser
escolhido na variável ``GEMINI_MODELO``.
"""

from __future__ import annotations

import json
import os
import re
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Callable

from .tarefas import extrair_tarefas

VARIAVEL_CHAVE = "GOOGLE_API_KEY"
VARIAVEL_MODELO = "GEMINI_MODELO"
MODELO_PREDEFINIDO = "gemini-2.5-flash"
URL_BASE = "https://generativelanguage.googleapis.com/v1beta/models"

INSTRUCOES = """Estrutura o texto de uma nota pessoal, em português europeu.
Devolve apenas Markdown com:
- um título (linha que começa por #);
- um resumo curto, em 2 a 4 frases;
- as secções que fizerem sentido, sem acrescentar factos que não estejam no texto;
- uma linha por tarefa, no formato exato "- [ ] texto". Mantenha as tarefas que já existem no texto.
Não escreva nada além do Markdown."""


class ErroIA(Exception):
    """Falha que faz a app guardar o texto sem estruturação."""


@dataclass(frozen=True)
class Resultado:
    texto: str
    estruturado: bool
    motivo: str  # explicação para o utilizador quando não estruturado


def chave() -> str:
    valor = os.environ.get(VARIAVEL_CHAVE, "").strip()
    if not valor:
        raise ErroIA(f"Defina a variável de ambiente {VARIAVEL_CHAVE}.")
    return valor


def e_privada(texto: str) -> bool:
    """Indica se o cabeçalho (entre linhas ``---``) tem ``privada: true``."""
    linhas = texto.replace("\r\n", "\n").split("\n")
    if not linhas or linhas[0].strip() != "---":
        return False
    for linha in linhas[1:]:
        if linha.strip() == "---":
            return False
        if re.fullmatch(r"privada\s*:\s*true\s*", linha.strip(), re.IGNORECASE):
            return True
    return False


def garantir_tarefas(original: str, saida: str) -> str:
    """Repõe no fim as tarefas do original que o modelo tenha deixado de fora."""
    presentes = {t.texto for t in extrair_tarefas(saida)}
    em_falta = []
    for linha in original.replace("\r\n", "\n").split("\n"):
        tarefas = extrair_tarefas(linha)
        if tarefas and tarefas[0].texto not in presentes:
            em_falta.append(linha.rstrip())
    if not em_falta:
        return saida
    return saida.rstrip() + "\n\n" + "\n".join(em_falta) + "\n"


def limpar_saida(saida: str, original: str) -> str:
    """Tira a cerca de código que alguns modelos acrescentam e garante as tarefas originais."""
    texto = saida.replace("\r\n", "\n").strip()
    cerca = re.fullmatch(r"```(?:markdown|md)?\s*\n(.*?)\n?```", texto, re.DOTALL)
    if cerca:
        texto = cerca.group(1).strip()
    return garantir_tarefas(original, texto)


def texto_da_resposta(dados: dict) -> str:
    candidatos = dados.get("candidates") or []
    if not candidatos:
        raise ErroIA("O Gemini não devolveu conteúdo (pode ter sido bloqueado por filtros).")
    partes = (candidatos[0].get("content") or {}).get("parts") or []
    texto = "".join(p.get("text", "") for p in partes).strip()
    if not texto:
        raise ErroIA("O Gemini devolveu uma resposta sem texto.")
    return texto


def _pedido_http(rascunho: str) -> str:
    modelo = os.environ.get(VARIAVEL_MODELO, "").strip() or MODELO_PREDEFINIDO
    url = f"{URL_BASE}/{modelo}:generateContent"
    corpo = {
        "systemInstruction": {"parts": [{"text": INSTRUCOES}]},
        "contents": [{"role": "user", "parts": [{"text": rascunho}]}],
        "generationConfig": {"temperature": 0.2},
    }
    dados = json.dumps(corpo).encode("utf-8")
    cabecalhos = {"x-goog-api-key": chave(), "Content-Type": "application/json"}

    tentativas = 3
    for n in range(tentativas):
        pedido = urllib.request.Request(url, data=dados, headers=cabecalhos, method="POST")
        try:
            with urllib.request.urlopen(pedido, timeout=60) as resposta:
                return texto_da_resposta(json.loads(resposta.read().decode("utf-8")))
        except urllib.error.HTTPError as erro:
            if erro.code in (429, 503) and n < tentativas - 1:
                time.sleep(2 * (n + 1))
                continue
            raise ErroIA(f"O Gemini respondeu com erro {erro.code}.") from erro
        except urllib.error.URLError as erro:
            raise ErroIA(f"Sem ligação ao Gemini ({erro.reason}).") from erro
    raise ErroIA("O Gemini está ocupado. Tente mais tarde.")


def estruturar(rascunho: str, pedir: Callable[[str], str] = _pedido_http) -> str:
    """Pede ao Gemini a estrutura da nota e devolve o Markdown já validado."""
    return limpar_saida(pedir(rascunho), rascunho)


def estruturar_com_recurso(
    rascunho: str, estruturador: Callable[[str], str] = estruturar
) -> Resultado:
    """Estrutura a nota, ou devolve o texto original se não for possível."""
    if e_privada(rascunho):
        return Resultado(rascunho, False, "A nota é privada e não foi enviada para o Gemini.")
    try:
        return Resultado(estruturador(rascunho), True, "")
    except ErroIA as erro:
        return Resultado(rascunho, False, f"O Gemini não respondeu: {erro}")
