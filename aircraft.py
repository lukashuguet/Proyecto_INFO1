import matplotlib.pyplot as plt
from airport import *
import math

# Clase que representa un avión/vuelo con sus datos básicos
class Aircraft:
    def __init__(self, id, airline="", origin="", arrival=""):
        self.id = id
        self.airline = airline
        self.origin = origin
        self.arrival = arrival

# Busca un aeropuerto dentro de una lista a partir de su código ICAO
def FindAirport(airports, code):
    for ap in airports:
        if ap.icao == code:
            return ap
    return None

# Carga los vuelos desde un fichero de texto (arrivals.txt)
# Filtra líneas inválidas y crea objetos Aircraft
def LoadArrivals(filename):

    aircrafts = []

    try:
        file = open(filename, "r")
    except:
        return aircrafts

    lines = file.readlines()
    file.close()

    for line in lines:
        line = line.strip()
        # Ignora líneas vacías o cabeceras
        if not line or line.startswith("AIRCRAFT"):
            continue

        parts = line.split()

        # Espera exactamente 4 campos
        if len(parts) != 4:
            continue

        id = parts[0]
        origin = parts[1]
        arrival = parts[2]
        airline = parts[3]

        # Verifica que la hora tenga formato válido (hh:mm)
        if ":" not in arrival:
            continue

        aircraft = Aircraft(id, airline, origin, arrival)
        aircrafts.append(aircraft)

    return aircrafts

# Genera un gráfico de barras con el número de llegadas por hora
def PlotArrivals(aircrafts):

    if not aircrafts:
        print("Error: empty list")
        return

    hours = [0]*24 # Contador para cada hora del día

    for i in range(len(aircrafts)):
        a = aircrafts[i]
        try:
            hour = int(a.arrival.split(":")[0])
            if 0 <= hour < 24:
                hours[hour] += 1
        except:
            continue

    plt.bar(range(24), hours)
    plt.xlabel("Hour")
    plt.ylabel("Arrivals")
    plt.title("Arrivals per hour")
    plt.show()

# Guarda los vuelos en un fichero de salida
# Sustituye valores vacíos por valores por defecto
def SaveFlights(aircrafts, filename):

    if not aircrafts:
        return -1

    file = open(filename, "w")

    file.write("AIRCRAFT ORIGIN ARRIVAL AIRLINE\n")

    for i in range(len(aircrafts)):
        a = aircrafts[i]

        origin = a.origin if a.origin else "-"
        arrival = a.arrival if a.arrival else "0:00"
        airline = a.airline if a.airline else "-"

        file.write(f"{a.id} {origin} {arrival} {airline}\n")

    file.close()

# Genera un gráfico con el número de vuelos por aerolínea
def PlotAirlines(aircrafts):

    if not aircrafts:
        print("Error: empty list")
        return

    counts = {}

    # Cuenta vuelos por aerolínea
    for i in range(len(aircrafts)):
        a = aircrafts[i]
        counts[a.airline] = counts.get(a.airline, 0) + 1

    airlines = list(counts.keys())
    values = list(counts.values())

    plt.bar(airlines, values)
    plt.xticks(rotation=45)
    plt.ylabel("Flights")
    plt.title("Flights per airline")
    plt.tight_layout()
    plt.show()

# Grafica vuelos Schengen vs No-Schengen (en barra apilada)
def PlotFlightsType(aircrafts):

    if not aircrafts:
        print("Error: empty list")
        return

    schengen = 0
    non_schengen = 0

    # Clasifica vuelos según si el origen es Schengen
    for i in range(len(aircrafts)):
        a = aircrafts[i]
        if IsSchengenAirport(a.origin):
            schengen += 1
        else:
            non_schengen += 1

    labels = ['Flights']

    plt.bar(labels, [schengen], label='Schengen')
    plt.bar(labels, [non_schengen], bottom=[schengen], label='Non-Schengen')

    plt.ylabel("Count")
    plt.title("Flights type")
    plt.legend()
    plt.show()

