from airport import *
import os
import tkinter as tk

# --- VARIABLES GLOBALES ---
lista_aeropuertos = []

# --- FUNCIONES DE LOS BOTONES (Lógica básica) ---
def ejecutar_cargar():
    global lista_aeropuertos
    lista_aeropuertos = LoadAirports("Airports.txt")
    etiqueta_estado.config(text="INFO: " + str(len(lista_aeropuertos)) + " aeropuertos en memoria.", fg="blue")

def ejecutar_anyadir():
    c = entrada_code.get().upper() # .upper() asegura que sea mayúsculas
    try:
        la = float(entrada_lat.get())
        lo = float(entrada_lon.get())
        nuevo = Airport(c, la, lo)
        AddAirport(lista_aeropuertos, nuevo)
        etiqueta_estado.config(text="OK: " + c + " añadido correctamente.", fg="green")
    except:
        etiqueta_estado.config(text="ERROR: Datos numéricos incorrectos.", fg="red")

def ejecutar_borrar():
    c = entrada_code.get().upper()
    RemoveAirport(lista_aeropuertos, c)
    etiqueta_estado.config(text="AVISO: Intento de borrado de " + c, fg="orange")

def ejecutar_validar():
    i = 0
    while i < len(lista_aeropuertos):
        SetSchengen(lista_aeropuertos[i])
        i = i + 1
    etiqueta_estado.config(text="OK: Datos Schengen actualizados.", fg="purple")

def ejecutar_grafico():
    PlotAirports(lista_aeropuertos)

def ejecutar_mapa():
    MapAirports(lista_aeropuertos)
    if os.path.exists("AirportsMap.kml"):
        os.startfile("AirportsMap.kml")
        etiqueta_estado.config(text="OK: Abriendo Google Earth...", fg="green")
    else:
        etiqueta_estado.config(text="ERROR: No se pudo abrir el mapa.", fg="red")

def ejecutar_guardar():
    SaveSchengenAirports(lista_aeropuertos, "Schengen_Solo.txt")

# --- CONSTRUCCIÓN DE LA INTERFAZ ---
root = tk.Tk()
root.title("Airport Management Tool - UPC")
root.geometry("450x600")
root.configure(bg="#f0f0f0") # Color de fondo gris claro

# 1. TÍTULO PRINCIPAL
tk.Label(root, text="GESTIÓN DE AEROPUERTOS", font=("Arial", 16, "bold"), bg="#f0f0f0").pack(pady=10)

# 2. BLOQUE DE DATOS (LabelFrame: una caja con título)
marco_datos = tk.LabelFrame(root, text=" Datos del Aeropuerto ", padx=10, pady=10)
marco_datos.pack(padx=20, pady=10, fill="x")

tk.Label(marco_datos, text="Código ICAO:").grid(row=0, column=0, sticky="w")
entrada_code = tk.Entry(marco_datos)
entrada_code.grid(row=0, column=1, pady=2)

tk.Label(marco_datos, text="Latitud (Decimal):").grid(row=1, column=0, sticky="w")
entrada_lat = tk.Entry(marco_datos)
entrada_lat.grid(row=1, column=1, pady=2)

tk.Label(marco_datos, text="Longitud (Decimal):").grid(row=2, column=0, sticky="w")
entrada_lon = tk.Entry(marco_datos)
entrada_lon.grid(row=2, column=1, pady=2)

# 3. BLOQUE DE GESTIÓN (Añadir/Borrar/Cargar)
marco_gestion = tk.LabelFrame(root, text=" Operaciones de Gestión ", padx=10, pady=10)
marco_gestion.pack(padx=20, pady=10, fill="x")

tk.Button(marco_gestion, text="Cargar Airports.txt", width=20, command=ejecutar_cargar).grid(row=0, column=0, padx=5, pady=2)
tk.Button(marco_gestion, text="Añadir a la lista", width=20, bg="#d4edda", command=ejecutar_anyadir).grid(row=0, column=1, padx=5, pady=2)
tk.Button(marco_gestion, text="Borrar por Código", width=20, bg="#f8d7da", command=ejecutar_borrar).grid(row=1, column=0, padx=5, pady=2)
tk.Button(marco_gestion, text="Validar Schengen", width=20, command=ejecutar_validar).grid(row=1, column=1, padx=5, pady=2)

# 4. BLOQUE DE VISUALIZACIÓN (Gráficos/Mapas)
marco_visual = tk.LabelFrame(root, text=" Visualización y Salida ", padx=10, pady=10)
marco_visual.pack(padx=20, pady=10, fill="x")

tk.Button(marco_visual, text="Ver Gráfico de Barras", width=20, command=ejecutar_grafico).grid(row=0, column=0, padx=5, pady=2)
tk.Button(marco_visual, text="Generar Mapa Google Earth", width=20, command=ejecutar_mapa).grid(row=0, column=1, padx=5, pady=2)
tk.Button(marco_visual, text="Guardar solo Schengen", width=43, bg="#cce5ff", command=ejecutar_guardar).grid(row=1, column=0, columnspan=2, pady=5)

# 5. BARRA DE ESTADO
etiqueta_estado = tk.Label(root, text="Estado: Esperando órdenes...", bd=1, relief="sunken", anchor="w", font=("Arial", 9, "italic"))
etiqueta_estado.pack(side="bottom", fill="x")

root.mainloop()

from airport import *


def Menu():
    # 1. Variables de almacenamiento
    lista_aeropuertos = []
    lista_llegadas = []
    mi_bcn = None

    while True:
        print("\n--- SISTEMA DE GESTIÓN AEROPUERTO LEBL ---")
        print("1. Leer ficheros (Estructura y Aeropuertos)")
        print("2. Imprimir vuelos y asignar puertas (Parte 3)")
        print("0. Salir")

        opcion = input("Selecciona una opción: ")

        if opcion == "1":
            # Cargamos la estructura del aeropuerto (Parte 3)
            mi_bcn = LoadAirportStructure("Terminals.txt")
            # Cargamos la base de datos de aeropuertos del mundo (Parte 1)
            lista_aeropuertos = LoadAirports("Airports.txt")
            # Cargamos los vuelos que llegan (Parte 2)
            # Nota: Aquí deberías tener tu función LoadFlights o similar
            # Para el ejemplo, supongamos que ya tienes vuelos cargados
            print("Archivos cargados correctamente.")

        elif opcion == "2":
            if mi_bcn is None:
                print("Error: Primero debes cargar la estructura (Opción 1)")
            else:
                # Simulamos que tenemos una lista de vuelos cargada para probar
                # En tu código real, usa la lista que cargues del archivo Arrivals.txt
                print("\nASIGNACIÓN DE PUERTAS EN TIEMPO REAL:")

                # USAMOS FOR IN RANGE COMO PEDISTE
                for i in range(len(lista_llegadas)):
                    vuelo = lista_llegadas[i]

                    # A) Miramos si el origen es Schengen
                    es_schengen = IsSchengenAirport(vuelo.origin)

                    # B) ASIGNAMOS LA PUERTA (Aquí se conecta la lógica de la Parte 3)
                    puerta = AssignGate(mi_bcn, vuelo.airline, es_schengen)

                    print(f"Vuelo: {vuelo.id} | Aerolínea: {vuelo.airline} | Puerta: {puerta}")

        elif opcion == "0":
            break


if __name__ == "__main__":
    Menu()