# =============================================================================
# IMPORTACIÓN DE LIBRERÍAS Y MÓDULOS DEL PROYECTO
# =============================================================================
# Importamos todas las clases y funciones de las lógicas previas (Airport, Flight, etc.)
from airport import *
from aircraft import *
import LEBL
import os
import subprocess
import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt

# =============================================================================
# VARIABLES GLOBALES (ESTADO DE LA APLICACIÓN)
# =============================================================================
lista_aeropuertos = []  # Lista en memoria para almacenar la Base de Datos Mundial (objetos Airport)
lista_vuelos = []  # Lista en memoria para almacenar las aeronaves programadas (objetos Flight)
objeto_lebl = None  # Objeto de control que guardará toda la estructura física del aeropuerto

# =============================================================================
# PALETA DE COLORES PASTEL SELECCIONADA
# =============================================================================
COLOR_BG = "#f8f9fa"  # Gris muy claro y limpio para el fondo de la aplicación
COLOR_PASTEL_BLUE = "#e8f4fd"  # Azul cielo pastel para la base de datos, kml y estadísticas
COLOR_PASTEL_GREEN = "#d4edda"  # Verde pastel para el botón de confirmación/añadido manual
COLOR_PASTEL_RED = "#f8d7da"  # Rosa/Rojo pastel para acciones destructivas o de borrado
COLOR_PASTEL_YELLOW = "#fff3cd"  # Amarillo crema pastel para la carga de datos de LEBL
COLOR_PASTEL_PURPLE = "#cce5ff"  # Azul/Púrpura suave para guardar archivos
COLOR_ASIGNAR = "#17a2b8"  # Azul cian corporativo para resaltar el botón principal de asignación


# =============================================================================
# FUNCIONES CONTROLADORAS (BLOQUE 2: BASE DE DATOS MUNDIAL)
# =============================================================================

def ejecutar_cargar():
    """Lee el archivo plano 'Airports.txt' y carga los aeropuertos en la lista global."""
    global lista_aeropuertos
    lista_aeropuertos = LoadAirports("Airports.txt")
    messagebox.showinfo("Éxito", "Airports.txt cargado correctamente.")


def ejecutar_anyadir():
    """Recupera el texto de los campos manuales e inserta un nuevo aeropuerto en la lista."""
    c = entrada_code.get().upper()  # Extrae el ICAO y lo fuerza a mayúsculas
    try:
        # Intenta convertir las coordenadas de texto a números decimales
        la = float(entrada_lat.get())
        lo = float(entrada_lon.get())

        nuevo = Airport(c, la, lo)  # Instancia el nuevo objeto de la clase Airport
        AddAirport(lista_aeropuertos, nuevo)  # Lo añade usando la lógica del backend
        messagebox.showinfo("Éxito", f"Aeropuerto {c} añadido.")
    except ValueError:
        # Captura el error si el usuario escribe caracteres no válidos en latitud o longitud
        messagebox.showerror("Error", "Datos numéricos incorrectos.")


def ejecutar_borrar():
    """Busca el código ICAO introducido y lo elimina de la base de datos temporal."""
    c = entrada_code.get().upper()
    RemoveAirport(lista_aeropuertos, c)
    messagebox.showinfo("Éxito", f"Aeropuerto {c} eliminado.")


def ejecutar_validar():
    """Recorre todos los aeropuertos cargados evaluando si pertenecen al espacio Schengen."""
    global lista_aeropuertos
    i = 0
    while i < len(lista_aeropuertos):
        SetSchengen(lista_aeropuertos[i])  # Modifica internamente el atributo booleano '.schengen'
        i = i + 1
    messagebox.showinfo("Éxito", "Validación Schengen completada.")


