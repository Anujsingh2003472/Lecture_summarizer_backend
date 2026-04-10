from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import json
from openai import OpenAI

app = FastAPI()
client = OpenAI(api_key="YOUR_API_KEY") # Replace with your key

# Allow your frontend to talk to your backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/process-lecture")
async def process_lecture(file: UploadFile = File(...)):
    # 1. Read the uploaded text file
    content = await file.read()
    lecture_text = content.decode("utf-8")
    
    # 2. The AI Prompt (from our MVP)
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

    # 3. Call the AI
    response = client.chat.completions.create(
        model="gpt-4o",
        response_format={ "type": "json_object" },
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    
    # 4. Return the JSON to the frontend
    return json.loads(response.choices[0].message.content)

# Run this server by typing `uvicorn main:app --reload` in your terminal.