from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request
import os
import aiofiles
from src.agent.chart_agent import ChartAgent
from src.utils.file_handler import FileHandler
from typing import Dict, Any

class AppState:
    def __init__(self):
        self.current_file_data = None

class ChartAPI:
    def __init__(self):
        self.state = AppState()
        self.chart_agent = ChartAgent()
        self.file_handler = FileHandler()

    async def save_upload_file(self, file: UploadFile) -> str:
        """Save uploaded file and return the file path"""
        os.makedirs("uploads", exist_ok=True)
        file_path = f"uploads/{file.filename}"
        
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        return file_path

    def get_data_preview(self, data: Any) -> Dict:
        """Generate preview of the data"""
        return data.to_dict() if hasattr(data, 'to_dict') else data

    async def process_file_upload(self, file: UploadFile) -> Dict:
        """Handle file upload process"""
        try:
            
            print("Processing file upload...")
            file_path = await self.save_upload_file(file)
            self.state.current_file_data = self.file_handler.load_file(file_path)
            print(self.state.current_file_data)
            preview = self.get_data_preview(self.state.current_file_data)
            print(preview)
            return {
                "status": "success",
                "filename": file.filename,
                "preview": preview
            }
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def process_chart_command(self, command: str) -> Dict:
        """Handle chart generation command"""
        try:
            if self.state.current_file_data is None:
                raise HTTPException(status_code=400, detail="No file uploaded")
            response = await self.chart_agent.process_command(self.state.current_file_data, command)
            chart_config = response.get("chart_config")
            candidate_questions = response.get("candidate_questions")
            output_path = self.file_handler.save_chart(chart_config)
            return {
                "status": "success",
                "chart_path": f"/output/chart.html",
                "config": chart_config,
                "candidate_questions": candidate_questions,
                "output_path": output_path
            }
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def update_existing_chart(self, command: str) -> Dict:
        """Handle chart update command"""
        try:
            print("Updating chart...")
            updated_config = await self.chart_agent.update_chart(command)
            output_path = self.file_handler.save_chart(updated_config)
            print(updated_config)
            return {
                "status": "success",
                "chart_path": f"/output/chart.html",
                "config": updated_config,
                "output_path": output_path
            }
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

# Initialize FastAPI app
app = FastAPI(title="ChatSlide.ai")
api = ChartAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/output", StaticFiles(directory="output"), name="output")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Render home page"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Handle file upload endpoint"""
    return await api.process_file_upload(file)

@app.post("/process")
async def process_command(command: str = Form(...)):
    """Handle chart generation endpoint"""
    return await api.process_chart_command(command)

@app.post("/update")
async def update_chart(command: str = Form(...)):
    """Handle chart update endpoint"""
    return await api.update_existing_chart(command) 