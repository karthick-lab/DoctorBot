from PIL import Image

def extract_text_from_image(image_path):
    # Placeholder: simulate reading text from image
    # You can replace this with a custom pixel parser or ML model later
    try:
        img = Image.open(image_path)
        width, height = img.size
        return f"Image loaded: {width}x{height}. Please enter symptoms manually."
    except Exception as e:
        return f"Error reading image: {str(e)}"