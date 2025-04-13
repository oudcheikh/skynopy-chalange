import asyncio
import aio_pika
import os
import aiohttp
from typing import AsyncGenerator

async def receive_tm() -> AsyncGenerator[None, None]:
    """
    Asynchronously receives telemetry data from RabbitMQ.
    """
    connection = await aio_pika.connect_robust(os.getenv("AMQP_URL", "amqp://guest:guest@rabbitmq/"))
    channel = await connection.channel()
    queue = await channel.declare_queue("", exclusive=True)
    await queue.bind("tm")
    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            print(f"[TM] Received: {len(message.body)} bytes")
            await message.ack()

async def send_tc(data: bytes = b"CMD: CHECK_STATUS") -> None:
    """
    Asynchronously sends a telecommand to RabbitMQ.
    
    :param data: The data to be sent as a telecommand.
    """
    connection = await aio_pika.connect_robust(os.getenv("AMQP_URL", "amqp://guest:guest@rabbitmq/"))
    channel = await connection.channel()
    await channel.default_exchange.publish(aio_pika.Message(body=data), routing_key="tc")
    print("[TC] Sent telecommand.")

async def get_metrics() -> None:
    """
    Asynchronously retrieves metrics from the modem.
    """
    async with aiohttp.ClientSession() as session:
        while True:
            for endpoint in ["status", "signal_strength", "bit_error_rate", "statistics"]:
                async with session.get(f"http://modem:8000/metrics/{endpoint}") as resp:
                    data = await resp.json()
                    print(f"[METRICS] {endpoint}: {data}")
            await asyncio.sleep(5)

async def main() -> None:
    """
    The main entry point for the client script.
    """
    await asyncio.gather(
        receive_tm(),
        get_metrics(),
        send_tc()
    )

if __name__ == "__main__":
    asyncio.run(main())
