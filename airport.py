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
