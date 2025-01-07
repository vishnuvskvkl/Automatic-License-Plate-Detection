import os
import tempfile
from fastapi import APIRouter, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from app.utils.handler_detection import (
    handle_video_and_cleanup,
    analyze_image_paddle
)
from app.utils.handler_data import (
    get_detected_plates,
    get_filtered_plates,
    search_plate
)

from ..utils.log_config import get_logger

logger = get_logger()
router = APIRouter()


@router.get("/health")
async def check_health():
    """Endpoint to check API health."""
    logger.info("Health check performed")
    return {"status": "healthy"}


@router.get("/process_image")
def process_image_paddle(file: UploadFile = File(...)):
    """Process image using PaddleOCR detection."""
    try:
        image_name = file.filename
        image_data = file.file.read()
        result = analyze_image_paddle(image_data)
        
        logger.info(f"PaddleOCR processing complete: {image_name}")
        return JSONResponse(
            status_code=200,
            content={'status': 'image processing completed'}
        )

    except Exception as e:
        logger.exception(f"Image processing failed: {e}")
        raise HTTPException(status_code=500, detail="Server processing error")



@router.post("/process_video")
async def process_video_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    """Process video file for license plate detection."""
    try:
        video_name = file.filename
        file_ext = os.path.splitext(video_name)[1]
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
            temp_file.write(await file.read())
            video_path = temp_file.name

        background_tasks.add_task(handle_video_and_cleanup, video_path)
        
        logger.info(f"Video processing initiated: {video_name}")
        return JSONResponse(
            status_code=200,
            content={'status': 'video processing initiated'}
        )

    except Exception as e:
        logger.exception(f"Video processing failed: {e}")
        raise HTTPException(status_code=500, detail="Server processing error")
    

@router.get("/get_results")
def fetch_results():
    """Fetch all detected license plates."""
    try:
        detected_plates = get_detected_plates()
        return JSONResponse(status_code=200, content=detected_plates)
    except Exception as e:
        logger.exception(f"Failed to retrieve results: {e}")
        raise HTTPException(status_code=500, detail="Server processing error")
    

@router.get("/filter_results")
def filter_results(start_date: str = None, end_date: str = None, plate_number: str = None):
    """Filter detected license plates based on date range and/or plate number."""
    try:
        filtered_plates = get_filtered_plates(start_date, end_date, plate_number)
        return JSONResponse(status_code=200, content=filtered_plates)
    except Exception as e:
        logger.exception(f"Failed to filter results: {e}")
        raise HTTPException(status_code=500, detail="Server processing error")
    

@router.get("/search_plate")
def search_plate_number(plate_number: str):
    """Search for a specific license plate number."""
    try:
        plate_data = search_plate(plate_number)
        return JSONResponse(status_code=200, content=plate_data)
    except Exception as e:
        logger.exception(f"Failed to search plate: {e}")
        raise HTTPException(status_code=500, detail="Server processing error")
    
