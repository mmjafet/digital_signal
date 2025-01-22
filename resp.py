import requests

url = "https://pantalla-anuncios-rasp.onrender.com/media"

try:
    response = requests.get(url)
    response.raise_for_status()  # Esto lanza un error si la solicitud no fue exitosa

    # Imprimir el contenido de la respuesta
    print("Status Code:", response.status_code)
    print("Headers:", response.headers)
    print("Content:", response.text)  # o response.json() si es JSON
except requests.exceptions.RequestException as e:
    print(f"Error fetching data from {url}: {e}")
