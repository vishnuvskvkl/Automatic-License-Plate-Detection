import os
import cv2
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import threading
from ultralytics import YOLO
from ..config import settings
from PIL import Image
import io
from paddleocr import PaddleOCR
import re
from .log_config import get_logger, get_result_logger

log = get_logger()
result_log = get_result_logger()

csv_mutex = threading.Lock()

if not os.path.exists(settings.csv_file):
    with csv_mutex:
        df = pd.DataFrame(columns=['timestamp', 'license_plate', 'image_path'])
        df.to_csv(settings.csv_file, index=False)

images_dir = os.path.join('app','data', 'detected_plates')
os.makedirs(images_dir, exist_ok=True)

try:
    yolo_model = YOLO(settings.yolo_model_path)
    log.info("YOLOv11 model loaded successfully.")
except Exception as e:
    log.error(f"Failed to load YOLO model: {e}")
    raise


try:
    paddle_ocr = PaddleOCR(use_angle_cls=True, lang='en')
    log.info("PaddleOCR reader initialized successfully.")
except Exception as e:
    log.error(f"Failed to initialize PaddleOCR: {e}")
    raise

def handle_video_and_cleanup(video_path: str):
    try:
        log.info(f"Starting video processing for {video_path}")
        handle_video(video_path)
        log.info("Video processing completed.")
    except Exception as e:
        log.error(f"Error during video processing: {e}")
    finally:
        os.unlink(video_path)
        log.info(f"Temporary file {video_path} deleted")


class IndianPlateValidator:
    @staticmethod
    def is_valid_state_code(state_code: str) -> bool:
        valid_states = {
            'AN', 'AP', 'AR', 'AS', 'BR', 'CG', 'CH', 'DD', 'DL', 'DN', 'GA',
            'GJ', 'HP', 'HR', 'JH', 'JK', 'KA', 'KL', 'LA', 'LD', 'MH', 'ML',
            'MN', 'MP', 'MZ', 'NL', 'OD', 'PB', 'PY', 'RJ', 'SK', 'TN', 'TR',
            'TS', 'UK', 'UP', 'WB'
        }
        return state_code in valid_states

    @staticmethod
    def process_license_plate(license_plate: str) -> str:
        plate = license_plate.replace(' ', '').replace('-', '').upper()

        if not (8 <= len(plate) <= 10):
            return None

        state_code = plate[:2]
        if not IndianPlateValidator.is_valid_state_code(state_code):
            return None

        patterns = [
            r'^[A-Z]{2}[0-9]{2}[A-Z]{2}[0-9]{4}$',
            r'^[A-Z]{2}[0-9]{2}[A-Z]{1}[0-9]{4}$',
            r'^[A-Z]{2}[0-9]{2}[0-9]{4}$',
            r'^[A-Z]{2}[0-9]{2}[A-Z]{1}[0-9]{4}$',
            r'^[A-Z]{2}[0-9]{2}[A-Z]{3}[0-9]{4}$'
        ]

        for pattern in patterns:
            if re.match(pattern, plate):
                if len(plate) == 10:
                    return f"{plate[:2]} {plate[2:4]} {plate[4:6]} {plate[6:]}"
                elif len(plate) == 9:
                    return f"{plate[:2]} {plate[2:4]} {plate[4:5]} {plate[5:]}"
                else:
                    return f"{plate[:2]} {plate[2:4]} {plate[4:]}"

        return None
    
