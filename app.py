from pathlib import Path
from PIL import Image
import io
from flask import Flask, request, send_file, render_template_string

app = Flask(__name__)

def resize_image(image_data, target_size_kb: int) -> bytes:
    """Resize an image to fit under the provided size constraint in KB."""
    with Image.open(io.BytesIO(image_data)) as img:
        # Start with a high quality and reduce until file size target is reached
        quality = 100  # Start with high quality
        img_byte_arr = io.BytesIO()
        
        # Compress image and check file size, adjust quality as needed
        while True:
            img_byte_arr.seek(0)  # Reset the buffer before saving the image
            img.save(img_byte_arr, format='WEBP', quality=quality)
            img_byte_arr.seek(0)
            file_size_kb = len(img_byte_arr.getvalue()) / 1024  # Convert bytes to KB
            
            # If the file size is within the target size, break the loop
            if file_size_kb <= target_size_kb:
                break
            
            # Gradually reduce the quality to shrink the file size
            quality -= 5
            if quality <= 10:  # Stop reducing quality if it gets too low
                break
        
        return img_byte_arr

@app.route('/')
def upload_form():
    return render_template_string('''
        <html>
            <body>
                <h1>Image Resize Form</h1>
                <form method="POST" enctype="multipart/form-data">
                    <label for="file">Upload an Image:</label>
                    <input type="file" id="file" name="file" accept="image/*" required><br><br>
                    
                    <label for="target_size">Expected File Size (KB):</label>
                    <input type="number" id="target_size" name="target_size" required><br><br>
                    
                    <input type="submit" value="Upload & Resize">
                    <!--email_off-->tejas.gadhave@gramener.com<!--/email_off-->
                </form>
            </body>
        </html>
    ''')

@app.route('/', methods=['POST'])
def handle_file_upload():
    file = request.files['file']
    target_size_kb = int(request.form['target_size'])

    image_data = file.read()
    resized_image = resize_image(image_data, target_size_kb)
    
    return send_file(resized_image, mimetype='image/webp', as_attachment=True, download_name="resized_image.webp")

if __name__ == '__main__':
    app.run(debug=True)
