from airport import *
from aircraft import *
from LEBL import *
import os
import subprocess
import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt

# =============================================================================
# VARIABLES GLOBALES (ESTADO DE LA APLICACIÓN - VERSIÓN 4 DINÁMICA)
# =============================================================================
lista_aeropuertos = []
lista_llegadas = []
lista_salidas = []
lista_movimientos_merged = []
objeto_lebl = None

# Variable de control de tiempo para la simulación interactiva por horas
hora_actual_simulacion = 0

# =============================================================================
# PALETA DE COLORES RE-ESTRUCTURADA Y COHERENTE
# =============================================================================
COLOR_BG = "#f8f9fa"  # Gris muy claro y limpio para el fondo general

# Bloques y jerarquías de botones
COLOR_BTN_NEUTRAL = "#e9ecef"  # Gris neutro para cargas de archivos (.txt) y guardados
COLOR_BTN_PRIMARY = "#e8f4fd"  # Azul suave para análisis y funciones principales (Gráficos, KML, Merge)
COLOR_BTN_SUCCESS = "#d4edda"  # Verde pastel para añadir manual e inicializar aviones nocturnos
COLOR_BTN_ALERT = "#f8d7da"  # Rosa/Rojo pastel para acciones destructivas o de borrado
COLOR_ASIGNAR = "#17a2b8"  # Cian destacado para el motor dinámico de asignación horaria

# =============================================================================
# VENTANA PRINCIPAL Y COMPONENTES BASE (Para evitar Unresolved Reference)
# =============================================================================
root = tk.Tk()
root.title("Airport Tool - University Dynamic Gate System (V4 Final)")
root.geometry("1450x880")
root.configure(bg=COLOR_BG)

frame_izquierdo = tk.Frame(root, bg=COLOR_BG)
frame_izquierdo.pack(side="left", padx=20, pady=10, fill="y")

frame_derecho = tk.Frame(root, bg=COLOR_BG)
frame_derecho.pack(side="right", padx=20, pady=10, fill="both", expand=True)

# Monitor gráfico derecho e inicialización del Canvas para las funciones de dibujo
tk.Label(frame_derecho, text="DIAGRAMA DE OCUPACIÓN COMPLETO EN TIEMPO REAL", font=("Arial", 13, "bold"),
         bg=COLOR_BG, fg="#000000").pack(pady=5)

canvas_frame = tk.Frame(frame_derecho, bg="#ffffff")
canvas_frame.pack(fill="both", expand=True, pady=5)

canvas_visualizador = tk.Canvas(canvas_frame, bg="#ffffff", bd=2, relief="sunken", highlightthickness=0)
canvas_visualizador.pack(side="left", fill="both", expand=True)

scrollbar_v = tk.Scrollbar(canvas_frame, orient="vertical", command=canvas_visualizador.yview)
scrollbar_v.pack(side="right", fill="y")

canvas_visualizador.config(yscrollcommand=scrollbar_v.set)


