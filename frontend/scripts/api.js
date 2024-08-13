const API_BASE_URL = "https://naturrate-2-latest.onrender.com";

// Upload the video to the backend
async function uploadVideo(file) {
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch(`${API_BASE_URL}/upload_video`, {
        method: "POST",
        body: formData
    });

    if (!response.ok) {
        throw new Error("Failed to upload video");
    }

    return await response.json();
}

// Get the final video result from the backend
async function getVideoResult(videoId) {
    const response = await fetch(`${API_BASE_URL}/get_video_result/${videoId}`);

    if (!response.ok) {
        throw new Error("Failed to retrieve video result");
    }

    return await response.json();
}
