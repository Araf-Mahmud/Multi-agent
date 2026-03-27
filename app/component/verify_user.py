import uuid
from langgraph.graph import START, StateGraph, END
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import MemorySaver
from langgraph.store.memory import InMemoryStore
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage, SystemMessage


from langgraph.types import interrupt

from app.schemas.customer_suppprt_schema import Customer_Support_State
from app.utilities.identifier import verify_user_info
from app.services.ai_services.agents.routing_agent import supervisor_prebuilt

checkpointer = MemorySaver()
in_memory_store = InMemoryStore()

def human_input(state: Customer_Support_State, config: RunnableConfig):
    """
    Human-in-the-loop node that interrupts the workflow to request user input.
    """
    user_input = interrupt("Please provide your customer ID, email, or phone number.")
    
    return {"messages": [user_input]}

def should_interrupt(state : Customer_Support_State, config : RunnableConfig):
    # If customer_id exists, continue to supervisor
    if state.get('customer_id'):
        return "continue"
    # Otherwise, interrupt for human input
    return "interrupt"


verify_graph = StateGraph(Customer_Support_State)

verify_graph.add_node('verify_user_info', verify_user_info)
verify_graph.add_node('human_input', human_input)
verify_graph.add_node('supervisor', supervisor_prebuilt)

verify_graph.add_edge(START, 'verify_user_info')
verify_graph.add_conditional_edges(
    'verify_user_info',
    should_interrupt,
    {
        'continue': 'supervisor',
        'interrupt': 'human_input'
    }
)
verify_graph.add_edge('human_input', 'verify_user_info')
verify_graph.add_edge('supervisor', END)

verify_workflow = verify_graph.compile(
    name="multi_agent_verify",
    checkpointer=checkpointer,
    store=in_memory_store
)

# Only run test code when executed directly
if __name__ == "__main__":
    from langgraph.types import Command
    

    thread_id = uuid.uuid4()
    question = "How much was my most recent purchase?"
    config = {"configurable": {"thread_id": thread_id}}

    result = verify_workflow.invoke({"messages": [HumanMessage(content=question)]}, config=config)
    for message in result["messages"]:
        message.pretty_print()
        
    config = {"configurable": {"thread_id": thread_id}}
    question = "My phone number is +55 (12) 3923-5555."
    
    result = verify_workflow.invoke(Command(resume=question), config=config)
    
    for message in result["messages"]:
        message.pretty_print()