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

### Formatação do texto

Selecione um trecho numa linha e use os botões acima do editor, ou os atalhos:

| Botão | Atalho | Resultado no ficheiro |
|---|---|---|
| N | Ctrl+B | `**negrito**` |
| I | Ctrl+I | `*itálico*` |
| S | Ctrl+U | `<u>sublinhado</u>` |
| cor | — | `<span style="color:#c0392b">texto</span>` |

As seis cores são Vermelho, Laranja, Verde, Azul, Roxo e Cinzento. Os ficheiros
continuam legíveis noutros editores de Markdown. Na lista de tarefas, as marcas
não aparecem, só o texto.

A formatação funciona dentro de uma linha. Se selecionar mais do que uma linha, a
app avisa.

### Opções das tarefas

Cada tarefa pode ter três opções, guardadas na própria linha da nota:

- **Dra. Elvira**: marca a tarefa como precisando de validação da Dra. Elvira (`#elvira`).
- **Colega**: quem está responsável (`@Nome`). Espaços no nome são escritos como `_`.
- **Área**: RH, Procurement ou Geral (`#rh`, `#procurement`, `#geral`). Sem marca, é Geral.

Para editar, clique em **Opções** na lista de tarefas da nota. Os colegas ficam numa lista
em `%USERPROFILE%\.notas_tarefas.json`, e pode acrescentar novos no próprio diálogo.

Exemplo de linha:

```markdown
- [ ] Rever contrato #procurement @Ana_Silva #elvira
```

Na vista **Tarefas**, pode filtrar por área, por colega e pelas tarefas que precisam da
Dra. Elvira. Estes filtros combinam-se com os restantes.

### Assistente (Gemini)

No seletor **Notas / Tarefas / Assistente**, escreva o rascunho na caixa da esquerda e
clique em **Estruturar com Gemini**. A proposta aparece à direita, para corrigir
antes de guardar. Nada entra numa nota sem clicar em **Guardar proposta como nota**.

Para usar, defina a chave antes de abrir a app (no PowerShell):

```powershell
setx GOOGLE_API_KEY "a-sua-chave"
```

O modelo predefinido é `gemini-2.5-flash`. Para escolher outro, defina `GEMINI_MODELO`.

**Quando o Gemini falha**: se não houver ligação, se a chave estiver em falta ou se a API
responder com erro, o texto escrito é guardado sozinho como nota nova, sem estruturação.
A app diz o nome da nota criada. Nada se perde.

**Privacidade**: o texto das notas é enviado ao Google. Notas com `privada: true` no
cabeçalho nunca são enviadas; nesse caso o texto é guardado sem estruturação.

No nível gratuito da API, o Google pode usar os pedidos para melhorar os produtos, e
pessoas podem revê-los. No nível pago, com faturação ativa, isso não acontece.

### Vista de tarefas

No seletor **Notas / Tarefas**, no topo da coluna da esquerda, a vista
**Tarefas** junta as tarefas de todas as notas numa só lista.

- **Estado**: Todas, Por fazer ou Concluídas.
- **Pasta**: todas as pastas, só a raiz, ou uma pasta específica.
- **Pesquisa**: procura no texto da tarefa e no nome da nota.

Os filtros combinam-se entre si. Marcar uma tarefa nesta vista grava a nota
de origem. Clicar no nome da nota abre a nota no sítio da tarefa.

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

Lembretes e sincronização. As notas são ficheiros locais; só o Assistente usa a rede.
