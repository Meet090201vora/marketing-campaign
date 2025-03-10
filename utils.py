import os
import io
import base64
from PIL import Image
import requests
from prompt import system_prompt_image
from dotenv import load_dotenv
load_dotenv()

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

def image_summarizer(input_email, base64_image, url_flag:bool=False):
    """This function takes an image as input and returns a summary of the image content.

    Args:
        image (str): path of the image to be processed
    """

    system_prompt_image_dynamic = system_prompt_image.replace("<email_content>", input_email)

    status = False
    try:
        
        url = f"data:image/jpeg;base64,{base64_image}"
        if url_flag:
            url = base64_image

        # Prepare API headers
        headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
        }

        #print(base64_image)
    
        # API payload
        payload = {
            "model": "gpt-4o",
            "messages": 
            [
                {
                    "role": "user",
                    "content": 
                    [
                        {
                            "type": "text",
                            "text": system_prompt_image_dynamic
                        },
                        {
                            "type": "image_url",
                            "image_url": 
                            {
                                "url": url
                            }
                        }
                    ]
                }
            ],
            # "max_tokens": 800
        }

        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        
        if response.status_code == 200:
            status = True
            img_resp = response.json()

        if status:
            return status, img_resp['choices'][0]['message']['content']
            
        return False, str(response.status_code) + " Error while executing function image_summarizer"
        
    except Exception as e:
        return False, "Error while executing function image_summarizer"
    

def decode_image_base64(path_to_img, encoded_image):
    """This function converts a given encoded image into jpg format and stores it in the folder path_to_img

    Args:
        path_to_img (str): directory where the encoded image will be stored
        encoded_img (str): encoded image which would be converted to original RGB format image
    
    Return:
        status (bool): Whether the execution was successful or not
        mssg (str): Message indicating success or failure
    """
    
    status = False
    try:
        output_folder = "/".join(path_to_img.split("/")[:-1])
        # Create the folder if it doesn't exist
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        image_data = base64.b64decode(encoded_image)
        # Write the binary data to a .jpg file
        with open(path_to_img, 'wb') as image_file:
            image_file.write(image_data)

        return True, "Image saved successfully to the folder"
    
    except Exception as e:
        return False, "An exception occured while executing function decode_image_base64"
    


def get_image_base64(image):
    """
    Converts an image to its base64-encoded JPEG representation.

    Args:
        image (str): The file path or file object of the image to be converted.

    Returns:
        status (bool): Boolean value showing whether execution was successful or not, if not then return False
        img_str (str): The base64-encoded string of the image in JPEG format.
    """
    
    status = False
    try: 
        # If the input is a string (file path), open the image
        if isinstance(image, str):
            image = Image.open(image).convert('RGB')

        # If the image is already a PIL Image object, skip opening it
        elif isinstance(image, Image.Image):
            image = image.convert('RGB')


        buffered = io.BytesIO()
        image.save(buffered, format="JPEG")

        img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
        status = True

        return status, img_str
    
    except Exception as e:
        return status, "Failed to convert image into base64 enocoded string."
    


def process_image_input(path_to_image:str, is_url:bool=False):
    """This function takes request_id and URL of website as input passes it to evaluate_text function for threat analysis.

    Args:
        path_to_image (str): path of the image to be processed
    
    Returns:
        status (bool): whether execution was successful or not
        mssg (str): message regarding the execution
    """

    # a dictionary containing information which will be pushed to database in case of unsafe content
    try:

        
        # If given input image is not URL
        if not is_url:
            
            status_encoding_img, encoded_image = get_image_base64(path_to_image)
            
            if not status_encoding_img:
                raise("Error while converting image to encoded string")
            
            temp_image_path = f"temp/image/snapshot.jpg"
            image_saved_status, image_saved_status_mssg = decode_image_base64(temp_image_path, encoded_image)
            if not image_saved_status:
                raise("Error while saving image to the temporary directory.")

            status_img_sum, text = image_summarizer(encoded_image, url_flag=False)
            if not status_img_sum:
                raise("Error while summarizing the image content.")
            
            return True, text

    except Exception as e:
        return False, e