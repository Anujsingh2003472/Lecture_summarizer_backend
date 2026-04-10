from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq
import json
import os
import shutil

app = FastAPI()

# Paste your free Groq key here
client = Groq(api_key="gsk_YOUR_GROQ_KEY_HERE...") 

# Allow frontend to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/process-lecture")
async def process_lecture(file: UploadFile = File(...)):
    # 1. Save the uploaded file temporarily
    temp_file_path = f"temp_{file.filename}"
    with open(temp_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    lecture_text = ""

    try:
        filename_lower = file.filename.lower()
        
        # 2. Transcribe Audio/Video using Groq's Free Whisper Model
        if filename_lower.endswith(('.mp3', '.mp4', '.m4a', '.wav', '.webm')):
            with open(temp_file_path, "rb") as audio_file:
                transcript = client.audio.transcriptions.create(
                  model="whisper-large-v3", 
                  file=(temp_file_path, audio_file.read())
                )
            lecture_text = transcript.text
            
        # 3. Handle standard text files
        elif filename_lower.endswith('.txt'):
            with open(temp_file_path, "r", encoding="utf-8") as f:
                lecture_text = f.read()
                
        else:
            raise HTTPException(status_code=400, detail="Unsupported format. Use .txt, .mp3, or .mp4")

        # 4. Generate Notes using Groq's Free Llama 3 Model
        prompt = f"""
        Analyze this lecture and return strictly valid JSON:
        {{
            "notes": "Comprehensive summary",
            "highlights": ["Point 1", "Point 2"],
            "flashcards": [{{"q": "Question", "a": "Answer"}}],
            "mind_map": "Mermaid.js syntax"
        }}
        Lecture: {lecture_text}
        """

        response = client.chat.completions.create(
            model="llama3-70b-8192",
            response_format={ "type": "json_object" },
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        
        return json.loads(response.choices[0].message.content)

    finally:
        # 5. Clean up the temporary file so the server doesn't crash
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)