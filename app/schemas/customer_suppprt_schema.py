from typing import Annotated, List
from typing_extensions import TypedDict
from langgraph.managed.is_last_step import RemainingSteps
from langgraph.graph.message import AnyMessage, add_messages

class Customer_Support_State(TypedDict):
    
    customer_id : int
    invoice_id : int
    messages : Annotated[List[AnyMessage],add_messages]
    loaded_memory : str
    # remaining_steps : RemainingSteps
    


