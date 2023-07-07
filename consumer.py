import asyncio
from aio_pika import connect, IncomingMessage
from tools.settings import settings
import json
from tools.s3 import s3, s3_r, add_file, get_file
from tools.db import *
import ffmpeg
import subprocess
import io
import threading


def doNothing(hash: str):
    print(hash)
    if s.query(Message).filter(Message.hash==hash).first():
        s.query(Message).filter(Message.hash==hash).first().status = 2
        s.commit()

def doSomeThing(hash: str, message: IncomingMessage):
    m = s.query(Message).filter(Message.hash==hash).first()
    input_data = get_file("basic", f"{m.id}file")
    s3_r.Object('basic', f"{m.id}file").delete()
    args = (ffmpeg
        .input('pipe:', format=m.from_)
        .output('pipe:', format=m.to_)
        .get_args()
    )
    p = subprocess.Popen(['ffmpeg'] + args, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    out = p.communicate(input=input_data.read())
    output_data = io.BytesIO(out[0])
    output_data.seek(0)
    add_file(output_data, "basic", f"{m.id}file")
    if s.query(Message).filter(Message.hash==hash).first() and p.returncode != 1:
        s.query(Message).filter(Message.hash==hash).first().status = 1
        s.commit()
    elif s.query(Message).filter(Message.hash==hash).first():
        s.query(Message).filter(Message.hash==hash).first().status = 2
        s.commit()
    
    
tasks = [doSomeThing, doNothing]
s = get_s()

async def on_message(message: IncomingMessage):
    txt = message.body
    t = threading.Thread(target=tasks[0], args=(txt.decode("utf-8"), message))
    t.start()
    t.join()
    await message.ack()
    

async def main(loop):
    connection = await connect(f"amqp://{settings.rabbitmq_ak}:{settings.rabbitmq_sk}@{settings.rabbitmq_host}/?heartbeat=0")
    channel = await connection.channel()
    queue = await channel.declare_queue("task_queue")
    await queue.consume(on_message, no_ack=False)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(main(loop))
    loop.run_forever()