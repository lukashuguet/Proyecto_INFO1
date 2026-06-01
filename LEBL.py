"""
MÓDULO LEBL.PY (Lógica del Aeropuerto de Barcelona)
Este archivo contiene la estructura de datos jerárquica del aeropuerto
y los algoritmos principales de asignación de puertas (Gate Assignment Problem).
No contiene nada visual, solo pura lógica de negocio y procesamiento de datos.
"""

from airport import *
from matplotlib.figure import Figure  # Usamos Figure en lugar de plt para incrustarlo en Tkinter
import copy  # Para duplicar estructuras de datos sin modificar las originales

# =============================================================================
# DEFINICIÓN DE CLASES (Programación Orientada a Objetos)
# =============================================================================
# Estas clases forman una jerarquía: Un Aeropuerto tiene Terminales,
# las Terminales tienen Áreas, y las Áreas tienen Puertas (Gates).

class Gate:
    """Representa una única puerta de embarque física."""
    def __init__(self, name):
        self.name = name
        self.occupied = False
        self.aircraft = ""  # Guarda la matrícula del avión aparcado aquí


class BoardingArea:
    """Representa un pasillo o zona (Ej: Zona A, Zona B). Agrupa múltiples Gates."""
    def __init__(self, name, area_type):
        self.name = name
        self.type = area_type  # Guarda si es 'Schengen' o 'non-Schengen'
        self.gates = []        # Lista de objetos Gate


class Terminal:
    """Representa una terminal entera (Ej: T1, T2). Agrupa Zonas y Aerolíneas asociadas."""
    def __init__(self, name):
        self.name = name
        self.boarding_areas = [] # Lista de objetos BoardingArea
        self.airlines = []       # Lista de códigos ICAO de aerolíneas que operan aquí


class BarcelonaAP:
    """Clase principal (Raíz). Representa todo el aeropuerto de Barcelona."""
    def __init__(self, code):
        self.code = code
        self.terminals = []      # Lista de objetos Terminal


# =============================================================================
# MONITOR DE OCUPACIÓN
# =============================================================================
def GateOccupancy(airport_structure):
    """
    Recorre toda la jerarquía del aeropuerto y extrae una lista plana
    con el estado de cada puerta. Útil para informes de texto.
    """
    lista_resultado = []
    if not airport_structure or not hasattr(airport_structure, 'terminals'):
        return lista_resultado

    for i in range(len(airport_structure.terminals)):
        terminal = airport_structure.terminals[i]
        for j in range(len(terminal.boarding_areas)):
            area = terminal.boarding_areas[j]
            for k in range(len(area.gates)):
                gate = area.gates[k]
                info = {
                    'gate': gate.name,
                    'terminal': terminal.name,
                    'area': area.name,
                    'occupied': gate.occupied,
                    'aircraft': gate.aircraft if gate.occupied else ""
                }
                lista_resultado.append(info)
    return lista_resultado


# =============================================================================
# FUNCIONES DE CARGA DE ARCHIVOS (Parsing)
# =============================================================================
def SetGates(area, init_gate, end_gate, prefix):
    """Crea múltiples objetos Gate de golpe usando un bucle y los mete en un Área."""
    if end_gate <= init_gate:
        return -1
    for i in range(init_gate, end_gate + 1):
        name = prefix + str(i)
        nueva_gate = Gate(name)
        area.gates.append(nueva_gate)
    return 0


def LoadAirlines(terminal, t_name):
    """
    Lee el archivo T1_Airlines.txt o T2_Airlines.txt y vincula esas
    aerolíneas a la Terminal correspondiente.
    """
    filename = t_name + "_Airlines.txt"
    try:
        f = open(filename, "r", encoding="utf-8")
        terminal.airlines = []
        lines = f.readlines()
        f.close()
        for i in range(len(lines)):
            linea = lines[i].strip()
            # Ignoramos líneas vacías o guiones decorativos
            if linea and not linea.startswith("---"):
                partes = linea.split('\t')
                if len(partes) > 1:
                    terminal.airlines.append(partes[1].strip())
        return 0
    except:
        return -1


