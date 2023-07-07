from aio_pika import connect, Message
from tools.settings import settings

    
async def send_rabbitmq(id: str):
    connection = await connect(f"amqp://{settings.rabbitmq_ak}:{settings.rabbitmq_sk}@{settings.rabbitmq_host}/")

    channel = await connection.channel()
    message = Message(f"{id}".encode("utf-8"),)
    await channel.default_exchange.publish(
        message, routing_key="task_queue",
    )

    await connection.close()
