class Airport:
    def __init__(self, code, latitude, longitude):
        self.code = code
        self.latitude = latitude
        self.longitude = longitude
        self.schengen = False

def IsSchengenAirport(code):
    if code == "":
        schengen = False
        return schengen
    schengen_codes = [ 'LO', 'EB', 'LK', 'LC', 'EK', 'EE', 'EF', 'LF', 'ED', 'LG', 'EH', 'LH',
'BI','LI', 'EV', 'EY', 'EL', 'LM', 'EN', 'EP', 'LP', 'LZ', 'LJ', 'LE', 'ES',
'LS']
    prefix = code[0:2]
    if prefix in schengen_codes:
        schengen = True
        return schengen
    else:
        schengen = False
        return schengen

def SetSchengen(airport):
    status = IsSchengenAirport(airport.code)
    airport.schengen = status

def PrintAirport(airport):
    print("Código ICAO:", airport.code)
    print("Latitud:", airport.latitude)
    print("Longitud:", airport.longitude)
    print("Schengen:", airport.schengen)

def LoadAirports(filename):
    list_airports = []
    Fichero = open(filename, 'r')
    linea = Fichero.readline() #Esta primera es para saltar la linea donde pone lo de CODE LAT LON
    linea = Fichero.readline()

    while linea != "":
        datos = linea.split()
        if len(datos) >=3:
            code = datos[0]
            lat_txt = datos[1]
            lon_txt = datos[2]

            #Aqui convertimos el texto de la latitud en Float y lo pasamos a formato de grados decimales
            lat_deg = float(lat_txt[1:3])
            lat_min = float(lat_txt[3:5])
            lat_sec = float(lat_txt[5:7])
            lat_dec = lat_deg + (lat_min / 60) + (lat_sec / 3600)#Esta es la que los pasa a grados decimales, es como la formula
            if lat_txt[0] == 'S':
                lat_dec = -lat_dec #Cuando es hacia el sud las coordenadas canvian de signo

            #Aqui hacemos lo mimso pero con la longitud
            lon_deg = float(lon_txt[1:3])
            lon_min = float(lon_txt[3:5])
            lon_sec = float(lon_txt[5:7])
            lon_dec = lon_deg + (lon_min / 60) + (lon_sec / 3600)
            if lon_txt[0] == 'W':
                lon_dec = -lon_dec

        actual_airport = Airport(code, lat_deg, lon_dec)
        list_airports.append(actual_airport)
        linea = Fichero.readline()
    fichero.close()
    return list_airports
def SaveSchengenAirports(airports, filename):
    if len(airports) == 0:
        print("Error:No hay ningun aeropuerto")
    else:
        Fichero_editado = open(filename, 'w')
        Fichero_editado.write("CODE LAT LON")
        i = 0
        while i < len(airports):
            actual_airport = airports[i]
            if actual_airport.schengen == True:
                linea_w = aeropuerto_actual.code + " " + str(aeropuerto_actual.lat) + " " + str(aeropuerto_actual.lon) + "\n"
                f.write(linea_w)
            i = i + 1
        Fichero_editado.close()
        print("Fichero guardado")

def AddAirport(airports, airport):
    existe = False
    i = 0
    while i < len(airports):
        if airports[i].code == airport.code:
            existe = True
        i = i + 1
    if existe == False:
        airports.append(airport)
        print("Aeropuerto añadido con éxito")
    else:
        print("El aeropuerto con código ", airport.code, " ya existe")

def RemoveAirport(airports, code):
    encontrado = False
    i = 0
    while i < len(airports) and not encontrado:












