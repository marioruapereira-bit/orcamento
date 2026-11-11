"""Interface CustomTkinter: lista de notas à esquerda, editor ao centro e tarefas à direita.

As regras de negócio estão em ``tarefas``, ``notas`` e ``configuracao``.
Este módulo só liga a interface a essas funções.
"""

from __future__ import annotations

from pathlib import Path
from tkinter import TclError, filedialog, messagebox

import customtkinter as ctk

from . import agregado, configuracao, formatacao, notas
from .tarefas import Tarefa, alternar_tarefa, extrair_tarefas

LARGURA_NOTAS = 260
LARGURA_TAREFAS = 300
TODAS_PASTAS = "Todas as pastas"
RAIZ = "(raiz)"


class Aplicacao(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Notas e tarefas")
        self.geometry("1200x720")
        self.minsize(900, 500)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.pasta_raiz: Path | None = configuracao.pasta_notas()
        if self.pasta_raiz is not None and not self.pasta_raiz.is_dir():
            self.pasta_raiz = None

        self.caminho_atual: Path | None = None
        self._texto_guardado = ""
        self._eol = "\n"  # fim de linha do ficheiro aberto; o editor usa sempre "\n"
        self._tarefas_mostradas: tuple | None = None
        self._modo = "Notas"  # "Notas" ou "Tarefas"

        self._criar_lista_notas()
        self._criar_editor()
        self._criar_painel_tarefas()
        self._criar_painel_todos()

        self.bind("<Control-s>", lambda _e: self._guardar())
        self.bind("<Control-b>", lambda _e: self._aplicar_formato("negrito"))
        self.bind("<Control-i>", lambda _e: self._aplicar_formato("italico"))
        self.bind("<Control-u>", lambda _e: self._aplicar_formato("sublinhado"))
        self.protocol("WM_DELETE_WINDOW", self._fechar)

        self._atualizar_arvore()
        self._atualizar_estado()

    # ------------------------------------------------------------------
    # Construção da interface
    # ------------------------------------------------------------------

    def _criar_lista_notas(self) -> None:
        barra = ctk.CTkFrame(self, width=LARGURA_NOTAS, corner_radius=0)
        barra.grid(row=0, column=0, sticky="nsew")
        barra.grid_rowconfigure(3, weight=1)
        barra.grid_columnconfigure(0, weight=1)

        self.seletor = ctk.CTkSegmentedButton(
            barra, values=["Notas", "Tarefas"], command=self._mudar_modo
        )
        self.seletor.set("Notas")
        self.seletor.grid(row=0, column=0, padx=10, pady=(10, 4), sticky="ew")

        ctk.CTkButton(barra, text="Escolher pasta…", command=self._escolher_pasta).grid(
            row=1, column=0, padx=10, pady=4, sticky="ew"
        )
        self.botao_nova = ctk.CTkButton(barra, text="Nova nota", command=self._nova_nota)
        self.botao_nova.grid(row=2, column=0, padx=10, pady=4, sticky="ew")
        self.lista_notas = ctk.CTkScrollableFrame(barra, label_text="Notas")
        self.lista_notas.grid(row=3, column=0, padx=10, pady=(4, 10), sticky="nsew")

    def _criar_editor(self) -> None:
        painel = ctk.CTkFrame(self, fg_color="transparent")
        painel.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.painel_editor = painel
        painel.grid_rowconfigure(2, weight=1)
        painel.grid_columnconfigure(0, weight=1)

        topo =ctk.CTkFrame(painel, fg_color="transparent")
        topo.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        topo.grid_columnconfigure(0, weight=1)

        self.titulo = ctk.CTkLabel(
            topo,
            text="Nenhuma nota aberta",
            anchor="w",
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        self.titulo.grid(row=0, column=0, sticky="ew")

        self.estado = ctk.CTkLabel(topo, text="", text_color="gray")
        self.estado.grid(row=0, column=1, padx=8)

        self.botao_guardar = ctk.CTkButton(
            topo, text="Guardar (Ctrl+S)", width=140, command=self._guardar, state="disabled"
        )
        self.botao_guardar.grid(row=0, column=2)

        self.editor = ctk.CTkTextbox(
            painel,
            wrap="word",
            font=ctk.CTkFont(family="Consolas", size=14),
            state="disabled",
        )
        barra_formatos = ctk.CTkFrame(painel, fg_color="transparent")
        barra_formatos.grid(row=1, column=0, sticky="w", pady=(0, 6))
        negrito = ctk.CTkFont(size=13, weight="bold")
        ctk.CTkButton(barra_formatos, text="N", width=32, font=negrito,
                      command=lambda: self._aplicar_formato("negrito")).pack(side="left", padx=(0, 4))
        ctk.CTkButton(barra_formatos, text="I", width=32, font=ctk.CTkFont(size=13, slant="italic"),
                      command=lambda: self._aplicar_formato("italico")).pack(side="left", padx=(0, 4))
        ctk.CTkButton(barra_formatos, text="S", width=32, font=ctk.CTkFont(size=13, underline=True),
                      command=lambda: self._aplicar_formato("sublinhado")).pack(side="left", padx=(0, 12))
        for cor in formatacao.PALETA.values():
            ctk.CTkButton(barra_formatos, text="", width=24, height=24, fg_color=cor, hover_color=cor,
                          command=lambda c=cor: self._aplicar_formato("cor", c)).pack(side="left", padx=2)

        self.editor.grid(row=2, column=0, sticky="nsew")
        tk_texto = self.editor._textbox
        tk_texto.tag_configure("fmt_negrito", font=("Consolas", 14, "bold"))
        tk_texto.tag_configure("fmt_italico", font=("Consolas", 14, "italic"))
        tk_texto.tag_configure("fmt_sublinhado", underline=True)
        # Quando o texto muda, o Tk marca a flag "modified". Usamos isso para
        # atualizar o estado (por guardar) e a lista de tarefas.
        self.editor._textbox.bind("<<Modified>>", self._ao_modificar_editor)

    def _criar_painel_tarefas(self) -> None:
        painel = ctk.CTkFrame(self, width=LARGURA_TAREFAS)
        painel.grid(row=0, column=2, sticky="nsew", padx=(0, 10), pady=10)
        self.painel_tarefas = painel
        painel.grid_rowconfigure(1, weight=1)
        painel.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            painel,
            text="Tarefas da nota",
            anchor="w",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).grid(row=0, column=0, padx=10, pady=(10, 4), sticky="ew")

        self.lista_tarefas = ctk.CTkScrollableFrame(painel)
        self.lista_tarefas.grid(row=1, column=0, padx=6, pady=(0, 10), sticky="nsew")

    # ------------------------------------------------------------------
    # Acesso ao editor
    # ------------------------------------------------------------------

    def _texto_editor(self) -> str:
        return self.editor.get("1.0", "end-1c")

    def _mostrar_texto(self, texto: str, manter_cursor: bool = False) -> None:
        tk_texto = self.editor._textbox
        cursor = tk_texto.index("insert") if manter_cursor else None

        self.editor.configure(state="normal")
        self.editor.delete("1.0", "end")
        self.editor.insert("1.0", texto)
        if cursor is not None:
            tk_texto.mark_set("insert", cursor)
        tk_texto.edit_modified(False)
        self.editor.configure(state="normal" if self.caminho_atual else "disabled")
        self._realcar()

    def _realcar(self) -> None:
        """Aplica as cores, o negrito e o sublinhado do texto, sem alterar o conteúdo."""
        tk_texto = self.editor._textbox
        for nome in tk_texto.tag_names():
            if nome.startswith("fmt_"):
                tk_texto.tag_remove(nome, "1.0", "end")
        texto = self._texto_editor()
        for inicio, fim, nome in formatacao.encontrar(texto):
            if nome.startswith("fmt_cor_"):
                tk_texto.tag_configure(nome, foreground=nome[len("fmt_cor_"):])
            tk_texto.tag_add(nome, f"1.0+{inicio}c", f"1.0+{fim}c")

    def _aplicar_formato(self, nome: str, cor: str | None = None) -> None:
        """Aplica ou remove uma formatação no texto selecionado (ou no cursor)."""
        if self.caminho_atual is None:
            return
        tk_texto = self.editor._textbox
        try:
            ini_tk = tk_texto.index("sel.first")
            fim_tk = tk_texto.index("sel.last")
        except TclError:
            ini_tk = fim_tk = tk_texto.index("insert")

        if "\n" in tk_texto.get(ini_tk, fim_tk):
            messagebox.showinfo("Formatação", "Selecione texto de uma só linha.", parent=self)
            return

        texto = self._texto_editor()
        inicio = len(tk_texto.get("1.0", ini_tk))
        fim = len(tk_texto.get("1.0", fim_tk))
        abre, fecha, pode_desfazer = formatacao.marcas_de(nome, cor)
        novo, n_ini, n_fim = formatacao.alternar_marca(texto, inicio, fim, abre, fecha, pode_desfazer)

        self._mostrar_texto(novo)
        tk_texto.tag_remove("sel", "1.0", "end")
        tk_texto.tag_add("sel", f"1.0+{n_ini}c", f"1.0+{n_fim}c")
        tk_texto.mark_set("insert", f"1.0+{n_fim}c")
        tk_texto.focus_set()
        self._atualizar_estado()

    def _ao_modificar_editor(self, _evento=None) -> None:
        tk_texto = self.editor._textbox
        if tk_texto.edit_modified():
            tk_texto.edit_modified(False)  # o reset também dispara o evento; ignoramos esse
            self._atualizar_estado()

    # ------------------------------------------------------------------
    # Estado e tarefas
    # ------------------------------------------------------------------

    def _atualizar_estado(self) -> None:
        texto = self._texto_editor() if self.caminho_atual else ""
        alterado = self.caminho_atual is not None and texto != self._texto_guardado

        if self.caminho_atual is None:
            self.estado.configure(text="")
        elif alterado:
            self.estado.configure(text="Alterações por guardar", text_color=("#B5533A", "#E08B6E"))
        else:
            self.estado.configure(text="Guardado", text_color="gray")

        self.botao_guardar.configure(state="normal" if alterado else "disabled")
        self._atualizar_tarefas(texto)

    def _atualizar_tarefas(self, texto: str) -> None:
        tarefas: list[Tarefa] = extrair_tarefas(texto) if self.caminho_atual else []
        chave = (self.caminho_atual, tuple(tarefas))
        if chave == self._tarefas_mostradas:
            return
        self._tarefas_mostradas = chave

        for widget in self.lista_tarefas.winfo_children():
            widget.destroy()

        if self.caminho_atual is None:
            self._texto_vazio(self.lista_tarefas, "Abra uma nota para ver as tarefas.")
            return
        if not tarefas:
            self._texto_vazio(
                self.lista_tarefas,
                "Esta nota não tem tarefas.\nEscreva uma linha no formato:\n- [ ] texto",
            )
            return

        for tarefa in tarefas:
            caixa = ctk.CTkCheckBox(
                self.lista_tarefas,
                text=formatacao.sem_marcas(tarefa.texto),
                command=lambda i=tarefa.linha: self.after_idle(self._alternar_tarefa, i),
            )
            if tarefa.concluida:
                caixa.select()
            caixa.pack(anchor="w", padx=6, pady=4, fill="x")

    @staticmethod
    def _texto_vazio(pai, texto: str) -> None:
        ctk.CTkLabel(pai, text=texto, justify="left", anchor="w", text_color="gray").pack(
            anchor="w", padx=6, pady=6
        )

    def _alternar_tarefa(self, linha: int) -> None:
        """Conclui ou reabre a tarefa e grava a nota de imediato.

        Usa o texto atual do editor, por isso não perde alterações que ainda
        não foram guardadas noutras linhas.
        """
        if self.caminho_atual is None:
            return
        try:
            novo_texto = alternar_tarefa(self._texto_editor(), linha)
        except (IndexError, ValueError):
            self._atualizar_estado()
            return
        self._mostrar_texto(novo_texto, manter_cursor=True)
        self._gravar_texto(novo_texto)

    # ------------------------------------------------------------------
    # Abrir, guardar e fechar
    # ------------------------------------------------------------------

    def _abrir_nota(self, caminho: Path) -> None:
        if not self._descartar_alteracoes():
            return
        try:
            bruto = notas.ler_nota(caminho)
        except OSError as erro:
            messagebox.showerror("Erro ao abrir", str(erro), parent=self)
            return

        self.caminho_atual = caminho
        self._eol = "\r\n" if "\r\n" in bruto else "\n"
        texto = bruto.replace("\r\n", "\n")
        self._texto_guardado = texto
        self.titulo.configure(text=caminho.stem)
        self._mostrar_texto(texto)
        self._atualizar_arvore()
        self._atualizar_estado()

    def _fechar_nota(self) -> None:
        self.caminho_atual = None
        self._texto_guardado = ""
        self.titulo.configure(text="Nenhuma nota aberta")
        self._mostrar_texto("")
        self._atualizar_arvore()
        self._atualizar_estado()

    def _guardar(self) -> bool:
        if self.caminho_atual is None:
            return True
        return self._gravar_texto(self._texto_editor())

    def _gravar_texto(self, texto: str) -> bool:
        assert self.caminho_atual is not None
        bruto = texto.replace("\n", self._eol) if self._eol == "\r\n" else texto
        try:
            notas.gravar_nota(self.caminho_atual, bruto)
        except OSError as erro:
            messagebox.showerror("Erro ao guardar", str(erro), parent=self)
            return False
        self._texto_guardado = texto
        self._atualizar_estado()
        return True

    def _descartar_alteracoes(self) -> bool:
        """Pergunta o que fazer se a nota aberta tiver alterações.

        Devolve False se o utilizador cancelar a ação em curso.
        """
        if self.caminho_atual is None or self._texto_editor() == self._texto_guardado:
            return True
        resposta = messagebox.askyesnocancel(
            "Alterações por guardar",
            f"Guardar as alterações em «{self.caminho_atual.stem}»?",
            parent=self,
        )
        if resposta is None:
            return False
        if resposta:
            return self._guardar()
        return True

    def _fechar(self) -> None:
        if self._descartar_alteracoes():
            self.destroy()

    # ------------------------------------------------------------------
    # Lista de notas e pasta
    # ------------------------------------------------------------------

    def _atualizar_arvore(self) -> None:
        for widget in self.lista_notas.winfo_children():
            widget.destroy()

        if self.pasta_raiz is None:
            self._texto_vazio(
                self.lista_notas,
                "Ainda não há pasta escolhida.\nUse «Escolher pasta…».",
            )
            return

        entradas = notas.listar_arvore(self.pasta_raiz)
        if not entradas:
            self._texto_vazio(self.lista_notas, "A pasta não tem notas .md.\nUse «Nova nota».")
            return

        for entrada in entradas:
            recuo = "    " * entrada.profundidade
            if entrada.pasta:
                ctk.CTkLabel(
                    self.lista_notas,
                    text=f"{recuo}{entrada.nome}/",
                    anchor="w",
                    text_color="gray",
                ).pack(anchor="w", fill="x", padx=2, pady=(6, 0))
            else:
                selecionada = entrada.caminho == self.caminho_atual
                ctk.CTkButton(
                    self.lista_notas,
                    text=f"{recuo}{entrada.nome}",
                    anchor="w",
                    fg_color=("gray75", "gray30") if selecionada else "transparent",
                    text_color=("gray10", "gray90"),
                    hover_color=("gray70", "gray35"),
                    command=lambda c=entrada.caminho: self._abrir_nota(c),
                ).pack(fill="x", pady=1)

    def _escolher_pasta(self) -> None:
        escolhida = filedialog.askdirectory(title="Escolha a pasta das notas", parent=self)
        if not escolhida:
            return
        if not self._descartar_alteracoes():
            return
        self.pasta_raiz = Path(escolhida)
        configuracao.definir_pasta_notas(self.pasta_raiz)
        self._fechar_nota()
        self._atualizar_todos()

    def _nova_nota(self) -> None:
        if self.pasta_raiz is None:
            messagebox.showinfo("Nova nota", "Escolha primeiro a pasta das notas.", parent=self)
            return

        pasta = self.caminho_atual.parent if self.caminho_atual else self.pasta_raiz
        nome = ctk.CTkInputDialog(text="Nome da nova nota:", title="Nova nota").get_input()
        if not nome or not nome.strip():
            return
        if not self._descartar_alteracoes():
            return

        try:
            caminho = notas.criar_nota(pasta, nome)
        except (ValueError, FileExistsError, OSError) as erro:
            messagebox.showerror("Nova nota", str(erro), parent=self)
            return
        self._abrir_nota(caminho)

    # ------------------------------------------------------------------
    # Vista de tarefas (todas as notas)
    # ------------------------------------------------------------------

    def _criar_painel_todos(self) -> None:
        painel = ctk.CTkFrame(self, fg_color="transparent")
        painel.grid(row=0, column=1, columnspan=2, sticky="nsew", padx=10, pady=10)
        self.painel_todos = painel
        painel.grid_rowconfigure(2, weight=1)
        painel.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            painel,
            text="Tarefas de todas as notas",
            anchor="w",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).grid(row=0, column=0, sticky="ew", pady=(0, 8))

        filtros = ctk.CTkFrame(painel, fg_color="transparent")
        filtros.grid(row=1, column=0, sticky="ew", pady=(0, 8))
        filtros.grid_columnconfigure(2, weight=1)

        self.filtro_estado = ctk.CTkSegmentedButton(
            filtros,
            values=list(agregado.ESTADOS),
            command=lambda _v: self._atualizar_todos(),
        )
        self.filtro_estado.set("Por fazer")
        self.filtro_estado.grid(row=0, column=0, padx=(0, 8))

        self.filtro_pasta = ctk.CTkOptionMenu(
            filtros,
            values=[TODAS_PASTAS],
            width=170,
            command=lambda _v: self._atualizar_todos(),
        )
        self.filtro_pasta.set(TODAS_PASTAS)
        self.filtro_pasta.grid(row=0, column=1, padx=(0, 8))

        self.filtro_pesquisa = ctk.CTkEntry(filtros, placeholder_text="Pesquisar texto ou nota…")
        self.filtro_pesquisa.grid(row=0, column=2, sticky="ew")
        self.filtro_pesquisa.bind("<KeyRelease>", lambda _e: self._atualizar_todos())

        self.lista_todos = ctk.CTkScrollableFrame(painel)
        self.lista_todos.grid(row=2, column=0, sticky="nsew")

        self.contador = ctk.CTkLabel(painel, text="", anchor="w", text_color="gray")
        self.contador.grid(row=3, column=0, sticky="ew", pady=(6, 0))

        painel.grid_remove()  # só aparece quando o modo "Tarefas" está ativo

    def _mudar_modo(self, valor: str) -> None:
        self._modo = valor
        self.seletor.set(valor)
        if valor == "Tarefas":
            self.painel_editor.grid_remove()
            self.painel_tarefas.grid_remove()
            self.botao_nova.grid_remove()
            self.lista_notas.grid_remove()
            self.painel_todos.grid()
            self._atualizar_todos()
        else:
            self.painel_todos.grid_remove()
            self.painel_editor.grid()
            self.painel_tarefas.grid()
            self.botao_nova.grid()
            self.lista_notas.grid()

    def _pasta_filtro(self) -> str | None:
        valor = self.filtro_pasta.get()
        if valor == TODAS_PASTAS:
            return None
        if valor == RAIZ:
            return ""
        return valor

    def _atualizar_todos(self) -> None:
        """Recalcula a lista de tarefas de todas as notas. Só faz trabalho no modo "Tarefas"."""
        if self._modo != "Tarefas":
            return
        for widget in self.lista_todos.winfo_children():
            widget.destroy()

        if self.pasta_raiz is None:
            self._texto_vazio(self.lista_todos, "Escolha primeiro a pasta das notas.")
            self.contador.configure(text="")
            return

        # A nota aberta usa o texto do editor, para incluir alterações por guardar.
        sobrepor = {self.caminho_atual: self._texto_editor()} if self.caminho_atual else {}
        todas = agregado.recolher(self.pasta_raiz, sobrepor)

        opcoes = [TODAS_PASTAS, RAIZ] + agregado.pastas_disponiveis(todas)
        self.filtro_pasta.configure(values=opcoes)
        if self.filtro_pasta.get() not in opcoes:
            self.filtro_pasta.set(TODAS_PASTAS)

        filtradas = agregado.filtrar(
            todas,
            estado=self.filtro_estado.get(),
            pasta=self._pasta_filtro(),
            pesquisa=self.filtro_pesquisa.get(),
        )
        self.contador.configure(text=f"{len(filtradas)} de {len(todas)} tarefas")

        if not todas:
            self._texto_vazio(
                self.lista_todos,
                "Nenhuma nota tem tarefas.\nEscreva linhas no formato:\n- [ ] texto",
            )
        elif not filtradas:
            self._texto_vazio(self.lista_todos, "Nenhuma tarefa corresponde aos filtros.")
        for item in filtradas:
            self._linha_todo(item)

    def _linha_todo(self, item: agregado.TarefaDeNota) -> None:
        linha = ctk.CTkFrame(self.lista_todos, fg_color="transparent")
        linha.pack(fill="x", pady=2)

        caixa = ctk.CTkCheckBox(
            linha,
            text=formatacao.sem_marcas(item.tarefa.texto),
            command=lambda i=item: self.after_idle(self._alternar_tarefa_de, i.caminho, i.tarefa.linha),
        )
        if item.tarefa.concluida:
            caixa.select()
        caixa.pack(side="left", fill="x", expand=True, padx=(4, 8))

        destino = item.nota + (f"  ·  {item.pasta}" if item.pasta else "")
        ctk.CTkButton(
            linha,
            text=destino,
            width=160,
            anchor="e",
            fg_color="transparent",
            text_color="gray",
            hover_color=("gray75", "gray30"),
            command=lambda i=item: self._abrir_a_partir_de_todos(i.caminho, i.tarefa.linha),
        ).pack(side="right")

    def _alternar_tarefa_de(self, caminho: Path, linha: int) -> None:
        """Conclui ou reabre uma tarefa de qualquer nota, a partir da vista de tarefas."""
        if caminho == self.caminho_atual:
            self._alternar_tarefa(linha)
        else:
            try:
                bruto = notas.ler_nota(caminho)
                eol = "\r\n" if "\r\n" in bruto else "\n"
                novo = alternar_tarefa(bruto.replace("\r\n", "\n"), linha)
                notas.gravar_nota(caminho, novo.replace("\n", eol) if eol == "\r\n" else novo)
            except (OSError, ValueError, IndexError) as erro:
                messagebox.showerror("Erro ao gravar", str(erro), parent=self)
        self._atualizar_todos()

    def _abrir_a_partir_de_todos(self, caminho: Path, linha: int) -> None:
        """Abre a nota no modo "Notas" e posiciona o cursor na linha da tarefa."""
        self._mudar_modo("Notas")
        if caminho != self.caminho_atual:
            self._abrir_nota(caminho)
            if caminho != self.caminho_atual:  # o utilizador cancelou
                return
        tk_texto = self.editor._textbox
        tk_texto.mark_set("insert", f"{linha + 1}.0")
        tk_texto.see("insert")


def iniciar() -> None:
    ctk.set_appearance_mode("system")
    Aplicacao().mainloop()
