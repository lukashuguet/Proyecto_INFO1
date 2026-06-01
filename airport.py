"""
MÓDULO AIRPORT.PY (Fundación y Geografía)
Este archivo contiene la clase base para los aeropuertos y todas las herramientas 
matemáticas y geográficas asociadas (conversión de coordenadas, mapas KML).
Actúa como la base de datos de ubicaciones mundiales.
"""

import matplotlib.pyplot as plt


# =============================================================================
# DEFINICIÓN DE CLASES
# =============================================================================
class Airport:
    """
    Clase que representa un aeropuerto genérico en el mundo.
    Guarda su código de identificación, dónde está en el mapa, 
    y si pertenece al espacio de libre circulación europeo (Schengen).
    """

    def __init__(self, icao, lat, lon):
        self.icao = icao
        self.coordinates = (lat, lon)  # Tupla con Latitud y Longitud en grados decimales
        self.schengen = False  # Por defecto asumimos que no es Schengen


def LoadAirlines(terminal, t_name):
    """
    IMPORTANTE: Aunque esta función está aquí, pertenece conceptualmente a LEBL.py.
    Abre un archivo (Ej: 'T1_Airlines.txt') que está separado por tabuladores ('\t')
    y guarda el código de la aerolínea en la terminal correspondiente.
    """
    f = open(t_name + "_Airlines.txt", "r")
    lines = f.readlines()
    f.close()
    for i in range(len(lines)):
        linea = lines[i].strip()
        if linea:
            partes = linea.split('\t')
            if len(partes) > 1:
                terminal.airlines.append(partes[1])


# =============================================================================
# LÓGICA SCHENGEN
# =============================================================================

def IsSchengenAirport(code):
    """
    Comprueba si el código ICAO pertenece a un país del tratado Schengen.
    La lógica se basa en analizar las 2 primeras letras del código (Ej: 'LE' = España).
    """
    if not code:
        return False

    # Lista de prefijos ICAO de países europeos Schengen
    schengen_prefixes = [
        'LO', 'EB', 'LK', 'LC', 'EK', 'EE', 'EF', 'LF', 'ED', 'LG',
        'EH', 'LH', 'BI', 'LI', 'EV', 'EY', 'EL', 'LM', 'EN', 'EP',
        'LP', 'LZ', 'LJ', 'LE', 'ES', 'LS'
    ]

    # code[:2] extrae exactamente los dos primeros caracteres del string
    return code[:2] in schengen_prefixes


def SetSchengen(airport):
    """Actualiza el atributo interno del objeto Airport usando nuestra función de comprobación."""
    airport.schengen = IsSchengenAirport(airport.icao)


def PrintAirport(airport):
    """Función de depuración (debug) para imprimir en consola los datos de un objeto."""
    print("ICAO:", airport.icao)
    print("Coordinates:", airport.coordinates)
    print("Schengen:", airport.schengen)
    print()


# =============================================================================
# FUNCIONES DE FICHERO (Lectura/Escritura)
# =============================================================================

def LoadAirports(filename):
    """
    Lee el archivo principal de aeropuertos mundiales.
    Llama internamente a 'ConvertCoord' para traducir las coordenadas de texto a matemáticas.
    """
    airports = []

    try:
        file = open(filename, "r")
    except:
        return airports  # Retorna lista vacía si el archivo no existe

    lines = file.readlines()
    file.close()

    for line in lines:
        line = line.strip()

        # Ignoramos líneas vacías o la cabecera que empieza por "CODE"
        if not line or line.startswith("CODE"):
            continue

        parts = line.split()

        # Control de seguridad: Si la línea no tiene 3 trozos, está corrupta y la saltamos
        if len(parts) != 3:
            continue

        code = parts[0]
        # Convertimos texto a número decimal para poder calcular distancias luego
        lat = ConvertCoord(parts[1])
        lon = ConvertCoord(parts[2])

        airport = Airport(code, lat, lon)
        airports.append(airport)

    return airports


def SaveSchengenAirports(airports, filename):
    """
    Filtra la lista y guarda físicamente en un TXT solo aquellos 
    aeropuertos que sean Schengen, devolviendo las coordenadas a su formato texto original.
    """
    if not airports:
        return -1

    file = open(filename, "w")
    file.write("CODE LAT LON\n")

    for airport in airports:
        if airport.schengen:
            # Reconversión a texto (Ej: N412345)
            lat_str = FormatCoord(airport.coordinates[0], True)
            lon_str = FormatCoord(airport.coordinates[1], False)

            file.write(f"{airport.icao} {lat_str} {lon_str}\n")

    file.close()


# =============================================================================
# GESTIÓN DE LISTAS
# =============================================================================

def AddAirport(airports, airport):
    """Añade un aeropuerto comprobando antes que no exista un duplicado (Mismo ICAO)."""
    for a in airports:
        if a.icao == airport.icao:
            return
    airports.append(airport)


def RemoveAirport(airports, code):
    """Busca un aeropuerto por ICAO y lo extrae de la lista global."""
    for a in airports:
        if a.icao == code:
            airports.remove(a)
            return
    return -1  # Devuelve -1 si no lo encontró


