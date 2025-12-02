from dotenv import load_dotenv

load_dotenv(dotenv_path="../.env")
from typing import Annotated, Literal
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.mongodb import MongoDBSaver

llm = init_chat_model(model="gpt-4.1-mini", model_provider="openai")


class State(TypedDict):
    # 1. creating state defination
    messages: Annotated[list, add_messages]


# 2. Define nodes, and functions are nodes in langgraph
def chatbot(state: State):
    print(state["messages"])
    response = llm.invoke(state.get("messages"))
    return {"messages": [response]}
    # return state


def endnode(state: State):
    return state


# . Create a builder obj and use compile to create actual graph
graph_builder = StateGraph(State)

# 3. Register nodes.
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("endnode", endnode)

# 4. Define edges and flow
graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)

# 5.Compile the graph with all nodes and edges and flow and then we can invoke it
# graph = graph_builder.compile()


# 6. Create a graph with checkpointer
def compile_graph_with_checkpointer(checkpointer):
    return graph_builder.compile(checkpointer=checkpointer)


DB_URI = "mongodb://admin:admin@localhost:27017"
with MongoDBSaver.from_conn_string(DB_URI) as checkpointer:
    graph = compile_graph_with_checkpointer(checkpointer=checkpointer)
    config = {"configurable": {"thread_id": "abhi"}}

    #Prints all messages at once
    # updated_state = graph.invoke(State({"messages": "Hi lets start"}), 
    #                              config=config)

    #. Stream each mesaage
    for chunk in graph.stream(State({'messages':'to get langgraph details'}), config, 
                              stream_mode="values"):
        
        chunk['messages'][-1].pretty_print()

    # print("updated state: ", updated_state)
