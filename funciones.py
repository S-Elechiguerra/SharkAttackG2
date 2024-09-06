import pandas as pd
import re
import matplotlib.pyplot as plt

# Funciones de carga y preprocesamiento de datos
def load_data(url):
    """Carga de datos."""
    return pd.read_excel(url)

def clean_column_names(df, rename_map=None):
    """Limpieza en encabezados de columnas."""
    df = df.iloc[:, :15]
    df.columns = df.columns.str.lower()
    if rename_map:
        df.rename(columns=rename_map, inplace=True)
    return df

def remove_na_duplicates(df):
    """Limpieza de valores nulos y duplicados"""
    df = df.dropna(how="all")
    df = df.drop_duplicates()
    df.reset_index(drop=True, inplace=True)
    return df

def clean_invalid_values(df, mappings):
    """Limpieza de valores invalidos en columnas type,fatality"""
    for column, mapping in mappings.items():
        df[column] = df[column].replace(mapping, regex=False)
    return df

def remove_inconsistencies_places(df, places, patron_negativo):
    """Limpieza variables de lugares country,state,location.-- patron_negativo(r'\?|[0-9]|beetween')"""
    for column in places:
        df = df[~df[column].str.contains(patron_negativo, na=False)]
    return df    

def limit_for_bussinescase(df, limits):
    """Limites para análisis según el bussines case year>2000 ,eliminar paises freq ataq<30"""
    for column, limit in limits.items():
        if column == "year":
            # Filtrar por el año
            df = df[df[column] >= limit]
        elif column == "country":
            # Filtrar por frecuencias en 'country'
            conteo_valores = df["country"].value_counts()
            valores_frecuentes = conteo_valores[conteo_valores > limit].index
            df = df[df["country"].isin(valores_frecuentes)]
    return df          
    
def clean_activity_column(df, keywords):
    # Limpieza de columna activity
    df['activity'] = df['activity'].str.lower()  # Convertir a minúsculas todas las actividades

    keyword_list = keywords.split('|')  # Dividir las palabras clave en una lista

    def extract_first_keyword(text):
        if isinstance(text, str):  # Verificar que el valor sea una cadena
            for word in keyword_list:  # Recorrer las palabras clave
                if word in text:  # Si la palabra clave está en el texto
                    return word  # Retornar la primera coincidencia
        return 'No especificado'  # Si no es cadena o no hay coincidencias

    # Aplicar la función a la columna 'activity'
    df['actividad_2'] = df['activity'].apply(extract_first_keyword)
    return df
    
def clean_date_column(df):
    """Limpieza de columna date"""
    df = df[df["date"].str.contains(r'Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec', na=False)]
    df["date"] = df["date"].str.replace(r'Reported ', '', regex=True)\
                           .str.replace(r' ', '-', regex=True)\
                           .str.replace(r'--', '-', regex=True)\
                           .str.replace(r'June', 'Jun', regex=True)
    df['date'] = pd.to_datetime(df['date'], format='%d-%b-%Y', errors='coerce')
    df['month'] = df['date'].dt.strftime('%b')
    df['year'] = df['date'].dt.strftime('%Y')
  
    return df

def clean_time_column(df):
    #limpieza de time
    def extract_time(value):
        if not isinstance(value, str):
            return "No especificado"
        match = re.search(r'\b(\d{2}h\d{2})\b', value)
        if match:
            return match.group(1)
        return "No especificado"

    df['time_clean'] = df['time'].apply(extract_time)
    return df

def fill_value(df, fill_values):
    """Llenar valores nulos"""
    for column, value in fill_values.items():
        df[column] = df[column].fillna(value)
    return df

def create_indice(df):
    df['indice'] = range(1, len(df) + 1)
    return df

def graficos(df):

