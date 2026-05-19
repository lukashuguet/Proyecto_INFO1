from airport import *
from aircraft import *
import LEBL
import os
import subprocess
import tkinter as tk
from tkinter import messagebox

lista_aeropuertos = []
lista_vuelos = []
objeto_lebl = None


def ejecutar_cargar():
    global lista_aeropuertos
    lista_aeropuertos = LoadAirports("Airports.txt")
    messagebox.showinfo("Éxito", "Airports.txt cargado correctamente.")


def ejecutar_anyadir():
    c = entrada_code.get().upper()
    try:
        la = float(entrada_lat.get())
        lo = float(entrada_lon.get())
        nuevo = Airport(c, la, lo)
        AddAirport(lista_aeropuertos, nuevo)
        messagebox.showinfo("Éxito", f"Aeropuerto {c} añadido.")
    except:
        messagebox.showerror("Error", "Datos numéricos incorrectos.")


def ejecutar_borrar():
    c = entrada_code.get().upper()
    RemoveAirport(lista_aeropuertos, c)
    messagebox.showinfo("Éxito", f"Aeropuerto {c} eliminado.")


def ejecutar_validar():
    global lista_aeropuertos
    i = 0
    while i < len(lista_aeropuertos):
        SetSchengen(lista_aeropuertos[i])
        i = i + 1
    messagebox.showinfo("Éxito", "Validación Schengen completada.")


def ejecutar_grafico():
    PlotArrivals(lista_vuelos)


def ejecutar_mapa():
    MapAirports(lista_aeropuertos)
    if os.path.exists("airports.kml"):
        try:
            if hasattr(os, 'startfile'):
                os.startfile("airports.kml")
            else:
                subprocess.call(["open", "-e", "airports.kml"])
        except:
            messagebox.showerror("Error", "No se pudo abrir automáticamente el KML.")
    else:
        messagebox.showerror("Error", "No se encontró airports.kml")


def ejecutar_guardar():
    SaveSchengenAirports(lista_aeropuertos, "Schengen_Solo.txt")
    messagebox.showinfo("Éxito", "Archivo Schengen_Solo.txt guardado.")


def ejecutar_cargar_lebl():
    global objeto_lebl
    objeto_lebl = LEBL.LoadAirportStructure("Terminals.txt")
    if objeto_lebl == -1 or not objeto_lebl or len(objeto_lebl.terminals) == 0:
        messagebox.showerror("Error", "No se pudo cargar Terminals.txt o está vacío.")
    else:
        actualizar_pantalla_ocupacion()


def ejecutar_cargar_vuelos():
    global lista_vuelos
    lista_vuelos = LoadArrivals("Arrivals.txt")
    messagebox.showinfo("Éxito", "Arrivals.txt cargado correctamente.")


def ejecutar_asignar_puertas():
    global objeto_lebl, lista_aeropuertos, lista_vuelos
    if not objeto_lebl or not lista_vuelos or not lista_aeropuertos:
        messagebox.showwarning("Atención", "Faltan datos por cargar (Airports, Terminals o Arrivals).")
        return

    ejecutar_validar()
    for i in range(len(lista_vuelos)):
        vuelo = lista_vuelos[i]
        aeropuerto_origen = FindAirport(lista_aeropuertos, vuelo.origin)
        es_schengen = aeropuerto_origen.schengen if aeropuerto_origen else False
        LEBL.AssignGate(objeto_lebl, vuelo, es_schengen)

    actualizar_pantalla_ocupacion()
    messagebox.showinfo("Éxito", "Puertas asignadas correctamente.")


def actualizar_pantalla_ocupacion():
    global objeto_lebl
    if not objeto_lebl: return
    txt_visualizador.delete("1.0", tk.END)
    datos_ocupacion = LEBL.GateOccupancy(objeto_lebl)

    resumen_texto = "=== MONITOR DE PUERTAS LEBL ===\n\n"
    if not datos_ocupacion:
        resumen_texto += "No se encontraron puertas cargadas en la estructura.\n"
    else:
        for i in range(len(datos_ocupacion)):
            p = datos_ocupacion[i]
            estado = "[OCUPADA]" if p['occupied'] else "[LIBRE]"
            avion = f"-> Avión: {p['aircraft']}" if p['occupied'] else ""
            resumen_texto += f"Puerta: {p['gate']:5} | {p['terminal']} | {estado:9} {avion}\n"

    txt_visualizador.insert(tk.END, resumen_texto)


# INTERFAZ GRÁFICA MAC-FRIENDLY
root = tk.Tk()
root.title("Airport Tool - University Management System")
root.geometry("1100x650")
root.configure(bg="#f8f9fa")

frame_izquierdo = tk.Frame(root, bg="#f8f9fa")
frame_izquierdo.pack(side="left", padx=20, pady=10, fill="y")

frame_derecho = tk.Frame(root, bg="#f8f9fa")
frame_derecho.pack(side="right", padx=20, pady=10, fill="both", expand=True)

tk.Label(frame_izquierdo, text="PANEL DE CONFIGURACIÓN", font=("Arial", 13, "bold"), bg="#f8f9fa", fg="#212529").pack(
    pady=10)

# BLOQUE 1
marco_datos = tk.LabelFrame(frame_izquierdo, text=" 1. Añadir Aeropuerto Manual ", font=("Arial", 10, "bold"),
                            bg="#f8f9fa", fg="#212529", padx=10, pady=5)
