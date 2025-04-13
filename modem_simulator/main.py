import asyncio
import random
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn
from typing import Dict

app = FastAPI()

stats: Dict[str, int] = {"downlink": 0, "uplink": 0}

# ------------------ TELEMETRY SERVER (1234) ------------------

async def tm_handler(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
    """
    Handles telemetry data transmission to the client.
    """
    while True:
        await asyncio.sleep(random.uniform(0.1, 0.5))
        data = bytes([random.randint(0, 255) for _ in range(1024)])
        writer.write(data)
        await writer.drain()
        stats["downlink"] += 1

async def start_tm_server() -> None:
    """
    Starts the telemetry server.
    """
    server = await asyncio.start_server(tm_handler, "0.0.0.0", 1234)
    print("✅ TM Server listening on 1234")
    async with server:
        await server.serve_forever()

# ------------------ TELECOMMAND SERVER (4321) ------------------

async def tc_handler(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
    """
    Handles telecommand data reception from the client.
    """
    while True:
        data = await reader.read(1024)
        if not data:
            break
        print(f"[TC RECEIVED] {len(data)} bytes")
        stats["uplink"] += 1
        writer.write(b"ACK")
        await writer.drain()

async def start_tc_server() -> None:
    """
    Starts the telecommand server.
    """
    server = await asyncio.start_server(tc_handler, "0.0.0.0", 4321)
    print("✅ TC Server listening on 4321")
    async with server:
        await server.serve_forever()

# ------------------ API METRICS ------------------

@app.get("/metrics/status")
async def status() -> JSONResponse:
    """
    Returns the status of the system.
    """
    return JSONResponse({"status": "OK" if random.random() > 0.1 else "ERROR"})

@app.get("/metrics/signal_strength")
async def signal_strength() -> JSONResponse:
    """
    Returns the signal strength.
    """
    return JSONResponse({"signal_strength": random.randint(0, 100)})

@app.get("/metrics/bit_error_rate")
async def bit_error_rate() -> JSONResponse:
    """
    Returns the bit error rate.
    """
    return JSONResponse({"bit_error_rate": round(random.uniform(0, 1), 4)})

@app.get("/metrics/statistics")
async def statistics() -> JSONResponse:
    """
    Returns the system statistics.
    """
    return JSONResponse(stats)

@app.get("/health")
async def health() -> Dict[str, str]:
    """
    Returns the health status of the system.
    """
    return {"status": "ok"}

# ------------------ COMBINED ASYNC ENTRYPOINT ------------------

async def main() -> None:
    """
    Main entrypoint for the application.
    """
    asyncio.create_task(start_tm_server())
    asyncio.create_task(start_tc_server())
    config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    asyncio.run(main())
