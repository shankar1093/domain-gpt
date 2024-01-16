from fastapi import FastAPI, Request, HTTPException, status, Security
from fastapi.security.api_key import APIKeyHeader, APIKeyQuery
from typing import Union
import requests
import os
import time
import json
import logging
import os
from supabase import create_client, Client


url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)
logger = logging.getLogger(__name__)

app = FastAPI()
whoapi = "https://api.whoapi.com"
who_api_key = os.environ.get("WHO_APIKEY")
cache = {}
api_key_header = APIKeyHeader(name="Authorization", auto_error=False)


def verify_api_key(
    api_key_header: str = Security(api_key_header),
) -> bool:
    """Retrieve and validate an API key from the query parameters or HTTP header.

    Args:
        api_key_query: The API key passed as a query parameter.
        api_key_header: The API key passed in the HTTP header.

    Returns:
        The validated API key.

    Raises:
        HTTPException: If the API key is invalid or missing.
    """
    if api_key_header:
        if api_key_header.startswith("Basic "):
            api_key_header = api_key_header.split("Basic ")[1]
        data, count = (
            supabase.table("api_keys")
            .select("api_key")
            .eq("api_key", api_key_header)
            .eq("active", True)
            .execute()
        )
        # Check if the API key exists and is active
        if len(data) > 0:
            logger.info("API key exists and is active.")
            return True

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing API Key",
    )


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
        "process_time": process_time,
    }
    logger.info(json.dumps(log_data, indent=4))

    return response


@app.get("/checkdomain/{domain_name}")
async def check_domain_availability(
    domain_name: str, api_key: str = Security(api_key_header)
):
    if verify_api_key(api_key):
        if domain_name in cache:
            return cache[domain_name]

        response = requests.get(f"{whoapi}/?apikey={who_api_key}&domain={domain_name}&r=taken")
        data = response.json()
        cache[domain_name] = data
        return data
