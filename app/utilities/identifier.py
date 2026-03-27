import ast
from typing import Optional
from langchain_core.runnables import RunnableConfig
from langchain.messages import SystemMessage, AIMessage

from app.core.config import Config
from app.schemas.customer_suppprt_schema import UserInfo, Customer_Support_State
from app.db.sqlite3_client import db

llm = Config().get_oss_llm()
structured_llm = llm.with_structured_output(schema=UserInfo)


def get_user_id(customer_info: str) -> Optional[int]:
    if not customer_info:
        return None
    
    if customer_info.isdigit():
        return int(customer_info)
    
    elif customer_info and customer_info[0] == "+":
        query = f"SELECT CustomerId FROM Customer WHERE Phone = '{customer_info}';"
        result = db.run(query)
        formatted_result = ast.literal_eval(result)
        if formatted_result:
            return formatted_result[0][0]
        
    elif "@" in customer_info:
        query = f"SELECT CustomerId FROM Customer WHERE Email = '{customer_info}';"
        result = db.run(query)
        formatted_result = ast.literal_eval(result)
        if formatted_result:
            return formatted_result[0][0]
    
    return None


def verify_user_info(state: Customer_Support_State, config: RunnableConfig):
    
    if not state.get('customer_id'):
        
        system_instructions = """Extract the customer identifier from the user's message.
The identifier can be:
- customer ID (number)
- email
- phone number

IMPORTANT:
- You MUST always return a valid JSON using the schema.
- If no identifier is found, return an empty string for customer_identifier.
- Do NOT return null."""
        
        user_input = state.get('messages', [])
        
        if not user_input:
            return {"messages": [AIMessage(content="Please provide your customer ID, email, or phone number.")]}
        
        last_message = user_input[-1] if user_input else ""
        
        parsed_info = structured_llm.invoke([SystemMessage(content=system_instructions), last_message])
        
        identifier = parsed_info.customer_identifier.strip()
        
        # If no identifier provided, ask for it
        if not identifier:
            response = llm.invoke([SystemMessage(content="Ask the user for their customer ID, email, or phone number.")] + user_input)
            return {"messages": [response]}
        
        # Try to find customer
        customer_id = get_user_id(identifier)
        
        if customer_id is not None:
            intent_message = SystemMessage(
                content=f"Thank you for providing your information! I was able to verify your account with customer id {customer_id}."
            )
            return {
                "customer_id": customer_id,
                "messages": [intent_message]
            }
        else:
            response = llm.invoke([SystemMessage(content="The identifier was not found. Ask the user to provide a valid customer ID, email, or phone number.")] + user_input)
            return {"messages": [response]}
        
    else:
        return {}