from flask import Flask, request, render_template, send_file, redirect, url_for
from PIL import Image, ImageDraw, ImageFont
import os

app = Flask(__name__)

# Path to store temporary uploaded and output images
UPLOAD_FOLDER = 'static/uploads'
OUTPUT_IMAGE_PATH = os.path.join(UPLOAD_FOLDER, 'news_thumbnail.png')

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get the uploaded image file and text input
        image_file = request.files['image']
        text = request.form['text']

        if image_file and text:
            # Save the uploaded image
            image_path = os.path.join(UPLOAD_FOLDER, 'uploaded_image.png')
            image_file.save(image_path)

            # Create the thumbnail with the given text
            create_news_thumbnail(image_path, text, OUTPUT_IMAGE_PATH)

            # Redirect to show the generated image
            return redirect(url_for('index', show_image=True))

    # Render the template, optionally showing the image
    show_image = request.args.get('show_image', False)
    return render_template('index.html', show_image=show_image, image_path=OUTPUT_IMAGE_PATH)

def create_news_thumbnail(image_path, text, output_path='news_thumbnail.png'):
    with Image.open(image_path) as img:
        img = img.convert('RGB')
        draw = ImageDraw.Draw(img)
        text = text.upper()
        words = text.split()
        if len(words) > 3:
            text_lines = [' '.join(words[:3]), ' '.join(words[3:])]
        else:
            text_lines = [' '.join(words)]
        max_font_size = 80
        min_font_size = 20
        font_size = max_font_size

        while font_size >= min_font_size:
            try:
                font = ImageFont.truetype(os.path.join('static', 'fonts', 'arialbd.ttf'), font_size)
            except IOError:
                font = ImageFont.load_default()
            
            fits = all(draw.textbbox((0, 0), line, font=font)[2] <= img.width - 20 for line in text_lines)
            if fits:
                break
            font_size -= 2

        text_heights = [draw.textbbox((0, 0), line, font=font)[3] for line in text_lines]
        total_text_height = sum(text_heights) + (len(text_lines) - 1) * 10
        y_position = img.height - total_text_height - 20

        for line in text_lines:
            text_width = draw.textbbox((0, 0), line, font=font)[2]
            x_position = 20
            rect_position = [x_position - 10, y_position - 10, x_position + text_width + 10, y_position + text_heights[0] + 10]
            draw.rectangle(rect_position, fill=(139, 0, 0, 255))
            draw.text((x_position, y_position), line, font=font, fill="white")
            y_position += text_heights[0] + 10

        img.save(output_path)
        print(f"Thumbnail saved as {output_path}")

if __name__ == '__main__':
    app.run(debug=True)
