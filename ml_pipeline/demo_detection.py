import cv2
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))
from app.services.inference_service import InferenceService

print("🚀 NEZA AI Detection Demo")
print("=" * 40)

# Test on a regular image
service = InferenceService()
img = cv2.imread('test_regular.jpg')

if img is not None:
    result = service.process_image(img, {
        "survey_id": "DEMO",
        "latitude": 20.5937,
        "longitude": 78.9629
    })
    
    print(f"\n📊 Detected {result['summary']['total_detections']} objects:")
    for det in result['detections']:
        print(f"  ✅ {det['class']}: {det['confidence']}% confidence")
        print(f"     Priority: {det['priority']}")
        print(f"     Location: ({det['latitude']}, {det['longitude']})")
else:
    print("❌ Image not found. Run: curl -o test_regular.jpg https://ultralytics.com/images/bus.jpg")
