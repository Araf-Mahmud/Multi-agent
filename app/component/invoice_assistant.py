import uuid

from langgraph.prebuilt import ToolNode
from langchain.agents import create_agent
from langgraph.graph import START, StateGraph, END
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage, SystemMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.store.memory import InMemoryStore

from app.core.config import Config
from app.schemas.customer_suppprt_schema import Customer_Support_State
from app.services.ai_services.tools.invoice_info_tools import invloice_info_tools

checkpointer = MemorySaver()
in_memory_store = InMemoryStore()

thread_id = str(uuid.uuid4())
config = {"configurable": {"thread_id": thread_id}}

prompt = """
    You are a subagent among a team of assistants. You are specialized for retrieving and processing invoice information. You are routed for invoice-related portion of the questions, so only respond to them.. 

    You have access to three tools. These tools enable you to retrieve and process invoice information from the database. Here are the tools:
    - get_invoices_by_customer_sorted_by_date: This tool retrieves all invoices for a customer, sorted by invoice date.
    - get_invoices_sorted_by_unit_price: This tool retrieves all invoices for a customer, sorted by unit price.
    - get_employee_by_invoice_and_customer: This tool retrieves the employee information associated with an invoice and a customer.
    
    If you are unable to retrieve the invoice information, inform the customer you are unable to retrieve the information, and ask if they would like to search for something else.
    
    CORE RESPONSIBILITIES:
    - Retrieve and process invoice information from the database
    - Provide detailed information about invoices, including customer details, invoice dates, total amounts, employees associated with the invoice, etc. when the customer asks for it.
    - Always maintain a professional, friendly, and patient demeanor
    
    You may have additional context that you should use to help answer the customer's query. It will be provided to you below:
    """

invoice_agent = create_agent(
    name = "invoice_agent",
    model = Config().get_oss_llm(),
    tools = invloice_info_tools,
    system_prompt = prompt,
    state_schema = Customer_Support_State,
    checkpointer = checkpointer,
    store = in_memory_store
)

# question = "My customer id is 1. What was my most recent invoice, and who was the employee that helped me with it?"

# result = invoice_agent.invoke({"messages": [HumanMessage(content=question)]}, config=config)

# for message in result["messages"]:
#     message.pretty_print()