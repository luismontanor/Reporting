import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from fpdf import FPDF
from datetime import datetime
import openai

# Configuración de la conexión a la base de datos
db_config = {
    'user': 'postulante',
    'password': 'HB<tba!Sp6U2j5CN',
    'host': '54.219.2.160',
    'database': 'prueba_postulantes'
}

# Conexión a la base de datos
conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

# Consulta para obtener los datos de la encuesta
query = "SELECT * FROM encuesta"
cursor.execute(query)

# Cargar los datos en un DataFrame de pandas
columns = [desc[0] for desc in cursor.description]
data = cursor.fetchall()
df = pd.DataFrame(data, columns=columns)

# Cerrar la conexión
cursor.close()
conn.close()

# Convertir la columna 'fecha' a datetime
df['fecha'] = pd.to_datetime(df['fecha'])

# Calcular el total de respuestas
total_respuestas = len(df)

# Definir satisfacción, neutro e insatisfacción
satisfaccion = df[df['satisfeccion_general'] >= 6].shape[0]
neutro = df[df['satisfeccion_general'] == 5].shape[0]
insatisfaccion = df[df['satisfeccion_general'] <= 4].shape[0]

# Calcular porcentajes
porcentaje_satisfaccion = (satisfaccion / total_respuestas) * 100
porcentaje_insatisfaccion = (insatisfaccion / total_respuestas) * 100

# Calcular SNG
sng_satisfaccion = round(porcentaje_satisfaccion) - round(porcentaje_insatisfaccion)

# Cálculo de otras métricas
total_conocia_empresa = df[df['conocia_empresa'] == 'Sí'].shape[0]
sng_recomendacion = round((df[df['recomendacion'] >= 6].shape[0] * 100 / total_respuestas) - (df[df['recomendacion'] <= 4].shape[0] * 100 / total_respuestas))
nota_promedio_recomendacion = df['recomendacion'].mean()

# Filtrar comentarios válidos (no nulos y no vacíos)
comentarios_validos = df['recomendacion_abierta'].dropna()
comentarios_validos = comentarios_validos[comentarios_validos.str.strip() != '']
total_comentarios = len(comentarios_validos)

# Calcular días y meses que llevó la encuesta
fecha_inicio = df['fecha'].min()
fecha_fin = df['fecha'].max()
dias_encuesta = (fecha_fin - fecha_inicio).days
meses_encuesta = dias_encuesta / 30

# Configurar OpenAI API
openai.api_key = 'sk-proj-Y421g8tWPMUYe44pEyH9T3BlbkFJ1udNIa2Vdr8zxWmwQ3V8'

# Función para clasificar los comentarios utilizando ChatGPT
def clasificar_sentimiento_chatgpt(comentario):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Eres un asistente que clasifica comentarios en positivos, negativos o neutrales."},
            {"role": "user", "content": f"Clasifica el siguiente comentario como Positivo, Negativo o Neutral: {comentario}"}
        ]
    )
    sentimiento = response['choices'][0]['message']['content'].strip().lower()
    if 'positivo' in sentimiento:
        return 'Positivo'
    elif 'negativo' in sentimiento:
        return 'Negativo'
    elif 'neutral' in sentimiento:
        return 'Neutral'
    else:
        return 'Indeterminado'

# Aplicar la clasificación de sentimientos a los comentarios válidos
comentarios_validos = comentarios_validos.apply(clasificar_sentimiento_chatgpt)

# Verificar la clasificación de sentimientos
print(comentarios_validos.head(10))

# Configuración de estilo de seaborn
sns.set_theme(style="whitegrid")

# Crear gráfico de barras para la distribución de la satisfacción general
plt.figure(figsize=(10, 6))
ax = sns.histplot(df['satisfeccion_general'], bins=7, kde=False, color='skyblue', edgecolor='black')
ax.set_title('Distribución de la Satisfacción General', fontsize=16)
ax.set_xlabel('Nivel de Satisfacción (1-7)', fontsize=14)
ax.set_ylabel('Frecuencia', fontsize=14)
ax.grid(axis='y', linestyle='--', alpha=0.7)
ax.set_xticks(range(1, 8))
for p in ax.patches:
    ax.annotate(f'{int(p.get_height())}', (p.get_x() + p.get_width() / 2., p.get_height()), ha='center', va='center', xytext=(0, 10), textcoords='offset points')
