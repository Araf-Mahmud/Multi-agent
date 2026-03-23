import ast

from typing import Optional
from langchain_core.runnables import RunnableConfig
from langchain.messages import SystemMessage

from app.core.config import Config
from app.schemas.customer_suppprt_schema import UserInfo, Customer_Support_State

from app.db.sqlite3_client import db

llm = Config().get_oss_llm()
structured_llm = llm.with_structured_output(schema = UserInfo)


def get_user_id(customer_info : str) -> Optional[int]:
    
    if customer_info.isdigit():
        return int(customer_info)
    
    elif customer_info[0] == "+":
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


def verify_user_info( state : Customer_Support_State, config : RunnableConfig):
    
    if not state.get('customer_id'):
        
        system_instructions = f"""
        You are a music store agent, where you are trying to verify the customer identity as the first step of the customer support process. 
        Only after their account is verified, you would be able to support them on resolving the issue. 
        In order to verify their identity, one of their customer ID, email, or phone number needs to be provided.
        If the customer has not provided their identifier, please ask them for it.
        If they have provided the identifier but cannot be found, please ask them to revise it.
        """
        
        user_input = state.get('messages')[-1]
        
        parsed_info = structured_llm(SystemMessage(content = system_instructions) + user_input)
        
        identifier = parsed_info.customer_identifier
        
        customer_id = get_user_id(parsed_info) 
        
        if customer_id is not None:
            intent_message = SystemMessage(
                content= f"Thank you for providing your information! I was able to verify your account with customer id {customer_id}."
            )
            return {
                  "customer_id": customer_id,
                  "messages" : [intent_message]
                  }
        else:
            response = llm.invoke([SystemMessage(content=system_instructions)]+state['messages'])
            return {"messages": [response]}
        
    else:
        pass
        