def ejecutar_grafico():
    """Muestra la estadística horaria de Matplotlib y añade un nuevo gráfico de sectores."""
    global lista_vuelos, lista_aeropuertos
    if not lista_vuelos or not lista_aeropuertos:
        messagebox.showwarning("Atención", "Primero debes cargar los Airports.txt y los Arrivals.txt")
        return

    # 1. Llama a la gráfica de barras nativa de tu backend para ver los vuelos por hora
    PlotArrivals(lista_vuelos)

    # 2. Contadores locales para calcular el reparto de vuelos Schengen
    schengen_count = 0
    non_schengen_count = 0

    for vuelo in lista_vuelos:
        aeropuerto_origen = FindAirport(lista_aeropuertos, vuelo.origin)
        if aeropuerto_origen:
            if getattr(aeropuerto_origen, 'schengen', False):
                schengen_count += 1
            else:
                non_schengen_count += 1
        else:
            non_schengen_count += 1  # Si el origen es desconocido, lo tratamos como internacional

    # 3. Renderizado del Gráfico Circular de tarta (Pie Chart)
    labels = ['Schengen', 'Non-Schengen']
    valores = [schengen_count, non_schengen_count]
    colores = ['#4caf50', '#f44336']  # Verde para tráfico europeo, Rojo para internacional
    explode = (0.05, 0)  # Destaca ligeramente la porción de vuelos Schengen

    plt.figure("Proporción de Vuelos - LEBL")
    plt.pie(valores, explode=explode, labels=labels, colors=colores,
            autopct='%1.1f%%', shadow=True, startangle=140,
            textprops={'fontsize': 12, 'weight': 'bold'})
    plt.title("Distribución de Vuelos: Schengen vs Non-Schengen", fontsize=14, weight='bold', pad=20)
    plt.axis('equal')  # Garantiza que el círculo se dibuje de forma perfectamente simétrica
    plt.show()


def ejecutar_mapa():
    """Genera el documento de marcas geográficas KML e intenta abrirlo en el equipo."""
    MapAirports(lista_aeropuertos)
    if os.path.exists("airports.kml"):
        try:
            if hasattr(os, 'startfile'):
                os.startfile("airports.kml")  # Instrucción nativa de apertura para Windows
            else:
                subprocess.call(["open", "-e", "airports.kml"])  # Instrucción nativa para macOS/Linux
        except:
            messagebox.showerror("Error", "No se pudo abrir automáticamente el KML.")
    else:
        messagebox.showerror("Error", "No se encontró airports.kml")


def ejecutar_guardar():
    """Exporta y escribe en un nuevo fichero los aeropuertos validados como Schengen."""
    SaveSchengenAirports(lista_aeropuertos, "Schengen_Solo.txt")
    messagebox.showinfo("Éxito", "Archivo Schengen_Solo.txt guardado.")


# =============================================================================
# FUNCIONES CONTROLADORAS (BLOQUE 3: OPERACIONES LEBL BARCELONA-EL PRAT)
# =============================================================================

def ejecutar_cargar_lebl():
    """Carga la estructura física interna del aeropuerto y dibuja el árbol por primera vez."""
    global objeto_lebl
    objeto_lebl = LEBL.LoadAirportStructure("Terminals.txt")
    if objeto_lebl == -1 or not objeto_lebl or len(objeto_lebl.terminals) == 0:
        messagebox.showerror("Error", "No se pudo cargar Terminals.txt o está vacío.")
    else:
        # Renderiza el lienzo gráfico inicial: muestra todas las terminales y puertas [LIBRES]
        ActualizarDiagramaVisual(objeto_lebl)


def ejecutar_cargar_vuelos():
    """Carga los datos de vuelos de llegada previstos para el día."""
    global lista_vuelos
    lista_vuelos = LoadArrivals("Arrivals.txt")
    messagebox.showinfo("Éxito", "Arrivals.txt cargado correctamente.")