plt.tight_layout()
plt.savefig('satisfaccion_general.png')


# Crear gráfico de barras para la distribución de la recomendación
plt.figure(figsize=(10, 6))
ax = sns.histplot(df['recomendacion'], bins=7, kde=False, color='lightgreen', edgecolor='black')
ax.set_title('Distribución de la Recomendación', fontsize=16)
ax.set_xlabel('Nivel de Recomendación (1-7)', fontsize=14)
ax.set_ylabel('Frecuencia', fontsize=14)
ax.grid(axis='y', linestyle='--', alpha=0.7)
ax.set_xticks(range(1, 8))  # Asegura que las etiquetas del eje x se alineen con las barras
plt.tight_layout()
plt.savefig('recomendacion.png')

# Crear gráfico de barras para el análisis de sentimientos
plt.figure(figsize=(10, 6))
sentimiento_counts = comentarios_validos.value_counts().reindex(['Positivo', 'Negativo', 'Neutral'], fill_value=0)
sentimiento_df = pd.DataFrame({'Sentimiento': sentimiento_counts.index, 'Cantidad': sentimiento_counts.values})
sentimiento_colors = ['lightgreen', 'lightcoral', 'lightblue']
ax = sns.barplot(x='Sentimiento', y='Cantidad', hue='Sentimiento', data=sentimiento_df, palette=sentimiento_colors, edgecolor='black', dodge=False)
ax.set_title('Análisis de Sentimientos de Comentarios', fontsize=16)
ax.set_xlabel('Sentimiento', fontsize=14)
ax.set_ylabel('Cantidad', fontsize=14)
ax.grid(axis='y', linestyle='--', alpha=0.7)

# Eliminar la leyenda si existe
if ax.legend_:
    ax.legend_.remove()

# Agregar etiquetas encima de las barras
for p in ax.patches:
    ax.annotate(f'{int(p.get_height())}', (p.get_x() + p.get_width() / 2., p.get_height()), ha='center', va='center', xytext=(0, 10), textcoords='offset points')

plt.tight_layout()  # Ajusta el espacio alrededor del gráfico
plt.savefig('sentimientos_barras.png')

# Crear gráfico de pastel para el análisis de sentimientos
labels = ['Positivo', 'Negativo', 'Neutral']
sizes = [sentimiento_counts.get('Positivo', 0), sentimiento_counts.get('Negativo', 0), sentimiento_counts.get('Neutral', 0)]
explode = (0.1, 0, 0)  # Resaltar la primera rebanada (Positivo)

fig1, ax1 = plt.subplots()
ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%', shadow=True, startangle=90)
ax1.axis('equal')  # Asegurar que el gráfico sea circular
plt.title("Análisis de Sentimientos de Comentarios")
plt.legend()
plt.savefig('grafica_pastel_sentimientos.png')

# Generación del informe en PDF
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Informe de Encuesta Proyecto Marla', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(5)

    def chapter_body(self, body):
        self.set_font('Arial', '', 12)
        self.multi_cell(0, 10, body)
        self.ln()

    def add_chart(self, image_path, title, description):
        self.add_page()
        self.chapter_title(title)
        self.image(image_path, x=(210 - 150) / 2, y=40, w=150)
        self.ln(95)
        self.chapter_body(description)

pdf = PDF()
pdf.add_page()
pdf.set_font('Arial', 'B', 20)
pdf.cell(0, 10, 'Informe de Encuesta Proyecto Marla', 0, 1, 'C')
pdf.ln(20)
pdf.image('logo-tga_w_1.png', x=80, w=50)
pdf.ln(20)
pdf.set_font('Arial', 'I', 12)
pdf.cell(0, 10, 'Fecha: ' + datetime.now().strftime('%Y-%m-%d'), 0, 1, 'C')
pdf.ln(10)
pdf.set_font('Arial', '', 14)
pdf.multi_cell(0, 10, 'Este informe presenta los resultados de la encuesta realizada para el proyecto Marla. El objetivo de la encuesta es evaluar la satisfacción general de los clientes, su conocimiento sobre la empresa, y la probabilidad de que recomienden la empresa a otros.', 0, 'C')
pdf.ln(20)