#GRÁFICO TOP PAISES

    top_paises = df.groupby("country")["indice"].count().sort_values(ascending=False).head()

    plt.figure(figsize=(10, 6))  # Opcional: ajustar el tamaño de la figura
    plt.bar(top_paises.index, top_paises.values, color='blue')  # Crear barras

    # Añadir títulos y etiquetas
    plt.title('Número de Incidentes por País (Top 5)')
    plt.xlabel('País')
    plt.ylabel('Número de Incidentes')

    # Mostrar el gráfico
    plt.xticks(rotation=45)  # Opcional: rotar etiquetas del eje x para mejor visibilidad
    plt.tight_layout()  # Ajustar automáticamente los parámetros del gráfico
    plt.show()

#GRÁFICO PIE USA TOP 5
    top_state_usa = df[df["country"] == "USA"].groupby(["state"])["indice"].count().sort_values(ascending=False).head()
    # Crear el gráfico de pastel
    plt.figure(figsize=(10, 8), facecolor='white')  # Ajustar el tamaño y el fondo de la figura

    # Crear el gráfico de pastel con etiquetas más grandes
    plt.pie(
        top_state_usa,
        labels=top_state_usa.index,
        autopct='%1.1f%%',
        colors=plt.cm.Paired(range(len(top_state_usa))),
        startangle=140,
        textprops={'fontsize': 14}  # Aumentar el tamaño de la fuente de las etiquetas
    )

    # Añadir título con fuente más grande
    plt.title('Número de Incidentes por Estado en USA (Top 5)', fontsize=16)

    # Mostrar el gráfico
    plt.axis('equal')  # Para que el gráfico sea un círculo perfecto
    plt.show()

#GRÁFICO BARRA USA
    # Crear una tabla dinámica

    # Filtrar las filas para el país USA
    df_usa = df[df["country"] == "USA"]

    # Crear una tabla dinámica solo para USA
    pivot_incidente_usa = df_usa.pivot_table(
        index="year",                  # Columnas para las filas de la tabla dinámica
        columns="fatality",            # Columnas para las columnas de la tabla dinámica
        values="indice",               # Columna cuyos valores se agregan
        aggfunc="count"                # Función de agregación para contar ocurrencias
    )

    # Crear gráfico de barras apiladas
    pivot_incidente_usa.plot(kind='bar', stacked=True, figsize=(10, 6))

    # Añadir títulos y etiquetas
    plt.title('Número de Incidentes por Año y Categoría de Fatality - USA')
    plt.xlabel('Año')
    plt.ylabel('Número de Incidentes')

    # Mostrar gráfico
    plt.legend(title='Fatality')
    plt.grid(axis='y')
    plt.show()   

#GRAFICO BARRAS MESES USA
    month_order = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    # Convertir la columna 'month' en una categoría con el orden definido
    df_usa['month'] = pd.Categorical(df_usa['month'], categories=month_order, ordered=True)

    # Agrupar por mes y contar los incidentes
    incidente_mes_usa = df_usa.groupby("month")["indice"].count().sort_index()

    plt.figure(figsize=(10, 6))  # Opcional: ajustar el tamaño de la figura
    plt.bar(incidente_mes_usa.index, incidente_mes_usa.values, color='red')  # Crear barras

    # Añadir títulos y etiquetas
    plt.title('Número de Incidentes por mes - USA)')
    plt.xlabel('Mes')
    plt.ylabel('Número de Incidentes')

    # Mostrar el gráfico
    plt.xticks(rotation=45)  # Opcional: rotar etiquetas del eje x para mejor visibilidad
    plt.tight_layout()  # Ajustar automáticamente los parámetros del gráfico
    plt.show()

#GRÁFICO PIE AUSTRALIA TOP 5    

    top_state_australia = df[df["country"] == "AUSTRALIA"].groupby(["state","fatality"])["indice"].count().sort_values(ascending=False).head(5)

    # Crear el gráfico de pastel
    plt.figure(figsize=(10, 8), facecolor='white')  # Ajustar el tamaño y el fondo de la figura

    # Crear el gráfico de pastel con etiquetas más grandes
    plt.pie(
        top_state_australia,
        labels=top_state_australia.index,
        autopct='%1.1f%%',
        colors=plt.cm.Paired(range(len(top_state_australia))),
        startangle=140,
        textprops={'fontsize': 14}  # Aumentar el tamaño de la fuente de las etiquetas
    )

    # Añadir título con fuente más grande
    plt.title('Número de Incidentes por Estado en AUSTRALIA (Top 5)', fontsize=16)

    # Mostrar el gráfico
    plt.axis('equal')  # Para que el gráfico sea un círculo perfecto
    plt.show()

