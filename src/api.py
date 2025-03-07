import requests
import uvicorn
import os
from io import BytesIO
from fastapi import FastAPI, Body
from starlette.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse, StreamingResponse
from static import *
import json
from pydantic import BaseModel
import crypt
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import tempfile, zipfile

app = FastAPI()
origins = ['*']
download_queue = []
#db = DB()
    
@app.get("/generate_hash")
async def gen_hash():
    return HTMLResponse(hash_page)

@app.post("/generate_hash_post")
async def gen_hash_post(hash: str=Body()):
    h = (json.loads(hash)["hash"])
    if hash != "":
        data = {'hash':crypt.crypt(h, crypt.mksalt(crypt.METHOD_SHA512))}
        return JSONResponse(data)
    else:
        return HTMLResponse(hash)
    

@app.get("/generate_keys")
async def gen_keys():
    private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048
    )
    
    pem_public_key = private_key.public_key().public_bytes(
    encoding=serialization.Encoding.OpenSSH,
    format=serialization.PublicFormat.OpenSSH
    )
    
    prv_file = BytesIO(private_key.private_bytes(encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.OpenSSH, encryption_algorithm=serialization.NoEncryption()))
    pub_file = BytesIO(pem_public_key)
    
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
        for file_name, data in [('id_rsa', prv_file), ('id_rsa.pub', pub_file)]:
            zip_file.writestr(file_name, data.getvalue())

    zip_buffer.seek(0)
    
    return StreamingResponse(zip_buffer, media_type="application/zip",
    headers={'Content-Disposition': 'inline; filename="ssh_keys.zip"'})
        



app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=4000, log_level=20)