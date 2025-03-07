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

#client = InfluxDBClient3(token="12c_EoEt4Fg8XW8_waPFKGRu-9znO9L36ysO4vrwD7Phz4GubMsdTVfYJAGFoVrp9PAS-MWwDjbE1XvWn0xc4A==",
#                         host="http://10.0.1.162",
#                         org="OSM",
#                         database="infra_metrics",
#                         write_port_overwrite=8086)


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
        
    

@app.get("/run_checks")
async def root():
    result = run_checks()
    body = ""
    for i in result.items():
        if i[1][1] == "200":
            bgcolor="green"
        else:
            bgcolor="red"
            
        body += f"<tr><td>{i[0]}</td><td>{i[1][0]}</td><td style='background-color: {bgcolor};'>{i[1][1]}</td></tr>"
    return HTMLResponse(head + body + footer)


def run_checks():
    # if the list item only has 2 values it'll be treated as a get request
    # otherwise it will treat the other options as headers and data for 
    # a post request. The headers *must* be valid json to convert to a dict for requests.post()
    hosts = [
        ['http://osmart.osmworldwide.us/OSMServices/TrackingRESTService.svc/Tracking',"Tracking API"],
        ['https://domrate.osmworldwide.us/API/PackageEstimate', 'Package Estimate', '{"ClientId": "1042", "APIKey": "3550445c-590d-3e23", "RatingKey": "mJamE8fFbZttv9Mj"}', "PENvbnRleHQ+PFJlcXVlc3RUeXBlPjA8L1JlcXVlc3RUeXBlPjxDb3N0Q2VudGVySWQ+MDwvQ29zdENlbnRlcklkPjxQYWNrYWdlcz48UGFja2FnZT48UGtnTnVtYmVyPjE8L1BrZ051bWJlcj48U2VydmljZUxldmVsPjE8L1NlcnZpY2VMZXZlbD48TWFpbENsYXNzPjE8L01haWxDbGFzcz48T3JpZ2luWmlwPjYwMDE4PC9PcmlnaW5aaXA+PERlc3RpbmF0aW9uWmlwPjkwMjEwPC9EZXN0aW5hdGlvblppcD48V2VpZ2h0TGJzPjAuNzU8L1dlaWdodExicz48TGVuZ3RoPjEuMzwvTGVuZ3RoPjxXaWR0aD40PC9XaWR0aD48SGVpZ2h0PjIuNTwvSGVpZ2h0PjxSZWZlcmVuY2UxPk15Rmlyc3RQa2c8L1JlZmVyZW5jZTE+PC9QYWNrYWdlPjxQYWNrYWdlPjxQa2dOdW1iZXI+MjwvUGtnTnVtYmVyPjxTZXJ2aWNlTGV2ZWw+MTwvU2VydmljZUxldmVsPjxNYWlsQ2xhc3M+MTwvTWFpbENsYXNzPjxPcmlnaW5aaXA+NjA1MDM8L09yaWdpblppcD48RGVzdGluYXRpb25aaXA+MzA0MDY8L0Rlc3RpbmF0aW9uWmlwPjxXZWlnaHRMYnM+NC4yPC9XZWlnaHRMYnM+PExlbmd0aD4xLjM8L0xlbmd0aD48V2lkdGg+NDwvV2lkdGg+PEhlaWdodD4yLjU8L0hlaWdodD48UmVmZXJlbmNlMT5NeVNlY29uZFBrZzwvUmVmZXJlbmNlMT48L1BhY2thZ2U+PC9QYWNrYWdlcz48L0NvbnRleHQ+"]
    ]

    check_results = {}

    for h in hosts:
        print(h.__len__())
        if h.__len__() > 2:
            print(h[2])
            hd = json.loads(h[2])
            check = requests.post(f"{h[0]}", data=h[3], headers=hd, timeout=5)
            check_results[h[1]] = [f"{h[0]}",f"{check.status_code}"]
        else:
            check = requests.get(f"{h[0]}", timeout=5)
            check_results[h[1]] = [f"{h[0]}",f"{check.status_code}"]
        
    return check_results



app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=4000, log_level=20)