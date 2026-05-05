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