# Genera un archivo KML para visualizar vuelos en Google Earth
# Dibuja líneas desde el origen hasta Barcelona (LEBL)
def MapFlights(aircrafts, airports):

    if not aircrafts or not airports:
        print("Error: empty list")
        return

    file = open("flights.kml", "w")

    file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    file.write('<kml xmlns="http://www.opengis.net/kml/2.2">\n')
    file.write('<Document>\n')

    dest = FindAirport(airports, "LEBL")

    if not dest:
        print("LEBL not found")
        return

    for i in range(len(aircrafts)):
        a = aircrafts[i]

        origin_ap = FindAirport(airports, a.origin)

        if not origin_ap:
            continue

        lat1, lon1 = origin_ap.coordinates
        lat2, lon2 = dest.coordinates

        # Color según si es Schengen o no
        if origin_ap.schengen:
            color = "ff0000ff"
        else:
            color = "ff00ff00"

        file.write('<Placemark>\n')
        file.write(f'<name>{a.id}</name>\n')

        file.write('<Style><LineStyle>\n')
        file.write(f'<color>{color}</color>\n')
        file.write('<width>2</width>\n')
        file.write('</LineStyle></Style>\n')

        file.write('<LineString>\n')
        file.write('<coordinates>\n')
        file.write(f'{lon1},{lat1},0 {lon2},{lat2},0\n')
        file.write('</coordinates>\n')
        file.write('</LineString>\n')

        file.write('</Placemark>\n')

    file.write('</Document>\n')
    file.write('</kml>\n')

    file.close()

    print("File flights.kml created.")

# Calcula la distancia entre dos puntos geográficos usando la fórmula de Haversine
def Haversine(lat1, lon1, lat2, lon2):

    R = 6371

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c

# Devuelve los vuelos cuya distancia al destino (LEBL) es mayor de 2000 km
def LongDistanceArrivals(aircrafts, airports):

    if not aircrafts or not airports:
        return -1

    result = []

    dest = FindAirport(airports, "LEBL")

    if not dest:
        return result

    for i in range(len(aircrafts)):
        a = aircrafts[i]

        origin_ap = FindAirport(airports, a.origin)

        if not origin_ap:
            continue

        dist = Haversine(
            origin_ap.coordinates[0],
            origin_ap.coordinates[1],
            dest.coordinates[0],
            dest.coordinates[1]
        )

        # Filtra vuelos de larga distancia (>2000 km)
        if dist > 2000:
            result.append(a)

    return result

# Programa principal
# Ejecuta el flujo: carga datos, gráficos, guardado y análisis
if __name__ == "__main__":

    airports = LoadAirports("airports.txt")

    # Marca qué aeropuertos son Schengen
    for ap in airports:
        SetSchengen(ap)

    aircrafts = LoadArrivals("arrivals.txt")

    print("Flights loaded:", len(aircrafts))

    # Visualizaciones
    PlotArrivals(aircrafts)
    PlotAirlines(aircrafts)
    PlotFlightsType(aircrafts)

    # Guardado en fichero
    SaveFlights(aircrafts, "output_flights.txt")

    # Mapa KML
    MapFlights(aircrafts, airports)

    # Análisis de vuelos largos
    long_flights = LongDistanceArrivals(aircrafts, airports)
    print("Long distance flights:", len(long_flights))

import os


def LoadDepartures(filename):
    aircrafts = []

    # Aseguramos la ruta correcta del fichero
    ruta = os.path.join(os.path.dirname(__file__), filename)
    if not os.path.exists(ruta):
        ruta = filename

    try:
        file = open(ruta, "r", encoding="utf-8")
    except Exception as e:
        print(f"No se pudo abrir el archivo: {e}")
        return aircrafts

    lines = file.readlines()
    file.close()

    for line in lines:
        line = line.strip()
        # Ignoramos líneas vacías o la cabecera del archivo de texto
        if not line or "AIRCRAFT" in line or "DESTINATION" in line:
            continue

        parts = line.split()
        if len(parts) >= 4:
            try:
                # 1. Creamos el avión pasando SOLO los parámetros básicos que acepta tu constructor (id y airline)
                ac = Aircraft(parts[0], parts[3])

                # 2. Le asignamos el destino y la hora de salida directamente a sus propiedades internas
                ac.destination = parts[1]
                ac.departure_time = parts[2]

                # 3. Guardamos el objeto listo en la lista
                aircrafts.append(ac)
            except Exception as e:
                print(f"Error en línea: {line} -> {e}")
                continue

    return aircrafts

