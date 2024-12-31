from flask import Flask, render_template, request, send_from_directory, redirect, url_for
from ultralytics import YOLO
import os
import shutil
from moviepy.editor import VideoFileClip


app = Flask(__name__)

# Directories for uploads and results
UPLOAD_FOLDER = "static/uploads"
RESULTS_FOLDER = "static/results"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)

# Allowed extensions for images and videos
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'avi', 'mov'}

# Load YOLO model once
model = YOLO("D:/ug_mini_proj/flask_app/static/best.pt")

def allowed_file(filename):
    """Check if the uploaded file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/detect_image', methods=['POST'])
def detect_image():
    # Handle image upload
    image_file = request.files['image_file']
    if not image_file or not allowed_file(image_file.filename):
        return "No valid image file uploaded", 400

    # Save the uploaded image
    image_path = os.path.join(UPLOAD_FOLDER, image_file.filename)
    image_file.save(image_path)

    # Perform detection using YOLO
    results = model(source=image_path, show=False, save=True, name="result")
    
    saved_image_path = os.path.join(results[0].save_dir, image_file.filename)
    if os.path.exists(saved_image_path):
        # Move the result image to static/results folder
        shutil.move(saved_image_path, os.path.join(RESULTS_FOLDER, "result.jpg"))
        # Redirect to the result page
        return redirect(url_for('show_result', image_name="result.jpg"))
    else:
        return "Error: Result image not found", 404

@app.route('/detect_video', methods=['POST'])
def detect_video():
    # Handle video upload
    video_file = request.files['video_file']
    if not video_file or not allowed_file(video_file.filename):
        return "No valid video file uploaded", 400

    # Save the uploaded video
    video_path = os.path.join(UPLOAD_FOLDER, video_file.filename)
    video_file.save(video_path)

    # Perform detection on the video
    results = model(source=video_path, show=False, save=True)
    result_video_dir = results[0].save_dir
    
     # YOLO saves the processed video with the original name but .avi extension
    original_name = os.path.splitext(video_file.filename)[0]  # Extract the name without extension
    result_video_filename = f"{original_name}.avi"  # Processed video name with .avi extension
    result_video_path = os.path.join(result_video_dir, result_video_filename)

    if os.path.exists(result_video_path):
        # Move the result video to the static/results folder
        final_video_path = os.path.join(RESULTS_FOLDER, result_video_filename)
        shutil.move(result_video_path, final_video_path)
        
        #for video rename
        clip = VideoFileClip(f"static/results/{result_video_filename}")
        clip.write_videofile(f"static/results/{original_name}.mp4", codec="libx264")
        os.remove(f"static/results/{result_video_filename}")
        # Redirect to the result page with video URL and flag
        return redirect(url_for('show_result', result_name=video_file.filename, is_video=True))
    else:
        return "Error: Video result not found", 404

@app.route('/result')
def show_result():
    # Get the result file name and the flag indicating if it's a video
    result_name = request.args.get('result_name', 'result.jpg')  # Default to result.jpg if no name
    is_video = request.args.get('is_video', 'false') == 'True'  # Get the is_video flag (converted to boolean)

    # Create the URL to access the result
    result_url = url_for('static', filename=f'results/{result_name}')
    print("Image/Video URL:", result_url)
    # Pass the result URL and is_video flag to the result template
    return render_template('result.html', image_url=result_url, is_video=is_video)

if __name__ == '__main__':
    app.run(debug=True)
