from models import OpenAIModel
from moviepy.editor import VideoFileClip, AudioFileClip
from elevenlabs import client, save
from twelvelabs import TwelveLabs
import asyncio
import os
import uuid
import json
from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from google.cloud import storage
from google.oauth2 import service_account
from pydantic import BaseModel
from datetime import datetime, timedelta
from dotenv import load_dotenv
load_dotenv()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Environment variables (make sure to set these)
TWELVELABS_API_KEY = os.getenv("TWELVE_LABS_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVEN_LABS_API_KEY")
STORAGE_KEY_FILE = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
GCS_BUCKET_NAME = "naturrate_data_bucket"

# Initialize clients
credentials = service_account.Credentials.from_service_account_file(
    STORAGE_KEY_FILE)
storage_client = storage.Client(credentials=credentials)
twelvelabs_client = TwelveLabs(api_key=TWELVELABS_API_KEY)
elevenlabs_client = client.ElevenLabs(api_key=ELEVENLABS_API_KEY)

# In-memory store for processing status (in a real app, use a database)
video_status = {}

# Models


class VideoResult(BaseModel):
    video_url: str
    chapter_text: str
    narration_script: str


class StatusUpdate(BaseModel):
    status: str
    message: str


# Helper functions


def update_status(video_id: str, message: str, **kwargs):
    status_update = StatusUpdate(
        status="processing", message=message).model_dump()
    status_update.update(kwargs)
    video_status[video_id] = status_update


def on_task_update(task):
    print(f"  Status={task.status}")


def generate_unique_id():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    return f"{timestamp}_{unique_id}"


async def process_video(video_id: str, file_path: str, index_id="66b90051ab9e0130df471775"):
    try:
        # Step 1: Upload video to TwelveLabs index
        update_status(video_id, "Uploading video to index")
        task = twelvelabs_client.task.create(
            index_id=index_id,
            file=file_path
        )
        task.wait_for_done(sleep_interval=5, callback=on_task_update)
        if task.status != "ready":
            raise RuntimeError(f"Indexing failed with status {task.status}")

        # Step 2: Generate chapters
        update_status(video_id, "Generating chapters")
        chapters = twelvelabs_client.generate.summarize(
            video_id=task.video_id,
            type="chapter"
        )
        chapters_text = "\n".join([
            f"Chapter {c.chapter_number}\n"
            f"Start: {c.start:.1f} seconds\n"
            f"End: {c.end:.1f} seconds\n"
            f"Title: {c.chapter_title}\n"
            f"Summary: {c.chapter_summary}"
            for c in chapters.chapters
        ])

        # Step 3: Generate narration script
        update_status(video_id, "Creating narration script")
        openai_model = OpenAIModel(api_key=OPENAI_API_KEY)
        narration_script = openai_model.generate_narration(chapters_text)

        # Store chapters_text and narration_script
        update_status(video_id, "Processing",
                      chapters_text=chapters_text,
                      narration_script=narration_script)

        # Step 4: Generate audio
        update_status(video_id, "Generating audio")
        audio = elevenlabs_client.generate(
            text=narration_script,
            voice="pvb9AjTFewcRSOPkd8pt",
            model="eleven_multilingual_v2"
        )
        audio_file_path = f"/tmp/{video_id}_narration.mp3"
        save(audio, audio_file_path)

        # Step 5: Combine video and audio
        update_status(video_id, "Creating final video")
        final_video_path = f"/tmp/{video_id}_final.mp4"

        # Load the video file
        video = VideoFileClip(file_path)

        # Load the saved audio file
        audio = AudioFileClip(audio_file_path)

        # Clip the audio to match the duration of the video
        if audio.duration > video.duration:
            audio = audio.subclip(0, video.duration)

        # Set the audio to the video
        video_with_audio = video.set_audio(audio)

        # Export the final video with the new audio
        video_with_audio.write_videofile(
            final_video_path, codec="libx264", audio_codec="aac")

        # Clean up
        audio.close()
        video.close()

        # Step 6: Upload to Google Cloud Storage
        update_status(video_id, "Uploading to Google Cloud Storage")
        bucket = storage_client.bucket(GCS_BUCKET_NAME)
        blob = bucket.blob(f"{video_id}.mp4")
        blob.upload_from_filename(final_video_path)

        # Clean up temporary files
        os.remove(file_path)
        os.remove(audio_file_path)
        os.remove(final_video_path)

        # Update final status
        update_status(video_id, "Processing completed",
                      status="completed",
                      chapters_text=chapters_text,
                      narration_script=narration_script)

    except Exception as e:
        error_message = str(e)
        print(f"Error processing video: {error_message}")
        update_status(video_id, error_message, status="error")


@app.post("/upload_video")
async def upload_video(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    unique_id = generate_unique_id()

    # Remove the file extension from the filename and add the unique ID
    base_filename = os.path.splitext(file.filename)[0]
    video_id = f"video_{base_filename}_{unique_id}"

    file_path = f"/tmp/{video_id}"
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())
    background_tasks.add_task(process_video, video_id, file_path)
    return JSONResponse({"video_id": video_id, "message": "Video upload started"})


@app.get("/video_status/{video_id}")
async def video_status_stream(video_id: str):
    async def event_generator():
        while True:
            if video_id in video_status:
                status = video_status[video_id]
                yield f"data: {json.dumps(status)}\n\n"
                if status['status'] in ["completed", "error"]:
                    break
            await asyncio.sleep(1)

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.get("/get_video_result/{video_id}", response_model=VideoResult)
async def get_video_result(video_id: str):
    if video_id not in video_status:
        raise HTTPException(status_code=404, detail="Video not found")

    status = video_status[video_id]
    if status["status"] != "completed":
        raise HTTPException(
            status_code=400, detail="Video processing not completed")

    bucket = storage_client.bucket(GCS_BUCKET_NAME)
    blob = bucket.blob(f"{video_id}.mp4")

    # Generate a signed URL that's valid for 1 hour
    url = blob.generate_signed_url(
        version="v4",
        expiration=timedelta(hours=1),
        method="GET"
    )

    return VideoResult(
        video_url=url,
        chapter_text=status.get("chapters_text", ""),
        narration_script=status.get("narration_script", "")
    )

# Run the FastAPI app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
