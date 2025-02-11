from typing import Any, Text, Dict, List
import requests
import tempfile
from urllib.parse import urlparse
import os
import mimetypes
from urllib.request import urlretrieve
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import UserUtteranceReverted

class ActionProductSearchWithImageAndColour(Action):
    def name(self) -> Text:
        return "action_product_search_with_image_and_colour"

    def get_file_extension(self, url: str) -> str:
        """Extract file extension from URL, defaulting to .jpg if none found"""
        parsed = urlparse(url)
        path = parsed.path
        ext = os.path.splitext(path)[1].lower()
        
        if not ext:
            return '.jpg'  # Default extension
        return ext

    def get_content_type(self, file_path: str) -> str:
        """Get the MIME type for the file"""
        content_type, _ = mimetypes.guess_type(file_path)
        return content_type or 'image/jpeg'  # Default to image/jpeg if type cannot be determined

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Extract entities
        entities = tracker.latest_message.get('entities', [])
        image_product_url = None
        colour = None
        
        for entity in entities:
            if entity.get('entity') == 'image_product':
                image_product_url = entity.get('value')
            elif entity.get('entity') == 'colour':
                colour = entity.get('value')
        
        print(image_product_url)
        print(colour)

        colour_id = None
        # API URL
        url = "https://vniu.info.vn/api/v1/chatbots/search-with-category-and-colour"
        payload = {
            "colourName": colour
        }

        try:
            # Send request
            response_colour = requests.post(url, json=payload, verify=False)  # `verify=False` to ignore SSL issues in dev

            if response_colour.status_code == 200:
                data_colour = response_colour.json()
                if data_colour.get("isSuccess"):
                    colour_id = data_colour["value"]["colourId"]
                else:
                    dispatcher.utter_message("Database connection error. Please try again by re-entering your query.")
            else:
                dispatcher.utter_message("Database connection error. Please try again by re-entering your query")

        except requests.RequestException as e:
            dispatcher.utter_message("Database connection error. Please try again by re-entering your query")

        if image_product_url:
            temp_file = None
            file_obj = None
            try:
                # Get the file extension from the URL
                file_extension = self.get_file_extension(image_product_url)
                
                # Create temporary file
                temp_file = tempfile.NamedTemporaryFile(suffix=file_extension, delete=False)
                temp_file.close()  # Close immediately after creation
                
                # Download the image
                urlretrieve(image_product_url, temp_file.name)
                
                # Get the content type for the file
                content_type = self.get_content_type(temp_file.name)
                
                # Open file for reading
                file_obj = open(temp_file.name, 'rb')
                
                # Prepare the files parameter for the POST request
                files = {
                    'file': (
                        f'image{file_extension}',
                        file_obj,
                        content_type
                    )
                }
                
                # Make the API request
                response = requests.post(
                    f"https://vniu.info.vn/image-search/images/search-by-image",
                    files=files
                )
                
                if response.status_code == 200:
                    # Process the API response
                    search_results = response.json()
                    product_ids = search_results.get('productItemIds', [])
                    
                    # Convert list of IDs to comma-separated string
                    product_ids_string = ','.join(product_ids)
                    
                    # Build base URL and parameters
                    base_url = "https://vniu.info.vn/api/v1/products/filter-and-sort?"
                    url_params = [f"ProductItemIdsString={product_ids_string}"]
                    
                    # Add colour parameter only if colour_id exists
                    if colour_id is not None:
                        url_params.append(f"ColourIdsString={colour_id}")
                    
                    # Add pagination parameters
                    url_params.extend(["PageIndex=1", "PageSize=3"])
                    
                    # Construct final URL
                    product_search_url = base_url + "&".join(url_params)

                    dispatcher.utter_message(f"{product_search_url}")
                else:
                    dispatcher.utter_message(f"Database connection error. Please try again by re-entering your query")
                    
            except Exception as e:
                dispatcher.utter_message(f"Database connection error. Please try again by re-entering your query")
            finally:
                # Clean up resources
                if file_obj:
                    file_obj.close()
                if temp_file and os.path.exists(temp_file.name):
                    try:
                        os.unlink(temp_file.name)
                    except Exception:
                        pass  # Ignore deletion errors
        else:
            dispatcher.utter_message("Database connection error. Please try again by re-entering your query")

        return []