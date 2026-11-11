"""Formatação do texto das notas: negrito, itálico, sublinhado e cor.

O texto fica guardado como Markdown com um pouco de HTML, para que o
ficheiro continue legível noutros programas:

    **negrito**    *itálico*    <u>sublinhado</u>
    <span style="color:#c0392b">cor</span>

A formatação só funciona dentro de uma linha. Não afeta as tarefas, porque
só mexe no texto depois de ``- [ ] ``.
"""

from __future__ import annotations

import re

# Nome visível -> cor em hexadecimal.
PALETA: dict[str, str] = {
    "Vermelho": "#c0392b",
    "Laranja": "#d35400",
    "Verde": "#27ae60",
    "Azul": "#2980b9",
    "Roxo": "#8e44ad",
    "Cinzento": "#7f8c8d",
}

_NEGRITO = re.compile(r"\*\*(?=\S)([^\n]+?)(?<=\S)\*\*")
_ITALICO = re.compile(r"(?<![*\w])\*(?![\s*])([^\n*]+?)(?<=\S)\*(?!\*)")
_SUBLINHADO = re.compile(r"<u>([^\n]*?)</u>")
_COR = re.compile(r'<span style="color:(#[0-9a-fA-F]{6})">([^\n]*?)</span>')


def encontrar(texto: str) -> list[tuple[int, int, str]]:
    """Devolve (início, fim, nome_da_tag) de cada trecho formatado.

    ``início`` e ``fim`` são posições de carácter no texto. O nome da tag é
    usado pela interface para aplicar o estilo, por exemplo ``fmt_negrito``
    ou ``fmt_cor_#c0392b``.
    """
    marcas: list[tuple[int, int, str]] = []
    for m in _NEGRITO.finditer(texto):
        marcas.append((m.start(1), m.end(1), "fmt_negrito"))
    for m in _ITALICO.finditer(texto):
        marcas.append((m.start(1), m.end(1), "fmt_italico"))
    for m in _SUBLINHADO.finditer(texto):
        marcas.append((m.start(1), m.end(1), "fmt_sublinhado"))
    for m in _COR.finditer(texto):
        marcas.append((m.start(2), m.end(2), "fmt_cor_" + m.group(1).lower()))
    return marcas


def marcas_de(nome: str, cor: str | None = None) -> tuple[str, str, bool]:
    """Devolve (abertura, fecho, pode_desfazer) para um tipo de formatação.

    ``nome`` é "negrito", "italico", "sublinhado" ou "cor". Para "cor",
    ``cor`` é um valor da PALETA. Aplicar cor nunca desfaz, porque uma nova
    cor sobre texto colorido fica dentro da anterior.
    """
    if nome == "negrito":
        return "**", "**", True
    if nome == "italico":
        return "*", "*", True
    if nome == "sublinhado":
        return "<u>", "</u>", True
    if nome == "cor" and cor:
        return f'<span style="color:{cor}">', "</span>", False
    raise ValueError(f"Formatação desconhecida: {nome}")


def alternar_marca(
    texto: str, inicio: int, fim: int, abre: str, fecha: str, pode_desfazer: bool = True
) -> tuple[str, int, int]:
    """Aplica ou remove uma formatação no trecho ``texto[inicio:fim]``.

    Se o trecho já estiver envolvido pelas marcas, remove-as. Caso contrário,
    envolve o trecho. Devolve o novo texto e a nova seleção.
    """
    antes = texto[:inicio]
    depois = texto[fim:]
    if pode_desfazer and antes.endswith(abre) and depois.startswith(fecha):
        # Em "**" com o itálico "*" não se deve desfazer o negrito por engano.
        resto = antes[: -len(abre)]
        if not (abre == "*" and resto.endswith("*")):
            ini = inicio - len(abre)
            novo = texto[:ini] + texto[inicio:fim] + texto[fim + len(fecha) :]
            return novo, ini, fim - len(abre)

    novo = texto[:inicio] + abre + texto[inicio:fim] + fecha + texto[fim:]
    return novo, inicio + len(abre), fim + len(abre)


def sem_marcas(texto: str) -> str:
    """Texto sem as marcas de formatação, para mostrar em listas simples."""
    texto = _COR.sub(r"\2", texto)
    texto = _SUBLINHADO.sub(r"\1", texto)
    texto = _NEGRITO.sub(r"\1", texto)
    return _ITALICO.sub(r"\1", texto)
