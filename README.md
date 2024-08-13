# 🐎 Naturrate (pronounced nay-chu-rate)

**Naturrate** is a web application that gives your video a David Attenborough-style commentary. It uses Twelve Labs' Pegasus-1 model to analyze and summarize your video content into timestamp based chapters, then OpenAI's GPT-4 model formats that summary into a narrative script. Then the Eleven Labs' voice model API is called to give a voice to the script. The application allows you to upload a video, processes it, and then displays the final result for you to download.

## Features

- **Upload Video**: Users can upload a video file (up to 5MB).
- **Video Processing**: The backend processes the video to generate chapters text and a narration script using Twelve Labs' Pegasus-1 model, OpenAI's GPT-4 model and Eleven Lab's voice clone API.
- **Final Output**: The processed video is displayed with the generated narration, and the chapters and narration text are shown below the processed video.

## Project Structure

frontend/: Contains the HTML, CSS, and JavaScript files for the frontend.
backend/: Contains the Python backend files (not required for frontend deployment).

## Technologies Used

Frontend
- HTML/CSS: Structure and styling of the web interface.
- JavaScript: Handles the video upload, interaction with the backend, and displaying the results.
- Vercel: Used for deploying the frontend.

Backend
- FastAPI: Python framework used for creating the backend API.
- Twelve Labs Pegasus-1: AI model used for video content summarization.
- OpenAI: Used to format the Pegasus-1 model output as a narration script.
- ElevenLabs API: Converts the generated narration script into speech.
- Google Cloud Storage: Used for storing the processed video files.

## Usage
- Upload Video: Go to the homepage and click "Choose File" to select a video file (up to 5MB), then click "Upload Video."
- Processing: The video will be processed, which will take a few minutes. 
- View Results: Once processing is complete, the video will be displayed along with the generated narration and chapters text.

## Challenges Faced

Initially, I tried to do everything with the Pegasus-1 model i.e. summarize and format the content like a narration but that wasn't effective. While the model is excellent at summarizing video content accurately, using GPT-4 to format the summary to be in a narration format helped a lot.

## License
- This project is open-source and available under the MIT License.