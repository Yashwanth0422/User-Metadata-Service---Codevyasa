from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import Response
from prometheus_client import generate_latest
import time
import json

from app.service import insert_user, get_user
from app.metrics import total_requests, success_count, failure_count, request_latency
from app.idempotency import check_idempotency
from app.db import get_connection

app = FastAPI()

@app.post("/user")
async def create_user(request: Request):
    start = time.time()
    total_requests.inc()

    cached = await check_idempotency(request)
    if cached:
        return cached

    data = await request.json()

    try:
        insert_user(data)

        response = {"message": "User created"}

        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO idempotency_keys (idempotency_key,response) VALUES (%s,%s)",
            (request.state.idempotency_key, json.dumps(response))
        )
        conn.commit()
        cur.close()
        conn.close()

        success_count.inc()
        return response

    except Exception as e:
        failure_count.inc()
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        request_latency.observe((time.time() - start) * 1000)


@app.get("/user/{user_id}")
def fetch_user(user_id: str):
    result = get_user(user_id)
    if not result:
        raise HTTPException(status_code=404, detail="User not found")
    return result


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type="text/plain")
