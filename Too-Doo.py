import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import sqlite3
from tkcalendar import DateEntry
import csv
import json
import shutil

root = ctk.CTk()
root.geometry("1920x1080")
root.title("TooDoo List – Treeview")

root.columnconfigure((0,1,2), weight=1)
root.rowconfigure((0,1,2), weight=1)

main_frame = ctk.CTkFrame(root)
main_frame.columnconfigure((0,1,2,3), weight=1)
main_frame.rowconfigure(0, weight=1)
main_frame.rowconfigure((1,2,3), weight=0)
main_frame.grid(row=1, column=1, sticky="nsew", pady=(150,50), padx=(200,50))

header = ctk.CTkLabel(root, text="ToDo App - Your personal asistance", font=("Consolas", 24, "bold"))
header.grid(row=0, column=1, pady=(30,10))

bottom_frame = ctk.CTkFrame(main_frame)
bottom_frame.grid(row=20, column=0, columnspan=2, pady=20)

filter_frame = ctk.CTkFrame(main_frame)
filter_frame.grid(row=6, column=0, columnspan=2, pady=10)

data_label = ctk.CTkLabel(main_frame, text="Data wykonania", font=("Consolas", 11))
data_label.grid(row=4, column=0, sticky="w")

data_entry = DateEntry(main_frame, width=12, background="darkblue", foreground="white", borderwidth=2, date_pattern="yyyy-mm-dd")
data_entry.grid(row=4, column=0, pady=(5,10))

selected_item_id = None

def backup_datebase():
    today = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
    shutil.copy("zadania.db", f"backup_{today}.db")
    messagebox.showinfo("Powiadomienie", f"Z pwodzeniem utworzono backup: backup_{today}.db")

tree = ttk.Treeview(main_frame, columns=("Nazwa zadania","Opis", "Priorytet", "Status", "Termin"), show="headings")
tree.grid(row=0, column=0, columnspan=2, padx=50, pady=(70,20), sticky="nsew")

tree.heading("#1", text="Nazwa zadania")
tree.heading("#2", text="Opis")
tree.heading("#3", text="Priorytet")
tree.heading("#4", text="Status")
tree.heading("#5", text="Termin")

tree.column("#1",anchor="w", width=200)
tree.column("#2",anchor="w", width=300)
tree.column("#3",anchor="center", width=100)
tree.column("#4",anchor="center", width=100)
tree.column("#5",anchor="center", width=100)

zadania = []

#FILTROWANIE

status_label = ctk.CTkLabel(main_frame, text="Ustal status", font=("Consolas", 12))
status_label.grid(row=5, column=0, sticky="w")

filtr_label = ctk.CTkLabel(main_frame,text="Filtruj zadania", font=("Consolas", 12))
filtr_label.grid(row=6, column=0, sticky="w")

filtr_priority = ttk.Combobox(filter_frame, values=["", "Niski", "Średni", "Wysoki"], state="readonly")
filtr_priority.set("Po priorytecie")
filtr_priority.grid(row=0, column=0, padx=5)

filtr_status = ttk.Combobox(filter_frame, values=["", "W trakcie", "Zrobione", "Niepowodzenie"], state="readonly")
filtr_status.set("Po statusie")
filtr_status.grid(row=0, column=1, padx=5)

search_entry = ctk.CTkEntry(filter_frame, placeholder_text="Po nazwie lub opisie")
search_entry.grid(row=0, column=2, padx=10, sticky="ew")

btnfiltruj = ctk.CTkButton(filter_frame, text="Filtruj", command=lambda : filtruj_zadania())
btnfiltruj.grid(row=0, column=3, padx=5)


def filtruj_zadania():
    tekst = search_entry.get()
    wybrany_prio = filtr_priority.get()
    wybrany_status = filtr_status.get()



    for row in tree.get_children():
        tree.delete(row)

    for zadanie in zadania:
        nazwa, opis, priorytet, status, termin = zadanie

        if (
            (tekst in nazwa.lower() or tekst in opis.lower() or tekst in termin.lower())
            and (wybrany_prio == "" or priorytet == wybrany_prio)
            and (wybrany_status == "" or status == wybrany_status)
        ):
            tree.insert("", tk.END, values=zadanie, tags=(priorytet,))
            tree.tag_configure(priorytet, background={"Niski": "green", "Średni": "orange", "Wysoki": "red"}[priorytet])


with sqlite3.connect("zadania.db") as conn:
    c = conn.cursor()

c.execute("""
    Create table if not exists ZADANIA (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          nazwa TEXT,
          opis TEXT,
          priorytet TEXT,
          status TEXT,
          termin TEXT
    )
""")

conn.commit()

c.execute("SELECT * FROM zadania")

def powiadomienia():
    dzisiaj = datetime.now().strftime("%Y-%m-%d")
    do_przypomnienia = []

    for item in tree.get_children():
        wartosci = tree.item(item)["values"]
        if len(wartosci) >=4:
            data_zadania = wartosci[3]
            if data_zadania == dzisiaj:
                do_przypomnienia.append(wartosci[0])
    if do_przypomnienia:
        messagebox.showinfo("Przypominajka!", f"masz zadanie do wykonania na dziś: \n• " + "\n•".join(do_przypomnienia))

def cykliczne_sprawdzenia():
    powiadomienia()
    root.after(10000, cykliczne_sprawdzenia)

