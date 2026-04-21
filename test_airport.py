from airport import *

def TestBasicFunctions():
    print("=== TEST BASIC FUNCTIONS ===")

    # Crear aeropuerto manualmente
    ap = Airport("LEBL", 41.297445, 2.0832941)

    # Set Schengen
    SetSchengen(ap)

    # Print
    PrintAirport(ap)

    print()


def TestLoadAirports():
    print("=== TEST LOAD AIRPORTS ===")

    airports = LoadAirports("airports.txt")

    print("Loaded airports:", len(airports))

    for ap in airports[:5]:  # mostrar solo algunos
        PrintAirport(ap)

    print()
    return airports


def TestSetSchengen(airports):
    print("=== TEST SET SCHENGEN ===")

    for ap in airports:
        SetSchengen(ap)

    # comprobar algunos
    for ap in airports[:5]:
        print(ap.icao, "->", ap.schengen)

    print()


def TestAddRemove(airports):
    print("=== TEST ADD / REMOVE ===")

    new_ap = Airport("TEST", 10.0, 20.0)

    AddAirport(airports, new_ap)
    print("Added TEST")

    # comprobar
    found = any(a.icao == "TEST" for a in airports)
    print("Exists after add:", found)

    RemoveAirport(airports, "TEST")
    print("Removed TEST")

    found = any(a.icao == "TEST" for a in airports)
    print("Exists after remove:", found)

    print()


def TestSave(airports):
    print("=== TEST SAVE SCHENGEN ===")

    SaveSchengenAirports(airports, "schengen_airports.txt")

    print("File 'schengen_airports.txt' created\n")


def TestPlot(airports):
    print("=== TEST PLOT ===")

    PlotAirports(airports)

    print()


def TestMap(airports):
    print("=== TEST MAP ===")

    MapAirports(airports)

    print()


if __name__ == "__main__":

    TestBasicFunctions()

    airports = TestLoadAirports()

    if airports:
        TestSetSchengen(airports)
        TestAddRemove(airports)
        TestSave(airports)
        TestPlot(airports)
        TestMap(airports)
    else:
        print("No airports loaded. Check file.")