import tkinter as tk
from tkinter import ttk

def simulation(pu, pp, rx, an, marie_pacse):    
    rx /= 100
    v_totaux = int_gen = k_terme = perf_reelle = part_optelios = frais_gestion = frais_total = k_final = total_part_optelios = total_frais_gestion = 0.0
    frais_total += pu * 0.01
    k_initial = pu * 0.99

    for i in range(an):        
        v_totaux = k_initial + (pp * 12)
        k_terme = vc_oneyear(k_initial, pp, rx)
        int_gen = k_terme - v_totaux
        perf_reelle = (k_terme / v_totaux) - 1
        part_optelios = ((perf_reelle - 0.05) / perf_reelle) * 0.1 * int_gen if perf_reelle > 0 else 0
        total_part_optelios += part_optelios
        frais_gestion = k_terme * 0.01
        total_frais_gestion += frais_gestion
        k_final = k_terme - part_optelios - frais_gestion
        k_initial = k_final

    rev_annuel, rev_mensuel, impot_pv = rev_compl(int_gen, part_optelios, an, frais_gestion, marie_pacse)
    return {
        "capital_final": k_final,
        "frais_optelios": total_part_optelios,
        "frais_gestion": total_frais_gestion,
        "revenu_annuel": rev_annuel,
        "revenu_mensuel": rev_mensuel,
        "impot": impot_pv,
        "annee": an
    }

def rev_compl(k_int, part_optelios, an, frais_gestion, marie_pacse):    
    rev_annuel = k_int - part_optelios - frais_gestion
    impot_pv = 0.0
    if an >= 8:
        seuil = 9200 if marie_pacse else 4600
        if rev_annuel > seuil:
            impot_pv = (rev_annuel - seuil) * 0.247
    else:
        impot_pv = rev_annuel * 0.3

    rev_annuel -= impot_pv
    rev_mensuel = rev_annuel / 12
    return rev_annuel, rev_mensuel, impot_pv

def vc_oneyear(pu, pp, rx):    
    rx_mens = (1 + rx) ** (1 / 12) - 1
    return pu * (1 + rx_mens) ** 12 + pp * (((1 + rx_mens) ** 12 - 1) / rx_mens)

