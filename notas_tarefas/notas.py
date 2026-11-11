"""Leitura e gravação de notas ``.md`` numa pasta escolhida pelo utilizador."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

EXTENSAO = ".md"

_CARACTERES_PROIBIDOS = set('<>:"/\\|?*')


@dataclass(frozen=True)
class Entrada:
    nome: str
    caminho: Path
    pasta: bool
    profundidade: int


def nome_valido(nome: str) -> bool:
    """Indica se o nome pode ser usado para uma nota ou pasta."""
    nome = nome.strip()
    if not nome or nome in {".", ".."} or nome.startswith("."):
        return False
    return not any(c in _CARACTERES_PROIBIDOS for c in nome)


def listar_arvore(raiz: Path) -> list[Entrada]:
    """Lista as pastas e notas de ``raiz``, em árvore.

    Cada pasta vem antes do seu conteúdo. Dentro de cada nível, a ordem é
    alfabética. Itens ocultos (nome com ponto) e ligações simbólicas são
    ignorados.
    """
    resultado: list[Entrada] = []

    def visitar(pasta: Path, profundidade: int) -> None:
        try:
            itens = sorted(pasta.iterdir(), key=lambda p: p.name.lower())
        except OSError:
            return
        for item in itens:
            if item.name.startswith(".") or item.is_symlink():
                continue
            if item.is_dir():
                resultado.append(Entrada(item.name, item, True, profundidade))
                visitar(item, profundidade + 1)
        for item in itens:
            if item.name.startswith(".") or item.is_symlink():
                continue
            if item.is_file() and item.suffix.lower() == EXTENSAO:
                resultado.append(Entrada(item.stem, item, False, profundidade))

    visitar(raiz, 0)
    return resultado


def ler_nota(caminho: Path) -> str:
    """Lê a nota tal como está no disco, sem alterar fins de linha."""
    with open(caminho, encoding="utf-8-sig", newline="") as ficheiro:
        return ficheiro.read()


def gravar_nota(caminho: Path, texto: str) -> None:
    """Grava a nota de forma segura: escreve num ficheiro temporário e depois substitui."""
    temporario = caminho.with_name(caminho.name + ".tmp")
    with open(temporario, "w", encoding="utf-8", newline="") as ficheiro:
        ficheiro.write(texto)
    os.replace(temporario, caminho)


def criar_nota(pasta: Path, nome: str) -> Path:
    """Cria uma nota vazia ``nome.md`` dentro de ``pasta`` e devolve o caminho.

    Levanta ``ValueError`` se o nome for inválido e ``FileExistsError`` se
    já existir uma nota com esse nome.
    """
    nome = nome.strip()
    if nome.lower().endswith(EXTENSAO):
        nome = nome[: -len(EXTENSAO)]
    if not nome_valido(nome):
        raise ValueError("Nome inválido. Não use / \\ : * ? \" < > | nem comece com ponto.")

    caminho = pasta / (nome + EXTENSAO)
    with open(caminho, "x", encoding="utf-8"):
        pass
    return caminho
