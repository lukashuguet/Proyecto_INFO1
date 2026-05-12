# definimos las 4 clases necesarias para representar el aeropuerto.

class Gate:
    def __init__(self, name):
        self.name = name
        self.occupied = False
        self.aircraft_id = ""

class BoardingArea:
    def __init__(self, name, area_type):
        self.name = name
        self.type = area_type  # 'Schengen' o 'non-Schengen'
        self.gates = []

class Terminal:
    def __init__(self, name):
        self.name = name
        self.boarding_areas = []
        self.airlines = [] # Lista de códigos ICAO de aerolíneas

class BarcelonaAP:
    def __init__(self, code):
        self.code = code
        self.terminals = []

# función que crea las puertas de una zona de embarque

def SetGates(area, init_gate, end_gate, prefix):
    # Si el número final no es mayor que el inicial, error [cite: 134]
    if end_gate <= init_gate:
        return -1

    area.gates = []  # Limpiamos si había antes [cite: 133]

    # Creamos las puertas una a una
    for i in range(init_gate, end_gate + 1):
        name = prefix + str(i)
        nueva_gate = Gate(name)
        area.gates.append(nueva_gate)

    return 0

#Lee qué aerolíneas van a cada terminal

def LoadAirlines(terminal, t_name):
    # El nombre del fichero se construye según la terminal
    filename = t_name + "_Airlines.txt"

    try:
        f = open(filename, "r")
        terminal.airlines = []  # Limpiamos lista previa [cite: 136]
        lines = f.readlines()
        f.close()

        for i in range(len(lines)):
            linea = lines[i].strip()
            if linea:
                # El código ICAO suele estar después del tabulador [cite: 124]
                partes = linea.split('\t')
                if len(partes) > 1:
                    terminal.airlines.append(partes[1])
        return 0
    except:
        return -1  # Si el fichero no existe [cite: 137]

# lee las terminales del archivo txt

def LoadAirportStructure(filename):
    try:
        f = open(filename, "r")
        lines = f.readlines()
        f.close()
    except:
        return -1

    # La primera línea tiene el código del aeropuerto (LEBL) [cite: 117]
    primera_linea = lines[0].split()
    bcn = BarcelonaAP(primera_linea[0])

    # Usamos un índice para recorrer las líneas manualmente y procesar bloques
    i = 1
    while i < len(lines):
        linea = lines[i].strip()

        # Si la línea empieza por 'Terminal' [cite: 118]
        if linea.startswith("Terminal"):
            partes = linea.split()
            nombre_t = partes[1]
            num_areas = int(partes[2])

            nueva_t = Terminal(nombre_t)
            LoadAirlines(nueva_t, nombre_t)  # Cargamos sus aerolíneas [cite: 139]

            # Leemos las siguientes N líneas que son las áreas de esta terminal [cite: 119, 120]
            for j in range(1, num_areas + 1):
                linea_area = lines[i + j].strip().split()
                # Ejemplo: Area A Schengen Gates 1 11
                nombre_area = linea_area[1]
                tipo_area = linea_area[2]
                g_ini = int(linea_area[4])
                g_fin = int(linea_area[5])

                area_obj = BoardingArea(nombre_area, tipo_area)
                # Prefijo para la puerta: "T1A" por ejemplo [cite: 140]
                prefix = nombre_t + nombre_area
                SetGates(area_obj, g_ini, g_fin, prefix)

                nueva_t.boarding_areas.append(area_obj)

            bcn.terminals.append(nueva_t)
            i = i + num_areas + 1  # Saltamos a la siguiente terminal
        else:
            i = i + 1

    return bcn

# Para saber a qué terminal va un avión y darle una puerta libre

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


def AssignGate(bcn, aircraft, origin_is_schengen):
    # 1. Buscamos la terminal de la aerolínea
    t_name = SearchTerminal(bcn, aircraft.airline)

    # 2. Buscamos la terminal en el objeto bcn
    for i in range(len(bcn.terminals)):
        term = bcn.terminals[i]
        if term.name == t_name:
            # 3. Buscamos área correcta (Schengen o no) [cite: 152]
            tipo_buscado = "Schengen" if origin_is_schengen else "non-Schengen"

            for j in range(len(term.boarding_areas)):
                area = term.boarding_areas[j]
                if area.type == tipo_buscado:
                    # 4. Buscamos la primera puerta libre [cite: 151]
                    for k in range(len(area.gates)):
                        gate = area.gates[k]
                        if not gate.occupied:
                            gate.occupied = True
                            gate.aircraft_id = aircraft.id
                            return gate.name
    return "No free gates"