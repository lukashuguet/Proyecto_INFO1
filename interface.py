"""
MÓDULO INTERFACE.PY
Este archivo contiene toda la interfaz gráfica (GUI) del proyecto.
Se encarga exclusivamente de recoger las acciones del usuario (botones, inputs)
y mostrar los resultados (textos, gráficos, diagrama visual).
La lógica compleja y los cálculos se importan de LEBL.py y aircraft.py.
"""

import tkinter as tk
from tkinter import ttk
from aircraft import *
from LEBL import *
import subprocess
import os
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

# =============================================================================
# VARIABLES GLOBALES (ESTADO DE LA APLICACIÓN)
# =============================================================================
# Estas variables actúan como la "memoria" temporal del programa mientras está abierto.
lista_aeropuertos = []
lista_llegadas = []
lista_salidas = []
lista_movimientos_merged = []
objeto_lebl = None
hora_actual_simulacion = 0

# =============================================================================
# PALETA DE COLORES
# =============================================================================
# Definir los colores aquí arriba permite cambiar el "tema" de la aplicación
# entera cambiando un solo código hexadecimal.
COLOR_BG = "#f8f9fa"  # Gris muy claro (fondo general)
COLOR_BTN_NEUTRAL = "#e9ecef"  # Gris claro (botones de carga)
COLOR_BTN_PRIMARY = "#e8f4fd"  # Azul clarito (acciones principales)
COLOR_BTN_SUCCESS = "#d4edda"  # Verde claro (acciones positivas/guardar)
COLOR_BTN_ALERT = "#f8d7da"  # Rojo claro (acciones de borrar/peligro)
COLOR_ASIGNAR = "#17a2b8"  # Azul verdoso (botones de graficar)

# =============================================================================
# CONFIGURACIÓN DE LA VENTANA PRINCIPAL
# =============================================================================
root = tk.Tk()
root.title("Gestión Aeroportuaria")
root.geometry("1920x1080")  # Resolución recomendada
root.configure(bg=COLOR_BG)

# =============================================================================
# ZONA INFERIOR DE NOTIFICACIONES
# =============================================================================
# Esta barra abajo del todo sirve para dar feedback al usuario (Errores, Éxitos, etc.)
marco_notificaciones = tk.Frame(root, bg=COLOR_BG, bd=1, relief="sunken", height=40)
marco_notificaciones.pack_propagate(False)  # Evita que el marco se encoja
marco_notificaciones.pack(side="bottom", fill="x", padx=0, pady=0)

label_info = tk.Label(marco_notificaciones, text="Información: Sistema listo.", bg=COLOR_BG, fg="black",
                      font=("Arial", 10, "italic"), anchor="w", justify="left")
label_info.pack(side="left", fill="both", expand=True, padx=10)

# =============================================================================
# ESTRUCTURA DE PESTAÑAS (NOTEBOOK)
# =============================================================================
# 1. Contenedor principal de pestañas
notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True, padx=5, pady=5)

# 2. Creación de las "carpetas" (Frames que irán dentro de cada pestaña)
pestana_control = tk.Frame(notebook, bg=COLOR_BG)
pestana_graficos = tk.Frame(notebook, bg=COLOR_BG)
pestana_grafico1 = tk.Frame(notebook, bg=COLOR_BG)  # Detalle Llegadas
pestana_grafico2 = tk.Frame(notebook, bg=COLOR_BG)  # Detalle Aerolíneas
pestana_grafico3 = tk.Frame(notebook, bg=COLOR_BG)  # Detalle Schengen
pestana_grafico4 = tk.Frame(notebook, bg=COLOR_BG)  # Detalle Ocupación 24h

# 3. Añadimos los Frames al menú superior visible
notebook.add(pestana_control, text=" Panel de Control ")
notebook.add(pestana_graficos, text=" Dashboard General ")
notebook.add(pestana_grafico1, text=" Llegadas/Hora ")
notebook.add(pestana_grafico2, text=" Vuelos/Aerolínea ")
notebook.add(pestana_grafico3, text=" Schengen ")
notebook.add(pestana_grafico4, text=" Ocupación 24h ")

# --- DISEÑO DE LA PESTAÑA 1 (CONTROL) - USANDO GRID ---
# Dividimos la pestaña principal en dos columnas. La derecha (diagrama) es más ancha.
pestana_control.columnconfigure(0, weight=0)  # Panel de botones (estrecho)
pestana_control.columnconfigure(1, weight=9)  # Panel visualizador (ancho)
pestana_control.rowconfigure(0, weight=1)  # Que ocupe toda la altura de la pantalla

frame_izquierdo = tk.Frame(pestana_control, bg=COLOR_BG)
frame_izquierdo.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

frame_derecho = tk.Frame(pestana_control, bg=COLOR_BG)
frame_derecho.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

# --- DISEÑO DE LA PESTAÑA 2 (DASHBOARD GENERAL) - 4 CUADRANTES ---
pestana_graficos.columnconfigure(0, weight=1, uniform="grupo1")
pestana_graficos.columnconfigure(1, weight=1, uniform="grupo1")
pestana_graficos.rowconfigure(0, weight=1, uniform="grupo1")
pestana_graficos.rowconfigure(1, weight=1, uniform="grupo1")

marco_grafico_1 = tk.Frame(pestana_graficos, bg=COLOR_BG, bd=2, relief="groove")
marco_grafico_1.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

marco_grafico_2 = tk.Frame(pestana_graficos, bg=COLOR_BG, bd=2, relief="groove")
marco_grafico_2.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

marco_grafico_3 = tk.Frame(pestana_graficos, bg=COLOR_BG, bd=2, relief="groove")
marco_grafico_3.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

marco_grafico_4 = tk.Frame(pestana_graficos, bg=COLOR_BG, bd=2, relief="groove")
marco_grafico_4.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)

# =============================================================================
# MONITOR GRÁFICO DERECHO (DIBUJO DE TERMINALES)
# =============================================================================
tk.Label(frame_derecho, text="DIAGRAMA DE OCUPACIÓN COMPLETO EN TIEMPO REAL", font=("Arial", 13, "bold"), bg=COLOR_BG,
         fg="#000000").pack(pady=5)

canvas_frame = tk.Frame(frame_derecho, bg="#ffffff")
canvas_frame.pack(fill="both", expand=True, pady=5)

# 1. Barras de desplazamiento para el plano del aeropuerto
scrollbar_v = tk.Scrollbar(canvas_frame, orient="vertical")
scrollbar_h = tk.Scrollbar(canvas_frame, orient="horizontal")

# 2. Canvas (el "lienzo" donde pintamos figuras geométricas)
canvas_visualizador = tk.Canvas(canvas_frame, bg="#ffffff", bd=2, relief="sunken", highlightthickness=0,
                                yscrollcommand=scrollbar_v.set, xscrollcommand=scrollbar_h.set)

# Empaquetamos todo
scrollbar_v.pack(side="right", fill="y")
scrollbar_h.pack(side="bottom", fill="x")
canvas_visualizador.pack(side="left", fill="both", expand=True)

# Conectamos las barras para que actúen sobre el Canvas
scrollbar_v.config(command=canvas_visualizador.yview)
scrollbar_h.config(command=canvas_visualizador.xview)


# =============================================================================
# FUNCIONES AUXILIARES DE INTERFAZ
# =============================================================================
def mostrar_notificacion(mensaje):
    """Actualiza la barra inferior con mensajes de estado o error."""
    label_info.config(text="Información: " + str(mensaje))


def actualizar_tabla_aeropuertos():
    """Vuelca la lista global de aeropuertos en la tabla visual (Treeview)."""
    global lista_aeropuertos

    # 1. Borrar lo que haya en la tabla para no duplicar
    # Obtenemos los elementos y los recorremos con un índice
    elementos_tabla = tabla_aeropuertos.get_children()

    i = 0
    while i < len(elementos_tabla):
        tabla_aeropuertos.delete(elementos_tabla[i])
        i = i + 1

    # 2. Recorrer la lista de objetos e insertarlos (¡Tu lógica perfecta!)
    j = 0
    while j < len(lista_aeropuertos):
        ap = lista_aeropuertos[j]

        if ap.schengen == True:
            schengen_str = "Sí"
        else:
            schengen_str = "No"

        # Concatenación clásica
        texto_coordenadas = "Lat: " + str(ap.coordinates[0]) + "  Lon: " + str(ap.coordinates[1])

        # Llamada a la interfaz (asumiendo que es obligatorio para el proyecto)
        tabla_aeropuertos.insert("", "end", values=(ap.icao, texto_coordenadas, schengen_str))

        j = j + 1


def incrustar_grafico(figura, marco_destino):
    """Coge un gráfico de Matplotlib y lo mete dentro de un Frame de Tkinter."""

    # 1. Obtenemos la lista de elementos (widgets) que hay en el marco
    elementos = marco_destino.winfo_children()

    # 2. Recorremos la lista para destruirlos
    i = 0
    while i < len(elementos):
        elementos[i].destroy()
        i = i + 1

    # 3. Traducimos la figura a un formato que Tkinter entienda
    canvas = FigureCanvasTkAgg(figura, master=marco_destino)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)


def crear_placeholder(marco_destino, titulo):
    """Crea una pantalla de espera con texto para cuando no hay gráficos cargados."""
    fig_vacia = Figure(figsize=(4, 3), dpi=100, facecolor=COLOR_BG)
    ax = fig_vacia.add_subplot(111)
    texto = "[" + str(titulo) + "]\nEsperando datos..."
    ax.text(0.5, 0.5, texto, horizontalalignment='center', verticalalignment='center', fontsize=10, color='gray')
    ax.axis('off')  # Ocultamos los ejes X e Y
    incrustar_grafico(fig_vacia, marco_destino)


# =============================================================================
# MOTOR DE DIBUJO ESQUEMÁTICO REALISTA (PLANO AEROPUERTO)
# =============================================================================
def ActualizarDiagramaVisual(bcn):
    """
    Función más compleja de UI. Dibuja el aeropuerto como un mapa en 2D.
    Utiliza coordenadas matemáticas relativas para colocar pasillos y puertas.
    """
    canvas_visualizador.delete("all")  # Limpiamos el lienzo anterior
    if bcn == None:
        return

    # Rastreadores para saber el tamaño final que tendrá el lienzo desplazable
    ancho_maximo_alcanzado = 1200
    y_offset_terminal = 80  # Margen superior donde empieza a dibujar

    t_idx = 0
    while t_idx < len(bcn.terminals):
        terminal = bcn.terminals[t_idx]

        # Título principal de la Terminal (Ej: T1)
        canvas_visualizador.create_text(40, y_offset_terminal + 10, text=terminal.name, font=("Arial", 22, "bold"),
                                        anchor="e")

        num_areas = len(terminal.boarding_areas)
        if num_areas == 0:
            num_areas = 1

        # Matemáticas para la "espina dorsal" (Pasillo horizontal principal)
        x_spine_start = 60
        x_spine_end = x_spine_start + (num_areas * 260) + 50

        # Si el pasillo es muy largo, ampliamos el scroll horizontal
        if x_spine_end > ancho_maximo_alcanzado:
            ancho_maximo_alcanzado = x_spine_end + 150

        color_estructura = "#105b79"  # Azul oscuro para las infraestructuras
        canvas_visualizador.create_rectangle(x_spine_start, y_offset_terminal, x_spine_end, y_offset_terminal + 20,
                                             fill=color_estructura, outline="")

        a_idx = 0
        y_max_pier = y_offset_terminal  # Para recordar hasta dónde llegó el brazo más largo

        while a_idx < len(terminal.boarding_areas):
            area = terminal.boarding_areas[a_idx]

            x_pier = x_spine_start + 60 + (a_idx * 260)  # Posición X de cada "brazo"

            # Calculamos la longitud del brazo basada en cuántas puertas tiene
            num_gates = len(area.gates)
            separacion_vertical = 35
            largo_brazo = 40 + (num_gates * separacion_vertical)
            y_pier_end = y_offset_terminal + 20 + largo_brazo

            if y_pier_end > y_max_pier:
                y_max_pier = y_pier_end

            # Dibujamos el brazo vertical
            canvas_visualizador.create_rectangle(x_pier, y_offset_terminal + 20, x_pier + 20, y_pier_end,
                                                 fill=color_estructura, outline="")

            # Textos de cabecera (Tipo de zona y nombre) flotando encima de la barra
            if area.type == "Schengen":
                tipo_zona = "Schengen"
            else:
                tipo_zona = "non-Schengen"

            texto_area = terminal.name + area.name
            texto_schengen = "(" + tipo_zona + ")"

            canvas_visualizador.create_text(x_pier + 10, y_offset_terminal - 25, text=texto_area,
                                            font=("Arial", 12, "bold"), anchor="w", fill="#000000")
            canvas_visualizador.create_text(x_pier + 10, y_offset_terminal - 10, text=texto_schengen,
                                            font=("Arial", 10, "italic"), anchor="w", fill="#555555")

            # Bucle de dibujo de puertas (Efecto "Cremallera")
            g_idx = 0
            while g_idx < len(area.gates):
                gate = area.gates[g_idx]

                if gate.occupied == True:
                    color_puerta = "#ff0000"  # Rojo ocupado
                else:
                    color_puerta = "#00b050"  # Verde libre

                # Cada puerta baja un "escalón" propio
                y_gate = y_offset_terminal + 50 + (g_idx * separacion_vertical)

                # Puertas pares van a la izquierda del brazo, impares a la derecha
                if g_idx % 2 == 0:
                    x_line_start = x_pier
                    x_line_end = x_pier - 40

                    canvas_visualizador.create_line(x_line_start, y_gate, x_line_end, y_gate, fill=color_estructura,
                                                    width=4)
                    canvas_visualizador.create_rectangle(x_line_end - 20, y_gate - 8, x_line_end, y_gate + 8,
                                                         fill=color_puerta, outline="")
                    canvas_visualizador.create_text(x_line_end - 10, y_gate - 16, text=gate.name, font=("Arial", 8))

                    # Pintar matrícula si está ocupado
                    if gate.occupied == True:
                        canvas_visualizador.create_text(x_line_end - 28, y_gate, text=gate.aircraft,
                                                        font=("Arial", 8, "bold"), anchor="e", fill="#000000")
                else:
                    x_line_start = x_pier + 20
                    x_line_end = x_pier + 60

                    canvas_visualizador.create_line(x_line_start, y_gate, x_line_end, y_gate, fill=color_estructura,
                                                    width=4)
                    canvas_visualizador.create_rectangle(x_line_end, y_gate - 8, x_line_end + 20, y_gate + 8,
                                                         fill=color_puerta, outline="")
                    canvas_visualizador.create_text(x_line_end + 10, y_gate - 16, text=gate.name, font=("Arial", 8))

                    if gate.occupied == True:
                        canvas_visualizador.create_text(x_line_end + 28, y_gate, text=gate.aircraft,
                                                        font=("Arial", 8, "bold"), anchor="w", fill="#000000")

                g_idx += 1
            a_idx += 1

        # Antes de iterar a la siguiente terminal, bajamos el cursor Y principal
        y_offset_terminal = y_max_pier + 100
        t_idx += 1

    # Finalmente, decimos al Canvas hasta dónde nos hemos expandido para que las barras de scroll funcionen
    canvas_visualizador.config(scrollregion=(0, 0, ancho_maximo_alcanzado, y_offset_terminal + 50))