# =============================================================================
# GRÁFICOS MATPLOTLIB
# =============================================================================

def PlotAirports(airports):
    """
    Genera un gráfico de barras apilado (Stacked Bar) mostrando la proporción
    de aeropuertos Schengen vs No Schengen usando la librería matplotlib.
    """
    # Validamos si la lista está vacía
    if len(airports) == 0:
        print("No hay datos")
    else:
        # Inicializamos los contadores
        schengen_count = 0
        no_schengen_count = 0

        # Usamos un bucle while básico para recorrer la lista
        i = 0
        while i < len(airports):
            if airports[i].schengen == True:
                schengen_count = schengen_count + 1
            else:
                no_schengen_count = no_schengen_count + 1

            # Incrementamos el índice
            i = i + 1

    labels = ['Airports']
    fig, ax = plt.subplots(figsize=(6, 5))

    # Barra base (Schengen)
    ax.bar(labels, [schengen_count], label='Schengen')
    # Barra superior (No Schengen) colocada mediante el parámetro 'bottom'
    ax.bar(labels, [no_schengen_count], bottom=[schengen_count], label='No Schengen')

    ax.set_ylabel('Count')
    ax.set_title('Schengen airports')
    ax.legend()
    plt.show()


# =============================================================================
# MAPAS KML (Google Earth)
# =============================================================================

def MapAirports(airports):
    """
    Genera un archivo XML con formato KML. Este archivo lo lee Google Earth
    para poner 'chinchetas' (Placemarks) en el globo terráqueo.
    """
    if not airports:
        print("Error: empty list")
        return

    file = open("airports.kml", "w")

    # Cabeceras estándar de un archivo KML
    file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    file.write('<kml xmlns="http://www.opengis.net/kml/2.2">\n')
    file.write('<Document>\n')

    for airport in airports:
        lat = airport.coordinates[0]
        lon = airport.coordinates[1]

        # Condicional clásico de color: Schengen = Rojo, No Schengen = Verde
        if airport.schengen:
            color = "ff0000ff"
        else:
            color = "ff00ff00"

            # Estructura obligatoria de Google Earth por cada punto en el mapa
        file.write('<Placemark>\n')
        file.write(f'<name>{airport.icao}</name>\n')
        file.write('<Style><IconStyle>\n')
        file.write(f'<color>{color}</color>\n')
        file.write('</IconStyle></Style>\n')
        file.write('<Point>\n')
        # Google Earth usa el formato LONGITUD, LATITUD (al revés que Google Maps)
        file.write(f'<coordinates>{lon},{lat},0</coordinates>\n')
        file.write('</Point>\n')
        file.write('</Placemark>\n')

    # Cierre de las etiquetas
    file.write('</Document>\n')
    file.write('</kml>\n')
    file.close()

    print("File airports.kml created.")


# =============================================================================
# MATEMÁTICAS DE COORDENADAS
# =============================================================================

def ConvertCoord(coord):
    """
    Convierte un string de formato sexagesimal (ej: N412345) a un decimal puro (41.3958).
    Fórmula: Grados + (Minutos / 60) + (Segundos / 3600)
    """
    direction = coord[0]  # N, S, E, W
    value = coord[1:]  # El resto de los números

    # Si tiene 6 números es Latitud (DDMMSS)
    if len(value) == 6:
        degrees = int(value[0:2])
        minutes = int(value[2:4])
        seconds = int(value[4:6])
    # Si tiene 7 números es Longitud (DDDMMSS) porque los grados pueden ser hasta 180
    else:
        degrees = int(value[0:3])
        minutes = int(value[3:5])
        seconds = int(value[5:7])

    decimal = degrees + minutes / 60 + seconds / 3600

    # Por convención matemática, el Sur y el Oeste son coordenadas negativas en el plano cartesiano
    if direction in ['S', 'W']:
        decimal = -decimal

    return decimal


def FormatCoord(value, is_lat):
    """
    Hace la operación matemática inversa a ConvertCoord.
    Pasa de un decimal puro (ej: 41.3958) a formato texto (N412345).
    """
    # Determinamos la letra de dirección
    if is_lat:
        direction = 'N' if value >= 0 else 'S'
    else:
        direction = 'E' if value >= 0 else 'W'

    value = abs(value)  # Trabajamos con valor absoluto para los cálculos

    # Extraemos la parte entera (Grados)
    degrees = int(value)

    # Extraemos la parte decimal, la pasamos a minutos y separamos la parte entera
    minutes_full = (value - degrees) * 60
    minutes = int(minutes_full)

    # El resto decimal de los minutos lo pasamos a segundos
    seconds = int((minutes_full - minutes) * 60)

    # El formato {:02d} asegura que siempre se pongan ceros a la izquierda si el número es < 10
    if is_lat:
        return f"{direction}{degrees:02d}{minutes:02d}{seconds:02d}"
    else:
        # La longitud usa 3 ceros a la izquierda para los grados
        return f"{direction}{degrees:03d}{minutes:02d}{seconds:02d}"