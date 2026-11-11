import tempfile
import unittest
from pathlib import Path

from notas_tarefas import configuracao


class Configuracao(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.ficheiro = Path(self._tmp.name) / "cfg.json"

    def tearDown(self):
        self._tmp.cleanup()

    def test_sem_ficheiro_devolve_none(self):
        self.assertIsNone(configuracao.pasta_notas(self.ficheiro))

    def test_guarda_e_le_pasta(self):
        configuracao.definir_pasta_notas(Path("C:/Notas"), self.ficheiro)
        self.assertEqual(configuracao.pasta_notas(self.ficheiro), Path("C:/Notas"))

    def test_preserva_outras_chaves(self):
        configuracao.guardar({"outra": 1}, self.ficheiro)
        configuracao.definir_pasta_notas(Path("D"), self.ficheiro)
        self.assertEqual(configuracao.carregar(self.ficheiro)["outra"], 1)

    def test_ficheiro_corrompido_nao_rebenta(self):
        self.ficheiro.write_text("{não é json", encoding="utf-8")
        self.assertEqual(configuracao.carregar(self.ficheiro), {})


class Colegas(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.ficheiro = Path(self._tmp.name) / "cfg.json"

    def tearDown(self):
        self._tmp.cleanup()

    def test_lista_vazia_por_defeito(self):
        self.assertEqual(configuracao.colegas(self.ficheiro), [])

    def test_adiciona_sem_duplicados_e_ordena(self):
        configuracao.adicionar_colega("Rui", self.ficheiro)
        configuracao.adicionar_colega("ana", self.ficheiro)
        lista = configuracao.adicionar_colega("Rui", self.ficheiro)
        self.assertEqual(lista, ["ana", "Rui"])

    def test_nao_perde_outras_chaves(self):
        configuracao.definir_pasta_notas(Path("D"), self.ficheiro)
        configuracao.adicionar_colega("Ana", self.ficheiro)
        self.assertEqual(configuracao.pasta_notas(self.ficheiro), Path("D"))

    def test_nome_vazio_nao_entra(self):
        self.assertEqual(configuracao.adicionar_colega("  ", self.ficheiro), [])


if __name__ == "__main__":
    unittest.main()