#GRÁFICO BARRA AUSTRALIA

    df_australia = df[df["country"] == "AUSTRALIA"]
    # Crear una tabla dinámica
    pivot_incidente_australia = df_australia.pivot_table(
        index="year",                  # Columnas para las filas de la tabla dinámica
        columns="fatality",            # Columnas para las columnas de la tabla dinámica
        values="indice",               # Columna cuyos valores se agregan
        aggfunc="count"                # Función de agregación para contar ocurrencias
    )

    # Crear gráfico de barras apiladas
    pivot_incidente_australia.plot(kind='bar', stacked=True, figsize=(10, 6))

    # Añadir títulos y etiquetas
    plt.title('Número de Incidentes por Año y Categoría de Fatality - AUSTRALIA')
    plt.xlabel('Año')
    plt.ylabel('Número de Incidentes')

    # Mostrar gráfico
    plt.legend(title='Fatality')
    plt.grid(axis='y')
    plt.show()    

#GRAFICO BARRAS MESES AUSTRALIA

    # Convertir la columna 'month' en una categoría con el orden definido
    df_australia['month'] = pd.Categorical(df_australia['month'], categories=month_order, ordered=True)

    # Agrupar por mes y contar los incidentes
    incidente_mes_australia = df_australia.groupby("month")["indice"].count().sort_index()

    plt.figure(figsize=(10, 6))  # Opcional: ajustar el tamaño de la figura
    plt.bar(incidente_mes_australia.index, incidente_mes_australia.values, color='red')  # Crear barras

    # Añadir títulos y etiquetas
    plt.title('Número de Incidentes por mes - AUSTRALIA)')
    plt.xlabel('Mes')
    plt.ylabel('Número de Incidentes')

    # Mostrar el gráfico
    plt.xticks(rotation=45)  # Opcional: rotar etiquetas del eje x para mejor visibilidad
    plt.tight_layout()  # Ajustar automáticamente los parámetros del gráfico
    plt.show()       

#GRÁFICO PIE SOUTH AFRICA TOP 3    

    top_state_south_africa = df[df["country"] == "SOUTH AFRICA"].groupby(["state","fatality"])["indice"].count().sort_values(ascending=False).head(3)

    # Crear el gráfico de pastel
    plt.figure(figsize=(10, 8), facecolor='white')  # Ajustar el tamaño y el fondo de la figura

    # Crear el gráfico de pastel con etiquetas más grandes
    plt.pie(
        top_state_south_africa,
        labels=top_state_south_africa.index,
        autopct='%1.1f%%',
        colors=plt.cm.Paired(range(len(top_state_south_africa))),
        startangle=140,
        textprops={'fontsize': 14}  # Aumentar el tamaño de la fuente de las etiquetas
    )

    # Añadir título con fuente más grande
    plt.title('Número de Incidentes por Estado en SOUTH AFRICA (Top 3)', fontsize=16)

    # Mostrar el gráfico
    plt.axis('equal')  # Para que el gráfico sea un círculo perfecto
    plt.show()

#GRÁFICO BARRA SOUTH AFRICA
    df_southafrica = df[df["country"] == "SOUTH AFRICA"]
    # Crear una tabla dinámica
    pivot_incidente_southafrica = df_southafrica.pivot_table(
        index="year",                  # Columnas para las filas de la tabla dinámica
        columns="fatality",            # Columnas para las columnas de la tabla dinámica
        values="indice",               # Columna cuyos valores se agregan
        aggfunc="count"                # Función de agregación para contar ocurrencias
    )

    # Crear gráfico de barras apiladas
    pivot_incidente_southafrica.plot(kind='bar', stacked=True, figsize=(10, 6))

    # Añadir títulos y etiquetas
    plt.title('Número de Incidentes por Año y Categoría de Fatality - SOUTH AFRICA')
    plt.xlabel('Año')
    plt.ylabel('Número de Incidentes')

    # Mostrar gráfico
    plt.legend(title='Fatality')
    plt.grid(axis='y')
    plt.show() 