# =============================================================================
# MOTOR DE DIBUJO ESQUEMÁTICO EN ÁRBOL COLUMNAS PARALELAS (T1 / T2)
# =============================================================================
def ActualizarDiagramaVisual(bcn):
    """Limpia el lienzo del Canvas y dibuja las terminales distribuidas lado a lado."""
    canvas_visualizador.delete("all")
    if not bcn or not hasattr(bcn, 'terminals'):
        return

    y_maxima_alcanzada = 50

    for t_idx, terminal in enumerate(bcn.terminals):
        if t_idx == 0:
            x_inicio = 40
        else:
            x_inicio = 550

        y_actual = 50

        canvas_visualizador.create_text(x_inicio, y_actual, text=terminal.name, font=("Arial", 16, "bold"), anchor="w",
                                        fill="#005a9c")
        y_linea_terminal = y_actual
        y_actual += 40

        for area in terminal.boarding_areas:
            canvas_visualizador.create_line(x_inicio + 15, y_linea_terminal, x_inicio + 15, y_actual, fill="#005a9c",
                                            width=3)
            canvas_visualizador.create_line(x_inicio + 15, y_actual, x_inicio + 45, y_actual, fill="#005a9c", width=3)

            tipo_zona = "Schengen" if area.type else "non-Schengen"
            canvas_visualizador.create_text(x_inicio + 55, y_actual, text=f"Area {area.name} ({tipo_zona})",
                                            font=("Arial", 11, "bold"), anchor="w", fill="#000000")

            y_linea_area = y_actual
            y_actual += 30

            for gate in area.gates:
                canvas_visualizador.create_line(x_inicio + 70, y_linea_area, x_inicio + 70, y_actual, fill="#005a9c",
                                                width=2)
                canvas_visualizador.create_line(x_inicio + 70, y_actual, x_inicio + 100, y_actual, fill="#005a9c",
                                                width=2)

                color_cuadro = "#dc3545" if gate.occupied else "#28a745"
                canvas_visualizador.create_rectangle(x_inicio + 100, y_actual - 9, x_inicio + 118, y_actual + 9,
                                                     fill=color_cuadro, outline="#000000", width=1.5)
                canvas_visualizador.create_text(x_inicio + 130, y_actual, text=gate.name, font=("Courier", 11, "bold"),
                                                anchor="w", fill="#000000")

                if gate.occupied:
                    info_avion = f" ➔ MATRÍCULA: {gate.aircraft}"
                    canvas_visualizador.create_text(x_inicio + 200, y_actual, text=info_avion,
                                                    font=("Arial", 11, "bold"), anchor="w", fill="#b22222")

                y_actual += 26
            y_actual += 15
        y_actual += 20

        if y_actual > y_maxima_alcanzada:
            y_maxima_alcanzada = y_actual

    canvas_visualizador.config(scrollregion=(0, 0, 1100, y_maxima_alcanzada + 50))


# =============================================================================
# FUNCIONES CONTROLADORAS (BLOQUE 2: BASE DE DATOS MUNDIAL)
# =============================================================================

def ejecutar_cargar():
    """Lee el archivo plano 'Airports.txt' y carga los aeropuertos en la lista global."""
    global lista_aeropuertos
    lista_aeropuertos = LoadAirports("Airports.txt")
    messagebox.showinfo("Éxito", "Airports.txt cargado correctamente.")


def ejecutar_anyadir():
    """Recupera el texto de los campos manuales e inserta un nuevo aeropuerto."""
    c = entrada_code.get().upper()
    try:
        la = float(entrada_lat.get())
        lo = float(entrada_lon.get())
        nuevo = Airport(c, la, lo)
        AddAirport(lista_aeropuertos, nuevo)
        messagebox.showinfo("Éxito", f"Aeropuerto {c} añadido.")
    except ValueError:
        messagebox.showerror("Error", "Datos numéricos incorrectos en campos Lat/Lon.")


def ejecutar_borrar():
    """Busca el código ICAO introducido y lo elimina de la base de datos temporal."""
    c = entrada_code.get().upper()
    RemoveAirport(lista_aeropuertos, c)
    messagebox.showinfo("Éxito", f"Aeropuerto {c} eliminado.")


def ejecutar_validar():
    """Recorre todos los aeropuertos evaluando si pertenecen al espacio Schengen."""
    global lista_aeropuertos
    i = 0
    while i < len(lista_aeropuertos):
        SetSchengen(lista_aeropuertos[i])
        i = i + 1
    messagebox.showinfo("Éxito", "Validación Schengen completada.")


def ejecutar_analisis_completo():
    """Botón Sección 2: Lanza los 3 gráficos operacionales basados en tus capturas"""
    global lista_movimientos_merged
    if not lista_movimientos_merged:
        messagebox.showwarning("Atención", "Debes cargar los movimientos y realizar la fusión (Merge) primero.")
        return

    PlotArrivalsPerHour(lista_movimientos_merged)
    PlotFlightsPerAirline(lista_movimientos_merged)
    PlotSchengenProportion(lista_movimientos_merged)


def ejecutar_plot_ocupacion_completa():
    """Botón Sección 4: Lanza el gráfico de líneas de ocupación T1/T2 reconstruyendo las 24 horas"""
    global objeto_lebl, lista_movimientos_merged
    if not objeto_lebl or not lista_movimientos_merged:
        messagebox.showwarning("Atención", "Estructura y movimientos unificados obligatorios.")
        return

    # Llamamos a tu gráfica necesaria pasando los objetos de la interfaz
    PlotDayOccupancy(objeto_lebl, lista_movimientos_merged)

