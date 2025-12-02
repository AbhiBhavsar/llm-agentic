from dotenv import load_dotenv
load_dotenv(dotenv_path='../.env')
from typing import Annotated, Literal
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model

llm = init_chat_model(model='gpt-4.1-mini',
                      model_provider='openai')


class State(TypedDict):
    #1. creating state defination
    messages: Annotated[list, add_messages]

#2. Define nodes, and functions are nodes in langgraph
def chatbot(state:State):
    print(state['messages'])
    response = llm.invoke(state.get('messages' ))
    return {"messages":[response]}
    # return state

def sample_node(state: State):
    print(state['messages'])
    return {'messages': 'i\'m a sample node'}
##1. This is a conditional node
def evaluate_response()->Literal['sample_node','endnode']:
    if True:
        return 'sample_node' #node name
    else:
        pass
        #return 'endnode' or END

def endnode(state: State):
    return state

#. Create a builder obj and use compile to create actual graph
graph_builder = StateGraph(State)

#3. Register nodes.
graph_builder.add_node('chatbot',chatbot)
graph_builder.add_node('evaluate_response', evaluate_response)
graph_builder.add_node('sample_node', sample_node)
graph_builder.add_node('endnode', endnode)

#4. Define edges and flow
graph_builder.add_edge(START,'chatbot')

#this will take care of next node call according to conditional nodes return node string
graph_builder.add_conditional_edges('chatbot', evaluate_response) 

graph_builder.add_edge('sample_node', 'endnode')
graph_builder.add_edge('endnode',END )

#5.Compile the graph with all nodes and edges and flow and then we can invoke it
graph = graph_builder.compile()
updated_state = graph.invoke(State({'messages':'Hi lets start'}))
print('updated state: ', updated_state)