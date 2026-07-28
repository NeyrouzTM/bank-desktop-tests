import tkinter as tk
import re
from tkinter import messagebox
from database import add_customer
from ui_background import apply_window_background, style_on_background


def open_customer_window():

    # NOTE: This project’s current UI app is a simplified simulation.
    # We extend “Create Customer” with an optional insurance flow so that
    # when the user checks “Insurance”, the subsequent screens are opened.

    email_pattern = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")

    window = tk.Toplevel()
    window.title("Create Customer")
    window.geometry("900x600")
    apply_window_background(window)

    label_name = tk.Label(window, text="Customer Name")
    style_on_background(label_name)
    label_name.pack(pady=(40, 0))
    entry_name = tk.Entry(window)
    style_on_background(entry_name)
    entry_name.pack()

    label_cin = tk.Label(window, text="CIN")
    style_on_background(label_cin)
    label_cin.pack()
    entry_cin = tk.Entry(window)
    style_on_background(entry_cin)
    entry_cin.pack()

    label_email = tk.Label(window, text="Email")
    style_on_background(label_email)
    label_email.pack()
    entry_email = tk.Entry(window)
    style_on_background(entry_email)
    entry_email.pack()

    # --- Insurance simulation (Vermeg-like flow) ---
    # Step 1 controls
    plan_var = tk.StringVar(value="simple")  # simple | insurance

    rb_simple = tk.Radiobutton(window, text="Compte bancaire simple", value="simple", variable=plan_var)
    rb_ins = tk.Radiobutton(window, text="Compte avec assurance", value="insurance", variable=plan_var)
    style_on_background(rb_simple)
    style_on_background(rb_ins)
    rb_simple.pack(pady=(10, 0))
    rb_ins.pack(pady=(5, 0))

    label_balance = tk.Label(window, text="Montant du compte")
    style_on_background(label_balance)
    label_balance.pack(pady=(10, 0))

    entry_balance = tk.Entry(window)
    style_on_background(entry_balance)
    entry_balance.insert(0, "1000")
    entry_balance.pack()

    def open_insurance_flow(initial_balance: float):
        flow = tk.Toplevel()
        flow.title("Insurance - Vermeg (simulation)")
        flow.geometry("900x600")
        apply_window_background(flow)

        # Step 2: choose insurance type + pack
        insurance_type_var = tk.StringVar(value="hospital")
        tk.Label(flow, text="Choisir le type d’assurance").pack(pady=(20, 0))
        tk.Radiobutton(flow, text="Assurance hospitalière", value="hospital", variable=insurance_type_var).pack(pady=(10, 0))
        tk.Radiobutton(flow, text="Assurance ambulatoire", value="ambulatoire", variable=insurance_type_var).pack(pady=(5, 0))

        tk.Label(flow, text="Choisir un pack").pack(pady=(20, 0))

        # Pack catalog
        packs = {
            "hospital": [("pack1", 200), ("pack2", 500), ("pack3", 800)],
            "ambulatoire": [("pack1", 100), ("pack2", 300), ("pack3", 600)],
        }

        pack_var = tk.StringVar(value="pack1")
        lb = tk.Listbox(flow, height=6)
        lb.pack(pady=10)

        def refresh_packs():
            lb.delete(0, tk.END)
            chosen = packs.get(insurance_type_var.get(), packs["hospital"])
            for pk, price in chosen:
                lb.insert(tk.END, f"{pk} - {price}€")

        def on_select(_event=None):
            sel = lb.curselection()
            if not sel:
                return
            text = lb.get(sel[0])
            pack_var.set(text.split(" - ")[0])

        refresh_packs()
        # Preselect first element for deterministic default
        try:
            lb.selection_set(0)
            on_select()
        except Exception:
            pass
        lb.bind("<<ListboxSelect>>", on_select)

        def next_step():
            refresh_packs()
            # keep currently selected pack (if any)
            on_select()


        def payer():
            chosen = packs.get(insurance_type_var.get(), packs["hospital"])
            price = next((p for (pk, p) in chosen if pk == pack_var.get()), 0)
            if price <= 0:
                messagebox.showerror("Error", "Pack invalide")
                return

            nonlocal initial_balance
            if initial_balance >= price:
                initial_balance -= price
                messagebox.showinfo(
                    "Success",
                    f"Paiement effectué: -{price}€. Solde restant: {initial_balance}€",
                )
            else:
                messagebox.showerror(
                    "Error",
                    "Vous ne pouvez pas payer cette assurance. Merci de recharger votre compte",
                )

            flow.destroy()

        tk.Button(flow, text="Suivant", command=next_step).pack(pady=10)
        tk.Button(flow, text="Payer", command=payer).pack(pady=10)

    def save():


        name = entry_name.get().strip()
        cin = entry_cin.get().strip()
        email = entry_email.get().strip()

        if not name or not cin or not email:
            messagebox.showerror("Error", "All fields are required")
            return

        if len(name) < 3:
            messagebox.showerror("Error", "Name must contain at least 3 characters")
            return

        if not cin.isdigit() or len(cin) != 8:
            messagebox.showerror("Error", "Invalid CIN")
            return

        if not email_pattern.fullmatch(email):
            messagebox.showerror("Error", "Invalid email format")
            return

        success = add_customer(name, cin, email)

        if success:
            messagebox.showinfo("Success", "Customer added successfully")

            entry_name.delete(0, tk.END)
            entry_cin.delete(0, tk.END)
            entry_email.delete(0, tk.END)

            entry_name.focus()

            # If insurance is selected, open additional screens.
            if plan_var.get() == "insurance":
                try:
                    balance = float(entry_balance.get().strip().replace(",", "."))
                except Exception:
                    balance = 0.0
                open_insurance_flow(balance)


        else:
            messagebox.showerror("Error", "CIN already exists")

    btn_save = tk.Button(window, text="Save Customer", command=save)
    style_on_background(btn_save)
    btn_save.pack(pady=10)

