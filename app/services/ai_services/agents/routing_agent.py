import uuid

from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.store.memory import InMemoryStore

from langgraph_supervisor import create_supervisor

from app.services.ai_services.agents.invoice_agent import invoice_agent
from app.services.ai_services.agents.music_agent import find_music_agent
from app.schemas.customer_suppprt_schema import Supervisor_Agent_State
from app.core.config import Config


llm = Config().get_oss_llm()

checkpointer = MemorySaver()
in_memory_store = InMemoryStore()

supervisor_prompt = """You are an expert customer support assistant for a digital music store. 
You are dedicated to providing exceptional service and ensuring customer queries are answered thoroughly. 
You have a team of subagents that you can use to help answer queries from customers. 
Your primary role is to serve as a supervisor/planner for this multi-agent team that helps answer queries from customers. 

Your team is composed of two subagents that you can use to help answer the customer's request:
1. music_catalog_information_subagent: this subagent has access to user's saved music preferences. It can also retrieve information about the digital music store's music 
catalog (albums, tracks, songs, etc.) from the database. 
3. invoice_information_subagent: this subagent is able to retrieve information about a customer's past purchases or invoices 
from the database. 

Based on the existing steps that have been taken in the messages, your role is to generate the next subagent that needs to be called. 
This could be one step in an inquiry that needs multiple sub-agent calls. """

supervisor_prebuilt_workflow = create_supervisor(
    model = llm,
    agents = [invoice_agent, find_music_agent],
    prompt = (supervisor_prompt),
    state_schema = Supervisor_Agent_State,
    output_mode = "last_message"
)

supervisor_prebuilt = supervisor_prebuilt_workflow.compile(
    name = "master-agent",
    store = in_memory_store,
    checkpointer = checkpointer
)

# thread_id = uuid.uuid4()

# question = "My customer ID is 1. How much was my most recent purchase? What albums do you have by U2?"

# config = {"configurable": {"thread_id": thread_id}}

# result = supervisor_prebuilt.invoke({"messages": [HumanMessage(content=question)], "remaining_steps":10}, config=config)

# for message in result["messages"]:
#     message.pretty_print()