# Índice
pdf.add_page()
pdf.chapter_title('Índice')
pdf.chapter_body('1. Introducción\n2. Resumen Ejecutivo\n3. Análisis de Datos\n4. Análisis de Sentimientos\n5. Conclusiones y Recomendaciones\n6. Gráficos y Visualizaciones\n')

# Introducción
pdf.add_page()
pdf.chapter_title('Introducción')
pdf.chapter_body('Este informe presenta los resultados de la encuesta realizada para el proyecto Marla. El objetivo de la encuesta es evaluar la satisfacción general de los clientes, su conocimiento sobre la empresa, y la probabilidad de que recomienden la empresa a otros.')

# Resumen Ejecutivo
pdf.chapter_title('Resumen Ejecutivo')
pdf.chapter_body(f'SNG de la satisfacción general: {sng_satisfaccion:.2f}\nTotal de personas que conocían a la empresa: {total_conocia_empresa}\nSNG de la recomendación: {sng_recomendacion:.2f}\nNota promedio de la recomendación: {nota_promedio_recomendacion:.2f}\nTotal de personas que hicieron un comentario: {total_comentarios}\nDías que llevó la encuesta: {dias_encuesta}\nMeses que llevó la encuesta: {meses_encuesta:.2f}')

# Análisis de Datos
pdf.chapter_title('Análisis de Datos')
pdf.chapter_body(f'En esta sección se presentan los datos obtenidos de la encuesta, incluyendo la satisfacción general, el conocimiento de la empresa y la recomendación.\n\n'
                 f'     - Satisfacción General\n'
                 f'El promedio de satisfacción general es {sng_satisfaccion:.2f}, lo que indica que los encuestados están generalmente satisfechos con la empresa.\n'
                 f'La mayoría de los encuestados se encuentran en el rango de satisfacción media a alta, con una concentración notable en los valores superiores de la escala.\n\n'
                 f'     - Conocimiento de la Empresa\n'
                 f'Un total de {total_conocia_empresa} encuestados conocían la empresa antes de la encuesta.\n'
                 f'El porcentaje de encuestados que conocían la empresa es aproximadamente {(total_conocia_empresa / total_respuestas) * 100:.2f}%.\n\n'
                 f'     - Recomendación\n'
                 f'El promedio de recomendación es {nota_promedio_recomendacion:.2f}, lo que indica una alta probabilidad de que los encuestados recomienden la empresa.\n'
                 f'Similar a la satisfacción general, la mayoría de los encuestados se encuentran en el rango de recomendación media a alta.\n\n'
                 f'     - Comentarios Abiertos\n'
                 f'Un total de {total_comentarios} encuestados proporcionaron comentarios abiertos.')

# Análisis de Sentimientos
pdf.chapter_title('Análisis de Sentimientos')
pdf.chapter_body('El análisis de sentimientos se realizó utilizando ChatGPT para evaluar los comentarios abiertos proporcionados por los encuestados. Este análisis nos ayuda a entender el tono general de los comentarios, ya sea positivo, negativo o neutral.\n\n'
                 '      - Resultados del Análisis de Sentimientos\n'
                 '- Sentimientos Positivos: Comentarios que expresan satisfacción y aspectos positivos de la empresa.\n'
                 '- Sentimientos Negativos: Comentarios que expresan insatisfacción y aspectos negativos de la empresa.\n'
                 '- Sentimientos Neutrales: Comentarios que no expresan un sentimiento claro o son mixtos.\n'
                 'La mayoría de los comentarios son negativos, lo que indica áreas de mejora que deben ser abordadas para mejorar la satisfacción del cliente.\n\n'
                 'La distribución de los sentimientos se puede visualizar en un gráfico de barras que muestra la frecuencia de cada tipo de sentimiento.')