def ejecutar_asignar_puertas():
    """Cruza los vuelos con las puertas del aeropuerto y redibuja el panel en tiempo real."""
    global objeto_lebl, lista_aeropuertos, lista_vuelos
    if not objeto_lebl or not lista_vuelos or not lista_aeropuertos:
        messagebox.showwarning("Atención", "Faltan datos por cargar (Airports, Terminals o Arrivals).")
        return

    # Nos aseguramos de realizar la validación geográfica obligatoria antes de asignar
    ejecutar_validar()

    # Procesamos uno a uno todos los vuelos de entrada cargados
    for i in range(len(lista_vuelos)):
        vuelo = lista_vuelos[i]
        aeropuerto_origen = FindAirport(lista_aeropuertos, vuelo.origin)
        es_schengen = aeropuerto_origen.schengen if aeropuerto_origen else False

        # Invocamos al motor algorítmico del backend para emparejar avión y puerta
        LEBL.AssignGate(objeto_lebl, vuelo, es_schengen)

    # REFRESH DINÁMICO (V4): Redibuja el lienzo. Las puertas asignadas pasarán a ROJO mostrando el avión
    ActualizarDiagramaVisual(objeto_lebl)
    messagebox.showinfo("Éxito", "Puertas asignadas correctamente.")

# =============================================================================
# MOTOR DE DIBUJO ESQUEMÁTICO EN ÁRBOL (MODIFICADO PARA T1 EN UN LADO Y T2 EN OTRO)
# =============================================================================
def ActualizarDiagramaVisual(bcn):
    """Limpia el lienzo del Canvas y dibuja las terminales divididas en dos columnas."""
    canvas_visualizador.delete("all")  # Resetea y borra cualquier gráfico previo en el lienzo
    if not bcn or not hasattr(bcn, 'terminals'):
        return

    y_maxima_alcanzada = 50  # Rastreará cuál es el punto más bajo pintado para configurar el scrollbar

    # Iteramos sobre las terminales para posicionarlas horizontalmente
    for t_idx, terminal in enumerate(bcn.terminals):

        # CONFIGURACIÓN DE COLUMNAS:
        # Si es la primera terminal (T1), se dibuja a la izquierda (x = 40)
        # Si es la segunda terminal (T2) o posteriores, se desplaza a la derecha (x = 550)
        if t_idx == 0:
            x_inicio = 40
        else:
            x_inicio = 550

        y_actual = 50  # Ambas columnas empiezan arriba a la misma altura (Y = 50)

        # Dibujamos el texto indicador de la Terminal (Raíz jerárquica)
        canvas_visualizador.create_text(x_inicio, y_actual, text=terminal.name, font=("Arial", 18, "bold"), anchor="w",
                                        fill="#005a9c")
        y_linea_terminal = y_actual  # Guardamos la cota Y para colgar el tronco principal
        y_actual += 40

        # -------------------------------------------------------------------------
        # ITERACIÓN 2: Recorremos las Áreas de embarque de dicha terminal
        # -------------------------------------------------------------------------
        for area in terminal.boarding_areas:
            # Línea vertical (Eje de la Terminal hacia abajo)
            canvas_visualizador.create_line(x_inicio + 15, y_linea_terminal, x_inicio + 15, y_actual, fill="#005a9c",
                                            width=3)
            # Línea horizontal (Desvío hacia el nodo del Área de Embarque)
            canvas_visualizador.create_line(x_inicio + 15, y_actual, x_inicio + 45, y_actual, fill="#005a9c", width=3)

            # Escribimos el nombre informativo de la zona en color negro regular
            tipo_zona = "Schengen" if area.type else "non-Schengen"
            canvas_visualizador.create_text(x_inicio + 55, y_actual, text=f"Area {area.name} ({tipo_zona})",
                                            font=("Arial", 12, "bold"), anchor="w", fill="#000000")

            y_linea_area = y_actual  # Guardamos la cota Y del área para colgar las ramas secundarias de las puertas
            y_actual += 30

            # -------------------------------------------------------------------------
            # ITERACIÓN 3: Recorremos las Puertas (Gates) asociadas a la zona de embarque
            # -------------------------------------------------------------------------
            for gate in area.gates:
                # Línea vertical secundaria (Eje que baja del Área actual)
                canvas_visualizador.create_line(x_inicio + 70, y_linea_area, x_inicio + 70, y_actual, fill="#005a9c",
                                                width=2)
                # Línea horizontal final (Apunta directamente al indicador de estado de la puerta)
                canvas_visualizador.create_line(x_inicio + 70, y_actual, x_inicio + 100, y_actual, fill="#005a9c",
                                                width=2)

                # ASIGNACIÓN DE COLOR DINÁMICO: Rojo si está ocupada, Verde si está desocupada
                color_cuadro = "#dc3545" if gate.occupied else "#28a745"

                # Pintamos el rectángulo de estado (Grosor aumentado para una mejor nitidez)
                canvas_visualizador.create_rectangle(x_inicio + 100, y_actual - 9, x_inicio + 118, y_actual + 9,
                                                     fill=color_cuadro, outline="#000000", width=1.5)

                # Pintamos el texto con el nombre único de la puerta (Fuente Courier para aspecto técnico)
                canvas_visualizador.create_text(x_inicio + 130, y_actual, text=gate.name, font=("Courier", 11, "bold"),
                                                anchor="w", fill="#000000")

                # REQUERIMIENTO V4 (MÁS GRANDE): Si la puerta está reservada, imprimimos el código del avión
                if gate.occupied:
                    info_avion = f" ➔  ✈ AVION: {gate.aircraft}"
                    canvas_visualizador.create_text(x_inicio + 220, y_actual, text=info_avion,
                                                    font=("Arial", 13, "bold"), anchor="w", fill="#b22222")

                y_actual += 26  # Incrementamos la distancia vertical entre puertas adyacentes
            y_actual += 20  # Añadimos un colchón de espacio muerto entre zonas de embarque
        y_actual += 30  # Añadimos un colchón de espacio muerto al terminar la terminal completa

        # Guardamos cuál de las dos columnas ha sido más larga para que el scroll cubra todo el espacio necesario
        if y_actual > y_maxima_alcanzada:
            y_maxima_alcanzada = y_actual

    # Ajustamos la región total navegable (tanto horizontal como vertical) para albergar las dos columnas cómodamente
    canvas_visualizador.config(scrollregion=(0, 0, 1100, y_maxima_alcanzada + 50))