def ejecutar_mapa():
    """Genera el mapa de marcas geográficas KML e intenta abrirlo en el sistema."""
    MapAirports(lista_aeropuertos)
    if os.path.exists("airports.kml"):
        try:
            if hasattr(os, 'startfile'):
                os.startfile("airports.kml")
            else:
                subprocess.call(["open", "-e", "airports.kml"])
        except:
            messagebox.showerror("Error", "No se pudo abrir automáticamente el archivo KML.")
    else:
        messagebox.showerror("Error", "No se encontró el fichero 'airports.kml'.")


def ejecutar_guardar():
    """Exporta los aeropuertos validados como Schengen a un fichero de texto."""
    SaveSchengenAirports(lista_aeropuertos, "Schengen_Solo.txt")
    messagebox.showinfo("Éxito", "Archivo Schengen_Solo.txt guardado con éxito.")


# =============================================================================
# FUNCIONES CONTROLADORAS (BLOQUE 3: OPERACIONES LEBL DINÁMICAS)
# =============================================================================

def ejecutar_cargar_lebl():
    """Carga la estructura física base del aeropuerto (Terminals.txt)."""
    global objeto_lebl
    objeto_lebl = LoadAirportStructure("Terminals.txt")
    if objeto_lebl == -1 or not objeto_lebl or len(objeto_lebl.terminals) == 0:
        messagebox.showerror("Error", "No se pudo procesar Terminals.txt.")
    else:
        ActualizarDiagramaVisual(objeto_lebl)


def ejecutar_cargar_vuelos():
    """Carga de forma separada las llegadas (Arrivals.txt)."""
    global lista_llegadas
    lista_llegadas = LoadArrivals("Arrivals.txt")
    messagebox.showinfo("Éxito", "Arrivals.txt cargado correctamente en memoria.")


def ejecutar_cargar_salidas():
    global lista_salidas
    lista_salidas = LoadDepartures("Departures.txt")
    if isinstance(lista_salidas, int) or not lista_salidas:
        messagebox.showerror("Error", "Error al abrir o procesar Departures.txt.")
    else:
        messagebox.showinfo("Éxito", f"Departures.txt cargado. {len(lista_salidas)} salidas detectadas.")


def ejecutar_unificar_movimientos():
    """Ejecuta MergeMovements para entrelazar arribos y despegues diarios."""
    global lista_llegadas, lista_salidas, lista_movimientos_merged
    if not lista_llegadas or not lista_salidas:
        messagebox.showwarning("Atención", "Debes cargar tanto Arrivals.txt como Departures.txt primero.")
        return

    lista_movimientos_merged = MergeMovements(lista_llegadas, lista_salidas)
    messagebox.showinfo("Éxito", f"Fusión completada. {len(lista_movimientos_merged)} aeronaves consolidadas.")


def ejecutar_preparar_noche():
    """Detecta y posiciona los aviones nocturnos (NightAircraft) en sus puertas de origen."""
    global objeto_lebl, lista_movimientos_merged
    if not objeto_lebl or not lista_movimientos_merged:
        messagebox.showwarning("Atención", "Estructura cargada y Movimientos unificados requeridos.")
        return

    lista_nocturnos = NightAircraft(lista_movimientos_merged)
    AssignNightGates(objeto_lebl, lista_nocturnos)
    ActualizarDiagramaVisual(objeto_lebl)
    messagebox.showinfo("Éxito", f"Aviones nocturnos posicionados en sus puertas de salida.")


def ejecutar_simular_hora():
    global objeto_lebl, lista_movimientos_merged, hora_actual_simulacion
    if not objeto_lebl or not lista_movimientos_merged:
        return

    # Sincronizamos la lectura con el valor que tenga el control deslizable
    hora_actual_simulacion = int(slider_tiempo.get())
    string_hora = f"{hora_actual_simulacion:02d}:00"

    # Procesamos la simulación para ese tramo
    no_asignados = AllocateGatesDynamic(objeto_lebl, lista_movimientos_merged, string_hora)

    # Actualizamos el lienzo visual
    ActualizarDiagramaVisual(objeto_lebl)
    label_status_hora.config(text=f"Hora Activa: {string_hora} | No asignados en este tramo: {no_asignados}")


