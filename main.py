from fastapi import FastAPI
from typing import Union
import requests
import os

app = FastAPI()
whoapi = 'https://api.whoapi.com'
api_key = os.environ.get('WHO_APIKEY')
cache = {}

@app.get("/checkdomain/{domain_name}")
async def check_domain_availability(domain_name: str):
    if domain_name in cache:
        return cache[domain_name]

    response = requests.get(f'{whoapi}/?apikey={api_key}&domain={domain_name}&r=taken')
    data = response.json()
    cache[domain_name] = data
    return data
