from typing import Annotated, List, Optional
from typing_extensions import TypedDict
from langgraph.managed.is_last_step import RemainingSteps
from pydantic import BaseModel, Field
from langgraph.graph.message import AnyMessage, add_messages

class Customer_Support_State(TypedDict):
    
    customer_id : int
    invoice_id : int
    messages : Annotated[List[AnyMessage],add_messages]
    loaded_memory : str
    # remaining_steps : RemainingSteps
    
class Supervisor_Agent_State(TypedDict):
    
    customer_id : int
    invoice_id : int
    messages : Annotated[List[AnyMessage],add_messages]
    loaded_memory : str
    remaining_steps : RemainingSteps


from pydantic import BaseModel, Field

class UserInfo(BaseModel):
    """Schema for parsing user-provided account information."""
    customer_identifier: str = Field(
        default="", 
        description="Identifier (customer ID, email, or phone). Return empty string if not found."
    )

