import asyncio
import aio_pika
import os

async def forward_tm():
    connection = await aio_pika.connect_robust(os.getenv("AMQP_URL", "amqp://guest:guest@rabbitmq/"))
    channel = await connection.channel()
    exchange = await channel.declare_exchange("tm", aio_pika.ExchangeType.FANOUT)
    reader, _ = await asyncio.open_connection("modem", 1234)
    while True:
        data = await reader.read(1024)
        await exchange.publish(aio_pika.Message(body=data), routing_key="")

async def forward_tc():
    connection = await aio_pika.connect_robust(os.getenv("AMQP_URL", "amqp://guest:guest@rabbitmq/"))
    channel = await connection.channel()
    queue = await channel.declare_queue("tc")
    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            reader, writer = await asyncio.open_connection("modem", 4321)
            writer.write(message.body)
            await writer.drain()
            ack = await reader.read(1024)
            print(f"[ACK] {ack}")
            await message.ack()
            writer.close()
            await writer.wait_closed()

async def main():
    await asyncio.gather(forward_tm(), forward_tc())

if __name__ == "__main__":
    asyncio.run(main())
