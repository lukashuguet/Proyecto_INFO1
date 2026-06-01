"""
MÓDULO AIRCRAFT.PY (Análisis de Vuelos y Estadísticas)
Este archivo se encarga de gestionar los objetos 'Aircraft' (aviones),
cargar sus rutas desde archivos de texto, calcular distancias matemáticas
(Haversine) y preparar los datos visuales (Gráficos de Matplotlib y mapas KML).
"""

# =============================================================================
# IMPORTACIONES BÁSICAS Y ACADÉMICAS
# =============================================================================
import math  # Para los senos y cosenos de la fórmula de Haversine

# =============================================================================
# DEFINICIÓN DE CLASES
# =============================================================================
class Aircraft:
    """
    Representa un vuelo físico (llegada o salida).
    Guarda su matrícula (id), de qué compañía es, de dónde viene y a dónde va.
    """

    def __init__(self, id, airline="", origin="", arrival=""):
        self.id = id
        self.airline = airline
        self.origin = origin
        self.arrival = arrival  # Texto crudo de llegada
        self.arrival_time = arrival  # Hora procesada de llegada
        self.departure_time = ""  # Hora de salida (si aplica)
        self.destination = ""  # Código ICAO de destino (si aplica)
        self.is_schengen = False  # Etiqueta para saber si el vuelo es intra-europeo


# =============================================================================
# FUNCIONES DE LECTURA, GUARDADO Y BÚSQUEDA
# =============================================================================
def FindAirport(airports, code):
    """
    Busca un aeropuerto en la lista global usando un bucle 'while' puro y
    un booleano para detener la búsqueda cuando lo encuentra.
    """
    i = 0
    encontrado = False
    resultado = None
    while i < len(airports) and not encontrado:
        if airports[i].icao == code:
            encontrado = True
            resultado = airports[i]
        i = i + 1
    return resultado


def LoadArrivals(filename):
    """Carga los vuelos de llegadas de forma robusta."""
    aircrafts = []

    try:
        # 1. Apertura explícita en modo lectura 'r'
        file = open(filename, "r")
        linea = file.readline()

        while linea != "":
            linea_limpia = linea.strip('\n')

            if len(linea_limpia) > 0 and linea_limpia[0:8] != "AIRCRAFT":
                partes = linea_limpia.split(' ')

                if len(partes) >= 4:
                    # Creamos el objeto
                    aircraft = Aircraft(partes[0], partes[3], partes[1], partes[2])
                    aircrafts.append(aircraft)

            linea = file.readline()
        file.close()

        # 2. Retorno doble: Éxito (True) y los datos
        return True, aircrafts

    except FileNotFoundError:
        # 3. Robustez: Si el archivo falta, avisamos devolviendo False
        return False, []
    except Exception:
        # Captura cualquier otro error inesperado (formato, permisos)
        return False, []


def SaveFlights(aircrafts, filename):
    """
    Guarda la lista de aviones en un archivo .txt.
    Utiliza concatenación de strings clásica (con '+') muy valorada en cursos básicos.
    """
    if len(aircrafts) == 0:
        return -1

    file = open(filename, "w")
    file.write("AIRCRAFT ORIGIN ARRIVAL AIRLINE\n")

    i = 0
    while i < len(aircrafts):
        a = aircrafts[i]
        # Operadores ternarios para poner un guion '-' si el dato está vacío
        origin = a.origin if a.origin != "" else "-"
        arrival = a.arrival if a.arrival != "" else "0:00"
        airline = a.airline if a.airline != "" else "-"

        # Concatenación clásica
        linea_texto = a.id + " " + origin + " " + arrival + " " + airline + "\n"
        file.write(linea_texto)
        i = i + 1

    file.close()


def MapFlights(lista_vuelos, lista_aeropuertos, filename):
    """
    Genera un archivo KML de forma robusta.
    lista_vuelos: La lista de objetos Aircraft a pintar.
    lista_aeropuertos: La base de datos de aeropuertos para buscar coordenadas.
    filename: El nombre del archivo donde guardar el KML.
    """
    # Si algo falta, retornamos False
    if len(lista_vuelos) == 0 or len(lista_aeropuertos) == 0:
        return False

    # 2. Búsqueda de destino
    dest = FindAirport(lista_aeropuertos, "LEBL")
    if dest is None:
        return False

    try:
        # 3. Apertura usando la variable 'filename'
        file = open(filename, "w")

        file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        file.write('<kml xmlns="http://www.opengis.net/kml/2.2">\n')
        file.write('<Document>\n')

        i = 0
        while i < len(lista_vuelos):
            vuelo = lista_vuelos[i]
            # Buscamos el aeropuerto de origen del vuelo
            origin_ap = FindAirport(lista_aeropuertos, vuelo.origin)

            if origin_ap is not None:
                lat1 = origin_ap.coordinates[0]
                lon1 = origin_ap.coordinates[1]
                lat2 = dest.coordinates[0]
                lon2 = dest.coordinates[1]

                color = "ff0000ff" if origin_ap.schengen else "ff00ff00"

                file.write('<Placemark>\n')
                file.write('<name>' + str(vuelo.id) + '</name>\n')
                file.write('<Style><LineStyle>\n')
                file.write('<color>' + color + '</color>\n')
                file.write('<width>2</width>\n')
                file.write('</LineStyle></Style>\n')
                file.write('<LineString>\n')
                file.write('<coordinates>\n')
                file.write(str(lon1) + ',' + str(lat1) + ',0 ' + str(lon2) + ',' + str(lat2) + ',0\n')
                file.write('</coordinates>\n')
                file.write('</LineString>\n')
                file.write('</Placemark>\n')
            i = i + 1

        file.write('</Document>\n')
        file.write('</kml>\n')
        file.close()
        return True  # Perfecto

    except Exception:
        # Si falla el 'open' o cualquier escritura, informamos de error
        return False