#GRAFICO BARRAS MESES ASOUTH AFRICA

    # Convertir la columna 'month' en una categoría con el orden definido
    df_southafrica['month'] = pd.Categorical(df_southafrica['month'], categories=month_order, ordered=True)

    # Agrupar por mes y contar los incidentes
    incidente_mes_southafrica = df_southafrica.groupby("month")["indice"].count().sort_index()

    plt.figure(figsize=(10, 6))  # Opcional: ajustar el tamaño de la figura
    plt.bar(incidente_mes_southafrica.index, incidente_mes_southafrica.values, color='red')  # Crear barras

    # Añadir títulos y etiquetas
    plt.title('Número de Incidentes por mes en South Africa)')
    plt.xlabel('Mes')
    plt.ylabel('Número de Incidentes')

    # Mostrar el gráfico
    plt.xticks(rotation=45)  # Opcional: rotar etiquetas del eje x para mejor visibilidad
    plt.tight_layout()  # Ajustar automáticamente los parámetros del gráfico
    plt.show()    

#GRAFICO Tipo de incidentes por top paises

    paises_top = df[df["country"].isin(["USA", "AUSTRALIA", "SOUTH AFRICA"])]

    paises_top.pivot_table(index = "type",columns = "country" ,values =["indice"],aggfunc = "count")

    
    # Crear la tabla dinámica
    paises_top_pivot = paises_top.pivot_table(
        index="type",                  # Índice: tipo de incidente
        columns="country",             # Columnas: países
        values="indice",               # Valores: cuenta de los incidentes
        aggfunc="count"                # Función de agregación: contar
    )

    # Graficar la tabla dinámica
    paises_top_pivot.plot(kind='bar', stacked=True, figsize=(10, 6))

    # Añadir títulos y etiquetas
    plt.title('Número de Incidentes por Tipo y País (USA, AUSTRALIA, SOUTH AFRICA)')
    plt.xlabel('Tipo de Incidente')
    plt.ylabel('Número de Incidentes')

    # Mostrar el gráfico
    plt.xticks(rotation=45, ha='right')  # Rotar etiquetas del eje x para mejor visibilidad
    plt.legend(title='País')
    plt.tight_layout()  # Ajustar automáticamente los márgenes del gráfico
    plt.show()   

   

def main(url, rename_map, mappings, places, patron_negativo, limits, keywords, fill_values):
    # 1. Cargar los datos
    df = load_data(url)

    # 2. Limpiar los nombres de las columnas
    df = clean_column_names(df, rename_map)

    # 3. Eliminar duplicados y NA
    df = remove_na_duplicates(df)

    # 4. Limpiar valores inválidos en columnas específicas
    df = clean_invalid_values(df, mappings)

    # 5. Eliminar inconsistencias en lugares específicos (columnas)
    df = remove_inconsistencies_places(df, places, patron_negativo)

    # 6. Aplicar los límites del business case (year y freq_ataque)
    df = limit_for_bussinescase(df, limits)

    # 7. Limpiar la columna 'activity' y extraer palabras clave
    df = clean_activity_column(df, keywords)

    # 8. Limpiar la columna 'date'
    df = clean_date_column(df)

    # 9. Limpiar la columna 'time'
    df = clean_time_column(df)

    # 10. Rellenar valores nulos según el diccionario de valores por defecto
    df = fill_value(df, fill_values)

    #11. Crear una columna indice
    df = create_indice(df)

    #12. Crear gráficos
    graficos(df)

    # 11. Retornar el DataFrame limpio
    return df
