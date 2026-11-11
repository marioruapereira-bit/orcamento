import os
import unittest
from unittest import mock

from notas_tarefas import ia


class Privada(unittest.TestCase):
    def test_cabecalho_com_privada_true(self):
        self.assertTrue(ia.e_privada("---\ntítulo: x\nprivada: true\n---\ntexto"))

    def test_sem_cabecalho(self):
        self.assertFalse(ia.e_privada("privada: true\ntexto"))

    def test_privada_false(self):
        self.assertFalse(ia.e_privada("---\nprivada: false\n---\ntexto"))

    def test_flag_fora_do_cabecalho_nao_conta(self):
        self.assertFalse(ia.e_privada("---\ntítulo: x\n---\nprivada: true"))

    def test_crlf(self):
        self.assertTrue(ia.e_privada("---\r\nprivada: true\r\n---\r\n"))


class Tarefas(unittest.TestCase):
    def test_repoe_tarefas_em_falta(self):
        original = "- [ ] Pagar renda\n- [x] Ligar ao banco\nTexto"
        saida = "# Resumo\n\n- [ ] Pagar renda"
        resultado = ia.garantir_tarefas(original, saida)
        self.assertIn("- [x] Ligar ao banco", resultado)
        self.assertEqual(resultado.count("Pagar renda"), 1)

    def test_nao_mexe_se_tarefas_presentes(self):
        original = "- [ ] Pagar renda"
        saida = "# Resumo\n- [ ] Pagar renda"
        self.assertEqual(ia.garantir_tarefas(original, saida), saida)

    def test_limpa_cerca_de_codigo(self):
        saida = "```markdown\n# Título\n- [ ] A\n```"
        self.assertEqual(ia.limpar_saida(saida, "- [ ] A"), "# Título\n- [ ] A")


class RespostaGemini(unittest.TestCase):
    def test_extrai_texto(self):
        dados = {"candidates": [{"content": {"parts": [{"text": "# A"}, {"text": "\n- [ ] b"}]}}]}
        self.assertEqual(ia.texto_da_resposta(dados), "# A\n- [ ] b")

    def test_sem_candidatos(self):
        with self.assertRaises(ia.ErroIA):
            ia.texto_da_resposta({"candidates": []})

    def test_sem_texto(self):
        with self.assertRaises(ia.ErroIA):
            ia.texto_da_resposta({"candidates": [{"content": {"parts": []}}]})

    def test_chave_em_falta(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ia.ErroIA):
                ia.chave()


class ComRecurso(unittest.TestCase):
    def test_estrutura_quando_gemini_responde(self):
        resultado = ia.estruturar_com_recurso("- [ ] A", lambda t: "# Resumo\n- [ ] A")
        self.assertTrue(resultado.estruturado)
        self.assertEqual(resultado.texto, "# Resumo\n- [ ] A")

    def test_recua_para_o_texto_original_quando_falha(self):
        def falha(_):
            raise ia.ErroIA("sem ligação")

        resultado = ia.estruturar_com_recurso("rascunho", falha)
        self.assertFalse(resultado.estruturado)
        self.assertEqual(resultado.texto, "rascunho")
        self.assertIn("sem ligação", resultado.motivo)

    def test_nota_privada_nao_e_enviada(self):
        chamadas = []

        def nunca(t):
            chamadas.append(t)
            return "x"

        texto = "---\nprivada: true\n---\nsegredo"
        resultado = ia.estruturar_com_recurso(texto, nunca)
        self.assertEqual(chamadas, [])
        self.assertFalse(resultado.estruturado)
        self.assertEqual(resultado.texto, texto)

    def test_estruturar_usa_o_pedido_indicado(self):
        self.assertEqual(ia.estruturar("- [ ] A", lambda t: "# T\n- [ ] A"), "# T\n- [ ] A")


if __name__ == "__main__":
    unittest.main()
