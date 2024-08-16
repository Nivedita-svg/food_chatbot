from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import db_helper
import generic_helper
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = FastAPI()

inprogress_orders = {}

@app.get("/")
def read_root():
    return {"message": "Hello World"}

@app.post("/")
async def handle_request(request: Request):
    try:
        # Retrieve the JSON data from the request
        payload = await request.json()

        # Extract the necessary information from the payload
        intent = payload['queryResult']['intent']['displayName']
        parameters = payload['queryResult']['parameters']
        output_contexts = payload['queryResult']['outputContexts']
        session_id = generic_helper.extract_session_id(output_contexts[0]["name"])

        # Define intent handler functions
        intent_handler_dict = {
            'order.add - context: ongoing-order': add_to_order,
            'order.remove - context: ongoing-order': remove_from_order,
            'order.complete - context: ongoing-order': complete_order,
            'track.order - context: ongoing-tracking': track_order
        }

        # Call the appropriate handler function based on the intent
        if intent in intent_handler_dict:
            return intent_handler_dict[intent](parameters, session_id)
        else:
            logging.error(f"Unknown intent: {intent}")
            return JSONResponse(content={"fulfillmentText": "Sorry, I couldn't understand that intent."})

    except Exception as e:
        logging.exception("An error occurred while handling the request.")
        return JSONResponse(content={"fulfillmentText": "An internal error occurred. Please try again later."})

def save_to_db(order: dict):
    try:
        next_order_id = db_helper.get_next_order_id()

        # Insert individual items along with quantity in orders table
        for food_item, quantity in order.items():
            rcode = db_helper.insert_order_item(food_item, quantity, next_order_id)
            if rcode == -1:
                return -1

        # Insert order tracking status
        db_helper.insert_order_tracking(next_order_id, "in progress")
        return next_order_id

    except Exception as e:
        logging.exception("Error occurred while saving to DB.")
        return -1

def complete_order(parameters: dict, session_id: str) -> JSONResponse:
    logging.debug(f"Received request to complete order for session_id: {session_id}")

    if session_id not in inprogress_orders:
        fulfillment_text = "I'm having trouble finding your order. Sorry! Can you place a new order, please?"
        logging.debug(f"Order not found for session_id: {session_id}")
    else:
        order = inprogress_orders[session_id]
        logging.debug(f"Order found: {order}")

        order_id = save_to_db(order)
        if order_id == -1:
            fulfillment_text = "Sorry, I couldn't process your order due to a backend error. Please place a new order again."
            logging.debug("Error saving order to DB")
        else:
            order_total = db_helper.get_total_order_price(order_id)
            fulfillment_text = (
                f"Awesome. We have placed your order. "
                f"Here is your order id # {order_id}. "
                f"Your order total is {order_total} which you can pay at the time of delivery!"
            )
            logging.debug(f"Order placed successfully with order_id: {order_id}, total price: {order_total}")

        del inprogress_orders[session_id]

    return JSONResponse(content={"fulfillmentText": fulfillment_text})

def add_to_order(parameters: dict, session_id: str) -> JSONResponse:
    logging.debug(f"Received request to add items to order for session_id: {session_id}")

    food_items = parameters.get("food-item", [])
    quantities = parameters.get("number", [])

    if len(food_items) != len(quantities):
        fulfillment_text = "Sorry, I didn't understand. Can you please specify food items and quantities clearly?"
        logging.debug("Food items and quantities do not match")
    else:
        new_food_dict = dict(zip(food_items, quantities))

        if session_id in inprogress_orders:
            current_food_dict = inprogress_orders[session_id]
            current_food_dict.update(new_food_dict)
            inprogress_orders[session_id] = current_food_dict
        else:
            inprogress_orders[session_id] = new_food_dict

        order_str = generic_helper.get_str_from_food_dict(inprogress_orders[session_id])
        fulfillment_text = f"So far you have: {order_str}. Do you need anything else?"
        logging.debug(f"Order updated: {inprogress_orders[session_id]}")

    return JSONResponse(content={"fulfillmentText": fulfillment_text})

def remove_from_order(parameters: dict, session_id: str) -> JSONResponse:
    logging.debug(f"Received request to remove items from order for session_id: {session_id}")

    if session_id not in inprogress_orders:
        return JSONResponse(content={
            "fulfillmentText": "I'm having trouble finding your order. Sorry! Can you place a new order, please?"
        })

    food_items = parameters.get("food-item", [])
    current_order = inprogress_orders[session_id]

    removed_items = []
    no_such_items = []

    for item in food_items:
        if item not in current_order:
            no_such_items.append(item)
        else:
            removed_items.append(item)
            del current_order[item]

    fulfillment_text = ""

    if removed_items:
        fulfillment_text += f"Removed {', '.join(removed_items)} from your order! "

    if no_such_items:
        fulfillment_text += f"Your current order does not have {', '.join(no_such_items)}. "

    if not current_order:
        fulfillment_text += "Your order is now empty!"
    else:
        order_str = generic_helper.get_str_from_food_dict(current_order)
        fulfillment_text += f"Here is what is left in your order: {order_str}"

    return JSONResponse(content={"fulfillmentText": fulfillment_text})

def track_order(parameters: dict, session_id: str) -> JSONResponse:
    logging.debug(f"Received request to track order for order_id: {parameters.get('order_id', '')}")

    order_id = int(parameters.get('order_id', 0))
    order_status = db_helper.get_order_status(order_id)

    if order_status:
        fulfillment_text = f"The order status for order id: {order_id} is: {order_status}"
    else:
        fulfillment_text = f"No order found with order id: {order_id}"

    return JSONResponse(content={"fulfillmentText": fulfillment_text})
