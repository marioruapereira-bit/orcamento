import unittest

from notas_tarefas.tarefas import Tarefa, alternar_tarefa, extrair_tarefas


class ExtrairTarefas(unittest.TestCase):
    def test_reconhece_abertas_e_concluidas(self):
        texto = "# Título\n- [ ] Pagar fatura\nTexto livre\n- [x] Enviar relatório\n"
        self.assertEqual(
            extrair_tarefas(texto),
            [
                Tarefa(linha=1, texto="Pagar fatura", concluida=False),
                Tarefa(linha=3, texto="Enviar relatório", concluida=True),
            ],
        )

    def test_maiusculo_X_conta_como_concluida(self):
        tarefas = extrair_tarefas("- [X] feito")
        self.assertTrue(tarefas[0].concluida)

    def test_ignora_linhas_que_nao_sao_tarefas(self):
        texto = "- item normal\n- [ ]\n-[ ] sem espaço\n[ ] sem hífen\n"
        self.assertEqual(extrair_tarefas(texto), [])

    def test_aceita_indentacao(self):
        tarefas = extrair_tarefas("  - [ ] subtarefa")
        self.assertEqual(tarefas[0].texto, "subtarefa")

    def test_le_ancora_no_fim(self):
        tarefas = extrair_tarefas("- [ ] Ligar ao banco ^a1b2c3")
        self.assertEqual(tarefas[0].texto, "Ligar ao banco")
        self.assertEqual(tarefas[0].ancora, "a1b2c3")

    def test_linha_sem_ancora(self):
        self.assertIsNone(extrair_tarefas("- [ ] simples")[0].ancora)

    def test_texto_sem_tarefas(self):
        self.assertEqual(extrair_tarefas(""), [])


class AlternarTarefa(unittest.TestCase):
    def test_marca_como_concluida(self):
        self.assertEqual(alternar_tarefa("- [ ] A", 0), "- [x] A")

    def test_desmarca(self):
        self.assertEqual(alternar_tarefa("- [x] A", 0), "- [ ] A")
        self.assertEqual(alternar_tarefa("- [X] A", 0), "- [ ] A")

    def test_altera_so_a_linha_indicada(self):
        texto = "- [ ] A\n- [ ] B\n- [ ] C"
        self.assertEqual(alternar_tarefa(texto, 1), "- [ ] A\n- [x] B\n- [ ] C")

    def test_so_muda_o_carácter_do_estado(self):
        # Espaços, acentos, âncora e fins de linha CRLF ficam como estavam.
        texto = "Nota\r\n  - [ ]   Pôr  o  café ^ab12\r\nfim"
        novo = alternar_tarefa(texto, 1)
        self.assertEqual(novo, "Nota\r\n  - [x]   Pôr  o  café ^ab12\r\nfim")
        self.assertEqual(len(novo), len(texto))

    def test_editar_outras_linhas_nao_altera_tarefas(self):
        # Mesmo texto antes e depois de uma edição noutra linha: a tarefa mantém o estado.
        original = "- [x] Feita\nparágrafo\n- [ ] Por fazer"
        editado = "- [x] Feita\nparágrafo reescrito e mais longo\n- [ ] Por fazer"
        self.assertEqual(extrair_tarefas(original)[0], extrair_tarefas(editado)[0])
        self.assertEqual(extrair_tarefas(original)[1].texto, extrair_tarefas(editado)[1].texto)

    def test_linha_inexistente(self):
        with self.assertRaises(IndexError):
            alternar_tarefa("- [ ] A", 5)

    def test_linha_que_nao_e_tarefa(self):
        with self.assertRaises(ValueError):
            alternar_tarefa("texto\n- [ ] A", 0)


if __name__ == "__main__":
    unittest.main()