# =============================================================================
# FUNCIONES CONTROLADORAS (Acciones de los botones)
# =============================================================================
def es_valido(code, lat_str, lon_str):
    """Filtro de seguridad que valida los inputs del usuario antes de guardarlos."""
    if len(code) != 4:
        return False
    if not code.isalpha():
        return False
    try:
        lat = float(lat_str)
        lon = float(lon_str)
        if lat < -90 or lat > 90:
            return False
        if lon < -180 or lon > 180:
            return False
    except ValueError:
        return False
    return True


def ejecutar_cargar():
    """Lee el TXT y lo carga en la memoria global."""
    global lista_aeropuertos
    lista_aeropuertos = LoadAirports("Airports.txt")
    actualizar_tabla_aeropuertos()
    mostrar_notificacion("Éxito: Airports.txt cargado correctamente.")


def ejecutar_anyadir():
    """Toma datos de las casillas, los valida, y crea un objeto nuevo."""
    c = entrada_code.get().upper()
    lat_str = entrada_lat.get()
    lon_str = entrada_lon.get()

    if es_valido(c, lat_str, lon_str):
        la = float(lat_str)
        lo = float(lon_str)
        nuevo = Airport(c, la, lo)
        AddAirport(lista_aeropuertos, nuevo)
        actualizar_tabla_aeropuertos()
        mostrar_notificacion("Éxito: Aeropuerto " + str(c) + " añadido.")
    else:
        mostrar_notificacion("Error: Datos inválidos. Revisa el ICAO y las coordenadas.")