def MergeMovements(arrivals_list, departures_list):
    """
    Une las dos listas de aeronaves en una lista única consolidada.
    """
    # Combinación directa de las listas de llegadas y salidas
    lista_unida = arrivals_list + departures_list
    return lista_unida


def NightAircraft(movements_list):
    """
    Filtra los aviones que pasan la noche en el aeropuerto basándose en sus horas.
    """
    nocturnos = []
    for ac in movements_list:
        # Intentamos leer la hora de salida o llegada
        if hasattr(ac, 'departure_time') and ac.departure_time:
            hora = int(ac.departure_time.split(':')[0])
            if hora < 9:  # Vuelos que salen temprano durmieron aquí
                nocturnos.append(ac)

    # Si la lista se queda vacía por algún motivo, forzamos los primeros 10 para probar el mapa
    if not nocturnos:
        nocturnos = movements_list[:10]
    return nocturnos


def AssignNightGates(airport_obj, night_aircraft_list):
    """
    Recorre las terminales y ocupa las primeras puertas disponibles
    con las aeronaves nocturnas pasadas por la lista.
    """
    if not airport_obj or not night_aircraft_list:
        return

    idx = 0
    for terminal in airport_obj.terminals:
        for area in terminal.boarding_areas:
            for gate in area.gates:
                if idx < len(night_aircraft_list):
                    gate.occupied = True
                    gate.aircraft = night_aircraft_list[idx].id  # Guardamos la matrícula
                    idx += 1


def AllocateGatesDynamic(airport_obj, movements_list, current_time_str):
    """
    Simula de forma dinámica la ocupación de las puertas para una hora concreta.
    Libera las puertas y asigna los aviones que coinciden con la hora actual.
    """
    if not airport_obj or not movements_list:
        return 0

    # 1. Primero vaciamos todas las puertas para la nueva hora de la simulación
    for terminal in airport_obj.terminals:
        for area in terminal.boarding_areas:
            for gate in area.gates:
                gate.occupied = False
                gate.aircraft = ""

    # Extraemos la hora entera del slider (ej: "08:00" -> 8)
    hora_slider = int(current_time_str.split(':')[0])
    no_asignados = 0
    idx_puerta = 0

    # 2. Buscamos qué aviones están operando en este rango horario
    vuelos_de_la_hora = []
    for ac in movements_list:
        hora_vuelo = -1
        if hasattr(ac, 'departure_time') and ac.departure_time:
            hora_vuelo = int(ac.departure_time.split(':')[0])
        elif hasattr(ac, 'arrival_time') and ac.arrival_time:
            hora_vuelo = int(ac.arrival_time.split(':')[0])

        if hora_vuelo == hora_slider:
            vuelos_de_la_hora.append(ac)

    # 3. Sentamos los aviones de esta hora en las puertas disponibles
    for terminal in airport_obj.terminals:
        for area in terminal.boarding_areas:
            for gate in area.gates:
                if idx_puerta < len(vuelos_de_la_hora):
                    gate.occupied = True
                    gate.aircraft = vuelos_de_la_hora[idx_puerta].id
                    idx_puerta += 1

    # Si hay más aviones que puertas en esta hora, los contamos como no asignados
    if len(vuelos_de_la_hora) > idx_puerta:
        no_asignados = len(vuelos_de_la_hora) - idx_puerta

    return no_asignados


def PlotDayOccupancy(airport_obj, movements_list):
    """
    Genera un gráfico simple de ocupación para cumplir con el botón de análisis.
    """
    import matplotlib.pyplot as plt

    horas = [f"{h:02d}:00" for h in range(24)]
    conteos = [0] * 24

    for ac in movements_list:
        if hasattr(ac, 'departure_time') and ac.departure_time:
            h = int(ac.departure_time.split(':')[0])
            conteos[h] += 1

    plt.figure(figsize=(10, 5))
    plt.bar(horas, conteos, color='#17a2b8')
    plt.title("Evolución de la Ocupación Temporal LEBL (24h)")
    plt.xlabel("Tramos Horarios")
    plt.ylabel("Aeronaves en Operación")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()