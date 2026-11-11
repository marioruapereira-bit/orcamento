import os
import unittest
from unittest import mock

from notas_tarefas import airtable


def registo(id_="rec01234567890abc", **campos):
    return {"id": id_, "fields": campos}


class Formulas(unittest.TestCase):
    def test_sem_filtros(self):
        self.assertIsNone(airtable.formula_filtros())

    def test_um_filtro(self):
        self.assertEqual(airtable.formula_filtros(tema="RH"), '{Tema}="RH"')

    def test_filtros_combinados(self):
        formula = airtable.formula_filtros(tema="Manutenção", prioridade="Alta", so_aguarda=True)
        self.assertEqual(
            formula,
            'AND({Tema}="Manutenção", {Prioridade}="Alta", {Aguarda autorização da Dra. Elvira}=TRUE())',
        )

    def test_aspas_escapadas(self):
        self.assertEqual(airtable.formula_filtros(tema='a"b'), '{Tema}="a\\"b"')

    def test_ancora_com_delimitador(self):
        # "ancora:a1;" não pode apanhar "ancora:a1b2;".
        self.assertEqual(
            airtable.formula_ancora("a1"),
            'FIND("ancora:a1;", {Observações})',
        )

    def test_ancora_invalida(self):
        with self.assertRaises(ValueError):
            airtable.formula_ancora('x"); DROP')

    def test_observacoes_para(self):
        self.assertEqual(
            airtable.observacoes_para("a1b2", "Trabalho/Reunião.md"),
            "ancora:a1b2; Trabalho/Reunião.md",
        )


class Token(unittest.TestCase):
    def test_sem_variavel_levanta_erro(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(airtable.ErroAirtable):
                airtable.token()

    def test_le_variavel(self):
        with mock.patch.dict(os.environ, {airtable.VARIAVEL_TOKEN: " pat123 "}):
            self.assertEqual(airtable.token(), "pat123")

    def test_cliente_sem_token(self):
        with self.assertRaises(airtable.ErroAirtable):
            airtable.Cliente("")


class Cliente(unittest.TestCase):
    def test_listar_segue_paginas(self):
        respostas = [
            {"records": [registo(**{"Nome da Tarefa": "A"})], "offset": "p2"},
            {"records": [registo("rec11111111111111", **{"Nome da Tarefa": "B"})]},
        ]
        pedidos = []

        def pedir(metodo, url, corpo):
            pedidos.append((metodo, url))
            return respostas[len(pedidos) - 1]

        nomes = [r.nome for r in airtable.Cliente("t", pedir).listar()]
        self.assertEqual(nomes, ["A", "B"])
        self.assertEqual(len(pedidos), 2)
        self.assertIn("offset=p2", pedidos[1][1])
        self.assertIn(airtable.BASE_ID, pedidos[0][1])
        self.assertIn(airtable.TABELA_ID, pedidos[0][1])

    def test_listar_lê_campos(self):
        dados = registo(**{
            "Nome da Tarefa": "Rever contrato",
            "Status": "Por Fazer",
            "Prioridade": "Alta",
            "Tema": "Procurement",
            "Data Limite": "2026-11-20",
            "Observações": "ancora:a1; Trabalho/Reunião.md",
            "Aguarda autorização da Dra. Elvira": True,
        })
        r = airtable.registo_de(dados)
        self.assertEqual((r.nome, r.estado, r.prioridade, r.tema), ("Rever contrato", "Por Fazer", "Alta", "Procurement"))
        self.assertEqual(r.limite, "2026-11-20")
        self.assertTrue(r.aguarda)

    def test_campos_em_falta_tem_valores_por_defeito(self):
        r = airtable.registo_de(registo())
        self.assertEqual((r.nome, r.estado, r.limite), ("", "", ""))
        self.assertFalse(r.aguarda)

    def test_encontrar_por_ancora(self):
        pedidos = []

        def pedir(metodo, url, corpo):
            pedidos.append(url)
            return {"records": [registo(**{"Nome da Tarefa": "X"})]}

        achado = airtable.Cliente("t", pedir).encontrar_por_ancora("a1")
        self.assertEqual(achado.nome, "X")
        self.assertIn("filterByFormula=", pedidos[0])

    def test_encontrar_por_ancora_sem_resultados(self):
        cliente = airtable.Cliente("t", lambda m, u, c: {"records": []})
        self.assertIsNone(cliente.encontrar_por_ancora("a1"))

    def test_definir_estado_envia_patch(self):
        pedidos = []

        def pedir(metodo, url, corpo):
            pedidos.append((metodo, url, corpo))
            return {}

        airtable.Cliente("t", pedir).definir_estado("rec01234567890abc", airtable.ESTADO_CONCLUIDA)
        metodo, url, corpo = pedidos[0]
        self.assertEqual(metodo, "PATCH")
        self.assertTrue(url.endswith("/rec01234567890abc"))
        self.assertEqual(corpo, {"fields": {"Status": "Concluída"}})

    def test_definir_estado_rejeita_id_invalido(self):
        with self.assertRaises(ValueError):
            airtable.Cliente("t", lambda m, u, c: {}).definir_estado("../x", "Concluída")


if __name__ == "__main__":
    unittest.main()