def LoadAirportStructure(filename):
    """
    Función MAESTRA de lectura. Abre Terminals.txt y va construyendo
    toda la jerarquía de clases dinámicamente línea a línea.
    """
    try:
        f = open(filename, "r", encoding="utf-8")
        lines = f.readlines()
        f.close()
    except:
        return -1

    if not lines:
        return -1

    # Extraemos el código del aeropuerto (Ej: LEBL)
    primera_linea = lines[0].split()
    if not primera_linea:
        return -1

    bcn = BarcelonaAP(primera_linea[0])
    terminal_actual = None

    # Bucle principal de lectura
    for line in lines[1:]:
        linea = line.strip()

        # Filtro de ruido: Ignoramos comentarios (#) y líneas decorativas (----)
        if not linea or linea.startswith("#") or (linea.startswith("-") and len(linea) > 5):
            continue

        partes = linea.split()
        if not partes:
            continue

        # Opción A: Detectamos que la línea define una Terminal
        if partes[0].lower().startswith("terminal") or (len(partes) == 2 and partes[0].upper().startswith("T")):
            try:
                nombre_t = partes[1] if partes[0].lower().startswith("terminal") else partes[0]
                terminal_actual = Terminal(nombre_t)
                LoadAirlines(terminal_actual, nombre_t)  # Vinculamos sus aerolíneas
                bcn.terminals.append(terminal_actual)
            except IndexError:
                continue

        # Opción B: Detectamos que la línea define un Área de Embarque
        elif (partes[0].lower().startswith("area") or partes[0].upper().startswith("ZONA")) and terminal_actual is not None:
            try:
                nombre_area = partes[1]
                tipo_area = partes[2]

                # Calculamos el rango de puertas (Ej: Gates 1 - 11)
                if partes[-2] == "-":
                    g_ini = int(partes[-3])
                    g_fin = int(partes[-1])
                else:
                    g_ini = int(partes[-2])
                    g_fin = int(partes[-1])

                area_obj = BoardingArea(nombre_area, tipo_area)
                prefix = terminal_actual.name + nombre_area
                SetGates(area_obj, g_ini, g_fin, prefix) # Creamos las puertas físicamente

                terminal_actual.boarding_areas.append(area_obj)
            except (IndexError, ValueError):
                continue

        # Opción C: Formato compacto de seguridad (por si no dice "Area")
        elif len(partes) >= 5 and terminal_actual is not None and partes[0].isalnum():
            try:
                nombre_area = partes[0]
                tipo_area = partes[1]

                if partes[-2] == "-":
                    g_ini = int(partes[-3])
                    g_fin = int(partes[-1])
                else:
                    g_ini = int(partes[-2])
                    g_fin = int(partes[-1])

                area_obj = BoardingArea(nombre_area, tipo_area)
                prefix = terminal_actual.name + nombre_area
                SetGates(area_obj, g_ini, g_fin, prefix)

                terminal_actual.boarding_areas.append(area_obj)
            except (IndexError, ValueError):
                continue

    return bcn


# =============================================================================
# FUNCIONES DE BÚSQUEDA (Helper Functions)
# =============================================================================
def IsAirlineInTerminal(terminal, airline_code):
    """Comprueba si un código (Ej: IBE) está en la lista de la terminal."""
    if not airline_code:
        return False
    for i in range(len(terminal.airlines)):
        if terminal.airlines[i] == airline_code:
            return True
    return False


def SearchTerminal(bcn, airline_code):
    """Busca por todas las terminales hasta encontrar dónde opera la aerolínea."""
    for i in range(len(bcn.terminals)):
        if IsAirlineInTerminal(bcn.terminals[i], airline_code):
            return bcn.terminals[i].name
    return ""


# =============================================================================
# LÓGICA DE ASIGNACIÓN DINÁMICA DE PUERTAS (El motor de la simulación)
# =============================================================================

def NightAircraft(aircrafts):
    if len(aircrafts) == 0:
        return -1

    nocturnos = []
    i = 0
    while i < len(aircrafts):
        ac = aircrafts[i]
        if (ac.arrival is None or ac.arrival == "") and (ac.departure_time is not None and ac.departure_time != ""):
            nocturnos.append(ac)
        i = i + 1

    return nocturnos


def AssignNightGates(bcn, nocturnos):
    if nocturnos is None or len(nocturnos) == 0:
        return -1

    for ac in nocturnos:
        puerta_asignada = AssignGate(bcn, ac, ac.is_schengen)
        ac.gate = puerta_asignada



