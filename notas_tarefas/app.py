"""Interface CustomTkinter: lista de notas à esquerda, editor ao centro e tarefas à direita.

As regras de negócio estão em ``tarefas``, ``notas`` e ``configuracao``.
Este módulo só liga a interface a essas funções.
"""

from __future__ import annotations

import queue
import threading
from datetime import datetime
from pathlib import Path
from tkinter import BooleanVar, TclError, filedialog, messagebox

import customtkinter as ctk

from . import agregado, configuracao, formatacao, ia, notas
from .tarefas import (
    AREAS,
    Tarefa,
    acrescentar_tarefa,
    alternar_tarefa,
    definir_opcoes,
    extrair_tarefas,
)

LARGURA_NOTAS = 260
LARGURA_TAREFAS = 300
TODAS_PASTAS = "Todas as pastas"
TODAS_AREAS = "Todas as áreas"
TODOS_COLEGAS = "Todos os colegas"
SEM_COLEGA = "Sem colega"
RAIZ = "(raiz)"


def _tarefa_na_linha(texto: str, linha: int) -> Tarefa | None:
    return next((t for t in extrair_tarefas(texto) if t.linha == linha), None)


def _resumo_opcoes(tarefa: Tarefa) -> str:
    partes = [tarefa.area]
    if tarefa.colega:
        partes.append(tarefa.colega)
    if tarefa.elvira:
        partes.append("Dra. Elvira")
    return " · ".join(partes)


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
        self._criar_painel_assistente()

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
            barra, values=["Notas", "Tarefas", "Assistente"], command=self._mudar_modo
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
        self.lista_tarefas.grid(row=1, column=0, padx=6, pady=(0, 6), sticky="nsew")

        adicionar = ctk.CTkFrame(painel, fg_color="transparent")
        adicionar.grid(row=2, column=0, padx=6, pady=(0, 10), sticky="ew")
        adicionar.grid_columnconfigure(0, weight=1)
        self.entrada_tarefa = ctk.CTkEntry(adicionar, placeholder_text="Nova tarefa…")
        self.entrada_tarefa.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        self.entrada_tarefa.bind("<Return>", lambda _e: self._adicionar_tarefa())
        ctk.CTkButton(adicionar, text="Adicionar", width=90, command=self._adicionar_tarefa).grid(
            row=0, column=1
        )

    # ------------------------------------------------------------------
    # Acesso ao editor
    # ------------------------------------------------------------------

    def _adicionar_tarefa(self) -> None:
        """Acrescenta uma tarefa aberta no fim da nota e grava a nota."""
        if self.caminho_atual is None:
            messagebox.showinfo("Nova tarefa", "Abra uma nota primeiro.", parent=self)
            return
        descricao = self.entrada_tarefa.get().strip()
        if not descricao:
            return
        try:
            novo_texto = acrescentar_tarefa(self._texto_editor(), descricao)
        except ValueError as erro:
            messagebox.showerror("Nova tarefa", str(erro), parent=self)
            return
        self.entrada_tarefa.delete(0, "end")
        self._mostrar_texto(novo_texto)
        self._gravar_texto(novo_texto)

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
            bloco = ctk.CTkFrame(self.lista_tarefas, fg_color="transparent")
            bloco.pack(fill="x", padx=2, pady=2)
            caixa = ctk.CTkCheckBox(
                bloco,
                text=formatacao.sem_marcas(tarefa.texto),
                command=lambda i=tarefa.linha: self.after_idle(self._alternar_tarefa, i),
            )
            if tarefa.concluida:
                caixa.select()
            caixa.pack(anchor="w", padx=4, pady=(2, 0), fill="x")
            opcoes = ctk.CTkFrame(bloco, fg_color="transparent")
            opcoes.pack(fill="x", padx=(28, 4))
            ctk.CTkLabel(
                opcoes, text=_resumo_opcoes(tarefa), text_color="gray",
                font=ctk.CTkFont(size=11), anchor="w",
            ).pack(side="left")
            ctk.CTkButton(
                opcoes, text="Opções", width=70, height=22,
                command=lambda i=tarefa.linha: self.after_idle(self._editar_opcoes, i),
            ).pack(side="right")

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

        self.filtro_area = ctk.CTkOptionMenu(
            filtros,
            values=[TODAS_AREAS, *AREAS],
            width=170,
            command=lambda _v: self._atualizar_todos(),
        )
        self.filtro_area.set(TODAS_AREAS)
        self.filtro_area.grid(row=1, column=0, padx=(0, 8), pady=(8, 0), sticky="w")

        self.filtro_colega = ctk.CTkOptionMenu(
            filtros,
            values=[TODOS_COLEGAS],
            width=170,
            command=lambda _v: self._atualizar_todos(),
        )
        self.filtro_colega.set(TODOS_COLEGAS)
        self.filtro_colega.grid(row=1, column=1, padx=(0, 8), pady=(8, 0), sticky="w")

        self.filtro_elvira = ctk.CTkCheckBox(
            filtros,
            text="Só as que precisam da Dra. Elvira",
            command=self._atualizar_todos,
        )
        self.filtro_elvira.grid(row=1, column=2, pady=(8, 0), sticky="w")

        self.lista_todos = ctk.CTkScrollableFrame(painel)
        self.lista_todos.grid(row=2, column=0, sticky="nsew")

        self.contador = ctk.CTkLabel(painel, text="", anchor="w", text_color="gray")
        self.contador.grid(row=3, column=0, sticky="ew", pady=(6, 0))

        painel.grid_remove()  # só aparece quando o modo "Tarefas" está ativo

    @staticmethod
    def _mostrar(widget, visivel: bool) -> None:
        if visivel:
            widget.grid()
        else:
            widget.grid_remove()

    def _mudar_modo(self, valor: str) -> None:
        self._modo = valor
        self.seletor.set(valor)
        self._mostrar(self.painel_editor, valor == "Notas")
        self._mostrar(self.painel_tarefas, valor == "Notas")
        self._mostrar(self.botao_nova, valor == "Notas")
        self._mostrar(self.lista_notas, valor == "Notas")
        self._mostrar(self.painel_todos, valor == "Tarefas")
        self._mostrar(self.painel_assistente, valor == "Assistente")
        if valor == "Tarefas":
            self._atualizar_todos()

    # ------------------------------------------------------------------
    # Assistente (Gemini)
    # ------------------------------------------------------------------

    def _criar_painel_assistente(self) -> None:
        painel = ctk.CTkFrame(self, fg_color="transparent")
        painel.grid(row=0, column=1, columnspan=2, sticky="nsew", padx=10, pady=10)
        self.painel_assistente = painel
        painel.grid_columnconfigure(0, weight=1)
        painel.grid_columnconfigure(1, weight=1)
        painel.grid_rowconfigure(3, weight=1)

        ctk.CTkLabel(
            painel, text="Assistente", anchor="w", font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 8))

        topo = ctk.CTkFrame(painel, fg_color="transparent")
        topo.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 8))
        topo.grid_columnconfigure(0, weight=1)
        self.entrada_nome = ctk.CTkEntry(topo, placeholder_text="Nome da nota (opcional)")
        self.entrada_nome.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self.botao_estruturar = ctk.CTkButton(
            topo, text="Estruturar com Gemini", command=self._estruturar_rascunho
        )
        self.botao_estruturar.grid(row=0, column=1, padx=(0, 8))
        ctk.CTkButton(topo, text="Guardar sem IA", command=self._guardar_rascunho_sem_ia).grid(
            row=0, column=2
        )

        ctk.CTkLabel(painel, text="Rascunho", anchor="w", text_color="gray").grid(
            row=2, column=0, sticky="ew"
        )
        ctk.CTkLabel(
            painel,
            text="Proposta estruturada (pode corrigir antes de guardar)",
            anchor="w",
            text_color="gray",
        ).grid(row=2, column=1, sticky="ew")

        self.rascunho = ctk.CTkTextbox(painel, wrap="word", font=ctk.CTkFont(family="Consolas", size=14))
        self.rascunho.grid(row=3, column=0, sticky="nsew", padx=(0, 6))
        self.previa = ctk.CTkTextbox(painel, wrap="word", font=ctk.CTkFont(family="Consolas", size=14))
        self.previa.grid(row=3, column=1, sticky="nsew", padx=(6, 0))

        rodape = ctk.CTkFrame(painel, fg_color="transparent")
        rodape.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(8, 0))
        rodape.grid_columnconfigure(0, weight=1)
        self.estado_assistente = ctk.CTkLabel(
            rodape, text="", anchor="w", justify="left", text_color="gray", wraplength=640
        )
        self.estado_assistente.grid(row=0, column=0, sticky="ew")
        self.botao_guardar_previa = ctk.CTkButton(
            rodape, text="Guardar proposta como nota", state="disabled", command=self._guardar_previa
        )
        self.botao_guardar_previa.grid(row=0, column=1)

        painel.grid_remove()

    def _definir_estado_assistente(self, mensagem: str) -> None:
        self.estado_assistente.configure(text=mensagem)

    def _criar_nota_automatica(self, texto: str) -> Path | None:
        """Cria uma nota nova com o texto. Se o nome já existir ou for inválido, usa outro."""
        if self.pasta_raiz is None:
            messagebox.showinfo("Assistente", "Escolha primeiro a pasta das notas.", parent=self)
            return None
        agora = datetime.now().strftime("Rascunho %Y-%m-%d %H%M")
        base = self.entrada_nome.get().strip() or agora
        nome, n = base, 1
        while True:
            try:
                caminho = notas.criar_nota(self.pasta_raiz, nome)
                break
            except ValueError:
                base = nome = agora
                n = 1
            except FileExistsError:
                n += 1
                nome = f"{base} ({n})"
            except OSError as erro:
                messagebox.showerror("Assistente", str(erro), parent=self)
                return None
        try:
            notas.gravar_nota(caminho, texto)
        except OSError as erro:
            messagebox.showerror("Assistente", str(erro), parent=self)
            return None
        self._atualizar_arvore()
        return caminho

    def _limpar_assistente(self) -> None:
        self.rascunho.delete("1.0", "end")
        self.previa.delete("1.0", "end")
        self.entrada_nome.delete(0, "end")
        self.botao_guardar_previa.configure(state="disabled")

    def _estruturar_rascunho(self) -> None:
        texto = self.rascunho.get("1.0", "end-1c")
        if not texto.strip():
            self._definir_estado_assistente("Escreva algo no rascunho primeiro.")
            return
        if self.pasta_raiz is None:
            messagebox.showinfo("Assistente", "Escolha primeiro a pasta das notas.", parent=self)
            return

        self.botao_estruturar.configure(state="disabled")
        self._definir_estado_assistente("A estruturar com o Gemini…")
        fila: queue.Queue = queue.Queue()
        self._fila_ia = fila

        def trabalhar() -> None:
            try:
                resultado = ia.estruturar_com_recurso(texto)
            except Exception as erro:  # nunca deixar a janela presa
                resultado = ia.Resultado(texto, False, f"Erro inesperado: {erro}")
            fila.put(resultado)

        threading.Thread(target=trabalhar, daemon=True).start()
        self.after(150, self._verificar_resultado_ia)

    def _verificar_resultado_ia(self) -> None:
        try:
            resultado = self._fila_ia.get_nowait()
        except queue.Empty:
            self.after(150, self._verificar_resultado_ia)
            return

        self.botao_estruturar.configure(state="normal")
        if resultado.estruturado:
            self._mostrar_previa(resultado.texto)
            self._definir_estado_assistente("Proposta pronta. Corrija se precisar e guarde.")
            return

        # O Gemini falhou (ou a nota é privada): o texto original vai para uma nota nova.
        caminho = self._criar_nota_automatica(resultado.texto)
        if caminho is None:
            return
        self._definir_estado_assistente(
            f"{resultado.motivo} Nota criada sem estruturação: {caminho.name}"
        )
        self._limpar_assistente()

    def _mostrar_previa(self, texto: str) -> None:
        self.previa.delete("1.0", "end")
        self.previa.insert("1.0", texto)
        self.botao_guardar_previa.configure(state="normal")

    def _guardar_previa(self) -> None:
        texto = self.previa.get("1.0", "end-1c")
        if not texto.strip():
            return
        caminho = self._criar_nota_automatica(texto)
        if caminho is None:
            return
        self._definir_estado_assistente(f"Nota criada: {caminho.name}")
        self._limpar_assistente()

    def _guardar_rascunho_sem_ia(self) -> None:
        texto = self.rascunho.get("1.0", "end-1c")
        if not texto.strip():
            self._definir_estado_assistente("Escreva algo no rascunho primeiro.")
            return
        caminho = self._criar_nota_automatica(texto)
        if caminho is None:
            return
        self._definir_estado_assistente(f"Nota criada sem IA: {caminho.name}")
        self._limpar_assistente()

    @staticmethod
    def _valor_filtro(menu: ctk.CTkOptionMenu, todos: str) -> str | None:
        valor = menu.get()
        return None if valor == todos else valor

    def _editar_opcoes(self, linha: int) -> None:
        """Abre um diálogo para indicar a validação da Dra. Elvira, o colega e a área."""
        if self.caminho_atual is None:
            return
        texto = self._texto_editor()
        tarefa = _tarefa_na_linha(texto, linha)
        if tarefa is None:
            return

        janela = ctk.CTkToplevel(self)
        janela.title("Opções da tarefa")
        janela.geometry("440x330")
        janela.transient(self)
        janela.after(150, janela.grab_set)

        ctk.CTkLabel(
            janela, text=tarefa.texto or "(sem texto)", anchor="w", justify="left",
            wraplength=400, font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(fill="x", padx=18, pady=(18, 10))

        var_elvira = BooleanVar(value=tarefa.elvira)
        ctk.CTkCheckBox(
            janela, text="Precisa de validação da Dra. Elvira", variable=var_elvira
        ).pack(anchor="w", padx=18, pady=6)

        linha_colega = ctk.CTkFrame(janela, fg_color="transparent")
        linha_colega.pack(fill="x", padx=18, pady=6)
        ctk.CTkLabel(linha_colega, text="Colega", width=70, anchor="w").pack(side="left")
        opcoes_colega = [SEM_COLEGA, *configuracao.colegas()]
        if tarefa.colega and tarefa.colega not in opcoes_colega:
            opcoes_colega.append(tarefa.colega)
        menu_colega = ctk.CTkOptionMenu(linha_colega, values=opcoes_colega, width=200)
        menu_colega.set(tarefa.colega or SEM_COLEGA)
        menu_colega.pack(side="left", padx=(0, 8))

        def novo_colega() -> None:
            nome = ctk.CTkInputDialog(text="Nome do colega:", title="Novo colega").get_input()
            if not nome or not nome.strip():
                return
            lista = configuracao.adicionar_colega(nome)
            menu_colega.configure(values=[SEM_COLEGA, *lista])
            menu_colega.set(nome.strip())

        ctk.CTkButton(linha_colega, text="Novo colega…", width=110, command=novo_colega).pack(side="left")

        linha_area = ctk.CTkFrame(janela, fg_color="transparent")
        linha_area.pack(fill="x", padx=18, pady=6)
        ctk.CTkLabel(linha_area, text="Área", width=70, anchor="w").pack(side="left")
        menu_area = ctk.CTkOptionMenu(linha_area, values=list(AREAS), width=200)
        menu_area.set(tarefa.area)
        menu_area.pack(side="left")

        def guardar() -> None:
            colega = menu_colega.get()
            novo = definir_opcoes(
                self._texto_editor(),
                linha,
                elvira=bool(var_elvira.get()),
                colega=None if colega == SEM_COLEGA else colega,
                area=menu_area.get(),
            )
            self._mostrar_texto(novo, manter_cursor=True)
            self._gravar_texto(novo)
            janela.destroy()

        rodape = ctk.CTkFrame(janela, fg_color="transparent")
        rodape.pack(side="bottom", fill="x", padx=18, pady=18)
        ctk.CTkButton(rodape, text="Cancelar", fg_color="transparent", border_width=1,
                      text_color=("gray10", "gray90"), command=janela.destroy).pack(side="right")
        ctk.CTkButton(rodape, text="Guardar", command=guardar).pack(side="right", padx=(0, 8))

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

        colegas = [TODOS_COLEGAS, *agregado.colegas_disponiveis(todas)]
        self.filtro_colega.configure(values=colegas)
        if self.filtro_colega.get() not in colegas:
            self.filtro_colega.set(TODOS_COLEGAS)

        filtradas = agregado.filtrar(
            todas,
            estado=self.filtro_estado.get(),
            pasta=self._pasta_filtro(),
            pesquisa=self.filtro_pesquisa.get(),
            area=self._valor_filtro(self.filtro_area, TODAS_AREAS),
            colega=self._valor_filtro(self.filtro_colega, TODOS_COLEGAS),
            so_elvira=bool(self.filtro_elvira.get()),
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
        destino += f"  ·  {_resumo_opcoes(item.tarefa)}"
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
