from fastapi import Request, HTTPException
from app.db import get_connection
import json

async def check_idempotency(request: Request):
    key = request.headers.get("Idempotency-Key")
    if not key:
        raise HTTPException(status_code=400, detail="Missing Idempotency-Key")

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT response FROM idempotency_keys WHERE idempotency_key=%s", (key,))
    row = cur.fetchone()

    if row:
        cur.close()
        conn.close()
        return json.loads(row[0])

    request.state.idempotency_key = key
    cur.close()
    conn.close()
    return None
