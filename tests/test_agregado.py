import tempfile
import unittest
from pathlib import Path

from notas_tarefas import agregado


class Agregado(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.raiz = Path(self._tmp.name)
        (self.raiz / "Trabalho").mkdir()
        (self.raiz / "Trabalho" / "Reunião.md").write_text(
            "# Reunião\n- [ ] Rever contrato\n- [x] Enviar agenda\n", encoding="utf-8"
        )
        (self.raiz / "Compras.md").write_text("- [ ] Pilhas AA\n", encoding="utf-8")
        (self.raiz / "Sem tarefas.md").write_text("só texto\n", encoding="utf-8")

    def tearDown(self):
        self._tmp.cleanup()

    def test_recolhe_tarefas_de_todas_as_notas(self):
        lista = agregado.recolher(self.raiz)
        self.assertEqual(
            [(i.nota, i.pasta, i.tarefa.texto, i.tarefa.concluida) for i in lista],
            [
                ("Reunião", "Trabalho", "Rever contrato", False),
                ("Reunião", "Trabalho", "Enviar agenda", True),
                ("Compras", "", "Pilhas AA", False),
            ],
        )

    def test_guarda_caminho_e_linha(self):
        item = agregado.recolher(self.raiz)[1]
        self.assertEqual(item.caminho, self.raiz / "Trabalho" / "Reunião.md")
        self.assertEqual(item.tarefa.linha, 2)

    def test_sobrepor_usa_texto_em_memoria(self):
        caminho = self.raiz / "Compras.md"
        lista = agregado.recolher(self.raiz, {caminho: "- [x] Pilhas AA\n- [ ] Pão\n"})
        compras = [i for i in lista if i.nota == "Compras"]
        self.assertEqual([i.tarefa.texto for i in compras], ["Pilhas AA", "Pão"])
        self.assertTrue(compras[0].tarefa.concluida)

    def test_pastas_disponiveis(self):
        self.assertEqual(agregado.pastas_disponiveis(agregado.recolher(self.raiz)), ["Trabalho"])

    def test_filtro_por_estado(self):
        lista = agregado.recolher(self.raiz)
        self.assertEqual(len(agregado.filtrar(lista, estado="Todas")), 3)
        por_fazer = agregado.filtrar(lista, estado="Por fazer")
        self.assertEqual([i.tarefa.texto for i in por_fazer], ["Rever contrato", "Pilhas AA"])
        concluidas = agregado.filtrar(lista, estado="Concluídas")
        self.assertEqual([i.tarefa.texto for i in concluidas], ["Enviar agenda"])

    def test_filtro_por_pasta(self):
        lista = agregado.recolher(self.raiz)
        self.assertEqual(len(agregado.filtrar(lista, pasta="Trabalho")), 2)
        self.assertEqual([i.nota for i in agregado.filtrar(lista, pasta="")], ["Compras"])

    def test_pesquisa_no_texto_e_no_nome_da_nota(self):
        lista = agregado.recolher(self.raiz)
        self.assertEqual([i.tarefa.texto for i in agregado.filtrar(lista, pesquisa="CONTRATO")], ["Rever contrato"])
        self.assertEqual(len(agregado.filtrar(lista, pesquisa="reunião")), 2)

    def test_filtros_combinam_se(self):
        lista = agregado.recolher(self.raiz)
        resultado = agregado.filtrar(lista, estado="Por fazer", pasta="Trabalho", pesquisa="rever")
        self.assertEqual([i.tarefa.texto for i in resultado], ["Rever contrato"])
        self.assertEqual(agregado.filtrar(lista, estado="Concluídas", pasta=""), [])


class FiltrosDeOpcoes(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.raiz = Path(self._tmp.name)
        (self.raiz / "Plano.md").write_text(
            "- [ ] Contrato #procurement @Ana_Silva #elvira\n"
            "- [ ] Férias #rh @Rui\n"
            "- [ ] Sem opções\n",
            encoding="utf-8",
        )

    def tearDown(self):
        self._tmp.cleanup()

    def test_filtra_por_area(self):
        lista = agregado.recolher(self.raiz)
        self.assertEqual([i.tarefa.texto for i in agregado.filtrar(lista, area="RH")], ["Férias"])
        self.assertEqual([i.tarefa.texto for i in agregado.filtrar(lista, area="Geral")], ["Sem opções"])

    def test_filtra_por_colega_e_elvira(self):
        lista = agregado.recolher(self.raiz)
        self.assertEqual(agregado.colegas_disponiveis(lista), ["Ana Silva", "Rui"])
        self.assertEqual([i.tarefa.texto for i in agregado.filtrar(lista, colega="Rui")], ["Férias"])
        self.assertEqual([i.tarefa.texto for i in agregado.filtrar(lista, so_elvira=True)], ["Contrato"])

    def test_opcoes_combinam_se(self):
        lista = agregado.recolher(self.raiz)
        self.assertEqual(agregado.filtrar(lista, area="RH", so_elvira=True), [])


if __name__ == "__main__":
    unittest.main()
