# Automatic License Plate Detection for Indian Registered Vehicles

This project is a complete solution for detecting and managing license plates of Indian vehicles. It uses a fine-tuned YOLOv11 model to identify license plates in images, validate their format, and store them in a CSV file. The system is designed to be intuitive and scalable, with a FastAPI backend for seamless integration and deployment.

## Key Features

### 1. License Plate Detection
The fine-tuned YOLOv11 model offers high accuracy in detecting license plates, even in complex scenarios like low light or partially obscured views.

### 2. Format Validation
Built-in validation logic ensures the detected license plates match the standard Indian vehicle registration format, preventing incorrect entries.

### 3. Data Storage
All valid license plates are stored in a CSV file (`detected_plates.csv`), making it easy to track and analyze results.

### 4. FastAPI-Powered API
A RESTful API allows users to upload images and receive detection results instantly. This API can be easily integrated with other applications or systems.


## Prerequisites

Make sure you have the following installed before running the project:

- **Python 3.8+**: Required for compatibility with the dependencies.
- **FastAPI**: Backend framework for creating APIs.
- **YOLOv11 Model Weights**: Pre-trained weights specific to license plate detection.
- **OpenCV**: For image manipulation and preprocessing.
- **PyTorch**: The deep learning library used by YOLOv11.
- **Uvicorn**: An ASGI server to run the FastAPI app.

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/vishnuvskvkl/Automatic-License-Plate-Detection.git
   cd automatic-license-plate-detection
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Place the YOLOv11 model weights in the `models/` directory (create this directory if it doesn’t exist).

## Usage

### Running the API

1. Start the FastAPI server:
   ```bash
   uvicorn main.app:app --reload
   ```

2. Open the API documentation in your browser at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

### API Endpoints

#### 1. Health Check

- **GET /health**
  - **Description**: Check the health of the API.
  - **Response**: `{"status": "healthy"}`

#### 2. Process Image

- **GET /process\_image**
  - **Description**: Process an image using PaddleOCR for license plate detection.
  - **Input**: Upload an image.
  - **Response**: `{ "status": "image processing completed" }`

#### 3. Process Video

- **POST /process\_video**
  - **Description**: Upload a video for license plate detection (processed in the background).
  - **Response**: `{ "status": "video processing initiated" }`

#### 4. Fetch All Results

- **GET /get\_results**
  - **Description**: Retrieve all detected license plates.
  - **Response**: List of all detected license plates in JSON format.

#### 5. Filter Results

- **GET /filter\_results**
  - **Description**: Filter license plates by date range and/or plate number.
  - **Parameters**:
    - `start_date` (optional): Start date for filtering.
    - `end_date` (optional): End date for filtering.
    - `plate_number` (optional): License plate number to filter by.
  - **Response**: Filtered results in JSON format.

#### 6. Search Plate Number

- **GET /search\_plate**
  - **Description**: Search for a specific license plate number.
  - **Parameter**: `plate_number` (required).
  - **Response**: Details of the searched license plate.




## Sample Images and Video

### Detected License Plates
Below is an example of a license plate and its corresponding Detection:

![Sample Image](sample_data/data/k.jpg) ![](sample_data/result/k.jpg)

### Video Demonstration

<video controls src="https://github.com/vishnuvskvkl/Automatic-License-Plate-Detection/blob/06cad32af737a1bc6ff80987a894f1389fd1a293/sample_data/result/new_sample.mp4" title="https://github.com/vishnuvskvkl/Automatic-License-Plate-Detection/blob/06cad32af737a1bc6ff80987a894f1389fd1a293/sample_data/result/new_sample.mp4"></video>

## Project Structure

```
.
├── app
│   ├── data                # Data-related operations
│   ├── routes              # API routes for detection
│   │   ├── __init__.py
│   │   └── detection_route.py
│   ├── utils               # Utility functions and configurations
│   │   ├── __init__.py
│   │   ├── handler_data.py # Data processing utilities
│   │   ├── handler_detection.py # Detection logic
│   │   ├── log_config.py   # Logging configuration
│   │   └── config.py       # Configuration settings
│   └── main.py             # FastAPI application entry point
├── sample_data             # Directory containing sample images
├── Dockerfile              # Docker container setup
├── LICENSE                 # License information
├── pyproject.toml          # Project metadata and dependencies
├── requirements.txt        # Python dependencies
└── README.md               # Project documentation
```

## Future Enhancements

- **Database Integration**: Migrate CSV storage to a scalable database for larger applications.
- **Cloud Deployment**: Deploy on cloud platforms like AWS or Azure for improved scalability.

## License

This project is licensed under the MIT License. See the LICENSE file for details.



