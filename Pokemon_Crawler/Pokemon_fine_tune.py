import os
import json
import base64

def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

import random

def transform_data(input_folder, output_file):
    data = []
    for pokemon_name in os.listdir(input_folder):
        pokemon_folder = os.path.join(input_folder, pokemon_name)
        if os.path.isdir(pokemon_folder):
            image_files = [f for f in os.listdir(pokemon_folder) if f.endswith(".jpg") or f.endswith(".png")]
            if image_files:
                selected_images = random.sample(image_files, min(3, len(image_files)))
                for image_file in selected_images:
                    image_path = os.path.join(pokemon_folder, image_file)
                    image_base64 = encode_image_to_base64(image_path)
                    entry = {
                        "messages": [
                            {"role": "system", "content": "You are a pokemon name detector"},
                            {"role": "user", "content": "detect the pokemon name"},
                            {"role": "user", "content": [{"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}]},
                            {"role": "assistant", "content": pokemon_name}
                        ]
                    }
                    data.append(entry)
    
    with open(output_file, 'w') as outfile:
        for entry in data:
            json.dump(entry, outfile)
            outfile.write('\n')

# Example usage
input_folder = 'Pokedex/train'
output_file = 'data/_pokemon_name_detector.jsonl'
transform_data(input_folder, output_file)
input_folder = 'Pokedex/test'
output_file = 'data/_pokemon_name_detector_test.jsonl'
transform_data(input_folder, output_file)
input_folder = 'Pokedex/valid'
output_file = 'data/_pokemon_name_detector_validation.jsonl'
transform_data(input_folder, output_file)