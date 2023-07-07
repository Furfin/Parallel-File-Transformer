from fastapi import FastAPI, Body, File, UploadFile, Response, Request
from fastapi.responses import FileResponse, StreamingResponse

from tools.db import init_db, get_s, Message
from tools.s3 import init_buckets, add_file, s3, s3_r, get_file, get_bytes
from tools.mbrocker import send_rabbitmq
import mimetypes
import datetime



#uvicorn main:app --reload
app = FastAPI()
mimetypes.init()


init_db()
s = get_s()
init_buckets()

@app.post("/upload")
async def upload(request: Request, response: Response, file: UploadFile = File(...), output_type: str = None):
    if request.cookies.get('session'):
        if not s.query(Message).filter(Message.hash==request.cookies.get('session')).first():
            response.delete_cookie(key="session")
        else:
            return {"message": f"Already uploaded {s.query(Message).filter(Message.hash==request.cookies.get('session')).first().filename}"}
    try:
        if "." in file.filename and f"{list(file.filename.split(sep='.'))[0]}" != "":
            file_type = f"{list(file.filename.split(sep='.'))[1]}"
        else:
            file_type = "txt"
        m = Message(
                    filename=file.filename,
                    from_ = file_type,
                    to_ = file_type)
        m.hash = str(hash(str(datetime.datetime.now())+f"{m.id}file"))
        if output_type:
            m.to_ = output_type
        s.add(m)
        s.commit()
        add_file(file.file, "basic", f"{m.id}file")
        await send_rabbitmq(m.hash)
        response.set_cookie(key="session", value=m.hash)
    except:
        return {"message": f"Error uploading {file.filename}, try again"}
    return {"message": f"Successfully uploaded {file.filename}"}


@app.get("/")
async def get_result(request: Request, response: Response):
    if request.cookies.get('session') and s.query(Message).filter(Message.hash==request.cookies.get('session')).first():
        if s.query(Message).filter(Message.hash==request.cookies.get('session')).first().status == 0:
            return {"message": "File is not ready"}
        elif s.query(Message).filter(Message.hash==request.cookies.get('session')).first().status == 2:
            return {"message": "Something went wrong, reapload file or change output format"}
        elif s.query(Message).filter(Message.hash==request.cookies.get('session')).first().status == 1:
            headers = {
                'Content-Disposition': f'attachment; filename="file.{s.query(Message).filter(Message.hash==request.cookies.get("session")).first().to_}"'
            }
            return StreamingResponse(get_file("basic",
                                    f"{s.query(Message).filter(Message.hash==request.cookies.get('session')).first().id}file"), headers=headers)
    else:
        response.status_code=200
        return {"message": "Session is empty"}


@app.get("/abandon")
async def abandon(request: Request, response: Response):
    if request.cookies.get('session'):
        hash = request.cookies.get('session')
        if s.query(Message).filter(Message.hash==hash).first():
            s3_r.Object('basic', f'{s.query(Message).filter(Message.hash==hash).first().id}file').delete()
            s.query(Message).filter(Message.hash==hash).delete()
            s.commit()
        response.delete_cookie(key="session")
        return {"message": "Deleted session"}
    else:
        return {"message": "Session is empty, upload file"}