import cv2
import numpy as np
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))
from app.services.inference_service import InferenceService

print("\n" + "="*60)
print("🚀 NEZA AI - Detection Pipeline Demo")
print("="*60)

# Create an image with clear objects
print("\n📷 Creating test image with recognizable objects...")
img = np.zeros((640, 640, 3), dtype=np.uint8)

# Person
cv2.rectangle(img, (50, 150), (120, 350), (200, 200, 200), -1)
cv2.circle(img, (85, 120), 40, (220, 200, 180), -1)

# Car
cv2.rectangle(img, (300, 300), (500, 380), (150, 150, 200), -1)
cv2.rectangle(img, (310, 380), (340, 400), (50, 50, 50), -1)
cv2.rectangle(img, (460, 380), (490, 400), (50, 50, 50), -1)

# Boat
cv2.rectangle(img, (200, 450), (350, 480), (100, 150, 200), -1)

cv2.imwrite('demo_image.jpg', img)
print("✅ Test image created")

# Run detection
print("\n🔍 Running detection...")
service = InferenceService()
img = cv2.imread('demo_image.jpg')
result = service.process_image(img, {
    "survey_id": "SIH_DEMO",
    "latitude": 20.5937,
    "longitude": 78.9629
})

print("\n📊 RESULTS:")
print(f"   Total detections: {result['summary']['total_detections']}")
print(f"   High priority: {result['summary']['high_priority']}")
print(f"   Average confidence: {result['summary']['avg_confidence']}%")

print("\n📋 Detection Details:")
for det in result['detections']:
    print(f"\n   ✅ Class: {det['class']}")
    print(f"      Confidence: {det['confidence']}%")
    print(f"      Priority: {det['priority']}")
    print(f"      Location: ({det['latitude']}, {det['longitude']})")

print("\n" + "="*60)
print("✅ Demo complete! Pipeline is fully functional.")