# =============================================================================
# CONSTRUCCIÓN DE LA ARQUITECTURA DE LA VENTANA (BOTONES Y MARCOS)
# =============================================================================
tk.Label(frame_izquierdo, text="PANEL DE CONTROL GENERAL", font=("Arial", 14, "bold"), bg=COLOR_BG,
         fg="#000000").pack(pady=10)

# SECTION 1: Añadir Aeropuerto Manual
marco_datos = tk.LabelFrame(frame_izquierdo, text=" 1. Añadir Aeropuerto Manual ", font=("Arial", 10, "bold"),
                            bg=COLOR_BG, fg="#000000", padx=10, pady=5)
marco_datos.pack(pady=5, fill="x")

tk.Label(marco_datos, text="ICAO:", font=("Arial", 9, "bold"), bg=COLOR_BG, fg="#000000").grid(row=0, column=0, padx=2)
entrada_code = tk.Entry(marco_datos, width=6, font=("Arial", 10))
entrada_code.grid(row=0, column=1, padx=4, pady=5)

tk.Label(marco_datos, text="Lat:", font=("Arial", 9, "bold"), bg=COLOR_BG, fg="#000000").grid(row=0, column=2, padx=2)
entrada_lat = tk.Entry(marco_datos, width=8, font=("Arial", 10))
entrada_lat.grid(row=0, column=3, padx=4)

tk.Label(marco_datos, text="Lon:", font=("Arial", 9, "bold"), bg=COLOR_BG, fg="#000000").grid(row=0, column=4, padx=2)
entrada_lon = tk.Entry(marco_datos, width=8, font=("Arial", 10))
entrada_lon.grid(row=0, column=5, padx=4)

# SECTION 2: Gestión de Base de Datos Mundial
marco_gestion = tk.LabelFrame(frame_izquierdo, text=" 2. Base de Datos Mundial ", font=("Arial", 10, "bold"),
                              bg=COLOR_BG, fg="#000000", padx=5, pady=5)
marco_gestion.pack(pady=5, fill="x")

tk.Button(marco_gestion, text="Cargar Airports.txt", width=18, pady=6, bg=COLOR_BTN_NEUTRAL,
          highlightbackground=COLOR_BTN_NEUTRAL, font=("Arial", 9, "bold"), command=ejecutar_cargar).grid(row=0,
                                                                                                          column=0,
                                                                                                          padx=4,
                                                                                                          pady=4)
tk.Button(marco_gestion, text="Añadir Manual", width=18, pady=6, bg=COLOR_BTN_SUCCESS,
          highlightbackground=COLOR_BTN_SUCCESS, font=("Arial", 9, "bold"), command=ejecutar_anyadir).grid(row=0,
                                                                                                           column=1,
                                                                                                           padx=4,
                                                                                                           pady=4)
tk.Button(marco_gestion, text="Borrar por ICAO", width=18, pady=6, bg=COLOR_BTN_ALERT,
          highlightbackground=COLOR_BTN_ALERT, font=("Arial", 9, "bold"), command=ejecutar_borrar).grid(row=1, column=0,
                                                                                                        padx=4, pady=4)
tk.Button(marco_gestion, text="Validar Schengen", width=18, pady=6, bg=COLOR_BTN_PRIMARY,
          highlightbackground=COLOR_BTN_PRIMARY, font=("Arial", 9, "bold"), command=ejecutar_validar).grid(row=1,
                                                                                                           column=1,
                                                                                                           padx=4,
                                                                                                           pady=4)

# El botón de estadísticas ahora está perfectamente integrado en la cuadrícula del bloque 2
tk.Button(marco_gestion, text="Ver Análisis de Estadísticas", width=18, pady=6, bg=COLOR_BTN_PRIMARY,
          highlightbackground=COLOR_BTN_PRIMARY, font=("Arial", 9, "bold"), command=ejecutar_analisis_completo).grid(
    row=2, column=0,
    padx=4, pady=4)

tk.Button(marco_gestion, text="Mapa Google Earth", width=18, pady=6, bg=COLOR_BTN_PRIMARY,
          highlightbackground=COLOR_BTN_PRIMARY, font=("Arial", 9, "bold"), command=ejecutar_mapa).grid(row=2, column=1,
                                                                                                        padx=4, pady=4)

