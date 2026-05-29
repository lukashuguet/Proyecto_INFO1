# Proyecto Aeropuerto

# Versión 1

Esta versión del proyecto consiste en el desarrollo de una herramienta para la gestión y visualización de datos aeroportuarios internacionales, centrada específicamente en la identificación del espacio Schengen. El sistema se construye con la creación de una clase base que almacena el código ICAO de cuatro caracteres, las coordenadas geográficas en formato decimal y un indicador booleano de pertenencia a la zona Schengen. Esta clasificación se realiza automáticamente mediante una lógica de filtrado que analiza los dos primeros caracteres del código ICAO, comparándolos con una lista oficial de prefijos de países firmantes del acuerdo.

La gestión de la información se apoya en un robusto sistema de procesamiento de datos capaz de leer archivos de texto externos. Una de las tareas es la conversión de coordenadas geográficas: el programa debe transformar cadenas de texto que representan grados, minutos y segundos en valores flotantes decimales utilizables para cálculos y representación gráfica. Además permite la manipulaciónde la base de datos en memoria, ofreciendo funciones para añadir nuevos aeropuertos o eliminar existentes, y permitiendo exportar selecciones específicas a nuevos archivos de texto.

También se generan gráficos de barras comparativos para analizar la distribución de aeropuertos y crean archivos compatibles con Google Earth, permitiendo mapear las ubicaciones con códigos de colores diferenciados. Todo este conjunto de funcionalidades se unifica bajo una interfaz gráfica amigable desarrollada en Tkinter, lo que permite que cualquier usuario opere el sistema de forma intuitiva sin necesidad de interactuar directamente con el código fuente.

# Versión 2 

La segunda versión amplía su alcance a la gestión de vuelos con destino a Barcelona (LEBL). Mediante la nueva clase Aircraft, el sistema procesa datos críticos como el identificador de vuelo, la aerolínea y la hora de llegada, incluyendo un motor de validación que descarta automáticamente registros erróneos o incompletos.

Esta actualización destaca por su capacidad analítica y visual, permitiendo generar gráficos de frecuencias horarias, estadísticas por aerolínea y comparativas de vuelos Schengen. Además, se incorpora el cálculo de distancias mediante la fórmula de Haversine para identificar vuelos de largo radio (+2000 km). Finalmente, la herramienta permite mapear en Google Earth las trayectorias completas desde el origen, todo integrado en una interfaz gráfica que centraliza la carga, el análisis y la exportación de operaciones aéreas.

# Versión 3

La tercera versión escala la complejidad del proyecto al centrarse en la arquitectura interna y la gestión operativa de las puertas de embarque (gates) del aeropuerto de Barcelona-El Prat (LEBL). El sistema se estructura mediante un modelo jerárquico de clases (aeropuerto, terminales, áreas de embarque y puertas) que almacena la distribución de las aerolíneas y el estado de ocupación en tiempo real.
Esta actualización introduce la carga dinámica de la infraestructura desde archivos externos (LEBL.txt y listados de aerolíneas) e incorpora la asignación estática de puertas. 

Este motor vincula los vuelos entrantes con la puerta disponible más adecuada, evaluando restricciones críticas como la terminal asignada a la aerolínea y el tipo de vuelo (Schengen o no-Schengen). Finalmente, se potencia la interfaz en Tkinter para permitir al usuario inicializar el aeropuerto, gestionar los flujos de aeronaves y monitorizar visualmente el estado de ocupación de forma centralizada.

# Versión 4 

La cuarta versión consolida el núcleo del proyecto mediante la unificación de los flujos de tráfico aéreo y el desarrollo de un motor de simulación temporal e interactivo para el aeropuerto de Barcelona-El Prat (LEBL). El sistema escala operativamente al introducir la fusión de movimientos diarios, entrelazando en una única estructura lineal y cronológica los listados independientes de arribos (Arrivals.txt) y despegues (Departures.txt). Asimismo, se implementa un algoritmo de gestión de aeronaves nocturnas (Night Aircraft) diseñado para detectar y posicionar de forma prioritaria en sus respectivas puertas de embarque a aquellos aviones que pernoctan en el aeropuerto antes del inicio de la franja matutina.

El componente central de esta actualización es la incorporación de una línea de tiempo dinámica en la interfaz gráfica de Tkinter. A través de un control deslizante (Slider) de 24 horas sincronizado mediante eventos optimizados, el usuario puede monitorizar y actualizar instantáneamente el estado de ocupación de la infraestructura en el lienzo visual (Canvas). El motor de asignación dinámico evalúa en cada tramo horario los vuelos activos, calcula el volumen de aeronaves que se quedan sin pasarela debido a limitaciones de capacidad y refresca de forma fluida el árbol jerárquico de terminales. El algoritmo evalúa el tráfico aéreo en cada intervalo temporal, calcula las aeronaves desplazadas debido a la saturación de las puertas de embarque y sincroniza de manera automática el lienzo interactivo con la distribución real de las terminales.

Finalmente, se maximiza la capacidad analítica y de representación geoespacial del software. Por un lado, se integra un apartado estadístico en la interfaz que despliega histogramas de frecuencias de llegadas por hora, volúmenes de tráfico ordenados por aerolínea operadora y análisis de flujos apilados para auditar la proporción de tráfico Schengen. Por otro lado, el módulo visual se potencia de forma natural mediante un gráfico histórico de líneas de ocupación horaria (T1 frente a T2), junto con un nuevo plot en la interfaz capaz de trazar arcos de vuelo tridimensionales hacia LEBL en Google Earth.
