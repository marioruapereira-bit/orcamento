"""Configuração da app, guardada num ficheiro JSON no perfil do utilizador."""

from __future__ import annotations

import json
from pathlib import Path

CAMINHO_PREDEFINIDO = Path.home() / ".notas_tarefas.json"


def carregar(caminho: Path = CAMINHO_PREDEFINIDO) -> dict:
    try:
        dados = json.loads(caminho.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return dados if isinstance(dados, dict) else {}


def guardar(dados: dict, caminho: Path = CAMINHO_PREDEFINIDO) -> None:
    caminho.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")


def pasta_notas(caminho: Path = CAMINHO_PREDEFINIDO) -> Path | None:
    valor = carregar(caminho).get("pasta_notas")
    return Path(valor) if isinstance(valor, str) and valor else None


def definir_pasta_notas(pasta: Path, caminho: Path = CAMINHO_PREDEFINIDO) -> None:
    dados = carregar(caminho)
    dados["pasta_notas"] = str(pasta)
    guardar(dados, caminho)


def colegas(caminho: Path = CAMINHO_PREDEFINIDO) -> list[str]:
    valor = carregar(caminho).get("colegas")
    if not isinstance(valor, list):
        return []
    return [c for c in valor if isinstance(c, str) and c.strip()]


def adicionar_colega(nome: str, caminho: Path = CAMINHO_PREDEFINIDO) -> list[str]:
    """Acrescenta um colega à lista, sem duplicados, e devolve a lista atualizada."""
    nome = nome.strip()
    lista = colegas(caminho)
    if nome and nome not in lista:
        lista.append(nome)
        lista.sort(key=str.lower)
        dados = carregar(caminho)
        dados["colegas"] = lista
        guardar(dados, caminho)
    return lista