# =============================================================================
# CONSTRUCCIÓN DE LA ARQUITECTURA DE LA VENTANA (TKINTER DESKTOP APP)
# =============================================================================
root = tk.Tk()
root.title("Airport Tool - University Management System (V4)")
root.geometry("1450x850")  # Ampliamos ligeramente el ancho total (1450) para que las dos columnas quepan holgadamente
root.configure(bg=COLOR_BG)

# PANEL IZQUIERDO (Panel de Mandos y Botones de acción)
frame_izquierdo = tk.Frame(root, bg=COLOR_BG)
frame_izquierdo.pack(side="left", padx=20, pady=10, fill="y")

# PANEL DERECHO (Espacio dedicado para el Lienzo de visualización interactivo)
frame_derecho = tk.Frame(root, bg=COLOR_BG)
frame_derecho.pack(side="right", padx=20, pady=10, fill="both", expand=True)

# Título de Cabecera Izquierda (MÁS GRANDE Y EN NEGRO PURO)
tk.Label(frame_izquierdo, text="PANEL DE CONFIGURACIÓN", font=("Arial", 15, "bold"), bg=COLOR_BG, fg="#000000").pack(
    pady=15)

# -----------------------------------------------------------------------------
# SUB-BLOQUE INTERFAZ 1: Entrada de Datos Manual (Estructura Rejilla Grid)
# -----------------------------------------------------------------------------
marco_datos = tk.LabelFrame(frame_izquierdo, text=" 1. Añadir Aeropuerto Manual ", font=("Arial", 11, "bold"),
                            bg=COLOR_BG, fg="#000000", padx=10, pady=5)