def AllocateGatesDynamic(airport_obj, movements_list, current_time_str):
    """
    El motor de la simulación. Recibe una hora concreta (Ej: '14:00'),
    vacía el aeropuerto, busca los vuelos de esa hora y los intenta aparcar.
    """
    if airport_obj == None or len(movements_list) == 0:
        return 0

    # 1. VACIAR TODAS LAS PUERTAS CORRECTAMENTE (Usando bucles WHILE puros)
    i = 0
    while i < len(airport_obj.terminals):
        terminal = airport_obj.terminals[i]
        j = 0
        while j < len(terminal.boarding_areas):
            area = terminal.boarding_areas[j]
            k = 0
            while k < len(area.gates):
                gate = area.gates[k]
                gate.occupied = False # Liberamos la puerta
                gate.aircraft = ""    # Borramos la matrícula anterior
                k = k + 1
            j = j + 1
        i = i + 1

    # 2. ENCONTRAR VUELOS DE ESA HORA
    partes_tiempo = current_time_str.split(':')
    hora_slider = int(partes_tiempo[0])

    vuelos_de_la_hora = []
    i = 0
    while i < len(movements_list):
        ac = movements_list[i]
        hora_vuelo = -1

        if ac.departure_time != "":
            hora_vuelo = int(ac.departure_time.split(':')[0])
        elif ac.arrival_time != "":
            hora_vuelo = int(ac.arrival_time.split(':')[0])

        # Si el vuelo opera a la hora que marca el slider, lo metemos a la lista
        if hora_vuelo == hora_slider:
            vuelos_de_la_hora.append(ac)
        i = i + 1

    # 3. COMPROBACIÓN SCHENGEN Y ASIGNACIÓN
    # Prefijos ICAO de países Schengen (Ej: LE = España, LF = Francia)
    SCHENGEN_PREFIXES = ['ED', 'ET', 'LO', 'EB', 'EK', 'LZ', 'LJ', 'LE', 'EE', 'EF', 'LF', 'LG', 'LH', 'BI', 'LI', 'EV',
                         'EY', 'LN', 'EH', 'EP', 'LP', 'LK', 'ES', 'LS']

    no_asignados = 0
    v = 0
    while v < len(vuelos_de_la_hora):
        ac = vuelos_de_la_hora[v]

        # Comprobamos si el avión es salida o llegada para sacar su código ICAO remoto (El país al que va/del que viene)
        if ac.destination != "":
            codigo_remoto = ac.destination
        else:
            codigo_remoto = ac.origin

        # Verificamos si ese código remoto pertenece al tratado Schengen
        is_schengen = True
        if len(codigo_remoto) >= 2:
            prefix = codigo_remoto[0:2]
            # Si no es un vuelo nacional (LE) y no está en la lista europea, no es Schengen
            if prefix != "LE" and prefix not in SCHENGEN_PREFIXES:
                is_schengen = False

        # Llamamos al trabajador 'AssignGate'
        resultado = AssignGate(airport_obj, ac, is_schengen)

        # Si el trabajador devuelve este string, significa que la terminal estaba llena
        if resultado == "No free gates":
            no_asignados = no_asignados + 1

        v = v + 1

    # Devolvemos cuántos aviones se han quedado "dando vueltas" por falta de sitio
    return no_asignados


def AssignGate(bcn, flight, origin_is_schengen):
    # 1. ACCESO DIRECTO A ATRIBUTOS
    airline_code = flight.airline
    aircraft_id = flight.id

    # Buscamos en qué terminal opera esta aerolínea
    t_name = SearchTerminal(bcn, airline_code)

    # Si no conocemos la aerolínea, a la terminal especial
    if t_name == "" or t_name is None:
        t_name = "T3"

    # 2. DEFINIR TIPO DE ÁREA BUSCADA
    if origin_is_schengen == True:
        tipo_buscado = "Schengen"
    else:
        tipo_buscado = "non-Schengen"

    # 3. BUCLE WHILE PARA NAVEGAR LAS TERMINALES
    i = 0
    while i < len(bcn.terminals):
        term = bcn.terminals[i]

        # Si encontramos la terminal correcta
        if term.name == t_name:

            # 4. BUCLE WHILE PARA NAVEGAR LAS ÁREAS DE EMBARQUE
            j = 0
            while j < len(term.boarding_areas):
                area = term.boarding_areas[j]
                # Si el área coincide con el tipo buscado
                if area.type == tipo_buscado:

                    # 5. BUCLE WHILE PARA NAVEGAR LAS PUERTAS
                    k = 0
                    while k < len(area.gates):
                        gate = area.gates[k]

                        # Si la puerta está libre, la ocupamos
                        if gate.occupied == False:
                            gate.occupied = True
                            gate.aircraft = aircraft_id
                            return gate.name

                        k = k + 1
                j = j + 1
        i = i + 1

    return "No free gates"


# =============================================================================
# BLOQUE DE GRÁFICOS (Matplotlib configurado para Tkinter)
# =============================================================================

def PlotDayOccupancy(bcn, aircrafts):
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

    estructura_temporal = copy.deepcopy(bcn)
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
        while i < len(aircrafts):
            ac = aircrafts[i]
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