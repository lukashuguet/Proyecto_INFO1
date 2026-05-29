import matplotlib.pyplot as plt
from airport import *
import math
import os

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
        if not line or line.startswith("AIRCRAFT"):
            continue

        parts = line.split()
        if len(parts) != 4:
            continue

        id = parts[0]
        origin = parts[1]
        arrival = parts[2]
        airline = parts[3]

        if ":" not in arrival:
            continue

        aircraft = Aircraft(id, airline, origin, arrival)
        # Sincronizamos la propiedad arrival_time para que el motor dinámico la reconozca uniformemente
        aircraft.arrival_time = arrival
        aircrafts.append(aircraft)

    return aircrafts

# Guarda los vuelos en un fichero de salida
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

# Genera un archivo KML para visualizar vuelos en Google Earth
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

        color = "ff0000ff" if origin_ap.schengen else "ff00ff00"

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

# Formula de Haversine
def Haversine(lat1, lon1, lat2, lon2):
    R = 6371
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

# Devuelve los vuelos de larga distancia (>2000 km)
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
        if dist > 2000:
            result.append(a)

    return result

def LoadDepartures(filename):
    aircrafts = []
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
        if not line or "AIRCRAFT" in line or "DESTINATION" in line:
            continue

        parts = line.split()
        if len(parts) >= 4:
            try:
                ac = Aircraft(parts[0], parts[3])
                ac.destination = parts[1]
                ac.departure_time = parts[2]
                aircrafts.append(ac)
            except Exception as e:
                print(f"Error en línea: {line} -> {e}")
                continue

    return aircrafts

def MergeMovements(arrivals_list, departures_list):
    return arrivals_list + departures_list

def NightAircraft(movements_list):
    nocturnos = []
    for ac in movements_list:
        if hasattr(ac, 'departure_time') and ac.departure_time:
            hora = int(ac.departure_time.split(':')[0])
            if hora < 9:
                nocturnos.append(ac)
    if not nocturnos:
        nocturnos = movements_list[:10]
    return nocturnos

def AssignNightGates(airport_obj, night_aircraft_list):
    if not airport_obj or not night_aircraft_list:
        return

    idx = 0
    for terminal in airport_obj.terminals:
        for area in terminal.boarding_areas:
            for gate in area.gates:
                if idx < len(night_aircraft_list):
                    gate.occupied = True
                    gate.aircraft = night_aircraft_list[idx].id
                    idx += 1

def AllocateGatesDynamic(airport_obj, movements_list, current_time_str):
    if not airport_obj or not movements_list:
        return 0

    for terminal in airport_obj.terminals:
        for area in terminal.boarding_areas:
            for gate in area.gates:
                gate.occupied = False
                gate.aircraft = ""

    hora_slider = int(current_time_str.split(':')[0])
    no_asignados = 0
    idx_puerta = 0

    vuelos_de_la_hora = []
    for ac in movements_list:
        hora_vuelo = -1
        if hasattr(ac, 'departure_time') and ac.departure_time:
            hora_vuelo = int(ac.departure_time.split(':')[0])
        elif hasattr(ac, 'arrival_time') and ac.arrival_time:
            hora_vuelo = int(ac.arrival_time.split(':')[0])

        if hora_vuelo == hora_slider:
            vuelos_de_la_hora.append(ac)

    for terminal in airport_obj.terminals:
        for area in terminal.boarding_areas:
            for gate in area.gates:
                if idx_puerta < len(vuelos_de_la_hora):
                    gate.occupied = True
                    gate.aircraft = vuelos_de_la_hora[idx_puerta].id
                    idx_puerta += 1

    if len(vuelos_de_la_hora) > idx_puerta:
        no_asignados = len(vuelos_de_la_hora) - idx_puerta

    return no_asignados

# =============================================================================
# BLOQUE DE GRÁFICOS SOLICITADOS (ACTUALIZADO Y ADAPTADO A TUS CAPTURAS)
# =============================================================================