class SimuApp:
    CARD_WIDTH = 260
    CARD_HEIGHT = 220
    CARD_MARGIN_X = 30

    def __init__(self, root):
        self.root = root
        self.root.title("Simulateur d'investissement Optélios")
        self.root.geometry("1080x680")
        self.root.configure(bg="#f7f7fb")

        # Frame principale centrée
        self.main_frame = tk.Frame(self.root, bg="#f7f7fb")
        self.main_frame.pack(expand=True, fill="both")

        self.create_form()

        self.cards_frame = tk.Frame(self.main_frame, bg="#f7f7fb")
        self.cards_frame.pack(pady=(35,10))

    def create_form(self):
        frm = tk.Frame(self.main_frame, bg="#f7f7fb")
        frm.pack(pady=(28,12))

        label_opts = dict(font=("Segoe UI", 12), bg="#f7f7fb")
        entry_opts = dict(width=16, font=("Segoe UI", 13))

        tk.Label(frm, text="Capital initial (€) :", **label_opts).grid(row=0, column=0, sticky="e", padx=8, pady=7)
        self.entry_pu = ttk.Entry(frm, **entry_opts)
        self.entry_pu.grid(row=0, column=1, pady=7)

        tk.Label(frm, text="Versement mensuel (€) :", **label_opts).grid(row=1, column=0, sticky="e", padx=8, pady=7)
        self.entry_pp = ttk.Entry(frm, **entry_opts)
        self.entry_pp.grid(row=1, column=1, pady=7)

        tk.Label(frm, text="Rendement annuel (%) :", **label_opts).grid(row=2, column=0, sticky="e", padx=8, pady=7)
        self.entry_rx = ttk.Entry(frm, **entry_opts)
        self.entry_rx.grid(row=2, column=1, pady=7)

        self.var_statut = tk.IntVar()
        ttk.Checkbutton(frm, text="Marié ou pacsé", variable=self.var_statut).grid(row=3, column=0, columnspan=2, pady=(2,9), sticky="w")

        tk.Label(frm, text="Nombre de simulations :", **label_opts).grid(row=4, column=0, sticky="e", padx=8, pady=7)
        self.entry_nb_sim = ttk.Entry(frm, width=6, font=("Segoe UI", 13))
        self.entry_nb_sim.grid(row=4, column=1, pady=7, sticky="w")
        self.btn_valider_nb_sim = ttk.Button(frm, text="Valider", command=self.valider_nb_sim)
        self.btn_valider_nb_sim.grid(row=4, column=2, padx=(8,0), pady=7, sticky="w")

        self.frame_simulations = tk.Frame(frm, bg="#f7f7fb")
        self.frame_simulations.grid(row=5, column=0, columnspan=4, pady=(2,10))

        self.btn_lancer_simulation = ttk.Button(frm, text="Lancer les simulations", command=self.lancer_simulations_gui, state="disabled")
        self.btn_lancer_simulation.grid(row=6, column=0, columnspan=4, pady=(20,5))

    def valider_nb_sim(self):
        try:
            nb_sim = int(self.entry_nb_sim.get())
            if not (1 <= nb_sim <= 4):
                raise ValueError
        except ValueError:
            tk.messagebox.showerror("Erreur", "Merci de saisir un nombre de simulations entre 1 et 4.")
            return

        for widget in self.frame_simulations.winfo_children():
            widget.destroy()

        self.entry_annees = []
        for i in range(nb_sim):
            ttk.Label(self.frame_simulations, text=f"Durée simulation {i + 1} (années) :", background="#f7f7fb", font=("Segoe UI", 11)).grid(row=i, column=0, sticky="e", padx=8, pady=4)
            entry = ttk.Entry(self.frame_simulations, width=10, font=("Segoe UI", 12))
            entry.grid(row=i, column=1, pady=4, sticky="w")
            self.entry_annees.append(entry)
        self.btn_lancer_simulation.config(state="normal")

    def lancer_simulations_gui(self):
        try:
            pu = float(self.entry_pu.get())
            pp = float(self.entry_pp.get())
            rx = float(self.entry_rx.get())
            marie_pacse = self.var_statut.get()
            nb_sim = len(self.entry_annees)
            annees = []
            for entry in self.entry_annees:
                duree = int(entry.get())
                if duree <= 0:
                    raise ValueError
                annees.append(duree)    

            for widget in self.cards_frame.winfo_children():
                widget.destroy()

            for idx, duree in enumerate(annees):
                res = simulation(pu, pp, rx, duree, marie_pacse)
                self.afficher_carte_simulation(self.cards_frame, res, idx)

        except Exception as e:
            for widget in self.cards_frame.winfo_children():
                widget.destroy()
            err_label = tk.Label(self.cards_frame, text="Erreur : merci de saisir des valeurs valides (>0).", font=("Segoe UI", 13, "bold"), fg="red", bg="#f7f7fb")
            err_label.pack(padx=40, pady=40)

    def afficher_carte_simulation(self, parent, res, idx):
        card = tk.Frame(parent, bg="#386ad7", bd=0, relief="ridge", width=self.CARD_WIDTH, height=self.CARD_HEIGHT)
        card.grid(row=0, column=idx, padx=(self.CARD_MARGIN_X//2, self.CARD_MARGIN_X//2), pady=8)
        card.grid_propagate(False)
        # ---- Année simulation (tout en haut) ----
        titre = tk.Label(card, text=f"{res['annee']} an{'s' if res['annee']>1 else ''}", font=("Segoe UI", 14, "bold"), fg="white", bg="#386ad7")
        titre.pack(pady=(13, 2))
        # ---- Titre revenu ----
        rev_txt = tk.Label(card, text="Revenu complémentaire mensuel", font=("Segoe UI", 11), fg="white", bg="#386ad7")
        rev_txt.pack(pady=(1, 1))
        rev = tk.Label(card, text=f"{int(res['revenu_mensuel']):,} €", font=("Segoe UI", 20, "bold"), fg="#00e676", bg="#386ad7")
        rev.pack(pady=(0, 7))
        # ---- Titre capital ----
        cap_txt = tk.Label(card, text="Capital à terme", font=("Segoe UI", 11), fg="white", bg="#386ad7")
        cap_txt.pack(pady=(2, 1))
        cap = tk.Label(card, text=f"{int(res['capital_final']):,} €", font=("Segoe UI", 20, "bold"), fg="#ffd600", bg="#386ad7")
        cap.pack(pady=(0, 8))
        # ---- Infos complémentaires ----
        txts = [
            f"Frais Optélios : {int(res['frais_optelios']):,} €".replace(",", " "),
            f"Frais de gestion : {int(res['frais_gestion']):,} €".replace(",", " "),
            f"{'Impôts annuels : '+str(int(res['impot']))+' €' if res['impot'] > 0 else 'Pas d’imposition'}",
            f"Revenu annuel : {int(res['revenu_annuel']):,} €".replace(",", " ")
        ]
        for t in txts:
            lbl = tk.Label(card, text=t, font=("Segoe UI", 10), fg="#d7eaff", bg="#386ad7")
            lbl.pack(pady=1)
        card.update_idletasks()


if __name__ == "__main__":
    root = tk.Tk()
    app = SimuApp(root)
    root.mainloop()