def handle_video(video_path: str) -> None:
    video = cv2.VideoCapture(video_path)
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    log.info(f"Total frames in video: {total_frames}")

    try:
        frame_idx = 0
        while video.isOpened():
            ret, frame = video.read()
            if not ret:
                log.info(f"End of video or failed to read frame at frame number {frame_idx}")
                break

            frame_idx += 1
            log.info(f"Processing frame {frame_idx}/{total_frames}")

            results = yolo_model.predict(frame, conf=settings.confidence_threshold, verbose=False)
            detections = results[0]

            if detections.boxes is not None:
                log.info(f"Detected {len(detections.boxes)} objects in the frame.")
                for box in detections.boxes:
                    cls = int(box.cls[0])
                    conf = float(box.conf[0])

                    if cls == 0:
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        plate_img = frame[y1:y2, x1:x2]

                        if plate_img.size == 0:
                            continue

                        gray_plate = cv2.cvtColor(plate_img, cv2.COLOR_BGR2GRAY)
                        result = paddle_ocr.ocr(gray_plate, cls=True)
                        license_plate = ''
                        if result and result[0] is not None:
                            for i in range(len(result[0])):
                                license_plate += result[0][i][1][0] + ' '

                            if license_plate:
                                processed_plate = IndianPlateValidator.process_license_plate(license_plate)
                                
                            if processed_plate:
                                if not is_duplicate(processed_plate):
                                    counter = 0
                                    while True:
                                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
                                        image_filename = f"plate_{timestamp}_{counter}.jpg"
                                        image_path = os.path.join(images_dir, image_filename)
                                        
                                        if not os.path.exists(image_path):
                                            break
                                        counter += 1
                                    cv2.imwrite(image_path, plate_img)
                                    timestamp_iso = datetime.now().isoformat()
                                    result_log.info(f"Detected License Plate: {processed_plate}")

                                    data = pd.DataFrame([[timestamp_iso, processed_plate, image_path]], 
                                                        columns=['timestamp', 'license_plate', 'image_path'])
                                    with csv_mutex:
 
                                        data.to_csv(settings.csv_file, mode='a', header=False, index=False)
 
                                else:
                                    log.info(f"Duplicate license plate detected within 10 seconds: {processed_plate}")
                            else:
                                log.info(f"Detected text does not match Netherlands license plate format: {license_plate}")
    except Exception as e:
        log.exception(f"An error occurred during video processing: {e}")
    finally:
        video.release()
        log.info("Video processing completed.")

def is_duplicate(license_plate: str) -> bool:
    try:
        with csv_mutex:
            if os.path.exists(settings.csv_file):
                df = pd.read_csv(settings.csv_file)
                if not df.empty:
                    df['timestamp'] = pd.to_datetime(df['timestamp'])
                    last_10_seconds = datetime.now() - timedelta(seconds=10)
                    recent_entries = df[(df['timestamp'] > last_10_seconds) & (df['license_plate'] == license_plate)]
                    return not recent_entries.empty
            return False
    except Exception as e:
        log.exception(f"Failed to read CSV file: {e}")
        return False



def analyze_image_paddle(image_bytes: bytes) -> None:
    try:
        image = Image.open(io.BytesIO(image_bytes))
        image = np.array(image)
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        results = yolo_model.predict(image, conf=settings.confidence_threshold, verbose=False)
        detections = results[0]

        if detections.boxes is not None:
            for box in detections.boxes:
                cls = int(box.cls[0])
                conf = float(box.conf[0])

                if cls == 0:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    plate_img = image[y1:y2, x1:x2]

                    if plate_img.size == 0:
                        continue

                    gray_plate = cv2.cvtColor(plate_img, cv2.COLOR_BGR2GRAY)
                    result = paddle_ocr.ocr(gray_plate, cls=True)
                    license_plate = ''
                    if result and result[0] is not None:
                        for i in range(len(result[0])):
                            license_plate += result[0][i][1][0] + ' '

                        if license_plate:
                            processed_plate = IndianPlateValidator.process_license_plate(license_plate.strip())

                        if processed_plate:
                            if not is_duplicate(processed_plate):
                                counter = 0
                                while True:
                                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
                                    image_filename = f"plate_{timestamp}_{counter}.jpg"
                                    image_path = os.path.join(images_dir, image_filename)
                                    
                                    if not os.path.exists(image_path):
                                        break
                                    counter += 1
                                cv2.imwrite(image_path, image)
                                
                                timestamp_iso = datetime.now().isoformat()
                                result_log.info(f"Detected License Plate: {processed_plate}")

                                data = pd.DataFrame([[timestamp_iso, processed_plate, image_path]], 
                                                columns=['timestamp', 'license_plate', 'image_path'])
                                with csv_mutex:
                                    data.to_csv(settings.csv_file, mode='a', header=False, index=False)

                            else:
                                log.info(f"Duplicate license plate detected within 10 seconds: {processed_plate}")
                        else:
                            log.info(f"Detected text does not match Netherlands license plate format: {license_plate}")
    except Exception as e:
        log.exception(f"An error occurred during image processing: {e}")
        raise Exception("Failed to process image")