marco_datos.pack(pady=8, fill="x")

# ICAO Input
tk.Label(marco_datos, text="ICAO:", font=("Arial", 10, "bold"), bg=COLOR_BG, fg="#000000").grid(row=0, column=0, padx=4)
entrada_code = tk.Entry(marco_datos, width=7, font=("Arial", 11), bg="#ffffff", fg="#000000")
entrada_code.grid(row=0, column=1, padx=4, pady=10)

# Latitud Input
tk.Label(marco_datos, text="Lat:", font=("Arial", 10, "bold"), bg=COLOR_BG, fg="#000000").grid(row=0, column=2, padx=4)
entrada_lat = tk.Entry(marco_datos, width=9, font=("Arial", 11), bg="#ffffff", fg="#000000")
entrada_lat.grid(row=0, column=3, padx=4)

# Longitud Input
tk.Label(marco_datos, text="Lon:", font=("Arial", 10, "bold"), bg=COLOR_BG, fg="#000000").grid(row=0, column=4, padx=4)
entrada_lon = tk.Entry(marco_datos, width=9, font=("Arial", 11), bg="#ffffff", fg="#000000")
entrada_lon.grid(row=0, column=5, padx=4)

# -----------------------------------------------------------------------------
# SUB-BLOQUE INTERFAZ 2: Botoneras de Gestión Global de Ficheros (Colores Pastel)
# -----------------------------------------------------------------------------
marco_gestion = tk.LabelFrame(frame_izquierdo, text=" 2. Base de Datos Mundial ", font=("Arial", 11, "bold"),
                              bg=COLOR_BG, fg="#000000", padx=10, pady=10)
marco_gestion.pack(pady=8, fill="x")

# Distribución ordenada de botones utilizando coordenadas de rejilla (Filas y Columnas)
tk.Button(marco_gestion, text="Cargar Airports.txt", width=18, pady=8, bg=COLOR_PASTEL_BLUE,
          highlightbackground=COLOR_PASTEL_BLUE, fg="black", font=("Arial", 9, "bold"), command=ejecutar_cargar).grid(
    row=0, column=0, padx=6, pady=6)
tk.Button(marco_gestion, text="Añadir Manual", width=18, pady=8, bg=COLOR_PASTEL_GREEN,
          highlightbackground=COLOR_PASTEL_GREEN, fg="black", font=("Arial", 9, "bold"), command=ejecutar_anyadir).grid(
    row=0, column=1, padx=6, pady=6)
tk.Button(marco_gestion, text="Borrar por ICAO", width=18, pady=8, bg=COLOR_PASTEL_RED,
          highlightbackground=COLOR_PASTEL_RED, fg="black", font=("Arial", 9, "bold"), command=ejecutar_borrar).grid(
    row=1, column=0, padx=6, pady=6)
tk.Button(marco_gestion, text="Validar Schengen", width=18, pady=8, bg=COLOR_PASTEL_BLUE,
          highlightbackground=COLOR_PASTEL_BLUE, fg="black", font=("Arial", 9, "bold"), command=ejecutar_validar).grid(
    row=1, column=1, padx=6, pady=6)
tk.Button(marco_gestion, text="Ver Gráfico", width=18, pady=8, bg=COLOR_PASTEL_BLUE,
          highlightbackground=COLOR_PASTEL_BLUE, fg="black", font=("Arial", 9, "bold"), command=ejecutar_grafico).grid(
    row=2, column=0, padx=6, pady=6)
tk.Button(marco_gestion, text="Mapa Google Earth", width=18, pady=8, bg=COLOR_PASTEL_BLUE,
          highlightbackground=COLOR_PASTEL_BLUE, fg="black", font=("Arial", 9, "bold"), command=ejecutar_mapa).grid(
    row=2, column=1, padx=6, pady=6)

