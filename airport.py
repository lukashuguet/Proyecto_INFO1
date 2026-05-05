import matplotlib.pyplot as plt


class Airport:
    # Clase que representa un aeropuerto con código, coordenadas y si es Schengen
    def __init__(self, icao, lat, lon):
        self.icao = icao
        self.coordinates = (lat, lon)
        self.schengen = False


# --------------------------------------------------
# SCHENGEN
# --------------------------------------------------

# Comprueba si un código ICAO pertenece a un país Schengen
def IsSchengenAirport(code):

    if not code:
        return False

    # Prefijos ICAO de países Schengen
    schengen_prefixes = [
        'LO', 'EB', 'LK', 'LC', 'EK', 'EE', 'EF', 'LF', 'ED', 'LG',
        'EH', 'LH', 'BI', 'LI', 'EV', 'EY', 'EL', 'LM', 'EN', 'EP',
        'LP', 'LZ', 'LJ', 'LE', 'ES', 'LS'
    ]

    return code[:2] in schengen_prefixes

# Asigna al aeropuerto si es Schengen o no
def SetSchengen(airport):
    airport.schengen = IsSchengenAirport(airport.icao)

# Imprime por pantalla los datos de un aeropuerto
def PrintAirport(airport):
    print("ICAO:", airport.icao)
    print("Coordinates:", airport.coordinates)
    print("Schengen:", airport.schengen)
    print()

# --------------------------------------------------
# FILE FUNCTIONS
# --------------------------------------------------

# Carga aeropuertos desde un fichero y crea objetos Airport
def LoadAirports(filename):

    airports = []

    try:
        file = open(filename, "r")
    except:
        return airports

    lines = file.readlines()
    file.close()

    for line in lines:
        line = line.strip()

        # Ignora líneas vacías o cabecera
        if not line or line.startswith("CODE"):
            continue

        parts = line.split()

        # Debe tener exactamente 3 campos
        if len(parts) != 3:
            continue

        code = parts[0]
        lat = ConvertCoord(parts[1])
        lon = ConvertCoord(parts[2])

        airport = Airport(code, lat, lon)
        airports.append(airport)

    return airports

# Guarda en un fichero solo los aeropuertos Schengen
def SaveSchengenAirports(airports, filename):

    if not airports:
        return -1

    file = open(filename, "w")

    file.write("CODE LAT LON\n")

    for airport in airports:
        if airport.schengen:
            lat_str = FormatCoord(airport.coordinates[0], True)
            lon_str = FormatCoord(airport.coordinates[1], False)

            file.write(f"{airport.icao} {lat_str} {lon_str}\n")

    file.close()


# --------------------------------------------------
# LIST MANAGEMENT
# --------------------------------------------------

# Añade un aeropuerto a la lista si no existe ya
def AddAirport(airports, airport):

    for a in airports:
        if a.icao == airport.icao:
            return

    airports.append(airport)

# Elimina un aeropuerto de la lista por su código ICAO
def RemoveAirport(airports, code):

    for a in airports:
        if a.icao == code:
            airports.remove(a)
            return

    return -1


# --------------------------------------------------
# PLOT
# --------------------------------------------------

# Muestra una gráfica con número de aeropuertos Schengen vs No Schengen
def PlotAirports(airports):

    if not airports:
        print("No data to plot")
        return

    schengen_count = sum(1 for a in airports if a.schengen)
    no_schengen_count = len(airports) - schengen_count

    labels = ['Airports']

    fig, ax = plt.subplots(figsize=(6, 5))

    ax.bar(labels, [schengen_count], label='Schengen')
    ax.bar(labels, [no_schengen_count],
           bottom=[schengen_count],
           label='No Schengen')

    ax.set_ylabel('Count')
    ax.set_title('Schengen airports')
    ax.legend()

    plt.show()


# --------------------------------------------------
# MAP (KML)
# --------------------------------------------------

# Genera un archivo KML para visualizar aeropuertos en Google Earth
def MapAirports(airports):

    if not airports:
        print("Error: empty list")
        return

    file = open("airports.kml", "w")

    file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    file.write('<kml xmlns="http://www.opengis.net/kml/2.2">\n')
    file.write('<Document>\n')

    for airport in airports:

        lat = airport.coordinates[0]
        lon = airport.coordinates[1]

        if airport.schengen:
            color = "ff0000ff"  # rojo
        else:
            color = "ff00ff00"  # verde

        file.write('<Placemark>\n')
        file.write(f'<name>{airport.icao}</name>\n')
        file.write('<Style><IconStyle>\n')
        file.write(f'<color>{color}</color>\n')
        file.write('</IconStyle></Style>\n')
        file.write('<Point>\n')
        file.write(f'<coordinates>{lon},{lat},0</coordinates>\n')
        file.write('</Point>\n')
        file.write('</Placemark>\n')

    file.write('</Document>\n')
    file.write('</kml>\n')

    file.close()

    print("File airports.kml created.")


# --------------------------------------------------
# COORDINATE FUNCTIONS
# --------------------------------------------------

# Convierte coordenadas de formato texto (N412345) a decimal (41.3958)
def ConvertCoord(coord):

    direction = coord[0]
    value = coord[1:]

    if len(value) == 6:  # latitud
        degrees = int(value[0:2])
        minutes = int(value[2:4])
        seconds = int(value[4:6])
    else:  # longitud
        degrees = int(value[0:3])
        minutes = int(value[3:5])
        seconds = int(value[5:7])

    decimal = degrees + minutes / 60 + seconds / 3600

    # Sur y Oeste son negativos
    if direction in ['S', 'W']:
        decimal = -decimal

    return decimal  # 🔥 MUY IMPORTANTE

# Convierte coordenadas decimales a formato texto (N412345)
def FormatCoord(value, is_lat):

    if is_lat:
        direction = 'N' if value >= 0 else 'S'
    else:
        direction = 'E' if value >= 0 else 'W'

    value = abs(value)

    degrees = int(value)
    minutes_full = (value - degrees) * 60
    minutes = int(minutes_full)
    seconds = int((minutes_full - minutes) * 60)

    if is_lat:
        return f"{direction}{degrees:02d}{minutes:02d}{seconds:02d}"
    else:
        return f"{direction}{degrees:03d}{minutes:02d}{seconds:02d}"