marco_datos.pack(pady=8, fill="x")

tk.Label(marco_datos, text="ICAO:", font=("Arial", 9, "bold"), bg="#f8f9fa").grid(row=0, column=0, padx=4)
entrada_code = tk.Entry(marco_datos, width=7, font=("Arial", 10))
entrada_code.grid(row=0, column=1, padx=4, pady=10)

tk.Label(marco_datos, text="Lat:", font=("Arial", 9, "bold"), bg="#f8f9fa").grid(row=0, column=2, padx=4)
entrada_lat = tk.Entry(marco_datos, width=9, font=("Arial", 10))
entrada_lat.grid(row=0, column=3, padx=4)

tk.Label(marco_datos, text="Lon:", font=("Arial", 9, "bold"), bg="#f8f9fa").grid(row=0, column=4, padx=4)
entrada_lon = tk.Entry(marco_datos, width=9, font=("Arial", 10))
entrada_lon.grid(row=0, column=5, padx=4)

# BLOQUE 2
marco_gestion = tk.LabelFrame(frame_izquierdo, text=" 2. Base de Datos Mundial ", font=("Arial", 10, "bold"),
                              bg="#f8f9fa", fg="#212529", padx=10, pady=10)
marco_gestion.pack(pady=8, fill="x")

tk.Button(marco_gestion, text="Cargar Airports.txt", width=18, pady=8, bg="#e2e6ea", highlightbackground="#e2e6ea",
          fg="black", font=("Arial", 9, "bold"), command=ejecutar_cargar).grid(row=0, column=0, padx=6, pady=6)
tk.Button(marco_gestion, text="Añadir Manual", width=18, pady=8, bg="#d4edda", highlightbackground="#d4edda",
          fg="black", font=("Arial", 9, "bold"), command=ejecutar_anyadir).grid(row=0, column=1, padx=6, pady=6)
tk.Button(marco_gestion, text="Borrar por ICAO", width=18, pady=8, bg="#f8d7da", highlightbackground="#f8d7da",
          fg="black", font=("Arial", 9, "bold"), command=ejecutar_borrar).grid(row=1, column=0, padx=6, pady=6)
tk.Button(marco_gestion, text="Validar Schengen", width=18, pady=8, bg="#e2e6ea", highlightbackground="#e2e6ea",
          fg="black", font=("Arial", 9, "bold"), command=ejecutar_validar).grid(row=1, column=1, padx=6, pady=6)
tk.Button(marco_gestion, text="Ver Gráfico", width=18, pady=8, bg="#e8f4fd", highlightbackground="#e8f4fd", fg="black",
          font=("Arial", 9, "bold"), command=ejecutar_grafico).grid(row=2, column=0, padx=6, pady=6)
tk.Button(marco_gestion, text="Mapa Google Earth", width=18, pady=8, bg="#e8f4fd", highlightbackground="#e8f4fd",
          fg="black", font=("Arial", 9, "bold"), command=ejecutar_mapa).grid(row=2, column=1, padx=6, pady=6)
tk.Button(marco_gestion, text="Guardar solo Schengen", width=39, pady=8, bg="#cce5ff", highlightbackground="#cce5ff",
          fg="black", font=("Arial", 10, "bold"), command=ejecutar_guardar).grid(row=3, column=0, columnspan=2, pady=8)

# BLOQUE 3
marco_lebl = tk.LabelFrame(frame_izquierdo, text=" 3. Operaciones LEBL ", font=("Arial", 10, "bold"), bg="#f8f9fa",
                           fg="#212529", padx=10, pady=10)
marco_lebl.pack(pady=12, fill="x")

tk.Button(marco_lebl, text="1. Cargar Estructura\n(Terminals.txt)", width=18, pady=8, bg="#fff3cd",
          highlightbackground="#fff3cd", fg="black", font=("Arial", 9, "bold"), command=ejecutar_cargar_lebl).grid(
    row=0, column=0, padx=6, pady=6)
tk.Button(marco_lebl, text="2. Cargar Tráfico\n(Arrivals.txt)", width=18, pady=8, bg="#fff3cd",
          highlightbackground="#fff3cd", fg="black", font=("Arial", 9, "bold"), command=ejecutar_cargar_vuelos).grid(
    row=0, column=1, padx=6, pady=6)
tk.Button(marco_lebl, text="3. Asignar Asignación Estática", width=39, pady=12, bg="#17a2b8",
          highlightbackground="#17a2b8", fg="black", font=("Arial", 10, "bold"), command=ejecutar_asignar_puertas).grid(
    row=1, column=0, columnspan=2, pady=12)

# MONITOR DERECHO
tk.Label(frame_derecho, text="MONITOR DE PUERTAS EN TIEMPO REAL", font=("Arial", 12, "bold"), bg="#f8f9fa",
         fg="#212529").pack(pady=10)

# El cuadro se crea limpio y configurado en letras negras
txt_visualizador = tk.Text(frame_derecho, width=65, height=32, wrap="none", font=("Courier", 11, "bold"),
                           bg="#ffffff", fg="#000000", bd=2, relief="sunken")
txt_visualizador.pack(fill="both", expand=True, pady=5)

root.mainloop()