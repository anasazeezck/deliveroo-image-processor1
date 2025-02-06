import streamlit as st
from PIL import Image
import io
import openai
import requests
import os
from io import BytesIO

# Load OpenAI API Key securely
openai.api_key = os.getenv("OPENAI_API_KEY")

# Function to generate Deliveroo-optimized SEO title and description
def generate_seo_content(product_name):
    try:
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
        response_text = response["choices"][0]["message"]["content"]

        # Extract title and description using structured parsing
        if "Title:" in response_text and "Description:" in response_text:
            title = response_text.split("Title:")[1].split("Description:")[0].strip()[:120]
            description = response_text.split("Description:")[1].strip()[:500]
        else:
            return "Error: OpenAI response format changed.", "Error: OpenAI response format changed."
        
        return title, description

    except Exception as e:
        return "Error: OpenAI API request failed.", str(e)

# Function to process product image to 1200x800 with a white background
def process_product_image(image_url):
    try:
        response = requests.get(image_url, stream=True)
        if response.status_code == 200:
            img = Image.open(BytesIO(response.content)).convert("RGB")

            # Check minimum resolution
            if img.width < 500 or img.height < 500:
                return None, "Error: Image resolution is too low. Minimum required: 500x500 pixels."

            base_width, base_height = 1200, 800
            img.thumbnail((base_width - 100, base_height - 100), Image.ANTIALIAS)

            # Create a white background
            white_canvas = Image.new("RGB", (base_width, base_height), (255, 255, 255))
            x_offset = (base_width - img.size[0]) // 2
            y_offset = (base_height - img.size[1]) // 2
            white_canvas.paste(img, (x_offset, y_offset))

            return white_canvas, None
        else:
            return None, "Error: Unable to fetch the image from the provided URL."
    
    except Exception as e:
        return None, f"Error processing image: {str(e)}"

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
            
            if "Error" in title:
                st.error(title)
            else:
                st.subheader("Generated SEO Title (Max 120 characters):")
                st.write(title)
                
                st.subheader("Generated SEO Description (Max 500 characters):")
                st.write(description)

            if error_msg:
                st.error(error_msg)
            else:
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
