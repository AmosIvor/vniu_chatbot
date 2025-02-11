import requests
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import UserUtteranceReverted

class ActionProductSearchWithCategoryAndColour(Action):

    def name(self) -> Text:
        return "action_product_search_with_category_and_colour"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Extract entities
        entities = tracker.latest_message.get('entities', [])

        category = None
        colour = None

        for entity in entities:
            if entity.get('entity') == 'category':
                category = entity.get('value')
            elif entity.get('entity') == 'colour':
                colour = entity.get('value')

        # API URL
        url = "https://vniu.info.vn/api/v1/chatbots/search-with-category-and-colour"
        payload = {
            "categoryName": category,
            "colourName": colour
        }

        try:
            # Send request
            response = requests.post(url, json=payload, verify=False)  # `verify=False` to ignore SSL issues in dev

            if response.status_code == 200:
                data = response.json()
                if data.get("isSuccess"):
                    category_id = data["value"]["categoryId"]
                    colour_id = data["value"]["colourId"]
                    
                    # Case 1: Both IDs are null
                    if category_id is None and colour_id is None:
                        dispatcher.utter_message(
                            "Please enter a valid category and colour."
                        )
                        return []
                    
                    # Build base URL
                    base_url = "https://vniu.info.vn/api/v1/products/filter-and-sort?"
                    url_params = []
                    
                    # Case 2: Only category_id is null
                    if category_id is None and colour_id is not None:
                        url_params.append(f"ColourIdsString={colour_id}")
                    
                    # Case 3: Only colour_id is null
                    elif category_id is not None and colour_id is None:
                        url_params.append(f"CategoryIdsString={category_id}")
                    
                    # Case 4: Both IDs are not null
                    elif category_id is not None and colour_id is not None:
                        url_params.extend([
                            f"CategoryIdsString={category_id}",
                            f"ColourIdsString={colour_id}"
                        ])
                    
                    # Add pagination parameters
                    url_params.extend(["PageIndex=1", "PageSize=3"])
                    
                    # Construct final URL
                    product_search_url = base_url + "&".join(url_params)
                    
                    dispatcher.utter_message(f"{product_search_url}")
                    
                else:
                    dispatcher.utter_message("Database connection error. Please try again by re-entering your query.")
            else:
                dispatcher.utter_message("Database connection error. Please try again by re-entering your query")

        except requests.RequestException as e:
            dispatcher.utter_message("Database connection error. Please try again by re-entering your query")

        return []