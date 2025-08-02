from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import requests
import base64

import os
COLLOV_API_KEY = os.environ.get("COLLOV_API_KEY")


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

COLLOV_API_KEY = "ck_FC2FACD9549312DAB14531DECD71D938"  # Replace if needed
COLLOV_UPLOAD_ENDPOINT = "https://api.collov.com/api/upload"
COLLOV_RESULT_ENDPOINT = "https://api.collov.com/api/render-result"

@app.post("/upload")
async def upload_image(image: UploadFile = File(...)):
    image_bytes = await image.read()
    image_b64 = base64.b64encode(image_bytes).decode()

    headers = {
        "x-api-key": COLLOV_API_KEY,
        "Content-Type": "application/json"
    }

    upload_payload = {
        "image": f"data:{image.content_type};base64,{image_b64}"
    }

    upload_response = requests.post(COLLOV_UPLOAD_ENDPOINT, json=upload_payload, headers=headers)
    upload_data = upload_response.json()
    image_id = upload_data.get("data", {}).get("id")

    if not image_id:
        return JSONResponse(content={"error": "Upload failed."}, status_code=400)

    # Polling result (simplified to 1 request for example)
    render_response = requests.get(f"{COLLOV_RESULT_ENDPOINT}?id={image_id}", headers=headers)
    render_data = render_response.json()
    renders = render_data.get("data", {}).get("renders", [])

    if not renders:
        return JSONResponse(content={"error": "No renders returned."}, status_code=400)

    # Take top 3 renders
    base64_results = []
    for r in renders[:3]:
        staged_image_url = r.get("image")
        if staged_image_url:
            img_res = requests.get(staged_image_url)
            img_b64 = base64.b64encode(img_res.content).decode()
            base64_results.append(f"data:image/jpeg;base64,{img_b64}")

    return {"images": base64_results}
