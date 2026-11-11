import tempfile
import unittest
from pathlib import Path

from notas_tarefas import notas


class ListarArvore(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.raiz = Path(self._tmp.name)
        (self.raiz / "Trabalho").mkdir()
        (self.raiz / "Trabalho" / "Reunião.md").write_text("x", encoding="utf-8")
        (self.raiz / "Ideias.md").write_text("x", encoding="utf-8")
        (self.raiz / "ficheiro.txt").write_text("x", encoding="utf-8")
        (self.raiz / ".oculta").mkdir()
        (self.raiz / ".oculta" / "segredo.md").write_text("x", encoding="utf-8")

    def tearDown(self):
        self._tmp.cleanup()

    def test_pastas_antes_do_conteudo_e_so_md(self):
        resultado = [(e.nome, e.pasta, e.profundidade) for e in notas.listar_arvore(self.raiz)]
        self.assertEqual(
            resultado,
            [
                ("Trabalho", True, 0),
                ("Reunião", False, 1),
                ("Ideias", False, 0),
            ],
        )

    def test_pasta_vazia(self):
        vazia = Path(tempfile.mkdtemp())
        self.assertEqual(notas.listar_arvore(vazia), [])


class LerGravar(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.pasta = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_grava_e_le_preservando_fins_de_linha(self):
        caminho = self.pasta / "n.md"
        texto = "linha 1\r\n- [ ] tarefa\r\nção\r\n"
        notas.gravar_nota(caminho, texto)
        self.assertEqual(notas.ler_nota(caminho), texto)
        self.assertFalse((self.pasta / "n.md.tmp").exists())

    def test_gravar_substitui_conteudo(self):
        caminho = self.pasta / "n.md"
        notas.gravar_nota(caminho, "antes")
        notas.gravar_nota(caminho, "depois")
        self.assertEqual(notas.ler_nota(caminho), "depois")


class CriarNota(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.pasta = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_cria_com_extensao(self):
        caminho = notas.criar_nota(self.pasta, "Compras")
        self.assertEqual(caminho, self.pasta / "Compras.md")
        self.assertTrue(caminho.exists())
        self.assertEqual(notas.ler_nota(caminho), "")

    def test_nao_duplica_extensao(self):
        self.assertEqual(notas.criar_nota(self.pasta, "Ideias.MD").name, "Ideias.md")

    def test_nao_substitui_nota_existente(self):
        notas.criar_nota(self.pasta, "A")
        with self.assertRaises(FileExistsError):
            notas.criar_nota(self.pasta, "A")

    def test_nomes_invalidos(self):
        for nome in ["", "   ", "a/b", "a:b", "..", ".oculta", "x*y"]:
            with self.subTest(nome=nome):
                with self.assertRaises(ValueError):
                    notas.criar_nota(self.pasta, nome)


if __name__ == "__main__":
    unittest.main()
