import os
import cv2
import numpy as np
import time
import json
from datetime import datetime
import matplotlib.pyplot as plt
from io import BytesIO
import base64

def analyze_video(video_path):
    """
    Analyze a video file for potential deepfake content.
    Returns a dictionary with detailed analysis results.
    """
    start_time = time.time()
    
    # Open the video file
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return {"error": "Could not open video file"}
    
    # Get video properties
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    duration = frame_count / fps if fps > 0 else 0
    
    # Initialize analysis variables
    frame_analysis = []
    face_detections = []
    consistency_scores = []
    lighting_scores = []
    motion_scores = []
    
    # Load face detection model
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    # Process frames
    frame_idx = 0
    prev_frame = None
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        # Analyze every 5th frame to save processing time
        if frame_idx % 5 == 0:
            # Convert to grayscale for face detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Face detection
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            
            # Calculate lighting consistency
            lighting_score = calculate_lighting_consistency(frame)
            
            # Calculate motion consistency
            motion_score = 1.0
            if prev_frame is not None:
                motion_score = calculate_motion_consistency(prev_frame, frame)
            
            # Calculate overall consistency score
            consistency_score = calculate_consistency_score(
                len(faces),
                lighting_score,
                motion_score
            )
            
            # Store frame analysis
            frame_analysis.append({
                "frame_idx": frame_idx,
                "timestamp": frame_idx / fps,
                "face_count": len(faces),
                "lighting_score": float(lighting_score),
                "motion_score": float(motion_score),
                "consistency_score": float(consistency_score)
            })
            
            face_detections.append(len(faces))
            consistency_scores.append(consistency_score)
            lighting_scores.append(lighting_score)
            motion_scores.append(motion_score)
            
            prev_frame = frame.copy()
        
        frame_idx += 1
    
    cap.release()
    
    # Calculate overall metrics
    processing_time = time.time() - start_time
    avg_consistency = np.mean(consistency_scores) if consistency_scores else 0.5
    avg_lighting = np.mean(lighting_scores) if lighting_scores else 0.5
    avg_motion = np.mean(motion_scores) if motion_scores else 0.5
    
    # Generate visualization
    plt.figure(figsize=(12, 8))
    
    # Plot consistency scores
    plt.subplot(2, 2, 1)
    plt.plot([f["timestamp"] for f in frame_analysis], 
             [f["consistency_score"] for f in frame_analysis], 
             label='Consistency')
    plt.title("Consistency Score Over Time")
    plt.xlabel("Time (seconds)")
    plt.ylabel("Score")
    plt.grid(True)
    
    # Plot lighting scores
    plt.subplot(2, 2, 2)
    plt.plot([f["timestamp"] for f in frame_analysis], 
             [f["lighting_score"] for f in frame_analysis], 
             label='Lighting', color='orange')
    plt.title("Lighting Consistency")
    plt.xlabel("Time (seconds)")
    plt.ylabel("Score")
    plt.grid(True)
    
    # Plot motion scores
    plt.subplot(2, 2, 3)
    plt.plot([f["timestamp"] for f in frame_analysis], 
             [f["motion_score"] for f in frame_analysis], 
             label='Motion', color='green')
    plt.title("Motion Consistency")
    plt.xlabel("Time (seconds)")
    plt.ylabel("Score")
    plt.grid(True)
    
    # Plot face detections
    plt.subplot(2, 2, 4)
    plt.plot([f["timestamp"] for f in frame_analysis], 
             [f["face_count"] for f in frame_analysis], 
             label='Faces', color='red')
    plt.title("Face Detections")
    plt.xlabel("Time (seconds)")
    plt.ylabel("Number of Faces")
    plt.grid(True)
    
    plt.tight_layout()
    
    # Save plot to base64 string
    img = BytesIO()
    plt.savefig(img, format='png', dpi=100, bbox_inches='tight')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode('utf-8')
    plt.close()
    
    # Determine if video is likely a deepfake
    is_deepfake = avg_consistency < 0.8
    
    # Prepare detailed analysis
    detailed_analysis = {
        "is_deepfake": bool(is_deepfake),
        "confidence_score": float(avg_consistency),
        "processing_time": processing_time,
        "frame_analysis": frame_analysis,
        "metadata": {
            "fps": fps,
            "frame_count": frame_count,
            "width": width,
            "height": height,
            "duration": duration,
            "face_detection_rate": sum(1 for f in face_detections if f > 0) / len(face_detections) if face_detections else 0,
            "avg_lighting_score": float(avg_lighting),
            "avg_motion_score": float(avg_motion)
        },
        "visualization": plot_url,
        "analysis_summary": {
            "overall_confidence": float(avg_consistency),
            "lighting_consistency": float(avg_lighting),
            "motion_consistency": float(avg_motion),
            "face_detection_stability": sum(1 for f in face_detections if f > 0) / len(face_detections) if face_detections else 0,
            "processing_efficiency": frame_count / (processing_time * fps) if processing_time > 0 else 0
        }
    }
    
    return detailed_analysis

def calculate_lighting_consistency(frame):
    """Calculate lighting consistency score for a frame."""
    # Convert to LAB color space
    lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
    l_channel = lab[:,:,0]
    
    # Calculate lighting statistics
    mean_light = np.mean(l_channel)
    std_light = np.std(l_channel)
    
    # Normalize score (higher score means more consistent lighting)
    score = 1.0 - (std_light / 128.0)  # 128 is max std dev for 8-bit image
    return max(0.0, min(1.0, score))

def calculate_motion_consistency(prev_frame, curr_frame):
    """Calculate motion consistency between two frames."""
    # Convert to grayscale
    prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
    curr_gray = cv2.cvtColor(curr_frame, cv2.COLOR_BGR2GRAY)
    
    # Calculate optical flow
    flow = cv2.calcOpticalFlowFarneback(prev_gray, curr_gray, None, 0.5, 3, 15, 3, 5, 1.2, 0)
    
    # Calculate magnitude of motion
    magnitude = np.sqrt(flow[..., 0]**2 + flow[..., 1]**2)
    mean_magnitude = np.mean(magnitude)
    
    # Normalize score (lower motion means higher score)
    score = 1.0 - (mean_magnitude / 10.0)  # 10.0 is threshold for significant motion
    return max(0.0, min(1.0, score))

def calculate_consistency_score(face_count, lighting_score, motion_score):
    """Calculate overall consistency score."""
    # Weight factors
    face_weight = 0.4
    lighting_weight = 0.3
    motion_weight = 0.3
    
    # Face score (higher when exactly one face is detected)
    face_score = 1.0 if face_count == 1 else 0.5 if face_count > 1 else 0.0
    
    # Calculate weighted average
    score = (
        face_weight * face_score +
        lighting_weight * lighting_score +
        motion_weight * motion_score
    )
    
    return score

def save_uploaded_file(file, upload_dir):
    """Save an uploaded file to the specified directory."""
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    
    # Generate a unique filename
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    original_filename = file.filename
    file_ext = os.path.splitext(original_filename)[1]
    filename = f"{timestamp}{file_ext}"
    file_path = os.path.join(upload_dir, filename)
    
    # Save the file
    file.save(file_path)
    
    return {
        "filename": filename,
        "original_filename": original_filename,
        "file_path": file_path,
        "file_type": file.content_type,
        "file_size": os.path.getsize(file_path)
    } 