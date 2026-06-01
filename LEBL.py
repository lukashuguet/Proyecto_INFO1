"""
MÓDULO LEBL.PY (Lógica del Aeropuerto de Barcelona)
Este archivo contiene la estructura de datos jerárquica del aeropuerto
y los algoritmos principales de asignación de puertas (Gate Assignment Problem).
No contiene nada visual, solo pura lógica de negocio y procesamiento de datos.
"""

from airport import *

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

def NightAircraft(movements_list):
    """Filtra y devuelve solo los vuelos que salen de madrugada (Antes de las 09:00)."""
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

    # Fallback de seguridad: si no hay nocturnos, devolvemos los 10 primeros
    if len(nocturnos) == 0:
        j = 0
        while j < 10 and j < len(movements_list):
            nocturnos.append(movements_list[j])
            j = j + 1
    return nocturnos


def AssignNightGates(airport_obj, night_aircraft_list):
    """Asigna los aviones nocturnos en las primeras puertas disponibles por la fuerza (Sin reglas estrictas)."""
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
    """
    Algoritmo de aparcamiento. Recibe un vuelo concreto y trata de encontrarle
    un hueco en la Terminal y la Zona correcta (Schengen o Non-Schengen).
    Retorna el nombre de la puerta si hay éxito, o un error si está lleno.
    """
    # 1. ACCESO DIRECTO A ATRIBUTOS
    airline_code = flight.airline
    aircraft_id = flight.id

    # Buscamos en qué terminal opera esta aerolínea (Ej: IBERIA -> T1)
    t_name = SearchTerminal(bcn, airline_code)

    # 2. DEFINIR TIPO DE ÁREA BUSCADA
    if origin_is_schengen == True:
        tipo_buscado = "Schengen"
    else:
        tipo_buscado = "non-Schengen"

    # 3. BUCLE WHILE PARA NAVEGAR LAS TERMINALES (Índice i)
    i = 0
    while i < len(bcn.terminals):
        term = bcn.terminals[i]

        # Si encontramos la terminal correcta, buceamos en ella
        if term.name == t_name:

            # 4. BUCLE WHILE PARA NAVEGAR LAS ÁREAS DE EMBARQUE (Índice j)
            j = 0
            while j < len(term.boarding_areas):
                area = term.boarding_areas[j]

                # Si el área coincide con el tipo buscado (Schengen / Non-Schengen)
                if area.type == tipo_buscado:

                    # 5. BUCLE WHILE PARA NAVEGAR LAS PUERTAS (Índice k)
                    k = 0
                    while k < len(area.gates):
                        gate = area.gates[k]

                        # Si la puerta está libre, la ocupamos
                        if gate.occupied == False:
                            gate.occupied = True
                            gate.aircraft = aircraft_id # Guardamos la matrícula

                            # Al hacer return, el algoritmo se detiene con éxito
                            return gate.name

                        k = k + 1  # Incrementamos puertas si esta estaba ocupada
                j = j + 1  # Incrementamos áreas
        i = i + 1  # Incrementamos terminales

    # Si terminamos de recorrer toda la terminal y no hizo "return", es que está colapsada
    return "No free gates"