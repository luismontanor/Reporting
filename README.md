

# Proyecto Marla - Análisis de Encuesta

Este proyecto contiene el análisis de una encuesta realizada para el proyecto inmobiliario Marla, desarrollado por la empresa MK. El objetivo del análisis es evaluar la satisfacción de los clientes, su conocimiento sobre la empresa y la probabilidad de que recomienden la empresa a otros.

## Descripción

El proyecto incluye un script en Python (`prueba.py`) que realiza las siguientes tareas:

1. Conexión a una base de datos MySQL para extraer los datos de la encuesta.
2. Cálculo de métricas clave:
   - SNG (Satisfacción Neta General) de la pregunta `satisfeccion_general`.
   - Total de personas que conocían a la empresa (`conocia_empresa`).
   - SNG de la recomendación (`recomendacion`).
   - Nota promedio de la recomendación (`recomendacion`).
   - Total de personas que hicieron un comentario.
   - Días y meses que llevó la encuesta.
3. Consulta a la API de OpenAI para clasificar los comentarios abiertos (`recomendacion_abierta`) en positivos, negativos o neutrales.
4. Generación de gráficos para visualizar la distribución de la satisfacción general, la recomendación y el análisis de sentimientos.
5. Creación de un informe en PDF (`Informe_Encuesta_Proyecto_Marla.pdf`) que incluye todos los datos, gráficos y análisis.

## Requisitos

- Python 3.x
- Bibliotecas de Python:
  - `mysql-connector-python`
  - `pandas`
  - `matplotlib`
  - `seaborn`
  - `fpdf`
  - `openai`

## Instalación

1. Clona este repositorio:

2. Instala las dependencias:
   ```bash
   pip install mysql-connector-python pandas matplotlib seaborn fpdf openai
   ```

## Uso

1. Configura las credenciales de la base de datos y la clave de la API de OpenAI en el archivo `prueba.py`.
2. Ejecuta el script:
   ```bash
   python prueba.py
   ```
3. El informe en PDF se generará como `Informe_Encuesta_Proyecto_Marla.pdf`.

## Estructura del Proyecto

- `prueba.py`: Script principal que realiza el análisis y genera el informe.
- `Informe_Encuesta_Proyecto_Marla.pdf`: Informe en PDF generado por el script.
- `README.md`: Este archivo.

## Contribuciones

Las contribuciones son bienvenidas. Por favor, abre un issue o envía un pull request para discutir cualquier cambio que te gustaría realizar.


