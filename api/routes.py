from fastapi import FastAPI, HTTPException
from app.core.generators import script_generator, video_generator

app = FastAPI()

@app.post("/generate-video")
async def generate_video(request: VideoRequest):
    try:
        script = script_generator.generate_script(request.topic)
        # Add implementation
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, str(e))
