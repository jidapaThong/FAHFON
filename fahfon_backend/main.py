from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
import crud.handysense as handysense
import crud.fahfon as fahfon

app = FastAPI(title="REST API")
app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
)
@app.get("/")
def root():
    return {"message": "unused route"}

@app.get("/fahfon/latest")
def getLatest():
    return fahfon.getLastest()

@app.get("/fahfon/update-active")
def getLatest():
    return fahfon.updateActive()

@app.get("/fahfon/insert")
def insertData():
    return fahfon.insertData()

@app.get("/fahfon/download/{serial}")
def downloadData(serial):
    csv_file = fahfon.downloadData(serial)
    headers = {
        "Content-Disposition": f"attachment; filename={serial}.csv",
        "Content-Type": "text/csv",
    }
    return Response(content = csv_file, headers = headers)

@app.get("/fahfon/graph/{serial}")
def getGraph(serial):
    return fahfon.getGraph(serial)

@app.get("/handysense/id")
def queryDeviceIDs():
    return handysense.queryDeviceIDs()

@app.get("/handysense/download/{deviceID}")
def download(deviceID):
    headers = {
        "Content-Disposition": f"attachment; filename=device_{deviceID}.csv",
        "Content-Type": "text/csv",
    }
    contents = handysense.download(deviceID)
    return Response(content = contents, headers = headers)