tk.Button(marco_gestion, text="Guardar solo Schengen", width=38, pady=6, bg=COLOR_BTN_NEUTRAL,
          highlightbackground=COLOR_BTN_NEUTRAL, font=("Arial", 9, "bold"), command=ejecutar_guardar).grid(row=3,
                                                                                                           column=0,
                                                                                                           columnspan=2,
                                                                                                           pady=6)

# SECTION 3: Núcleo de Operaciones Dinámicas LEBL
marco_lebl = tk.LabelFrame(frame_izquierdo, text=" 3. Procesamiento Dinámico LEBL ", font=("Arial", 10, "bold"),
                           bg=COLOR_BG, fg="#000000", padx=5, pady=5)
marco_lebl.pack(pady=5, fill="x")

tk.Button(marco_lebl, text="1. Estructura (Terminals.txt)", width=38, pady=6, bg=COLOR_BTN_NEUTRAL,
          highlightbackground=COLOR_BTN_NEUTRAL, font=("Arial", 9, "bold"), command=ejecutar_cargar_lebl).grid(row=0,
                                                                                                               column=0,
                                                                                                               columnspan=2,
                                                                                                               pady=3)
tk.Button(marco_lebl, text="2a. Cargar Arrivals.txt", width=18, pady=6, bg=COLOR_BTN_NEUTRAL,
          highlightbackground=COLOR_BTN_NEUTRAL, font=("Arial", 9, "bold"), command=ejecutar_cargar_vuelos).grid(row=1,
                                                                                                                 column=0,
                                                                                                                 padx=4,
                                                                                                                 pady=3)
tk.Button(marco_lebl, text="2b. Cargar Departures.txt", width=18, pady=6, bg=COLOR_BTN_NEUTRAL,
          highlightbackground=COLOR_BTN_NEUTRAL, font=("Arial", 9, "bold"), command=ejecutar_cargar_salidas).grid(row=1,
                                                                                                                  column=1,
                                                                                                                  padx=4,
                                                                                                                  pady=3)

tk.Button(marco_lebl, text="3. Fusionar Movimientos (Merge)", width=38, pady=6, bg=COLOR_BTN_PRIMARY,
          highlightbackground=COLOR_BTN_PRIMARY, font=("Arial", 9, "bold"), command=ejecutar_unificar_movimientos).grid(
    row=2, column=0, columnspan=2, pady=4)

tk.Button(marco_lebl, text="4. Posicionar Aviones Nocturnos", width=38, pady=6, bg=COLOR_BTN_SUCCESS,
          highlightbackground=COLOR_BTN_SUCCESS, font=("Arial", 9, "bold"), command=ejecutar_preparar_noche).grid(row=3,
                                                                                                                  column=0,
                                                                                                                  columnspan=2,
                                                                                                                  pady=4)

# SECTION 4: Control Deslizable y Simulación Temporal Interactiva
marco_simulacion = tk.LabelFrame(frame_izquierdo, text=" 4. Línea de Tiempo / Análisis Activo ",
                                 font=("Arial", 10, "bold"), bg=COLOR_BG, fg="#000000", padx=5, pady=5)
marco_simulacion.pack(pady=5, fill="x")

label_status_hora = tk.Label(marco_simulacion, text="Hora Activa: 00:00 | Listo para simular",
                             font=("Arial", 9, "bold"), bg=COLOR_BG, fg="#005a9c")
label_status_hora.pack(pady=2)

# Slider configurado para actualizarse únicamente al soltar el ratón
slider_tiempo = tk.Scale(marco_simulacion, from_=0, to=23, orient="horizontal", tickinterval=4, font=("Arial", 8),
                         bg=COLOR_BG)
slider_tiempo.pack(fill="x", padx=5, pady=5)

# Evento exclusivo para que la simulación no cause micro-tirones durante el arrastre
slider_tiempo.bind("<ButtonRelease-1>", lambda event: ejecutar_simular_hora())

tk.Button(marco_simulacion, text="Graficar Ocupación de Todo el Día", width=38, pady=8, bg=COLOR_ASIGNAR,
          highlightbackground=COLOR_ASIGNAR, font=("Arial", 9, "bold"), fg="black",
          command=ejecutar_plot_ocupacion_completa).pack(pady=6)

# =============================================================================
# ACTIVACIÓN DE LA APLICACIÓN
# =============================================================================
root.mainloop()