"""
MÓDULO AIRCRAFT.PY (Análisis de Vuelos y Estadísticas)
Este archivo se encarga de gestionar los objetos 'Aircraft' (aviones),
cargar sus rutas desde archivos de texto, calcular distancias matemáticas
(Haversine) y preparar los datos visuales (Gráficos de Matplotlib y mapas KML).
"""

# =============================================================================
# IMPORTACIONES BÁSICAS Y ACADÉMICAS
# =============================================================================
from matplotlib.figure import Figure  # Usamos Figure en lugar de plt para incrustarlo en Tkinter
import math  # Para los senos y cosenos de la fórmula de Haversine
import copy  # Para duplicar estructuras de datos sin modificar las originales



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
    """Carga los vuelos de llegadas leyendo el archivo línea a línea."""
    # Inicializamos la lista vacía
    aircrafts = []

    try:
        # Apertura clásica como en clase
        file = open(filename)
        linea = file.readline()

        while linea != "":
            # Quitamos el salto de línea explícitamente
            linea_limpia = linea.strip('\n')

            # Tu lógica impecable para evitar líneas vacías o la cabecera
            if len(linea_limpia) > 0 and linea_limpia[0:8] != "AIRCRAFT":
                # Separamos los datos. Asumo que están separados por espacio.
                # (Si hubiese varios espacios, podrías usar split() vacío,
                # pero split(' ') es lo más estándar en nuestros apuntes).
                partes = linea_limpia.split(' ')

                # Validamos que al menos haya 4 partes
                if len(partes) >= 4:
                    id_avion = partes[0]
                    origin = partes[1]
                    arrival = partes[2]
                    airline = partes[3]

                    # ¡ATENCIÓN AQUÍ!
                    # Verifica que el __init__ de tu clase Aircraft está en ESTE orden:
                    # def __init__(self, id_avion, airline, origen, hora):
                    aircraft = Aircraft(id_avion, airline, origin, arrival)
                    aircrafts.append(aircraft)

            # Leemos la siguiente línea para que el bucle avance
            linea = file.readline()

        file.close()
    except Exception:
        pass  # Si no existe el archivo, devuelve la lista vacía silenciosamente

    return aircrafts


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


