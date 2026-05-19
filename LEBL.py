import os
# =============================================================================
# DEFINICIÓN DE CLASES
# =============================================================================
class Gate:
    def __init__(self, name):
        self.name = name
        self.occupied = False
        self.aircraft = ""  # Sincronizado con la interfaz


class BoardingArea:
    def __init__(self, name, area_type):
        self.name = name
        self.type = area_type  # 'Schengen' o 'non-Schengen'
        self.gates = []


class Terminal:
    def __init__(self, name):
        self.name = name
        self.boarding_areas = []
        self.airlines = []


class BarcelonaAP:
    def __init__(self, code):
        self.code = code
        self.terminals = []


# =============================================================================
# MONITOR DE OCUPACIÓN
# =============================================================================
def GateOccupancy(airport_structure):
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
# FUNCIONES DE CARGA Y ASIGNACIÓN
# =============================================================================
def SetGates(area, init_gate, end_gate, prefix):
    if end_gate <= init_gate:
        return -1
    for i in range(init_gate, end_gate + 1):
        name = prefix + str(i)
        nueva_gate = Gate(name)
        area.gates.append(nueva_gate)
    return 0


def LoadAirlines(terminal, t_name):
    filename = t_name + "_Airlines.txt"
    try:
        f = open(filename, "r", encoding="utf-8")
        terminal.airlines = []
        lines = f.readlines()
        f.close()
        for i in range(len(lines)):
            linea = lines[i].strip()
            # Cambiado para evitar que se salte las aerolíneas si hay guiones aislados
            if linea and not linea.startswith("---"):
                partes = linea.split('\t')
                if len(partes) > 1:
                    terminal.airlines.append(partes[1].strip())
        return 0
    except:
        return -1


def LoadAirportStructure(filename):
    try:
        f = open(filename, "r", encoding="utf-8")
        lines = f.readlines()
        f.close()
    except:
        return -1

    if not lines:
        return -1

    # Código del aeropuerto (primera línea, ej: LEBL)
    primera_linea = lines[0].split()
    if not primera_linea:
        return -1

    bcn = BarcelonaAP(primera_linea[0])
    terminal_actual = None

    for line in lines[1:]:
        linea = line.strip()

        # MODIFICADO: Ahora solo saltamos la línea si está vacía, es un comentario o es una línea llena de guiones decorativos
        if not linea or linea.startswith("#") or (linea.startswith("-") and len(linea) > 5):
            continue

        # Separamos por cualquier espacio en blanco o tabulador interno
        partes = linea.split()
        if not partes:
            continue

        # Opción A: La línea define una Terminal (ej: "Terminal T1 5 boarding areas")
        if partes[0].lower().startswith("terminal") or (len(partes) == 2 and partes[0].upper().startswith("T")):
            try:
                nombre_t = partes[1] if partes[0].lower().startswith("terminal") else partes[0]
                terminal_actual = Terminal(nombre_t)
                LoadAirlines(terminal_actual, nombre_t)  # Carga aerolíneas asociadas
                bcn.terminals.append(terminal_actual)
            except IndexError:
                continue

        # Opción B: La línea define un Área (ej: "Area A Schengen Gates 1 - 11")
        elif (partes[0].lower().startswith("area") or partes[0].upper().startswith(
                "ZONA")) and terminal_actual is not None:
            try:
                nombre_area = partes[1]
                tipo_area = partes[2]

                # MODIFICADO: Ajuste dinámico de índices detectando el guion intermedio
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

        # Opción C: Formato directo por si tu archivo no lleva las palabras 'Terminal' ni 'Area'
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


def IsAirlineInTerminal(terminal, airline_code):
    if not airline_code:
        return False
    for i in range(len(terminal.airlines)):
        if terminal.airlines[i] == airline_code:
            return True
    return False


def SearchTerminal(bcn, airline_code):
    for i in range(len(bcn.terminals)):
        if IsAirlineInTerminal(bcn.terminals[i], airline_code):
            return bcn.terminals[i].name
    return ""


def AssignGate(bcn, flight, origin_is_schengen):
    airline_code = getattr(flight, 'airline', getattr(flight, 'code', ''))
    aircraft_id = getattr(flight, 'id', getattr(flight, 'code', ''))
    t_name = SearchTerminal(bcn, airline_code)

    for i in range(len(bcn.terminals)):
        term = bcn.terminals[i]
        if term.name == t_name:
            tipo_buscado = "Schengen" if origin_is_schengen else "non-Schengen"
            for j in range(len(term.boarding_areas)):
                area = term.boarding_areas[j]
                if area.type.lower() == tipo_buscado.lower():
                    for k in range(len(area.gates)):
                        gate = area.gates[k]
                        if not gate.occupied:
                            gate.occupied = True
                            gate.aircraft = aircraft_id
                            return gate.name
    return "No free gates"