def ejecutar_borrar():
    """Borra un aeropuerto verificando primero el código ICAO."""
    c = entrada_code.get().upper()
    if len(c) == 4 and c.isalpha():
        resultado = RemoveAirport(lista_aeropuertos, c)
        if resultado == -1:
            mostrar_notificacion("Error: Aeropuerto " + c + " no encontrado.")
        else:
            actualizar_tabla_aeropuertos()
            mostrar_notificacion("Éxito: Aeropuerto " + c + " eliminado.")
    else:
        mostrar_notificacion("Error: El código ICAO debe tener 4 letras.")


def ejecutar_validar():
    """Recorre todos los aeropuertos para comprobar si pertenecen al grupo Schengen."""
    global lista_aeropuertos
    i = 0
    while i < len(lista_aeropuertos):
        SetSchengen(lista_aeropuertos[i])
        i = i + 1
    actualizar_tabla_aeropuertos()
    mostrar_notificacion("Éxito: Validación Schengen completada.")


def ejecutar_analisis_completo():
    """Genera las gráficas de Matplotlib tanto para el Dashboard como individuales."""
    global lista_movimientos_merged
    if len(lista_movimientos_merged) == 0:
        mostrar_notificacion("Atención: Debes cargar y fusionar movimientos primero.")
        return

    # 1. Gráficos para el Dashboard General
    fig1 = PlotArrivalsPerHour(lista_movimientos_merged)
    fig2 = PlotFlightsPerAirline(lista_movimientos_merged)
    fig3 = PlotSchengenProportion(lista_movimientos_merged)

    incrustar_grafico(fig1, marco_grafico_1)
    incrustar_grafico(fig2, marco_grafico_2)
    incrustar_grafico(fig3, marco_grafico_3)

    # 2. Gráficos para las Pestañas Individuales (Matplotlib necesita figuras nuevas)
    fig1_ind = PlotArrivalsPerHour(lista_movimientos_merged)
    fig2_ind = PlotFlightsPerAirline(lista_movimientos_merged)
    fig3_ind = PlotSchengenProportion(lista_movimientos_merged)

    incrustar_grafico(fig1_ind, pestana_grafico1)
    incrustar_grafico(fig2_ind, pestana_grafico2)
    incrustar_grafico(fig3_ind, pestana_grafico3)

    notebook.select(pestana_graficos)  # Cambia la vista automáticamente
    mostrar_notificacion("Éxito: Análisis estadístico generado. Pestañas actualizadas.")


def ejecutar_plot_ocupacion_completa():
    """Llama a la gráfica de 24h y la incrusta en el dashboard y pestaña dedicada."""
    global objeto_lebl, lista_movimientos_merged
    if objeto_lebl == None or len(lista_movimientos_merged) == 0:
        mostrar_notificacion("Atención: Estructura y movimientos requeridos.")
        return

    fig4 = PlotDayOccupancy(objeto_lebl, lista_movimientos_merged)
    incrustar_grafico(fig4, marco_grafico_4)

    fig4_ind = PlotDayOccupancy(objeto_lebl, lista_movimientos_merged)
    incrustar_grafico(fig4_ind, pestana_grafico4)

    notebook.select(pestana_grafico4)
    mostrar_notificacion("Éxito: Gráfica de ocupación diaria generada.")


def ejecutar_mapa():
    """Genera un archivo KML y trata de abrirlo con Google Earth en Windows/Mac."""
    global lista_aeropuertos
    if len(lista_aeropuertos) == 0:
        mostrar_notificacion("Atención: No hay aeropuertos cargados.")
    else:
        MapAirports(lista_aeropuertos)
        if os.path.exists("airports.kml"):
            try:
                if hasattr(os, 'startfile'):
                    os.startfile("airports.kml")
                else:
                    subprocess.call(["open", "-e", "airports.kml"])
            except Exception:
                pass
            mostrar_notificacion("Éxito: 'airports.kml' generado y abierto.")