# Conclusiones y Recomendaciones
pdf.chapter_title('Conclusiones y Recomendaciones')
pdf.chapter_body('A partir de los resultados obtenidos, se pueden hacer las siguientes conclusiones y recomendaciones para mejorar la satisfacción de los clientes y la probabilidad de que recomienden la empresa.\n\n'
                 '      - Conclusiones\n'
                 '1. Alta Satisfacción General: La mayoría de los encuestados están satisfechos con la empresa, lo que se refleja en el alto promedio de satisfacción general.\n'
                 '2. Conocimiento de la Empresa: Un porcentaje significativo de los encuestados ya conocía la empresa, lo que puede indicar una buena presencia de marca.\n'
                 '3. Alta Probabilidad de Recomendación: Los encuestados están dispuestos a recomendar la empresa a otros, lo que es un indicador positivo de la lealtad del cliente.\n'
                 '4. Comentarios Negativos: La mayoría de los comentarios abiertos son negativos, lo que indica áreas de mejora que deben ser abordadas para mejorar la satisfacción del cliente.\n\n'
                 '      - Recomendaciones\n'
                 '1. Mantener la Calidad del Servicio: Continuar ofreciendo un servicio de alta calidad para mantener y mejorar la satisfacción general de los clientes.\n'
                 '2. Mejorar la Visibilidad de la Marca: Implementar estrategias de marketing para aumentar el conocimiento de la empresa entre los potenciales clientes.\n'
                 '3. Fomentar la Retroalimentación: Animar a los clientes a proporcionar más comentarios abiertos para obtener una visión más detallada de sus experiencias.\n'
                 '4. Abordar Comentarios Negativos: Analizar y abordar los comentarios negativos para identificar áreas de mejora y tomar acciones correctivas.')

# Agregar gráficos al informe
pdf.add_chart('satisfaccion_general.png', 'Distribución de la Satisfacción General',
              'Este gráfico muestra la distribución de las respuestas de los encuestados en la escala de satisfacción general, que va de 1 a 7.\n\n'
              'Interpretación:\n'
              '- Eje X (Satisfacción): Representa los niveles de satisfacción, donde 1 es muy insatisfecho y 7 es muy satisfecho.\n'
              '- Eje Y (Frecuencia): Representa el número de encuestados que seleccionaron cada nivel de satisfacción.\n'
              '- Conclusión: La mayoría de los encuestados se encuentran en el rango de satisfacción media a alta, lo que indica una percepción positiva general de la empresa.')

pdf.add_chart('recomendacion.png', 'Distribución de la Recomendación',
              'Este gráfico muestra la distribución de las respuestas de los encuestados en la escala de recomendación, que también va de 1 a 7.\n\n'
              'Interpretación:\n'
              '- Eje X (Recomendación): Representa los niveles de recomendación, donde 1 es muy improbable que recomiende y 7 es muy probable que recomiende.\n'
              '- Eje Y (Frecuencia): Representa el número de encuestados que seleccionaron cada nivel de recomendación.\n'
              '- Conclusión: Similar a la satisfacción general, la mayoría de los encuestados se encuentran en el rango de recomendación media a alta, lo que sugiere que los encuestados están dispuestos a recomendar la empresa a otros.')

pdf.add_chart('sentimientos_barras.png', 'Análisis de Sentimientos de Comentarios',
              'Este gráfico de barras muestra la frecuencia de los diferentes tipos de sentimientos (positivos, negativos y neutrales) expresados en los comentarios abiertos de los encuestados.\n\n'
              'Interpretación:\n'
              '- Sentimientos Positivos: Comentarios que expresan satisfacción y aspectos positivos de la empresa.\n'
              '- Sentimientos Negativos: Comentarios que expresan insatisfacción y aspectos negativos de la empresa.\n'
              '- Sentimientos Neutrales: Comentarios que no expresan un sentimiento claro o son mixtos.\n'
              '- Conclusión: La mayoría de los comentarios son negativos, lo que indica áreas de mejora que deben ser abordadas para mejorar la satisfacción del cliente.')

pdf.add_chart('grafica_pastel_sentimientos.png', 'Distribución de Sentimientos de Comentarios',
              'Este gráfico de pastel muestra la proporción de los diferentes tipos de sentimientos (positivos, negativos y neutrales) expresados en los comentarios abiertos de los encuestados.\n\n'
              'Interpretación:\n'
              '- Sentimientos Positivos: Comentarios que expresan satisfacción y aspectos positivos de la empresa.\n'
              '- Sentimientos Negativos: Comentarios que expresan insatisfacción y aspectos negativos de la empresa.\n'
              '- Sentimientos Neutrales: Comentarios que no expresan un sentimiento claro o son mixtos.\n'
              '- Conclusión: La mayoría de los comentarios son negativos, lo que indica áreas de mejora que deben ser abordadas para mejorar la satisfacción del cliente.')

# Finalizar y guardar el PDF
pdf.output('Informe_Encuesta_Proyecto_Marla.pdf', 'F')

print("Informe generado exitosamente.")
