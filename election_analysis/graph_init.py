from langgraph.graph import END, StateGraph
from IPython.display import Image, display
from langchain_core.runnables.graph import CurveStyle, MermaidDrawMethod, NodeColors
from typing import List
from typing_extensions import TypedDict

from llm_chains import build_chain, router

class GraphState(TypedDict):
    """
    Represents the state of our graph.

    Attributes:
        question: question
        generation: LLM generation
        web_search: whether to add search
        documents: list of documents
        
    """

    question: str
    generation: str
    web_docs: str
    documents: List[str]
    need_web_search: str
    rewrite: str
    memory: str

def build_graph():

    retrieve = build_chain.retrieve
    grade_rag = build_chain.grade_rag
    rewrite_rag_q = build_chain.rewrite_rag_q
    web_search = build_chain.web_search
    resume_websearch = build_chain.resume_web_search
    generate = build_chain.generate
    grade_generation = build_chain.grade_generation
    rewrite_query_web = build_chain.rewrite_query_web

    decide_to_rag = router.decide_to_rag
    decide_to_generate = router.decide_to_generate



    workflow = StateGraph(GraphState)

    # Define the nodes
    workflow.add_node("retrieve", retrieve)  # retrieve
    workflow.add_node("grade_rag", grade_rag)# grade_rag
    workflow.add_node("rewrite_rag_q", rewrite_rag_q)# rewrite_rag_q
    workflow.add_node("web_search", web_search)# web_search
    workflow.add_node("resume_websearch", resume_websearch)# resume_websearch
    workflow.add_node("generate", generate)# generate
    workflow.add_node("grade_generation", grade_generation)# grade_generation
    workflow.add_node("rewrite_query_web", rewrite_query_web)# rewrite_query_web


    workflow.set_entry_point("retrieve")
    workflow.add_edge("retrieve", "grade_rag")
    workflow.add_conditional_edges(
        "grade_rag",
        decide_to_rag,
        {
            "rewrite_question":"rewrite_rag_q",
            "websearch":"web_search"
        },
    )
    workflow.add_edge("rewrite_rag_q", "retrieve")
    workflow.add_edge("web_search", "resume_websearch")
    workflow.add_edge("resume_websearch", "generate")
    workflow.add_edge("generate", "grade_generation")
    workflow.add_conditional_edges(
        "grade_generation",
        decide_to_generate,
        {
            "rewrite_query_web":"rewrite_query_web",
            "useful": END,
        }

    )
    workflow.add_edge("rewrite_query_web", "web_search")

    # Compile
    app = workflow.compile()
    
    return app

def print_graph():
    app = build_graph()
    display(
    Image(
        app.get_graph().draw_mermaid_png(
            draw_method=MermaidDrawMethod.API,
        )
        )
    )
