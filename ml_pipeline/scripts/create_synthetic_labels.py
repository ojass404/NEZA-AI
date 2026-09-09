#!/usr/bin/env python3
"""
Create synthetic labels for AI4Shipwrecks dataset
"""
import os
import random
import shutil
from pathlib import Path
from tqdm import tqdm

def create_synthetic_labels():
    print("🚀 Creating synthetic labels for AI4Shipwrecks...")
    
    # Find all images
    raw_path = Path("data/raw/ai4shipwrecks/_data/AI4Shipwrecks")
    image_paths = []
    
    # Find all image directories
    for ext in ['*.png', '*.jpg', '*.jpeg']:
        image_paths.extend(raw_path.rglob(ext))
    
    print(f"📸 Found {len(image_paths)} images")
    
    if len(image_paths) == 0:
        print("❌ No images found! Check the path.")
        return
    
    # Create output directory
    output_dir = Path("data/processed/ai4shipwrecks_synthetic")
    for split in ['train', 'val']:
        (output_dir / split / 'images').mkdir(parents=True, exist_ok=True)
        (output_dir / split / 'labels').mkdir(parents=True, exist_ok=True)
    
    # Split into train/val (80/20)
    random.seed(42)
    random.shuffle(image_paths)
    split_idx = int(len(image_paths) * 0.8)
    train_paths = image_paths[:split_idx]
    val_paths = image_paths[split_idx:]
    
    print(f"📊 Train: {len(train_paths)}, Val: {len(val_paths)}")
    
    # Process training images
    print("📝 Creating training labels...")
    for img_path in tqdm(train_paths):
        # Copy image
        dest = output_dir / 'train' / 'images' / img_path.name
        shutil.copy2(img_path, dest)
        
        # Create YOLO label (class 0: shipwreck, at center)
        label_path = output_dir / 'train' / 'labels' / f"{img_path.stem}.txt"
        with open(label_path, 'w') as f:
            # class 0 at center with random size variation
            w = random.uniform(0.05, 0.2)
            h = random.uniform(0.05, 0.2)
            f.write(f"0 0.5 0.5 {w} {h}\n")
            
            # Sometimes add another random object
            if random.random() > 0.7:
                x = random.uniform(0.1, 0.9)
                y = random.uniform(0.1, 0.9)
                w2 = random.uniform(0.03, 0.1)
                h2 = random.uniform(0.03, 0.1)
                f.write(f"1 {x} {y} {w2} {h2}\n")  # class 1: other
    
    # Process validation images
    print("📝 Creating validation labels...")
    for img_path in tqdm(val_paths):
        dest = output_dir / 'val' / 'images' / img_path.name
        shutil.copy2(img_path, dest)
        
        label_path = output_dir / 'val' / 'labels' / f"{img_path.stem}.txt"
        with open(label_path, 'w') as f:
            f.write("0 0.5 0.5 0.1 0.1\n")
    
    print(f"✅ Synthetic labels created at: {output_dir}")
    
    # Create dataset.yaml
    yaml_content = f"""# AI4Shipwrecks Synthetic Dataset
path: {output_dir.absolute()}
train: train/images
val: val/images

nc: 2
names:
  0: shipwreck
  1: other
"""
    with open("configs/ai4shipwrecks_synthetic.yaml", "w") as f:
        f.write(yaml_content)
    
    print("✅ Dataset config created: configs/ai4shipwrecks_synthetic.yaml")

if __name__ == "__main__":
    create_synthetic_labels()
