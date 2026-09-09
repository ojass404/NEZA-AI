import sys
import cv2
from pathlib import Path

# Add backend to Python path
backend_path = Path(__file__).parent.parent / 'backend'
sys.path.insert(0, str(backend_path))

from app.services.inference_service import InferenceService

# Find images in the AI4Shipwrecks folder
image_dir = Path("/Users/ojasmahajan/Public/Projects/NEZA-AI/ml_pipeline/data/raw/ai4shipwrecks/_data/AI4Shipwrecks/extras/terrain/images")

print(f"📁 Looking for images in: {image_dir}")

# Try to find images
images = list(image_dir.glob("*.png"))

if images:
    print(f"📊 Found {len(images)} images")
    # Use the first image
    image_path = str(images[1])  # Changed to 1.png
    print(f"📷 Loading: {image_path}")
    image = cv2.imread(image_path)
    
    if image is not None:
        print("✅ Image loaded successfully")
        
        # Create service and process
        service = InferenceService()
        result = service.process_image(image, {
            "survey_id": "TEST_SURVEY",
            "latitude": 20.5937,
            "longitude": 78.9629
        })
        
        print(f"\n📊 Found {result['summary']['total_detections']} detections")
        for det in result['detections']:
            print(f"  - {det['class']}: {det['confidence']}% ({det['priority']})")
    else:
        print("❌ Failed to load image")
else:
    print("❌ No images found. Looking in specific paths...")
    
    # Try specific image paths
    possible_paths = [
        "/Users/ojasmahajan/Public/Projects/NEZA-AI/ml_pipeline/data/raw/ai4shipwrecks/_data/AI4Shipwrecks/extras/terrain/images/1.png",
        "/Users/ojasmahajan/Public/Projects/NEZA-AI/ml_pipeline/data/raw/ai4shipwrecks/_data/AI4Shipwrecks/extras/terrain/images/2.png",
    ]
    
    for path in possible_paths:
        img = cv2.imread(path)
        if img is not None:
            print(f"✅ Found image at: {path}")
            service = InferenceService()
            result = service.process_image(img, {
                "survey_id": "TEST_SURVEY",
                "latitude": 20.5937,
                "longitude": 78.9629
            })
            print(f"\n📊 Found {result['summary']['total_detections']} detections")
            for det in result['detections']:
                print(f"  - {det['class']}: {det['confidence']}% ({det['priority']})")
            break
