#!/usr/bin/env python3
"""
Analyze AI4Shipwrecks dataset structure and content
"""
import os
from pathlib import Path
import json
import cv2
from collections import defaultdict

def analyze_dataset(raw_dir="data/raw/ai4shipwrecks"):
    raw_path = Path(raw_dir)
    
    print("=" * 60)
    print("📊 AI4Shipwrecks Dataset Analysis")
    print("=" * 60)
    
    # Find all image directories
    image_dirs = []
    for ext in ['*.png', '*.jpg', '*.jpeg']:
        for img_path in raw_path.rglob(ext):
            image_dirs.append(img_path.parent)
    
    image_dirs = list(set(image_dirs))
    print(f"\n📁 Found {len(image_dirs)} image directories:")
    for d in image_dirs:
        count = len(list(d.glob('*.png')) + list(d.glob('*.jpg')))
        print(f"   - {d.relative_to(raw_path)}: {count} images")
    
    # Count total images
    total_images = 0
    for ext in ['*.png', '*.jpg', '*.jpeg']:
        total_images += len(list(raw_path.rglob(ext)))
    
    print(f"\n📸 Total images: {total_images}")
    
    # Check for labels
    label_files = list(raw_path.rglob('*.txt')) + list(raw_path.rglob('*.json'))
    print(f"📝 Label files found: {len(label_files)}")
    
    # Check image sizes
    print("\n📐 Sample image analysis...")
    sample_images = list(raw_path.rglob('*.png'))[:5] + list(raw_path.rglob('*.jpg'))[:5]
    sizes = []
    for img_path in sample_images:
        try:
            img = cv2.imread(str(img_path))
            if img is not None:
                sizes.append(img.shape[:2])
                print(f"   {img_path.name}: {img.shape[1]}x{img.shape[0]}")
        except:
            pass
    
    if sizes:
        avg_height = sum(h for h,w in sizes) // len(sizes)
        avg_width = sum(w for h,w in sizes) // len(sizes)
        print(f"\n📏 Average image size: {avg_width}x{avg_height}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    analyze_dataset()