def PlotDayOccupancy(airport_obj, movements_list):
    """
    Gráfico de líneas (Sección 4): Muestra el movimiento natural y real
    de la ocupación horaria dividiendo los vuelos en Schengen y No-Schengen.
    """
    import copy
    # Importamos tu función oficial de asignación
    from LEBL import AssignGate

    horas_eje = list(range(24))
    ocupacion_t1 = [0] * 24
    ocupacion_t2 = [0] * 24

    # Copia profunda para no alterar los colores de la interfaz de Tkinter
    estructura_temporal = copy.deepcopy(airport_obj)

    # Códigos de países del espacio Schengen para el filtrado nativo
    SCHENGEN_PREFIXES = {
        'ED', 'ET', 'LO', 'EB', 'EK', 'LZ', 'LJ', 'LE', 'EE', 'EF', 'LF', 'LG', 'LH',
        'BI', 'LI', 'EV', 'EY', 'LN', 'EH', 'EP', 'LP', 'LK', 'ES', 'LS', 'LH'
    }

    for h in range(24):
        # --- RESETEO NATURAL DE PUERTAS AL INICIO DE LA HORA ---
        for terminal in estructura_temporal.terminals:
            for area in terminal.boarding_areas:
                for gate in area.gates:
                    gate.occupied = False
                    if hasattr(gate, 'aircraft'): gate.aircraft = ""

        # --- ASIGNACIÓN DE VUELOS DE ESTA HORA ---
        for ac in movements_list:
            time_str = getattr(ac, 'arrival_time', getattr(ac, 'departure_time', getattr(ac, 'arrival', None)))
            if time_str and ":" in time_str:
                try:
                    hora_vuelo = int(time_str.split(':')[0])
                    if hora_vuelo == h:

                        # Determinación del estado Schengen real del vuelo
                        is_schengen = True

                        # Si es una salida, miramos el destino. Si es llegada, el origen.
                        codigo_remoto = getattr(ac, 'destination', getattr(ac, 'origin', ''))

                        if codigo_remoto and len(codigo_remoto) >= 2:
                            prefix = codigo_remoto[:2].upper()
                            # Si no empieza por España (LE) ni está en la lista Schengen, es internacional
                            if prefix != 'LE' and prefix not in SCHENGEN_PREFIXES:
                                is_schengen = False

                        # Llamamos a tu algoritmo original para que asigne según tus reglas del proyecto
                        AssignGate(estructura_temporal, ac, is_schengen)

                except ValueError:
                    continue

        # --- CONTEO MEDIDO DE LA HORA ---
        for terminal in estructura_temporal.terminals:
            puertas_ocupadas = 0
            for area in terminal.boarding_areas:
                for gate in area.gates:
                    if gate.occupied:
                        puertas_ocupadas += 1

            if "1" in terminal.name or terminal.name == "T1":
                ocupacion_t1[h] = puertas_ocupadas
            elif "2" in terminal.name or terminal.name == "T2":
                ocupacion_t2[h] = puertas_ocupadas

    # --- RENDERIZADO DEL GRÁFICO REAL ---
    fig, ax = plt.subplots(figsize=(10, 5), facecolor="#f8f9fa")

    linea_t1, = ax.plot(horas_eje, ocupacion_t1, color='#4a90e2', marker='o', linestyle='-', linewidth=2,
                        label='Occupied Gates T1')
    linea_t2, = ax.plot(horas_eje, ocupacion_t2, color='#2ecc71', marker='s', linestyle='-', linewidth=2,
                        label='Occupied Gates T2')

    ax.set_xlabel('Hora del Día (h)', fontsize=11, weight='bold')
    ax.set_ylabel('Puertas Ocupadas', fontsize=11, weight='bold')
    ax.set_xticks(horas_eje)
    ax.set_xticklabels([f"{h:02d}:00" for h in horas_eje], rotation=45, fontsize=9)
    ax.set_ylim(bottom=0)
    ax.legend(loc='upper left')
    ax.grid(True, linestyle=':', alpha=0.6)

    plt.title("Análisis Diario de Operaciones: Ocupación por Terminal (24h)", fontsize=12, weight='bold', pad=15)
    plt.tight_layout()
    plt.show()

def PlotArrivalsPerHour(movements_list):
    """Gráfico 2: Histograma de Barras - Arrivals per hour."""
    hours_count = [0] * 24
    for ac in movements_list:
        time_str = getattr(ac, 'arrival_time', getattr(ac, 'arrival', None))
        if time_str and ":" in time_str:
            try:
                hour = int(time_str.split(":")[0])
                if 0 <= hour < 24:
                    hours_count[hour] += 1
            except:
                continue

    plt.figure(figsize=(10, 6))
    plt.bar(range(24), hours_count, color='#1f77b4', width=0.8)
    plt.xlabel("Hour", fontsize=12)
    plt.ylabel("Arrivals", fontsize=12)
    plt.title("Arrivals per hour", fontsize=14)
    plt.xticks(range(24))
    plt.grid(axis='y', linestyle='-', alpha=0.3)
    plt.tight_layout()
    plt.show()


def PlotFlightsPerAirline(movements_list):
    """Gráfico 3: Histograma de Barras completo - Flights per airline."""
    counts = {}
    for ac in movements_list:
        counts[ac.airline] = counts.get(ac.airline, 0) + 1

    # Ordenamos descendente para asemejarlo al formato visual de la captura
    sorted_counts = dict(sorted(counts.items(), key=lambda x: x[1], reverse=True))
    airlines = list(sorted_counts.keys())
    values = list(sorted_counts.values())

    plt.figure(figsize=(12, 6))
    plt.bar(airlines, values, color='#1f77b4', width=0.6)
    plt.ylabel("Flights", fontsize=12)
    plt.title("Flights per airline", fontsize=14)
    plt.xticks(rotation=90, fontsize=8)
    plt.tight_layout()
    plt.show()


def PlotSchengenProportion(movements_list):
    """Gráfico 4: Barras Apiladas - Flights type (Schengen vs Non-Schengen)."""
    schengen = 0
    non_schengen = 0
    SCHENGEN_COUNTRIES = {'DE', 'AT', 'BE', 'DK', 'SK', 'SI', 'ES', 'EE', 'FI', 'FR', 'GR', 'HU',
                          'IS', 'IT', 'LV', 'LI', 'LT', 'LU', 'MT', 'NO', 'NL', 'PL', 'PT', 'CZ', 'SE', 'CH'}

    for ac in movements_list:
        if hasattr(ac, 'is_schengen'):
            if ac.is_schengen: schengen += 1
            else: non_schengen += 1
        else:
            origin_code = getattr(ac, 'origin', '')
            if origin_code and origin_code[:2] in SCHENGEN_COUNTRIES:
                schengen += 1
            else:
                non_schengen += 1

    plt.figure(figsize=(6, 6))
    plt.bar(['Flights'], [schengen], label='Schengen', color='#1f77b4', width=0.5)
    plt.bar(['Flights'], [non_schengen], bottom=[schengen], label='Non-Schengen', color='#ff7f0e', width=0.5)

    plt.ylabel("Count", fontsize=12)
    plt.title("Flights type", fontsize=14)
    plt.legend(loc='upper right')
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    # Mantener el bloque de ejecución directa intacto si se lanza aislado
    pass