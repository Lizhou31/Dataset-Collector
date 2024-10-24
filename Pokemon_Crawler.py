from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import os
from PIL import Image
import requests
from io import BytesIO
from openai import OpenAI
import base64

class WebCrawler:
    def __init__(self, driver):
        self.driver = driver

    def search_pinterest(self, keyword):
        self.keyword = keyword
        self.driver.get("https://www.pinterest.com/ideas/")
        time.sleep(2)
        search_box = self.driver.find_element(By.NAME, 'searchBoxInput')
        search_box.send_keys(self.keyword)
        search_box.send_keys(Keys.RETURN)
        time.sleep(2)

    def download_and_resize_images(self, max_images):
        os.makedirs(f"Pictures_temp/{self.keyword}", exist_ok=True)
        
        downloaded_images = set()
        image_count = 0
        while image_count < max_images:
            images = self.driver.find_elements(By.TAG_NAME, 'img')
            for img in images:
                try:
                    img_url = img.get_attribute('src')
                    if img_url and img_url not in downloaded_images:
                        original_img_url = img_url.replace('/236x/', '/originals/')
                        response = requests.get(original_img_url)
                        img_data = BytesIO(response.content)
                        # Open and resize the image while keeping the aspect ratio
                        with Image.open(img_data) as image:
                            # Calculate the new size while keeping the aspect ratio
                            aspect_ratio = min(224 / image.width, 224 / image.height)
                            new_size = (int(image.width * aspect_ratio), int(image.height * aspect_ratio))
                            image = image.resize(new_size, Image.ANTIALIAS)
                            
                            # Calculate coordinates to crop the image to 224x224
                            left = (image.width - 224) / 2
                            top = (image.height - 224) / 2
                            right = (image.width + 224) / 2
                            bottom = (image.height + 224) / 2
                            image = image.crop((left, top, right, bottom))
                            
                            # Save the image
                            image_path = f"Pictures_temp/{self.keyword}/{self.keyword}_{image_count}.jpg"
                            image.save(image_path)
                        
                        # Add the URL to the set and increment the count
                        downloaded_images.add(img_url)
                        image_count += 1

                        # Stop if we have reached 100 images
                        if image_count >= max_images:
                            break
                except Exception as e:
                    print(f"Error downloading image {image_count}: {e}")
        
            # Scroll down to load more images
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
        
class AI_Labeler:
    def __init__(self, image_path):
        self.client = OpenAI()
        self.image_path = image_path
    
    def label_image(self):
        with open(self.image_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')
            messages = [
                {"role": "system", "content": "You are a pokemon name detector"},
                {"role": "user", "content": "detect the pokemon name"},
                {"role": "user", "content": [{"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}]},
            ]

            response = self.client.chat.completions.create(
                model="ft:gpt-4o-2024-08-06:personal:pokemonexp:ALjNvVoh",
                messages=messages,
            )

        return response.choices[0].message.content

def main():
    os.makedirs("Pictures_test", exist_ok=True)
    os.makedirs("Pictures_temp", exist_ok=True)
    driver = webdriver.Chrome()
    crawler = WebCrawler(driver)
    crawler.search_pinterest("pokemon")
    crawler.download_and_resize_images(300)
    for image_file in os.listdir(f"Pictures_temp/{crawler.keyword}"):
        image_path = f"Pictures_temp/{crawler.keyword}/{image_file}"
        labeler = AI_Labeler(image_path)
        label = labeler.label_image()
        print(f"Image: {image_file}, Label: {label}")
        os.makedirs(f"Pictures_test/{label}", exist_ok=True)
        os.rename(image_path, f"Pictures_test/{label}/{image_file}")

if __name__ == "__main__":
    main()