def ejecutar_guardar():
    """Guarda físicamente en un archivo .txt de resultados."""
    SaveSchengenAirports(lista_aeropuertos, "Schengen_Solo.txt")
    mostrar_notificacion("Éxito: Archivo Schengen_Solo.txt guardado con éxito.")


def ejecutar_cargar_lebl():
    """Inicia la estructura del aeropuerto creando las clases Terminal, BoardingArea, etc."""
    global objeto_lebl
    objeto_lebl = LoadAirportStructure("Terminals.txt")
    if objeto_lebl == None:
        mostrar_notificacion("Error: No se pudo procesar Terminals.txt.")
    else:
        ActualizarDiagramaVisual(objeto_lebl)


def ejecutar_cargar_vuelos():
    """Abre Arrivals.txt y lo guarda en memoria."""
    global lista_llegadas
    lista_llegadas = LoadArrivals("Arrivals.txt")
    mostrar_notificacion("Éxito: Arrivals.txt cargado correctamente en memoria.")


def ejecutar_cargar_salidas():
    """Abre Departures.txt y lo guarda en memoria."""
    global lista_salidas
    lista_salidas = LoadDepartures("Departures.txt")
    mostrar_notificacion("Éxito: Departures.txt cargado. " + str(len(lista_salidas)) + " salidas.")


def ejecutar_unificar_movimientos():
    """Junta la lista de llegadas y salidas en un único listado para trabajar más fácil."""
    global lista_llegadas, lista_salidas, lista_movimientos_merged
    if len(lista_llegadas) == 0 or len(lista_salidas) == 0:
        mostrar_notificacion("Atención: Debes cargar Arrivals y Departures primero.")
        return

    lista_movimientos_merged = MergeMovements(lista_llegadas, lista_salidas)
    mostrar_notificacion("Éxito: Fusión completada. " + str(len(lista_movimientos_merged)) + " aeronaves.")


def ejecutar_mapa_vuelos():
    """Genera KML de líneas de vuelo usando Haversine internamente."""
    global lista_movimientos_merged, lista_aeropuertos
    if len(lista_movimientos_merged) == 0 or len(lista_aeropuertos) == 0:
        mostrar_notificacion("Atención: Faltan Aeropuertos o Movimientos.")
    else:
        MapFlights(lista_movimientos_merged, lista_aeropuertos)
        if os.path.exists("flights.kml"):
            try:
                if hasattr(os, 'startfile'):
                    os.startfile("flights.kml")
                else:
                    subprocess.call(["open", "-e", "flights.kml"])
            except Exception:
                pass
            mostrar_notificacion("Éxito: 'flights.kml' generado y abierto.")


def ejecutar_preparar_noche():
    """Asigna manualmente aviones a primera hora del día (Aparcamiento Nocturno)."""
    global objeto_lebl, lista_movimientos_merged
    if objeto_lebl == None or len(lista_movimientos_merged) == 0:
        mostrar_notificacion("Atención: Estructura cargada y Movimientos requeridos.")
        return

    lista_nocturnos = NightAircraft(lista_movimientos_merged)
    AssignNightGates(objeto_lebl, lista_nocturnos)
    ActualizarDiagramaVisual(objeto_lebl)
    mostrar_notificacion("Éxito: Aviones nocturnos posicionados.")


def ejecutar_simular_hora():
    """Función maestra activada por la barra deslizante. Posiciona aviones dinámicamente."""
    global objeto_lebl, lista_movimientos_merged, hora_actual_simulacion
    if objeto_lebl == None or len(lista_movimientos_merged) == 0:
        return

    # Leemos la barra (slider)
    hora_actual_simulacion = int(slider_tiempo.get())

    # Formateamos ej: 9 -> "09:00"
    if hora_actual_simulacion < 10:
        string_hora = "0" + str(hora_actual_simulacion) + ":00"
    else:
        string_hora = str(hora_actual_simulacion) + ":00"

    # Llamamos a nuestra lógica en LEBL.py
    no_asignados = AllocateGatesDynamic(objeto_lebl, lista_movimientos_merged, string_hora)

    # Repintamos la pantalla
    ActualizarDiagramaVisual(objeto_lebl)

    # Actualizamos los textos descriptivos
    texto_estado = "Hora Activa: " + string_hora + " | No asignados en este tramo: " + str(no_asignados)
    label_status_hora.config(text=texto_estado)


