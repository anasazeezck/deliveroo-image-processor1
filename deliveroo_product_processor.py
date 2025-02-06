import streamlit as st
from PIL import Image
import io
import openai
import os
import requests
from io import BytesIO

# Load OpenAI API Key from environment variable
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    st.error("OpenAI API Key is missing! Set it as an environment variable.")
    st.stop()

openai.api_key = OPENAI_API_KEY

# Function to generate Deliveroo-optimized SEO title and description
def generate_seo_content(product_name):
    prompt = f"""
    Generate a Deliveroo-optimized product title (max 120 characters) and description (max 500 characters) for the product: {product_name}.

    - **Title:** Use high-intent customer search keywords and make it conversion-focused.
    - **Description:** Highlight key benefits, use engaging language, and naturally insert keywords.
    - **Ensure:** The title and description comply with Deliveroo’s ranking algorithm.
    - **Format Output Strictly as:**
      Title: [Generated Title]
      Description: [Generated Description]
    """
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=600
    )
    result = response["choices"][0]["message"]["content"].split("\n")
    title = result[0].replace("Title:", "").strip()[:120]  # Ensure title is max 120 characters
    description = result[1].replace("Description:", "").strip()[:500]  # Ensure description is max 500 characters
    return title, description

# Function to process product image to 1200x800 with a white background
def process_product_image(image_url):
    response = requests.get(image_url, stream=True)
    if response.status_code == 200:
        img = Image.open(BytesIO(response.content)).convert("RGBA")
        if img.size[0] < 500 or img.size[1] < 500:
            return None, "Error: Image resolution is too low. Minimum required: 500x500 pixels."
        base_width, base_height = 1200, 800
        img.thumbnail((base_width - 100, base_height - 100))
        white_canvas = Image.new("RGBA", (base_width, base_height), (255, 255, 255, 255))
        x_offset = (base_width - img.size[0]) // 2
        y_offset = (base_height - img.size[1]) // 2
        white_canvas.paste(img, (x_offset, y_offset), img)
        return white_canvas.convert("RGB"), None
    else:
        return None, "Error: Unable to fetch the image from the provided URL."

# Streamlit Web App UI
def main():
    st.title("Deliveroo Product Processor")
    st.write("Enter a product name and paste an image URL to generate Deliveroo-optimized content and process the image.")
    
    product_name = st.text_input("Enter Product Name:")
    image_url = st.text_input("Paste Image URL:")
    
    if st.button("Process Product"):
        if product_name and image_url:
            title, description = generate_seo_content(product_name)
            processed_img, error_msg = process_product_image(image_url)
            
            if error_msg:
                st.error(error_msg)
            else:
                st.subheader("Generated SEO Title (Max 120 characters):")
                st.write(title)
                
                st.subheader("Generated SEO Description (Max 500 characters):")
                st.write(description)
                
                st.subheader("Processed Product Image:")
                st.image(processed_img, caption="Formatted Image", use_column_width=True)
                
                img_byte_arr = io.BytesIO()
                processed_img.save(img_byte_arr, format='JPEG', quality=100)
                img_byte_arr = img_byte_arr.getvalue()
                
                st.download_button(
                    label="Download Processed Image",
                    data=img_byte_arr,
                    file_name="formatted_product.jpg",
                    mime="image/jpeg"
                )
        else:
            st.error("Please enter a product name and a valid image URL.")

if __name__ == "__main__":
    main()