# Botón inferior que ocupa ambas columnas (columnspan=2) para un balance visual simétrico
tk.Button(marco_gestion, text="Guardar solo Schengen", width=39, pady=8, bg=COLOR_PASTEL_PURPLE,
          highlightbackground=COLOR_PASTEL_PURPLE, fg="black", font=("Arial", 10, "bold"),
          command=ejecutar_guardar).grid(row=3, column=0, columnspan=2, pady=8)

# -----------------------------------------------------------------------------
# SUB-BLOQUE INTERFAZ 3: Operaciones sobre el Núcleo del Aeropuerto LEBL
# -----------------------------------------------------------------------------
marco_lebl = tk.LabelFrame(frame_izquierdo, text=" 3. Operaciones LEBL ", font=("Arial", 11, "bold"), bg=COLOR_BG,
                           fg="#000000", padx=10, pady=10)
marco_lebl.pack(pady=12, fill="x")

tk.Button(marco_lebl, text="1. Cargar Estructura\n(Terminals.txt)", width=18, pady=8, bg=COLOR_PASTEL_YELLOW,
          highlightbackground=COLOR_PASTEL_YELLOW, fg="black", font=("Arial", 9, "bold"),
          command=ejecutar_cargar_lebl).grid(row=0, column=0, padx=6, pady=6)
tk.Button(marco_lebl, text="2. Cargar Tráfico\n(Arrivals.txt)", width=18, pady=8, bg=COLOR_PASTEL_YELLOW,
          highlightbackground=COLOR_PASTEL_YELLOW, fg="black", font=("Arial", 9, "bold"),
          command=ejecutar_cargar_vuelos).grid(row=0, column=1, padx=6, pady=6)

# Botón de Procesamiento de Asignación Final (Color Cian oscuro destacado)
tk.Button(marco_lebl, text="3. Asignar Asignación Estática", width=39, pady=12, bg=COLOR_ASIGNAR,
          highlightbackground=COLOR_ASIGNAR, fg="black", font=("Arial", 10, "bold"),
          command=ejecutar_asignar_puertas).grid(row=1, column=0, columnspan=2, pady=12)

# -----------------------------------------------------------------------------
# MONITOR GRÁFICO DERECHO: Encaje del Canvas Deslizable
# -----------------------------------------------------------------------------
# Cabecera superior del monitor de visualización (MÁS GRANDE Y EN NEGRO PURO)
tk.Label(frame_derecho, text="DIAGRAMA DE OCUPACIÓN EN TIEMPO REAL (V4)", font=("Arial", 14, "bold"), bg=COLOR_BG,
         fg="#000000").pack(pady=10)

# Frame contenedor secundario para emparejar el Canvas de dibujo al lado del Scrollbar de control
canvas_frame = tk.Frame(frame_derecho, bg="#ffffff")
canvas_frame.pack(fill="both", expand=True, pady=5)

# Creación del objeto Lienzo Canvas (Fondo blanco puro, bordes integrados)
canvas_visualizador = tk.Canvas(canvas_frame, bg="#ffffff", bd=2, relief="sunken", highlightthickness=0)
canvas_visualizador.pack(side="left", fill="both", expand=True)

# Instanciación de la Barra de Scroll Vertical acoplada al borde derecho
scrollbar_v = tk.Scrollbar(canvas_frame, orient="vertical", command=canvas_visualizador.yview)
scrollbar_v.pack(side="right", fill="y")

# Enlazamos de forma bidireccional el Scrollbar y el Lienzo interactivo de Tkinter
canvas_visualizador.config(yscrollcommand=scrollbar_v.set)

# =============================================================================
# ACTIVACIÓN DE LA APLICACIÓN
# =============================================================================
# Pone al programa a escuchar eventos del ratón y el teclado de forma indefinida
root.mainloop()