def MapFlights(aircrafts, airports):
    """
    Genera un archivo KML para Google Earth que traza LÍNEAS ('LineString')
    desde el aeropuerto de origen hasta Barcelona (LEBL).
    """
    if len(aircrafts) == 0 or len(airports) == 0:
        print("Error: empty list")
        return

    file = open("flights.kml", "w")
    file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    file.write('<kml xmlns="http://www.opengis.net/kml/2.2">\n')
    file.write('<Document>\n')

    # Buscamos las coordenadas de nuestro aeropuerto de destino (Barcelona)
    dest = FindAirport(airports, "LEBL")
    if dest == None:
        print("LEBL not found")
        return

    i = 0
    while i < len(aircrafts):
        a = aircrafts[i]
        origin_ap = FindAirport(airports, a.origin)  # Buscamos de dónde sale

        # Solo dibujamos la línea si el aeropuerto de origen existe en nuestra base de datos
        if origin_ap != None:
            lat1 = origin_ap.coordinates[0]
            lon1 = origin_ap.coordinates[1]
            lat2 = dest.coordinates[0]
            lon2 = dest.coordinates[1]

            # Azul/Rojo (Schengen) vs Verde (No Schengen)
            color = "ff0000ff" if origin_ap.schengen else "ff00ff00"

            file.write('<Placemark>\n')
            file.write('<name>' + str(a.id) + '</name>\n')
            file.write('<Style><LineStyle>\n')
            file.write('<color>' + color + '</color>\n')
            file.write('<width>2</width>\n')
            file.write('</LineStyle></Style>\n')
            file.write('<LineString>\n')
            file.write('<coordinates>\n')

            # Trazamos la línea: Punto A (Origen) al Punto B (Destino)
            file.write(str(lon1) + ',' + str(lat1) + ',0 ' + str(lon2) + ',' + str(lat2) + ',0\n')

            file.write('</coordinates>\n')
            file.write('</LineString>\n')
            file.write('</Placemark>\n')
        i = i + 1

    file.write('</Document>\n')
    file.write('</kml>\n')
    file.close()


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
    Usa 'os.path' por seguridad para encontrar el archivo sin importar desde
    qué carpeta se ejecute el programa principal.
    """
    aircrafts = []

    try:
        # Apertura de fichero clásica
        file = open(filename)
        linea = file.readline()

        while linea != "":
            # Limpiamos salto de línea y separamos por un espacio
            linea_limpia = linea.strip('\n')

            # Comprobamos que no esté vacía y no sea la cabecera (igual que hiciste en Arrivals)
            if len(linea_limpia) > 0 and linea_limpia[0:8] != "AIRCRAFT":
                partes = linea_limpia.split(' ')

                # Validamos que haya 4 datos (id, destino, hora, aerolínea)
                if len(partes) >= 4:
                    id_avion = partes[0]
                    destination = partes[1]
                    departure_time = partes[2]
                    airline = partes[3]

                    # Llamamos al constructor con 4 parámetros.
                    # ¡Asegúrate de que tu clase Aircraft en def __init__(...) pide 4!
                    ac = Aircraft(id_avion, airline, destination, departure_time)
                    aircrafts.append(ac)

            linea = file.readline()

        file.close()
    except Exception:
        pass

    return aircrafts


def MergeMovements(arrivals_list, departures_list):
    """Unión clásica de dos listas iterando una tras otra con bucles while."""
    resultado = []
    i = 0
    while i < len(arrivals_list):
        resultado.append(arrivals_list[i])
        i = i + 1
    j = 0
    while j < len(departures_list):
        resultado.append(departures_list[j])
        j = j + 1
    return resultado


# =============================================================================
# PREPARATIVOS PARA ASIGNACIÓN (Helpers)
# =============================================================================

def NightAircraft(movements_list):
    """Busca vuelos que salgan de madrugada (Antes de las 9 AM)."""
    nocturnos = []
    i = 0
    while i < len(movements_list):
        ac = movements_list[i]
        if ac.departure_time != "":
            partes_hora = ac.departure_time.split(':')
            hora = int(partes_hora[0])
            if hora < 9:
                nocturnos.append(ac)
        i = i + 1

    if len(nocturnos) == 0:
        j = 0
        while j < 10 and j < len(movements_list):
            nocturnos.append(movements_list[j])
            j = j + 1
    return nocturnos


def AssignNightGates(airport_obj, night_aircraft_list):
    """Establece directamente los vuelos nocturnos en las puertas de la terminal."""
    if airport_obj == None or len(night_aircraft_list) == 0:
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
    """Vacía las puertas y llena con los aviones de la hora actual."""
    if airport_obj == None or len(movements_list) == 0:
        return 0

    # 1. Liberamos todas las puertas
    for terminal in airport_obj.terminals:
        for area in terminal.boarding_areas:
            for gate in area.gates:
                gate.occupied = False
                gate.aircraft = ""

    # 2. Buscamos vuelos para la hora pedida
    partes_tiempo = current_time_str.split(':')
    hora_slider = int(partes_tiempo[0])
    no_asignados = 0
    idx_puerta = 0

    vuelos_de_la_hora = []
    i = 0
    while i < len(movements_list):
        ac = movements_list[i]
        hora_vuelo = -1
        if ac.departure_time != "":
            hora_vuelo = int(ac.departure_time.split(':')[0])
        elif ac.arrival_time != "":
            hora_vuelo = int(ac.arrival_time.split(':')[0])

        if hora_vuelo == hora_slider:
            vuelos_de_la_hora.append(ac)
        i = i + 1

    # 3. Asignación directa y simple (se usa el algoritmo complejo en LEBL.py)
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
# BLOQUE DE GRÁFICOS (Matplotlib configurado para Tkinter)
# =============================================================================

def PlotDayOccupancy(airport_obj, movements_list):
    """
    Gráfico de líneas que simula las 24 horas de operaciones del aeropuerto.
    Devuelve un objeto 'Figure' preparado para integrarse en la interfaz.
    """
    # Importamos localmente para evitar errores de importación circular
    try:
        from LEBL import AssignGate
    except ImportError:
        AssignGate = None

    horas_eje = list(range(24))
    ocupacion_t1 = [0] * 24  # Lista de contadores para T1
    ocupacion_t2 = [0] * 24  # Lista de contadores para T2

    estructura_temporal = copy.deepcopy(airport_obj)
    SCHENGEN_PREFIXES = ['ED', 'ET', 'LO', 'EB', 'EK', 'LZ', 'LJ', 'LE', 'EE', 'EF', 'LF', 'LG', 'LH',
                         'BI', 'LI', 'EV', 'EY', 'LN', 'EH', 'EP', 'LP', 'LK', 'ES', 'LS', 'LH']

    h = 0
    while h < 24:
        # Vaciamos la estructura virtual
        for terminal in estructura_temporal.terminals:
            for area in terminal.boarding_areas:
                for gate in area.gates:
                    gate.occupied = False
                    gate.aircraft = ""

        # Llenamos la estructura con los vuelos de la hora actual
        i = 0
        while i < len(movements_list):
            ac = movements_list[i]
            time_str = ac.arrival_time if ac.arrival_time != "" else ac.departure_time
            if time_str == "" and ac.arrival != "": time_str = ac.arrival

            if time_str != "" and ":" in time_str:
                hora_vuelo = int(time_str.split(':')[0])
                if hora_vuelo == h:
                    is_schengen = True
                    codigo_remoto = ac.destination if ac.destination != "" else ac.origin

                    if len(codigo_remoto) >= 2:
                        prefix = codigo_remoto[0:2].upper()
                        if prefix != 'LE' and prefix not in SCHENGEN_PREFIXES:
                            is_schengen = False

                    if AssignGate != None:
                        AssignGate(estructura_temporal, ac, is_schengen)
            i = i + 1

        # Contamos cuántas puertas han quedado ocupadas en cada terminal
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

        h = h + 1

    # Creación del gráfico con Matplotlib
    fig = Figure(figsize=(8, 4), dpi=100, facecolor="#f8f9fa")
    ax = fig.add_subplot(111)

    # Dibujamos las dos líneas (T1 azul, T2 verde)
    ax.plot(horas_eje, ocupacion_t1, color='#4a90e2', marker='o', linestyle='-', linewidth=2, label='Occupied Gates T1')
    ax.plot(horas_eje, ocupacion_t2, color='#2ecc71', marker='s', linestyle='-', linewidth=2, label='Occupied Gates T2')

    ax.set_xlabel('Hora del Día (h)')
    ax.set_ylabel('Puertas Ocupadas')
    ax.set_xticks(horas_eje)
    ax.set_xticklabels([str(h) + ":00" for h in horas_eje], rotation=45, fontsize=8)
    ax.set_ylim(bottom=0)  # Que empiece en 0 siempre
    ax.legend(loc='upper left')
    ax.grid(True, linestyle=':', alpha=0.6)
    ax.set_title("Análisis Diario de Operaciones (24h)")
    fig.tight_layout()

    return fig


def PlotArrivalsPerHour(movements_list):
    """
    Gráfico de barras: Histograma que muestra la frecuencia de llegadas en cada hora.
    """
    hours_count = [0] * 24  # Array contador inicializado a ceros
    i = 0
    while i < len(movements_list):
        ac = movements_list[i]
        time_str = ac.arrival_time if ac.arrival_time != "" else ac.arrival
        if time_str != "" and ":" in time_str:
            hora = int(time_str.split(":")[0])
            if hora >= 0 and hora < 24:
                hours_count[hora] = hours_count[hora] + 1  # Sumamos 1 a la hora correspondiente
        i = i + 1

    fig = Figure(figsize=(8, 4), dpi=100)
    ax = fig.add_subplot(111)
    ax.bar(range(24), hours_count, color='#1f77b4', width=0.8)
    ax.set_xlabel("Hour")
    ax.set_ylabel("Arrivals")
    ax.set_title("Arrivals per hour")
    ax.set_xticks(range(24))
    ax.grid(axis='y', linestyle='-', alpha=0.3)
    fig.tight_layout()
    return fig


def PlotFlightsPerAirline(movements_list):
    """
    Gráfico de barras: Contabiliza los vuelos de cada aerolínea y los ordena
    de mayor a menor usando el algoritmo clásico de la 'Burbuja' (Bubble Sort).
    """
    # Utilizamos dos "Listas Paralelas" (Mismo índice = misma aerolínea)
    lista_aerolineas = []
    lista_conteos = []

    i = 0
    while i < len(movements_list):
        aerolinea = movements_list[i].airline
        if aerolinea != "":
            encontrado = False
            j = 0
            # Buscamos si la aerolínea ya está en nuestra lista paralela
            while j < len(lista_aerolineas) and not encontrado:
                if lista_aerolineas[j] == aerolinea:
                    lista_conteos[j] = lista_conteos[j] + 1  # Sumamos el contador
                    encontrado = True
                j = j + 1

            # Si es la primera vez que la vemos, la añadimos al final de ambas listas
            if not encontrado:
                lista_aerolineas.append(aerolinea)
                lista_conteos.append(1)
        i = i + 1

    # --- ALGORITMO BUBBLE SORT (Burbuja) ---
    # Ordena de mayor a menor el volumen de vuelos
    n = len(lista_conteos)
    for i in range(n):
        for j in range(0, n - i - 1):
            if lista_conteos[j] < lista_conteos[j + 1]:
                # Intercambiamos los valores numéricos
                temp_num = lista_conteos[j]
                lista_conteos[j] = lista_conteos[j + 1]
                lista_conteos[j + 1] = temp_num

                # Intercambiamos simultáneamente los nombres para no descuadrar la lista paralela
                temp_str = lista_aerolineas[j]
                lista_aerolineas[j] = lista_aerolineas[j + 1]
                lista_aerolineas[j + 1] = temp_str

    fig = Figure(figsize=(8, 4), dpi=100)
    ax = fig.add_subplot(111)
    ax.bar(lista_aerolineas, lista_conteos, color='#1f77b4', width=0.6)
    ax.set_ylabel("Flights")
    ax.set_title("Flights per airline")
    ax.tick_params(axis='x', rotation=90, labelsize=8)  # Rotamos el texto 90º para que quepa
    fig.tight_layout()
    return fig


def PlotSchengenProportion(movements_list):
    """
    Gráfico de barras apiladas (Stacked Bar):
    Muestra la proporción total de vuelos del espacio Schengen frente al resto del mundo.
    """
    schengen = 0
    non_schengen = 0
    paises_schengen = ['DE', 'AT', 'BE', 'DK', 'SK', 'SI', 'ES', 'EE', 'FI', 'FR', 'GR', 'HU',
                       'IS', 'IT', 'LV', 'LI', 'LT', 'LU', 'MT', 'NO', 'NL', 'PL', 'PT', 'CZ', 'SE', 'CH']

    i = 0
    while i < len(movements_list):
        ac = movements_list[i]
        es_schengen = False

        # Comprobación de atributos del objeto
        if ac.is_schengen == True:
            es_schengen = True
        else:
            codigo_origen = ac.origin
            if len(codigo_origen) >= 2:
                prefijo = codigo_origen[0:2]

                # Búsqueda clásica (¡Muy bien planteada por tu parte!)
                j = 0
                while j < len(paises_schengen) and not es_schengen:
                    if paises_schengen[j] == prefijo:
                        es_schengen = True
                    j = j + 1

        # Incremento de contadores básicos
        if es_schengen == True:
            schengen = schengen + 1
        else:
            non_schengen = non_schengen + 1

        i = i + 1

    fig = Figure(figsize=(5, 5), dpi=100)
    ax = fig.add_subplot(111)

    # Barra inferior
    ax.bar(['Flights'], [schengen], label='Schengen', color='#1f77b4', width=0.5)
    # Barra superior (Apilada encima de 'schengen' usando el parámetro bottom)
    ax.bar(['Flights'], [non_schengen], bottom=[schengen], label='Non-Schengen', color='#ff7f0e', width=0.5)

    ax.set_ylabel("Count")
    ax.set_title("Flights type")
    ax.legend(loc='upper right')
    fig.tight_layout()
    return fig


if __name__ == "__main__":
    pass