def json_export():
    data = []
    for row in tree.get_children():
        row = tree.item(row)["values"]
        data.append({"title": row[0], "date": row[1], "priority": row[2]})
    with open("zadania.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

tree.grid(row=0, column=0, sticky="nsew")

priorytety = ["Niski", "Średni", "Wysoki"]
statusy = ["W trakcie", "Zrobione", "Niepowodzenie"]

combo_priority = ttk.Combobox(main_frame, values=priorytety, state="readonly")
combo_priority.current(0)
combo_priority.grid(row=3, column=0)

combo_status = ttk.Combobox(main_frame, values=statusy, state="readonly")
combo_status.current(0)
combo_status.grid(row=5, column=0)

entry_title = ctk.CTkEntry(main_frame, placeholder_text="Tytuł zadania")
entry_title.grid(row=1, column=0, padx=(100,100), sticky="ew")

entry_desc = ctk.CTkEntry(main_frame, placeholder_text="Opis zadania")
entry_desc.grid(row=2, column=0, padx=(100,100), sticky="ew")


label1 = ctk.CTkLabel(main_frame,text="Nazwa taska", font=("Consolas", 11))
label1.grid(row=1, column=0, sticky="w")

label2 = ctk.CTkLabel(main_frame, text="Opis taska", font=("Consolas", 11))
label2.grid(row=2, column=0, sticky="w")

label3 = ctk.CTkLabel(main_frame, text="Wybierz priorytet", font=("Consolas", 11))
label3.grid(row=3, column=0, sticky="w")


# Przykład dodania taska
def dodaj():
    nazwa = entry_title.get().strip()
    opis = entry_desc.get().strip()
    priorytet = combo_priority.get()
    status = combo_status.get()
    termin = data_entry.get()

    if not nazwa:
        messagebox.showwarning("Błąd.", "Tytuł jest pusty.")
        return

    kolor = {"Niski": "green", "Średni": "orange", "Wysoki": "red"}[priorytet]
    tree.insert("", tk.END, values=(nazwa, opis, priorytet, status, termin), tags=(priorytet,))
    tree.tag_configure(priorytet, background=kolor)

    c.execute("INSERT INTO zadania (nazwa, opis, priorytet, status, termin) VALUES (?,?,?,?,?)", (nazwa, opis, priorytet, status, termin))
    conn.commit()
    zadania.append((nazwa, opis, priorytet, status, termin))


btn_add = ctk.CTkButton(bottom_frame, text="Dodaj", command=dodaj)
btn_add.grid(row=0, column=0, padx=10)

def zaladuj_z_bazy():
    c.execute("SELECT nazwa, opis, priorytet, status, termin FROM zadania")
    for row in c.fetchall():
        zadania.append(row)
        tree.insert("", tk.END, values=row, tags=(row[2],))
        tree.tag_configure(row[2], background={"Niski": "green", "Średni": "orange", "Wysoki": "red"}[row[2]])


def on_selected(event):
    global selected_item_id, old_name, old_desc
    selected = tree.selection()
    values = tree.item(selected[0], "values")
    old_name = values[0]
    old_desc = values[1]
    if selected:
        entry_title.delete(0, tk.END)
        entry_title.insert(0, values[0])
        entry_desc.delete(0, tk.END)
        entry_desc.insert(0, values[1])
        combo_priority.set(values[2])
        combo_status.set(values[3])
        selected_item_id = selected[0]
        btn_update.configure(state="normal")
        btn_delete.configure(state="normal")

tree.bind("<<TreeviewSelect>>", on_selected, add="+")

def aktualizuj():
    global selected_item_id
    if selected_item_id:
        new_name = entry_title.get()
        new_disc = entry_desc.get()
        new_prio = combo_priority.get()
        new_status = combo_status.get()

        tree.item(selected_item_id, values=(new_name, new_disc, new_prio, new_status))

        selected_item_id = None
        btn_update.configure(state="normal")
        entry_title.delete(0, tk.END)
        entry_desc.delete(0, tk.END)
        combo_priority.set("Niski")
        combo_status.set("W trakcie")

        c.execute("UPDATE zadania SET nazwa=?, opis=?, priorytet=?, status=?, WHERE nazwa=?, AND opis=?""", (new_name, new_disc, new_prio, new_status, old_name, old_desc))

def csv_export():
    with open("zadania.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Tytuł", "Data", "Priorytet", "Status", "Termin"])
        for row in tree.get_children():
            writer.writerow(tree.item(row)["values"])
        messagebox.showinfo("Eksport", "Zapisano poprawnie do pliku zadania.csv")

def deleteTask():
    wybrane = tree.selection()
    for dele in wybrane:
        tree.delete(dele)

def searchTask(query):
    query = query.lower()

    for row in tree.get_children():
        tree.delete(row)

    for zadanie in zadania:
        nazwa, opis, priorytet, status, termin = zadanie
        if (
            query in nazwa.lower() or
            query in opis.lower() or
            query in priorytet.lower() or
            query in status.lower() or
            query in termin.lower() 
        ):
            tree.insert("", tk.END, values=zadanie, tags=(priorytet,))
            tree.tag_configure(priorytet, background={"Niski": "green", "Średni": "orange", "Wysoki": "red"}[priorytet])


btn_update = ctk.CTkButton(bottom_frame, text="Aktualizuj", state="disabled", command=aktualizuj)
btn_update.grid(row=0, column=1, padx=10)

btn_delete = ctk.CTkButton(bottom_frame, text="Usuń", state="disabled", command=deleteTask)
btn_delete.grid(row=0, column=2, padx=10)

btn_export_csv = ctk.CTkButton(bottom_frame, text="CSV Convert", command=csv_export)
btn_export_csv.grid(row=1, column=0, padx=10)

btn_export_json = ctk.CTkButton(bottom_frame, text="jsonV Convert", command=json_export)
btn_export_json.grid(row=1, column=1)

btn_backup = ctk.CTkButton(bottom_frame, text="BackUpDataBase", command=backup_datebase)
btn_backup.grid(row=1, column=2)

zaladuj_z_bazy()
cykliczne_sprawdzenia()
root.mainloop()
