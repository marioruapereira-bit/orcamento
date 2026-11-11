# Notas e tarefas (MVP)

App pessoal para Windows: notas em Markdown e tarefas dentro dessas notas.
Os dados ficam só no PC. Não há serviços externos nesta versão.

## Requisitos

- Python 3.10 ou superior
- `pip install -r requirements.txt` (instala CustomTkinter)

## Executar

Na pasta do projeto:

```bash
python -m notas_tarefas
```

Na primeira utilização, escolha a pasta das notas com **Escolher pasta…**.
A escolha fica guardada em `%USERPROFILE%\.notas_tarefas.json`.

## Como funciona

- Cada nota é um ficheiro `.md` dentro da pasta escolhida, ou numa subpasta.
- A coluna da esquerda mostra pastas e notas. **Nova nota** cria a nota na
  mesma pasta da nota aberta (ou na pasta principal, se não houver nota aberta).
- O editor ao centro guarda com **Ctrl+S** ou com o botão **Guardar**. Ao
  fechar a app ou trocar de nota com alterações pendentes, a app pergunta.
- A coluna da direita lista as tarefas da nota aberta.

### Tarefas

Uma tarefa é uma linha no formato:

```markdown
- [ ] Pagar a fatura da luz
- [x] Enviar relatório
```

- Marcar a caixa na coluna da direita muda `[ ]` para `[x]` só nessa linha,
  e grava a nota de imediato.
- Desmarcar faz o inverso.
- Editar outras partes da nota não altera as tarefas que já lá estão.
- Linhas com âncora no fim (`... ^a1b2c3`) são lidas e mantidas tal como estão.

## Testes

Os testes cobrem a lógica das tarefas, das notas e da configuração. Não
precisam de interface gráfica:

```bash
python -m unittest
```

## Fora desta versão

Integração com Airtable, extração de tarefas por IA (API Google Gemini),
filtros, notas privadas (`privada: true`), lembretes e sincronização.
