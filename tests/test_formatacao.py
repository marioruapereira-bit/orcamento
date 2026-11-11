import unittest

from notas_tarefas import formatacao
from notas_tarefas.tarefas import extrair_tarefas


class Encontrar(unittest.TestCase):
    def trechos(self, texto):
        return [(texto[i:f], tag) for i, f, tag in formatacao.encontrar(texto)]

    def test_negrito(self):
        self.assertEqual(self.trechos("um **dois** três"), [("dois", "fmt_negrito")])

    def test_italico_nao_confunde_com_negrito(self):
        self.assertEqual(self.trechos("**a** e *b*"), [("a", "fmt_negrito"), ("b", "fmt_italico")])

    def test_sublinhado(self):
        self.assertEqual(self.trechos("<u>x y</u>"), [("x y", "fmt_sublinhado")])

    def test_cor(self):
        texto = 'ver <span style="color:#C0392B">aviso</span>'
        self.assertEqual(self.trechos(texto), [("aviso", "fmt_cor_#c0392b")])

    def test_formatos_aninhados(self):
        texto = "<u>**forte**</u>"
        self.assertEqual(
            sorted(self.trechos(texto)),
            sorted([("forte", "fmt_negrito"), ("**forte**", "fmt_sublinhado")]),
        )

    def test_asterisco_solto_nao_formata(self):
        self.assertEqual(formatacao.encontrar("preço * 2 e 3 * 4"), [])

    def test_nao_atravessa_linhas(self):
        self.assertEqual(formatacao.encontrar("**a\nb**"), [])


class MarcasEAlternar(unittest.TestCase):
    def test_envolve_selecao(self):
        abre, fecha, desfaz = formatacao.marcas_de("negrito")
        novo, ini, fim = formatacao.alternar_marca("olá mundo", 4, 9, abre, fecha, desfaz)
        self.assertEqual(novo, "olá **mundo**")
        self.assertEqual(novo[ini:fim], "mundo")

    def test_desfaz_quando_ja_formatado(self):
        abre, fecha, desfaz = formatacao.marcas_de("negrito")
        texto = "olá **mundo**"
        novo, ini, fim = formatacao.alternar_marca(texto, 6, 11, abre, fecha, desfaz)
        self.assertEqual(novo, "olá mundo")
        self.assertEqual(novo[ini:fim], "mundo")

    def test_cursor_sem_selecao_fica_entre_marcas(self):
        abre, fecha, desfaz = formatacao.marcas_de("italico")
        novo, ini, fim = formatacao.alternar_marca("ab", 1, 1, abre, fecha, desfaz)
        self.assertEqual(novo, "a**b")
        self.assertEqual((ini, fim), (2, 2))

    def test_italico_dentro_de_negrito_nao_desfaz_o_negrito(self):
        abre, fecha, desfaz = formatacao.marcas_de("italico")
        texto = "**x**"
        novo, _, _ = formatacao.alternar_marca(texto, 2, 3, abre, fecha, desfaz)
        self.assertNotEqual(novo, "x")

    def test_cor_envolve_com_span(self):
        abre, fecha, desfaz = formatacao.marcas_de("cor", "#2980b9")
        novo, _, _ = formatacao.alternar_marca("texto", 0, 5, abre, fecha, desfaz)
        self.assertEqual(novo, '<span style="color:#2980b9">texto</span>')

    def test_nome_desconhecido(self):
        with self.assertRaises(ValueError):
            formatacao.marcas_de("tamanho")


class SemMarcas(unittest.TestCase):
    def test_remove_todas_as_marcas(self):
        texto = '**a** *b* <u>c</u> <span style="color:#27ae60">d</span>'
        self.assertEqual(formatacao.sem_marcas(texto), "a b c d")

    def test_formatacao_nao_altera_tarefas(self):
        texto = "- [ ] **Rever** <u>contrato</u>"
        tarefa = extrair_tarefas(texto)[0]
        self.assertFalse(tarefa.concluida)
        self.assertEqual(formatacao.sem_marcas(tarefa.texto), "Rever contrato")


if __name__ == "__main__":
    unittest.main()