# =============================================================================
# CONSTRUCCIÓN DE LA INTERFAZ - PANEL IZQUIERDO (BOTONES)
# =============================================================================
# En esta sección usamos LabelFrames para agrupar visualmente los botones.
tk.Label(frame_izquierdo, text="PANEL DE CONTROL GENERAL", font=("Arial", 14, "bold"), bg=COLOR_BG,
         fg="#000000").pack(pady=10)

marco_datos = tk.LabelFrame(frame_izquierdo, text="1. Añadir Aeropuerto Manual ", font=("Arial", 10, "bold"),
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

marco_gestion = tk.LabelFrame(frame_izquierdo, text=" 2. Base de Datos Mundial ", font=("Arial", 10, "bold"),
                              bg=COLOR_BG, fg="#000000", padx=5, pady=5)
marco_gestion.pack(pady=5, fill="x")
tk.Button(marco_gestion, text="Cargar Airports", width=18, pady=6, bg=COLOR_BTN_NEUTRAL, font=("Arial", 9, "bold"),
          command=ejecutar_cargar).grid(row=0, column=0, padx=4, pady=4)
tk.Button(marco_gestion, text="Añadir Manual", width=18, pady=6, bg=COLOR_BTN_SUCCESS, font=("Arial", 9, "bold"),
          command=ejecutar_anyadir).grid(row=0, column=1, padx=4, pady=4)
tk.Button(marco_gestion, text="Borrar por ICAO", width=18, pady=6, bg=COLOR_BTN_ALERT, font=("Arial", 9, "bold"),
          command=ejecutar_borrar).grid(row=1, column=0, padx=4, pady=4)
tk.Button(marco_gestion, text="Validar Schengen", width=18, pady=6, bg=COLOR_BTN_PRIMARY, font=("Arial", 9, "bold"),
          command=ejecutar_validar).grid(row=1, column=1, padx=4, pady=4)
tk.Button(marco_gestion, text="Ver Análisis", width=18, pady=6, bg=COLOR_BTN_PRIMARY,
          font=("Arial", 9, "bold"), command=ejecutar_analisis_completo).grid(row=2, column=0, padx=4, pady=4)
tk.Button(marco_gestion, text="Mapa Google Earth", width=18, pady=6, bg=COLOR_BTN_PRIMARY, font=("Arial", 9, "bold"),
          command=ejecutar_mapa).grid(row=2, column=1, padx=4, pady=4)
tk.Button(marco_gestion, text="Guardar solo Schengen", width=38, pady=6, bg=COLOR_BTN_NEUTRAL,
          font=("Arial", 9, "bold"), command=ejecutar_guardar).grid(row=3, column=0, columnspan=2, pady=6)

marco_lebl = tk.LabelFrame(frame_izquierdo, text=" 3. Procesamiento Dinámico LEBL ", font=("Arial", 10, "bold"),
                           bg=COLOR_BG, fg="#000000", padx=5, pady=5)
marco_lebl.pack(pady=5, fill="x")
tk.Button(marco_lebl, text="Cargar Estructura", width=38, pady=6, bg=COLOR_BTN_NEUTRAL,
          font=("Arial", 9, "bold"), command=ejecutar_cargar_lebl).grid(row=0, column=0, columnspan=2, pady=3)
tk.Button(marco_lebl, text="Cargar Arrivals", width=18, pady=6, bg=COLOR_BTN_NEUTRAL, font=("Arial", 9, "bold"),
          command=ejecutar_cargar_vuelos).grid(row=1, column=0, padx=4, pady=3)
tk.Button(marco_lebl, text="Cargar Departures", width=18, pady=6, bg=COLOR_BTN_NEUTRAL,
          font=("Arial", 9, "bold"), command=ejecutar_cargar_salidas).grid(row=1, column=1, padx=4, pady=3)
tk.Button(marco_lebl, text="Fusionar (Merge)", width=18, pady=6, bg=COLOR_BTN_PRIMARY, font=("Arial", 9, "bold"),
          command=ejecutar_unificar_movimientos).grid(row=2, column=0, padx=4, pady=4)
tk.Button(marco_lebl, text="Mapa Rutas Vuelo", width=18, pady=6, bg=COLOR_BTN_PRIMARY, font=("Arial", 9, "bold"),
          command=ejecutar_mapa_vuelos).grid(row=2, column=1, padx=4, pady=4)
tk.Button(marco_lebl, text="4. Posicionar Noche", width=38, pady=6, bg=COLOR_BTN_SUCCESS, font=("Arial", 9, "bold"),
          command=ejecutar_preparar_noche).grid(row=3, column=0, columnspan=2, pady=4)

marco_simulacion = tk.LabelFrame(frame_izquierdo, text=" 4. Línea de Tiempo / Análisis Activo ",
                                 font=("Arial", 10, "bold"), bg=COLOR_BG, fg="#000000", padx=5, pady=5)
marco_simulacion.pack(pady=5, fill="x")
label_status_hora = tk.Label(marco_simulacion, text="Hora Activa: 00:00 | Listo para simular",
                             font=("Arial", 9, "bold"), bg=COLOR_BG, fg="#005a9c")
label_status_hora.pack(pady=2)

# El "Slider" es el selector de horas. Al soltar el ratón ("<ButtonRelease-1>") llama a simular.
slider_tiempo = tk.Scale(marco_simulacion, from_=0, to=23, orient="horizontal", tickinterval=4, font=("Arial", 8),
                         bg=COLOR_BG)
slider_tiempo.pack(fill="x", padx=5, pady=5)
slider_tiempo.bind("<ButtonRelease-1>", lambda event: ejecutar_simular_hora())

tk.Button(marco_simulacion, text="Graficar Ocupación de Todo el Día", width=38, pady=8, bg=COLOR_ASIGNAR,
          font=("Arial", 9, "bold"), command=ejecutar_plot_ocupacion_completa).pack(pady=6)

# --- VISUALIZADOR AEROPUERTOS (LA TABLA INFERIOR) ---
lbl_titulo_tabla = tk.Label(frame_izquierdo, text="Aeropuertos en memoria:", bg=COLOR_BG, font=("Arial", 10, "bold"))
lbl_titulo_tabla.pack(pady=(10, 5))

marco_tabla = tk.Frame(frame_izquierdo, bg=COLOR_BG)
marco_tabla.pack(fill="x", padx=10, pady=5)

# Crear la tabla usando Treeview
columnas = ("icao", "nombre", "schengen")
tabla_aeropuertos = ttk.Treeview(marco_tabla, columns=columnas, show="headings", height=10)

tabla_aeropuertos.heading("icao", text="ICAO")
tabla_aeropuertos.heading("nombre", text="Nombre")
tabla_aeropuertos.heading("schengen", text="Schengen")

tabla_aeropuertos.column("icao", width=60)
tabla_aeropuertos.column("nombre", width=150)
tabla_aeropuertos.column("schengen", width=70)

scrollbar_tabla = tk.Scrollbar(marco_tabla, orient="vertical", command=tabla_aeropuertos.yview)
tabla_aeropuertos.config(yscrollcommand=scrollbar_tabla.set)

tabla_aeropuertos.pack(side="left", fill="x", expand=True)
scrollbar_tabla.pack(side="right", fill="y")

# =============================================================================
# INICIALIZACIÓN DEL PROGRAMA
# =============================================================================
# Antes de cargar datos, ponemos los textos de "Esperando datos..." en todos los lienzos
crear_placeholder(marco_grafico_1, "Llegadas por Hora")
crear_placeholder(marco_grafico_2, "Vuelos por Aerolínea")
crear_placeholder(marco_grafico_3, "Proporción Schengen")
crear_placeholder(marco_grafico_4, "Ocupación Diaria de Terminales")

crear_placeholder(pestana_grafico1, "Llegadas por Hora (Detalle)")
crear_placeholder(pestana_grafico2, "Vuelos por Aerolínea (Detalle)")
crear_placeholder(pestana_grafico3, "Proporción Schengen (Detalle)")
crear_placeholder(pestana_grafico4, "Ocupación Diaria (Detalle)")

# El "mainloop" es lo que mantiene la ventana abierta esperando que el usuario haga clic.
root.mainloop()