# =============================================================================
# MATEMÁTICAS AVANZADAS (Distancias Esféricas)
# =============================================================================
def Haversine(lat1, lon1, lat2, lon2):
    """
    Fórmula trigonométrica de Haversine.
    Calcula la distancia real en línea recta (en Kilómetros) entre dos puntos
    de una esfera (la Tierra), ignorando las elevaciones.
    """
    R = 6371  # Radio aproximado de la Tierra en km

    # Convertimos los grados decimales a radianes (necesario para math.sin y math.cos)
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    # Aplicación estricta de la fórmula
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c  # Distancia en km


def LongDistanceArrivals(aircrafts, airports):
    """Filtra y devuelve aquellos vuelos que recorren más de 2000 km."""
    if len(aircrafts) == 0 or len(airports) == 0:
        return -1

    result = []
    dest = FindAirport(airports, "LEBL")
    if dest == None:
        return result

    i = 0
    while i < len(aircrafts):
        a = aircrafts[i]
        origin_ap = FindAirport(airports, a.origin)
        if origin_ap != None:
            # Calculamos la distancia usando nuestra fórmula matemática
            dist = Haversine(
                origin_ap.coordinates[0],
                origin_ap.coordinates[1],
                dest.coordinates[0],
                dest.coordinates[1]
            )
            # Si supera los 2000 km, lo añadimos al resultado
            if dist > 2000:
                result.append(a)
        i = i + 1

    return result


def LoadDepartures(filename):
    """
    Carga el archivo de Salidas (Departures).
    Devuelve True/False y la lista cargada.
    """
    aircrafts = []

    try:
        # Añadimos "r" explícitamente para modo lectura
        file = open(filename, "r")
        linea = file.readline()

        while linea != "":
            linea_limpia = linea.strip('\n')

            if len(linea_limpia) > 0 and linea_limpia[0:8] != "AIRCRAFT":
                partes = linea_limpia.split(' ')

                if len(partes) >= 4:
                    id_avion = partes[0]
                    destination = partes[1]
                    departure_time = partes[2]
                    airline = partes[3]

                    # 1. Creamos el objeto (dejamos el origen y la llegada vacíos "")
                    ac = Aircraft(id_avion, airline, "", "")

                    # 2. Le inyectamos sus datos en los atributos correctos
                    ac.departure_time = departure_time
                    ac.destination = destination

                    # Añadimos el avión a la lista (¡Sin comprobar Schengen aquí!)
                    aircrafts.append(ac)

            linea = file.readline()

        file.close()
        # ÉXITO: Devolvemos True y la lista llena
        return True, aircrafts


    except FileNotFoundError:

        return False, []

    except Exception as e:

        # AQUÍ ESTÁ LA CLAVE: Imprimimos el error real en la consola

        print(f"DEBUG ERROR OCULTO EN SALIDAS: {e}")

        import traceback

        traceback.print_exc()  # Esto nos dirá la línea exacta del fallo

        return False, []



def MergeMovements(arrivals_list, departures_list):
    # 1. Comprobar listas vacías
    if len(arrivals_list) == 0 or len(departures_list) == 0:
        return -1

    resultado = []

    # 2. Copiamos todas las llegadas iniciales a la lista resultado
    i = 0
    while i < len(arrivals_list):
        resultado.append(arrivals_list[i])
        i = i + 1

    # 3. Iteramos sobre las salidas para fusionarlas
    j = 0
    while j < len(departures_list):
        avion_salida = departures_list[j]
        encontrado = False
        k = 0

        # Búsqueda clásica para encontrar su llegada correspondiente
        while k < len(resultado) and not encontrado:
            avion_llegada = resultado[k]

            # Condición de fusión
            if avion_llegada.id == avion_salida.id and avion_llegada.arrival < avion_salida.departure_time:
                if avion_llegada.departure_time is None or avion_llegada.departure_time == "":
                    # FUSIÓN DE DATOS REAL (sin almohadillas)
                    avion_llegada.departure_time = avion_salida.departure_time
                    avion_llegada.destination = avion_salida.destination
                    avion_llegada.is_schengen = avion_salida.is_schengen

                    encontrado = True
            k = k + 1

        # Si tras buscar en toda la lista no hemos encontrado su llegada compatible
        if not encontrado:
            resultado.append(avion_salida)

        j = j + 1

    return resultado