# Proyecto Aeropuerto

# Versión 1

Esta versión del proyecto consiste en el desarrollo de una herramienta para la gestión y visualización de datos aeroportuarios internacionales, centrada específicamente en la identificación del espacio Schengen. El sistema se construye con la creación de una clase base que almacena el código ICAO de cuatro caracteres, las coordenadas geográficas en formato decimal y un indicador booleano de pertenencia a la zona Schengen. Esta clasificación se realiza automáticamente mediante una lógica de filtrado que analiza los dos primeros caracteres del código ICAO, comparándolos con una lista oficial de prefijos de países firmantes del acuerdo.

La gestión de la información se apoya en un robusto sistema de procesamiento de datos capaz de leer archivos de texto externos. Una de las tareas es la conversión de coordenadas geográficas: el programa debe transformar cadenas de texto que representan grados, minutos y segundos en valores flotantes decimales utilizables para cálculos y representación gráfica. Además permite la manipulaciónde la base de datos en memoria, ofreciendo funciones para añadir nuevos aeropuertos o eliminar existentes, y permitiendo exportar selecciones específicas a nuevos archivos de texto.

También se generan gráficos de barras comparativos para analizar la distribución de aeropuertos y crean archivos compatibles con Google Earth, permitiendo mapear las ubicaciones con códigos de colores diferenciados. Todo este conjunto de funcionalidades se unifica bajo una interfaz gráfica amigable desarrollada en Tkinter, lo que permite que cualquier usuario opere el sistema de forma intuitiva sin necesidad de interactuar directamente con el código fuente.
