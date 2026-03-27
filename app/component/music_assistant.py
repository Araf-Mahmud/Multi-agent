import uuid

from langgraph.prebuilt import ToolNode

from langgraph.graph import START, StateGraph, END
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage, SystemMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.store.memory import InMemoryStore

from app.core.config import Config
from app.schemas.customer_suppprt_schema import Customer_Support_State

from app.services.ai_services.tools.music_catalog_tools import music_tools

graph = StateGraph(Customer_Support_State)

thread_id = str(uuid.uuid4())
config = {"configurable": {"thread_id": thread_id}}

checkpointer = MemorySaver()
in_memory_store = InMemoryStore()

llm = Config().get_oss_llm()

music_tools_node = ToolNode(music_tools)

llm_with_music_tools = llm.bind_tools(music_tools)


def generate_music_assistant_prompt(memory: str = "None") -> str:
    """
    Generate a system prompt for the music assistant agent.
    
    Args:
        memory (str): User preferences and context from long-term memory store
        
    Returns:
        str: Formatted system prompt for the music assistant
    """
    return f"""
    You are a member of the assistant team, your role specifically is to focused on helping customers discover and learn about music in our digital catalog. 
    If you are unable to find playlists, songs, or albums associated with an artist, it is okay. 
    Just inform the customer that the catalog does not have any playlists, songs, or albums associated with that artist.
    You also have context on any saved user preferences, helping you to tailor your response. 
    
    CORE RESPONSIBILITIES:
    - Search and provide accurate information about songs, albums, artists, and playlists
    - Offer relevant recommendations based on customer interests
    - Handle music-related queries with attention to detail
    - Help customers discover new music they might enjoy
    - You are routed only when there are questions related to music catalog; ignore other questions. 
    
    SEARCH GUIDELINES:
    1. Always perform thorough searches before concluding something is unavailable
    2. If exact matches aren't found, try:
       - Checking for alternative spellings
       - Looking for similar artist names
       - Searching by partial matches
       - Checking different versions/remixes
    3. When providing song lists:
       - Include the artist name with each song
       - Mention the album when relevant
       - Note if it's part of any playlists
       - Indicate if there are multiple versions
    
    Additional context is provided below: 

    Prior saved user preferences: {memory}
    
    Message history is also attached.  
    """
    
def find_music(state : Customer_Support_State, config : RunnableConfig):
    
    memory = None
    if "loaded_memory" in state:
        memory = state['loaded_memory']
        
    prompt = generate_music_assistant_prompt(memory)
    
    response = llm_with_music_tools.invoke([SystemMessage(content=prompt)] + state["messages"])
    
    return { "messages" : response }

def should_continue(state : Customer_Support_State, config : RunnableConfig):
    
    last_message = state['messages'][-1]
    
    if not getattr(last_message, "tool_calls"):
        return "end"
    
    return "continue"

graph.add_node('find_music', find_music)
graph.add_node('music_tools_node', music_tools_node)

graph.add_edge(START, 'find_music')
graph.add_conditional_edges(
    'find_music',
    should_continue,
    {
        "continue": "music_tools_node",
        "end": END
    }
)
graph.add_edge('music_tools_node', 'find_music')

find_music_agent = graph.compile(
    name = 'find_music_agent',
    checkpointer = checkpointer,
    store = in_memory_store
)

# question = "I like the Rolling Stones. What songs do you recommend by them or by other artists that I might like?"

# results = find_music_agent.invoke({"messages": [HumanMessage(content=question)]}, config=config)

# for message in results['messages']:
#     message.pretty_print()
