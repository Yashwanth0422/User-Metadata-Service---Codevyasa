import time
import json

from fastapi import FastAPI, Request, HTTPException, Header, Response
from pydantic import BaseModel
from prometheus_client import Counter, Histogram, generate_latest

from app.service import insert_user, get_user
from app.db import get_connection
from app.idempotency import check_idempotency

app = FastAPI()

# =========================
# Metrics
# =========================
total_requests = Counter("total_requests", "Total API Requests")
success_count = Counter("success_count", "Successful Requests")
failure_count = Counter("failure_count", "Failed Requests")
request_latency = Histogram("request_latency_ms", "Request latency in ms")

# =========================
# User Model (VERY IMPORTANT)
# =========================
class User(BaseModel):
    user_id: str
    name: str
    email: str
    phone: str


# =========================
# POST /user
# =========================
@app.post("/user")
async def create_user(
    user: User,
    request: Request,
    idempotency_key: str = Header(...)
):
    start = time.time()
    total_requests.inc()

    # Check idempotency
    cached = await check_idempotency(request)
    if cached:
        return cached

    data = user.dict()

    try:
        insert_user(data)

        response = {"message": "User created"}

        # Save idempotency response
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO idempotency_keys (idempotency_key, response) VALUES (%s,%s)",
            (idempotency_key, json.dumps(response))
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


# =========================
# GET /user/{user_id}
# =========================
@app.get("/user/{user_id}")
def fetch_user(user_id: str):
    result = get_user(user_id)

    if not result:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "user_id": result[0],
        "name": result[1],
        "email": result[2],
        "phone": result[3],
        "created_at": result[4]
    }


# =========================
# Metrics Endpoint
# =========================
@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type="text/plain")
