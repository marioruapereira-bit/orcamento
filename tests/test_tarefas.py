import unittest

from notas_tarefas.tarefas import (
    Tarefa,
    acrescentar_tarefa,
    alternar_tarefa,
    definir_opcoes,
    extrair_tarefas,
)


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



class AcrescentarTarefa(unittest.TestCase):
    def test_nota_vazia(self):
        self.assertEqual(acrescentar_tarefa("", "Pagar renda"), "- [ ] Pagar renda")

    def test_acrescenta_em_nova_linha(self):
        self.assertEqual(acrescentar_tarefa("# Nota", "Pagar renda"), "# Nota\n- [ ] Pagar renda")

    def test_nota_que_ja_termina_em_quebra(self):
        self.assertEqual(acrescentar_tarefa("# Nota\n", "Pagar renda"), "# Nota\n- [ ] Pagar renda")

    def test_a_tarefa_nova_aparece_como_aberta(self):
        novo = acrescentar_tarefa("- [x] feita", "nova")
        tarefas = extrair_tarefas(novo)
        self.assertEqual([(t.texto, t.concluida) for t in tarefas], [("feita", True), ("nova", False)])

    def test_nao_altera_o_resto_do_texto(self):
        original = "Título\n\n- [x] feita\nparágrafo"
        self.assertTrue(acrescentar_tarefa(original, "x").startswith(original + "\n"))

    def test_descricao_invalida(self):
        for descricao in ["", "   ", "linha 1\nlinha 2"]:
            with self.subTest(descricao=descricao):
                with self.assertRaises(ValueError):
                    acrescentar_tarefa("", descricao)



class Opcoes(unittest.TestCase):
    def test_sem_opcoes_usa_geral(self):
        t = extrair_tarefas("- [ ] Pagar renda")[0]
        self.assertEqual((t.elvira, t.colega, t.area), (False, None, "Geral"))

    def test_le_opcoes(self):
        t = extrair_tarefas("- [ ] Rever contrato #procurement @Ana_Silva #elvira")[0]
        self.assertEqual(t.texto, "Rever contrato")
        self.assertTrue(t.elvira)
        self.assertEqual(t.colega, "Ana Silva")
        self.assertEqual(t.area, "Procurement")

    def test_area_maiusculas_e_ancora(self):
        t = extrair_tarefas("- [x] Férias #RH ^a1b2")[0]
        self.assertEqual((t.texto, t.area, t.ancora, t.concluida), ("Férias", "RH", "a1b2", True))

    def test_nao_apanha_arroba_dentro_de_palavra(self):
        t = extrair_tarefas("- [ ] Enviar para ana@empresa.pt")[0]
        self.assertEqual(t.texto, "Enviar para ana@empresa.pt")
        self.assertIsNone(t.colega)

    def test_definir_opcoes_mantem_texto_estado_e_ancora(self):
        original = "- [x] **Rever** contrato #rh ^a1b2"
        novo = definir_opcoes(original, 0, elvira=True, colega="Ana Silva", area="Procurement")
        self.assertEqual(novo, "- [x] **Rever** contrato #elvira @Ana_Silva #procurement ^a1b2")
        t = extrair_tarefas(novo)[0]
        self.assertEqual((t.texto, t.concluida, t.ancora), ("**Rever** contrato", True, "a1b2"))

    def test_definir_opcoes_so_mexe_na_linha(self):
        texto = "Título\n- [ ] A\nparágrafo"
        novo = definir_opcoes(texto, 1, False, None, "RH")
        self.assertEqual(novo, "Título\n- [ ] A #rh\nparágrafo")

    def test_area_invalida(self):
        with self.assertRaises(ValueError):
            definir_opcoes("- [ ] A", 0, False, None, "Finanças")


if __name__ == "__main__":
    unittest.main()
