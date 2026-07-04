import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import json
import os
import threading
import time
import winsound
from tkcalendar import DateEntry

ARQUIVO = "alarmes.json"


class GerenciadorAlarmes:

    def __init__(self, root):

        self.root = root
        self.root.title("Meus Alertas")
        self.root.geometry("720x600")
        self.root.configure(bg="#1e1e1e")

        self.alarmes = []
        self.indice_edicao = None

        self.criar_interface()
        self.carregar_alarmes()

        threading.Thread(
            target=self.monitorar_alarmes,
            daemon=True
        ).start()

    def criar_interface(self):
        self.root.configure(bg="#171717")

        titulo = tk.Label(
            self.root,
            text="⏰ GERENCIADOR DE ALARMES",
            bg="#171717",
            fg="white",
            font=("Segoe UI", 20, "bold")
        )
        titulo.pack(pady=(15, 5))

        self.lbl_relogio = tk.Label(
            self.root,
            text="",
            bg="#171717",
            fg="#22c55e",
            font=("Segoe UI", 32, "bold")
        )
        self.lbl_relogio.pack()

        self.atualizar_relogio()

        # CARD SUPERIOR
        frame = tk.Frame(
            self.root,
            bg="#262626",
            padx=15,
            pady=15
        )

        frame.pack(
            fill="x",
            padx=15,
            pady=15
        )

        tk.Label(
            frame,
            text="Título",
            bg="#262626",
            fg="white",
            font=("Segoe UI", 10),
            anchor="w"
        ).grid(row=0, column=0, padx=(0, 10), pady=(0, 8), sticky="w")

        self.entry_titulo = tk.Entry(
            frame,
            font=("Segoe UI", 11),
            width=35
        )

        self.entry_titulo.grid(
            row=0,
            column=1,
            padx=(0, 20),
            pady=(0, 8),
            sticky="ew"
        )

        tk.Label(
            frame,
            text="Data",
            bg="#262626",
            fg="white",
            anchor="w"
        ).grid(row=1, column=0, padx=(0, 10), sticky="w")

        self.calendario = DateEntry(
            frame,
            width=15,
            date_pattern="dd/MM/yyyy"
        )

        self.calendario.grid(
            row=1,
            column=1,
            padx=(0, 20),
            sticky="w"
        )

        tk.Label(
            frame,
            text="Hora",
            bg="#262626",
            fg="white",
            anchor="w"
        ).grid(row=1, column=2, padx=(20, 8), sticky="w")

        self.entry_hora = tk.Entry(
            frame,
            width=10
        )

        self.entry_hora.grid(
            row=1,
            column=3,
            sticky="w"
        )

        # BOTÕES HORIZONTAIS

        frame_botoes = tk.Frame(
            self.root,
            bg="#171717"
        )

        frame_botoes.pack(
            fill="x",
            padx=15,
            pady=5
        )

        self.btn_adicionar = tk.Button(
            frame_botoes,
            text="➕ Adicionar",
            bg="#16a34a",
            fg="white",
            bd=0,
            font=("Segoe UI", 11, "bold"),
            padx=15,
            pady=8,
            command=self.adicionar_alarme
        )

        self.btn_adicionar.pack(
            side="left",
            padx=4
        )

        self.btn_editar = tk.Button(
            frame_botoes,
            text="✏ Editar",
            bg="#2563eb",
            fg="white",
            bd=0,
            font=("Segoe UI", 11, "bold"),
            padx=15,
            pady=8,
            command=self.editar_alarme
        )

        self.btn_editar.pack(
            side="left",
            padx=4
        )

        self.btn_salvar = tk.Button(
            frame_botoes,
            text="💾 Salvar",
            bg="#f59e0b",
            fg="black",
            bd=0,
            font=("Segoe UI", 11, "bold"),
            padx=15,
            pady=8,
            command=self.salvar_edicao
        )

        self.btn_salvar.pack(
            side="left",
            padx=4
        )

        self.btn_excluir = tk.Button(
            frame_botoes,
            text="🗑 Excluir",
            bg="#dc2626",
            fg="white",
            bd=0,
            font=("Segoe UI", 11, "bold"),
            padx=15,
            pady=8,
            command=self.excluir_alarme
        )

        self.btn_excluir.pack(
            side="left",
            padx=4
        )

        # LISTA DE ALARMES

        self.lista = tk.Listbox(
            self.root,
            bg="#262626",
            fg="white",
            selectbackground="#2563eb",
            selectforeground="white",
            font=("Segoe UI", 11),
            bd=0,
            highlightthickness=0,
            height=15
        )

        self.lista.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=10
        )

    def atualizar_relogio(self):

        agora = datetime.now().strftime(
            "%d/%m/%Y %H:%M:%S"
        )

        self.lbl_relogio.config(text=agora)

        self.root.after(
            1000,
            self.atualizar_relogio
        )

    def adicionar_alarme(self):

        titulo = self.entry_titulo.get().strip()
        data = self.calendario.get()
        hora = self.entry_hora.get().strip()

        if not titulo or not hora:

            messagebox.showwarning(
                "Aviso",
                "Preencha o título e a hora do alarme."
            )
            return

        try:

            datetime.strptime(
                f"{data} {hora}",
                "%d/%m/%Y %H:%M"
            )

        except ValueError:

            messagebox.showerror(
                "Erro",
                "Hora inválida.\n\nUse o formato HH:MM\nExemplo: 14:30"
            )
            return

        alarme = {
            "titulo": titulo,
            "data": data,
            "hora": hora,
            "executado": False
        }

        self.alarmes.append(alarme)

        self.salvar_alarmes()
        self.atualizar_lista()
        self.limpar_campos()

        messagebox.showinfo(
            "Sucesso",
            "Alarme adicionado com sucesso."
        )

    def editar_alarme(self):

        selecionado = self.lista.curselection()

        if not selecionado:

            messagebox.showwarning(
                "Aviso",
                "Selecione um alarme para editar."
            )
            return

        indice = selecionado[0]
        alarme = self.alarmes[indice]

        self.entry_titulo.delete(0, tk.END)
        self.entry_titulo.insert(0, alarme["titulo"])

        self.entry_hora.delete(0, tk.END)
        self.entry_hora.insert(0, alarme["hora"])

        try:

            data_obj = datetime.strptime(
                alarme["data"],
                "%d/%m/%Y"
            )

            self.calendario.set_date(data_obj)

        except ValueError:

            pass

        self.indice_edicao = indice

        messagebox.showinfo(
            "Modo edição",
            "Altere os dados e clique em 'Salvar Alterações'."
        )

    def salvar_edicao(self):

        if self.indice_edicao is None:

            messagebox.showwarning(
                "Aviso",
                "Nenhum alarme está em edição."
            )
            return

        titulo = self.entry_titulo.get().strip()
        data = self.calendario.get()
        hora = self.entry_hora.get().strip()

        if not titulo or not hora:

            messagebox.showwarning(
                "Aviso",
                "Preencha o título e a hora do alarme."
            )
            return

        try:

            datetime.strptime(
                f"{data} {hora}",
                "%d/%m/%Y %H:%M"
            )

        except ValueError:

            messagebox.showerror(
                "Erro",
                "Hora inválida.\n\nUse o formato HH:MM\nExemplo: 14:30"
            )
            return

        self.alarmes[self.indice_edicao] = {
            "titulo": titulo,
            "data": data,
            "hora": hora,
            "executado": False
        }

        self.salvar_alarmes()
        self.atualizar_lista()
        self.limpar_campos()

        self.indice_edicao = None

        messagebox.showinfo(
            "Sucesso",
            "Alarme atualizado com sucesso."
        )

    def excluir_alarme(self):

        selecionado = self.lista.curselection()

        if not selecionado:

            messagebox.showwarning(
                "Aviso",
                "Selecione um alarme para excluir."
            )
            return

        indice = selecionado[0]

        resposta = messagebox.askyesno(
            "Confirmar exclusão",
            "Deseja realmente excluir o alarme selecionado?"
        )

        if resposta:

            del self.alarmes[indice]

            self.salvar_alarmes()
            self.atualizar_lista()
            self.limpar_campos()

            self.indice_edicao = None

            messagebox.showinfo(
                "Sucesso",
                "Alarme excluído com sucesso."
            )

    def atualizar_lista(self):

        self.lista.delete(0, tk.END)

        for alarme in self.alarmes:

            status = "OK" if alarme.get("executado") else "PENDENTE"

            texto = (
                f"{alarme['data']} "
                f"{alarme['hora']} - "
                f"{alarme['titulo']} "
                f"[{status}]"
            )

            self.lista.insert(tk.END, texto)

    def limpar_campos(self):

        self.entry_titulo.delete(0, tk.END)
        self.entry_hora.delete(0, tk.END)

    def salvar_alarmes(self):

        with open(
            ARQUIVO,
            "w",
            encoding="utf-8"
        ) as arquivo:

            json.dump(
                self.alarmes,
                arquivo,
                indent=4,
                ensure_ascii=False
            )

    def carregar_alarmes(self):

        if os.path.exists(ARQUIVO):

            try:

                with open(
                    ARQUIVO,
                    "r",
                    encoding="utf-8"
                ) as arquivo:

                    self.alarmes = json.load(arquivo)

            except Exception:

                self.alarmes = []

        self.atualizar_lista()

    def tocar_som_alerta(self):

        for _ in range(15):

            winsound.Beep(
                2500,
                500
            )

    def exibir_alerta(self, titulo):

        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()
        self.root.attributes("-topmost", True)

        self.root.after(
            1500,
            lambda: self.root.attributes("-topmost", False)
        )

        alerta = tk.Toplevel(self.root)

        alerta.title("ALERTA")
        alerta.configure(bg="#cc0000")
        alerta.resizable(False, False)

        largura = 560
        altura = 330

        x = (alerta.winfo_screenwidth() // 2) - (largura // 2)
        y = (alerta.winfo_screenheight() // 2) - (altura // 2)

        alerta.geometry(f"{largura}x{altura}+{x}+{y}")

        alerta.attributes("-topmost", True)
        alerta.lift()
        alerta.focus_force()
        alerta.grab_set()

        frame_alerta = tk.Frame(
            alerta,
            bg="#cc0000"
        )
        frame_alerta.pack(
            expand=True,
            fill="both"
        )

        lbl_titulo = tk.Label(
            frame_alerta,
            text="🚨 ALERTA 🚨",
            bg="#cc0000",
            fg="white",
            font=("Segoe UI", 28, "bold")
        )
        lbl_titulo.pack(pady=(20, 5))

        lbl_nome_alarme = tk.Label(
            frame_alerta,
            text=titulo.upper(),
            bg="#cc0000",
            fg="#ffff00",
            font=("Segoe UI", 22, "bold"),
            wraplength=510,
            justify="center"
        )
        lbl_nome_alarme.pack(pady=(0, 12))

        lbl_hora = tk.Label(
            frame_alerta,
            text=datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            bg="#cc0000",
            fg="white",
            font=("Segoe UI", 11)
        )
        lbl_hora.pack(pady=(0, 8))

        lbl_instrucao = tk.Label(
            frame_alerta,
            text="Clique em OK para confirmar o alerta",
            bg="#cc0000",
            fg="white",
            font=("Segoe UI", 11)
        )
        lbl_instrucao.pack(pady=5)

        def parar_alerta():

            alerta.grab_release()
            alerta.destroy()

        btn_ok = tk.Button(
            frame_alerta,
            text="OK",
            font=("Segoe UI", 15, "bold"),
            width=14,
            bg="white",
            fg="black",
            command=parar_alerta
        )
        btn_ok.pack(pady=18)

        def piscar():

            if not alerta.winfo_exists():
                return

            cor_atual = frame_alerta.cget("bg")

            if cor_atual == "#cc0000":
                nova_cor = "#ff0000"
            else:
                nova_cor = "#cc0000"

            frame_alerta.configure(bg=nova_cor)
            lbl_titulo.configure(bg=nova_cor)
            lbl_nome_alarme.configure(bg=nova_cor)
            lbl_hora.configure(bg=nova_cor)
            lbl_instrucao.configure(bg=nova_cor)

            alerta.after(500, piscar)

        piscar()

        threading.Thread(
            target=self.tocar_som_alerta,
            daemon=True
        ).start()

    def monitorar_alarmes(self):

        while True:

            agora = datetime.now()

            for alarme in self.alarmes:

                if alarme.get("executado"):
                    continue

                try:

                    alvo = datetime.strptime(
                        f"{alarme['data']} {alarme['hora']}",
                        "%d/%m/%Y %H:%M"
                    )

                except ValueError:

                    continue

                if agora >= alvo:

                    alarme["executado"] = True

                    self.salvar_alarmes()
                    self.atualizar_lista()

                    self.root.after(
                        0,
                        lambda t=alarme["titulo"]: self.exibir_alerta(t)
                    )

            time.sleep(5)


if __name__ == "__main__":

    root = tk.Tk()

    app = GerenciadorAlarmes(root)

    root.mainloop()