from fastapi import FastAPI, Request
from typing import Union
import requests
import os
import time

app = FastAPI()
whoapi = 'https://api.whoapi.com'
api_key = os.environ.get('WHO_APIKEY')
cache = {}

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Get request metadata
    client_host = request.client.host
    request_method = request.method
    request_url = str(request.url)
    request_headers = json.dumps(dict(request.headers))
    request_query_params = json.dumps(dict(request.query_params))

    # Continue processing the request
    response = await call_next(request)

    # Calculate request processing time
    process_time = time.time() - start_time

    # Log the request data
    log_data = {
        "client_host": client_host,
        "request_method": request_method,
        "request_url": request_url,
        "request_headers": request_headers,
        "request_query_params": request_query_params,
        "response_status_code": response.status_code,
        "process_time": process_time
    }
    print(json.dumps(log_data, indent=4))

    return response

@app.get("/checkdomain/{domain_name}")
async def check_domain_availability(domain_name: str):
    if domain_name in cache:
        return cache[domain_name]

    response = requests.get(f'{whoapi}/?apikey={api_key}&domain={domain_name}&r=taken')
    data = response.json()
    cache[domain_name] = data
    return data
