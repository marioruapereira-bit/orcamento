"""Interface CustomTkinter: lista de notas à esquerda, editor ao centro e tarefas à direita.

As regras de negócio estão em ``tarefas``, ``notas`` e ``configuracao``.
Este módulo só liga a interface a essas funções.
"""

from __future__ import annotations

from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk

from . import configuracao, notas
from .tarefas import Tarefa, alternar_tarefa, extrair_tarefas

LARGURA_NOTAS = 260
LARGURA_TAREFAS = 300


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

        self._criar_lista_notas()
        self._criar_editor()
        self._criar_painel_tarefas()

        self.bind("<Control-s>", lambda _e: self._guardar())
        self.protocol("WM_DELETE_WINDOW", self._fechar)

        self._atualizar_arvore()
        self._atualizar_estado()

    # ------------------------------------------------------------------
    # Construção da interface
    # ------------------------------------------------------------------

    def _criar_lista_notas(self) -> None:
        barra = ctk.CTkFrame(self, width=LARGURA_NOTAS, corner_radius=0)
        barra.grid(row=0, column=0, sticky="nsew")
        barra.grid_rowconfigure(2, weight=1)
        barra.grid_columnconfigure(0, weight=1)

        ctk.CTkButton(barra, text="Escolher pasta…", command=self._escolher_pasta).grid(
            row=0, column=0, padx=10, pady=(10, 4), sticky="ew"
        )
        ctk.CTkButton(barra, text="Nova nota", command=self._nova_nota).grid(
            row=1, column=0, padx=10, pady=4, sticky="ew"
        )
        self.lista_notas = ctk.CTkScrollableFrame(barra, label_text="Notas")
        self.lista_notas.grid(row=2, column=0, padx=10, pady=(4, 10), sticky="nsew")

    def _criar_editor(self) -> None:
        painel = ctk.CTkFrame(self, fg_color="transparent")
        painel.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        painel.grid_rowconfigure(1, weight=1)
        painel.grid_columnconfigure(0, weight=1)

        topo = ctk.CTkFrame(painel, fg_color="transparent")
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
        self.editor.grid(row=1, column=0, sticky="nsew")
        # Quando o texto muda, o Tk marca a flag "modified". Usamos isso para
        # atualizar o estado (por guardar) e a lista de tarefas.
        self.editor._textbox.bind("<<Modified>>", self._ao_modificar_editor)

    def _criar_painel_tarefas(self) -> None:
        painel = ctk.CTkFrame(self, width=LARGURA_TAREFAS)
        painel.grid(row=0, column=2, sticky="nsew", padx=(0, 10), pady=10)
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
                text=tarefa.texto,
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


def iniciar() -> None:
    ctk.set_appearance_mode("system")
    Aplicacao().mainloop()
