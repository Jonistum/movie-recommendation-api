from fastapi import FastAPI
import pandas as pd

app = FastAPI()

# Cargar el dataset
df = pd.read_csv("DATA/movies_cleaned.csv")

# Convertir la columna release_date a datetime si aún no lo está
df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')
@app.get("/cantidad_filmaciones_mes/{mes}")
def cantidad_filmaciones_mes(mes: str):
    """ Devuelve la cantidad de películas estrenadas en el mes ingresado """
    # Convertir el mes ingresado a su equivalente en inglés
    meses_en_ingles = {
        "enero": "January",
        "febrero": "February",
        "marzo": "March",
        "abril": "April",
        "mayo": "May",
        "junio": "June",
        "julio": "July",
        "agosto": "August",
        "septiembre": "September",
        "octubre": "October",
        "noviembre": "November",
        "diciembre": "December"
    }
    
    mes_en_ingles = meses_en_ingles.get(mes.lower())
    
    if mes_en_ingles:
        peliculas_mes = df[df['release_date'].dt.month_name() == mes_en_ingles]
        cantidad = len(peliculas_mes)
        return {"mensaje": f"{cantidad} cantidad de películas fueron estrenadas en el mes de {mes}"}
    else:
        return {"mensaje": "Mes no válido"}

@app.get("/cantidad_filmaciones_dia/{dia}")
def cantidad_filmaciones_dia(dia: str):
    """ Devuelve la cantidad de películas estrenadas en el día ingresado """
    peliculas_dia = df[df['release_date'].dt.day_name().str.lower() == dia.lower()]
    cantidad = len(peliculas_dia)
    return {"mensaje": f"{cantidad} cantidad de películas fueron estrenadas en los días {dia}"}

@app.get("/score_titulo/{titulo_de_la_filmacion}")
def score_titulo(titulo_de_la_filmacion: str):
    """ Devuelve el título, año de estreno y score de la película """
    pelicula = df[df['title'].str.lower() == titulo_de_la_filmacion.lower()]
    if not pelicula.empty:
        titulo = pelicula.iloc[0]['title']
        año_estreno = pelicula.iloc[0]['release_date'].year
        score = pelicula.iloc[0]['popularity']
        return {"titulo": titulo, "año_estreno": año_estreno, "score": score}
    return {"mensaje": "Película no encontrada"}

@app.get("/votos_titulo/{titulo_de_la_filmacion}")
def votos_titulo(titulo_de_la_filmacion: str):
    """ Devuelve el título, cantidad de votos y el promedio de votos de la película """
    pelicula = df[df['title'].str.lower() == titulo_de_la_filmacion.lower()]
    if not pelicula.empty:
        votos = pelicula.iloc[0]['vote_count']
        if votos >= 2000:
            promedio_votos = pelicula.iloc[0]['vote_average']
            return {"titulo": titulo_de_la_filmacion, "votos": votos, "promedio_votos": promedio_votos}
        return {"mensaje": "La película no tiene suficientes votos (menos de 2000)"}
    return {"mensaje": "Película no encontrada"}

@app.get("/get_actor/{nombre_actor}")
def get_actor(nombre_actor: str):
    """ Devuelve el éxito del actor, la cantidad de películas en las que ha participado y el promedio de retorno """
    # Filtrar películas con el actor (suponiendo que la columna 'production_companies_names' contiene los actores)
    peliculas_actor = df[df['production_companies_names'].str.contains(nombre_actor, case=False, na=False)]
    if not peliculas_actor.empty:
        cantidad_peliculas = len(peliculas_actor)
        retorno_total = peliculas_actor['return'].sum()
        promedio_retorno = retorno_total / cantidad_peliculas if cantidad_peliculas > 0 else 0
        return {
            "actor": nombre_actor,
            "cantidad_peliculas": cantidad_peliculas,
            "retorno_total": retorno_total,
            "promedio_retorno": promedio_retorno
        }
    return {"mensaje": "Actor no encontrado"}

@app.get("/get_director/{nombre_director}")
def get_director(nombre_director: str):
    """ Devuelve el éxito del director con las películas, retorno, costo y ganancia """
    # Filtrar películas del director (suponiendo que la columna 'production_companies_names' contiene los directores)
    peliculas_director = df[df['production_companies_names'].str.contains(nombre_director, case=False, na=False)]
    if not peliculas_director.empty:
        peliculas_info = []
        for _, pelicula in peliculas_director.iterrows():
            peliculas_info.append({
                "titulo": pelicula['title'],
                "fecha_lanzamiento": pelicula['release_date'].strftime('%Y-%m-%d'),
                "retorno": pelicula['return'],
                "costo": pelicula['budget'],
                "ganancia": pelicula['revenue'] - pelicula['budget']
            })
        return {"director": nombre_director, "peliculas": peliculas_info}
    return {"mensaje": "Director no encontrado"}

@app.get("/recomendacion/{titulo}")
def recomendacion(titulo: str):
    """ Devuelve 5 películas recomendadas similares al título ingresado """
    pelicula = df[df['title'].str.lower() == titulo.lower()]
    if not pelicula.empty:
        # Calcular la similitud con otras películas en base al score de popularidad
        pelicula_score = pelicula.iloc[0]['popularity']
        df['similarity'] = abs(df['popularity'] - pelicula_score)
        peliculas_similares = df.nsmallest(6, 'similarity')
        peliculas_similares = peliculas_similares[peliculas_similares['title'] != titulo]
        recomendaciones = peliculas_similares['title'].tolist()
        return {"recomendaciones": recomendaciones[:5]}
    return {"mensaje": "Película no encontrada"}
