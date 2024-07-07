import os
import dotenv
import pprint

from llm_chains.create_chain import create_chain
from doc_preparation import create_vectdb

from langchain_core.output_parsers import StrOutputParser

from langchain.output_parsers import PydanticOutputParser
from langchain_community.tools import DuckDuckGoSearchRun, DuckDuckGoSearchResults
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper

from langchain_community.document_loaders import AsyncChromiumLoader
from langchain_community.document_transformers import BeautifulSoupTransformer


from langchain_community.retrievers import TavilySearchAPIRetriever

from pydantic import BaseModel, Field
from typing import Literal, Optional


dotenv.load_dotenv()

os.environ["TOKENIZERS_PARALLELISM"]='false'

base_root = os.getcwd() + "/"

MODEL_GRADER = os.getenv('MODEL_GRADER')
YAML_GRADER_PATH = f"{base_root}{os.getenv('YAML_GRADER_PATH')}"  

MODEL_QUERY_RAG_REWRITER = os.getenv('MODEL_QUERY_RAG_REWRITER')
YAML_QUERY_RAG_REWRITER_PATH = f"{base_root}{os.getenv('YAML_QUERY_RAG_REWRITER_PATH')}"

MODEL_GENERATOR = os.getenv('MODEL_GENERATOR')
YAML_GENERATOR_PATH = f"{base_root}{os.getenv('YAML_GENERATOR_PATH')}"

MODEL_CRITICS = os.getenv('MODEL_CRITICS')
YAML_CRITICS_PATH = f"{base_root}{os.getenv('YAML_CRITICS_PATH')}"

MODEL_QUERY_WEB_REWRITER = os.getenv('MODEL_QUERY_WEB_REWRITER')
YAML_QUERY_WEB_REWRITER_PATH = f"{base_root}{os.getenv('YAML_QUERY_WEB_REWRITER_PATH')}"

MODEL_SUMMARY = os.getenv('MODEL_SUMMARY')
YAML_SUMMARY_PATH = f"{base_root}{os.getenv('YAML_SUMMARY_PATH')}"

MODEL_RESUME_WEBSEARCH = os.getenv('MODEL_RESUME_WEBSEARCH')
YAML_RESUME_WEB_PATH = f"{base_root}{os.getenv('YAML_RESUME_WEB_PATH')}"

class EvaluationResult(BaseModel):
    Result: Literal['Yes', 'No']= Field(description="The expected outputs are Yes / No ")
    #Explanation: Optional[str] = Field(None, description="Explanation")


def invoke_db():

    POLITICAL_PARTI = os.getenv("POLITICAL_PARTI")

    print("invoke_db politics :", POLITICAL_PARTI)

    if POLITICAL_PARTI in ["nFP", "Ren", "RN"]:
        retriever = create_vectdb.load_chunk_persist_pdf(POLITICAL_PARTI)
    else:
        retriever = create_vectdb.txt_loader_db()

    return retriever


def retrieve(state):
    print("---RETRIEVE---")

    ### Retrieve RAG #### 
    retriever = invoke_db()
    
    question = state["question"]
    memory = state["memory"]
    documents = retriever.invoke(question)

    

    return {"documents": documents, "question": question, "memory":memory}

#### Grader Rag ####
def grade_rag(state):

    print("---GRADE RAG---")

    question = state["question"]
    documents = state["documents"]
    memory=state["memory"]

    parser = PydanticOutputParser(pydantic_object=EvaluationResult)

    grader_dict = {
        "documents": documents,
        "question": question,
        "json_formating": parser.get_format_instructions(), 
        "memory": memory
    }

    critics_grader_chain = create_chain(model=MODEL_GRADER, 
                                        model_output_format='json',
                                        model_temp=0,
                                        yaml_file=YAML_GRADER_PATH, 
                                        yaml_var_name="Template",
                                        format_dict=grader_dict, 
                                        parser=parser)
    
    try :
        grade = critics_grader_chain.Result
    except :
        grade = critics_grader_chain.result
    
    if grade.lower() == "yes":
            print("---GRADE: RAG RELEVANT---")
            rewrite = "No"
    else:
        print("---GRADE: RAG NOT RELEVANT---")
        # We do not include the document in filtered_docs
        # We set a flag to indicate that we want to run web search
        rewrite = "Yes"  

    return {"documents": documents, "question": question, "rewrite": rewrite, "memory":memory}

#### Question Re-writer RAG ####
def rewrite_rag_q(state):
    

    print("---REWRITE QUESTION FOR RAG---")

    question = state["question"]
    documents = state["documents"]
    memory=state["memory"]

    grader_dict = {
        "question": question,
        "memory": memory
    }

    rewrite_question_invole = create_chain(model=MODEL_QUERY_RAG_REWRITER, 
                                        model_output_format=None,
                                        model_temp=0.3,
                                        yaml_file=YAML_QUERY_RAG_REWRITER_PATH, 
                                        yaml_var_name="Template",
                                        format_dict=grader_dict, 
                                        parser=StrOutputParser())
    
    return {"question":rewrite_question_invole, "memory":memory}

#### Web Search ####
def web_search(state):

    #os.environ["TAVILY_API_KEY"] = getpass.getpass()

    print("---WEB SEARCH---")
    question = state["question"]
    documents = state["documents"]
    web_docs = state["web_docs"]
    memory=state["memory"]

    wrapper = DuckDuckGoSearchAPIWrapper(region="fr-fr", time="w", max_results=4)

    #ddg = DuckDuckGoSearchRun(api_wrapper=wrapper)
    web_results = wrapper.results(question, max_results=3)
    
    #retriever = TavilySearchAPIRetriever(k=1)
    #web_results = retriever.invoke(question)
    
    url_list = [item['link'] for item in web_results]
    # Load HTML
    loader = AsyncChromiumLoader(url_list)
    html = loader.load()
    # Transform
    bs_transformer = BeautifulSoupTransformer()
    docs_transformed = bs_transformer.transform_documents(
        html, tags_to_extract=["p"], remove_lines=True, remove_comments=True
    )

    if web_docs is not None:
        web_docs.append(docs_transformed)
    else:
        web_docs = [docs_transformed]


    return {"documents": documents, "question": question, "web_docs": web_docs, "memory":memory} 


#### Generate ####

def generate(state):
  
    print("---GENERATE A RESPONSE---")

    question = state["question"]
    documents = state["documents"]
    web_docs = state["web_docs"]
    memory=state["memory"]
        
    generator_dict = {
        "question": question,
        "documents": documents,
        "web_docs": web_docs,
        "memory": memory
    }

    generation = create_chain(model=MODEL_GENERATOR, 
                                        model_output_format=None,
                                        model_temp=0,
                                        yaml_file=YAML_GENERATOR_PATH, 
                                        yaml_var_name="Template",
                                        format_dict=generator_dict, 
                                        parser=StrOutputParser())
    
    return {"documents": documents, "question": question, "web_docs": web_docs, "generation": generation, "memory":memory}

###### Critics Grader ######
def grade_generation(state):
    
    
    print("---CHECK DOCUMENT RELEVANCE TO QUESTION---")

    documents = state["documents"]
    question = state["question"]
    web_docs = state["web_docs"]
    generation = state["generation"]
    memory = state["memory"]

    
    parser =  PydanticOutputParser(pydantic_object=EvaluationResult)
    critics_dict = {
        "generation": generation,
        "json_formating": parser.get_format_instructions(),
        "memory":memory,
    }

    grader_chain_invoke = create_chain(model=MODEL_CRITICS, 
                                        model_output_format='json',
                                        model_temp=0,
                                        yaml_file=YAML_CRITICS_PATH, 
                                        yaml_var_name="Template",
                                        format_dict=critics_dict, 
                                        parser=parser)
    try :
        grade = grader_chain_invoke.Result
    except :
        grade = grader_chain_invoke.result
    
    if grade.lower() == "yes":
            print("---GRADE: DOCUMENT RELEVANT---")
            need_web_search = "No"
    else:
        print("---GRADE: DOCUMENT NOT RELEVANT---")
        # We do not include the document in filtered_docs
        # We set a flag to indicate that we want to run web search
        need_web_search = "Yes"    
        
    return {"documents": documents, "question": question, "web_docs": web_docs, "generation": generation, "memory":memory, "need_web_search": need_web_search}

###### Web Query Writer ######
def rewrite_query_web(state):

 
    print("---REWRITE QUESTION FOR WEB QUERY---")
    documents = state["documents"]
    question = state["question"]
    memory = state["memory"]

    critics_dict = {
        "question": question,
        "memory": memory
    }

    webquery_chain_invoke = create_chain(model=MODEL_QUERY_WEB_REWRITER, 
                                        model_output_format=None,
                                        model_temp=0.2,
                                        yaml_file=YAML_QUERY_WEB_REWRITER_PATH, 
                                        yaml_var_name="Template",
                                        format_dict=critics_dict, 
                                        parser=StrOutputParser())
    
    return {"documents": documents, "question": webquery_chain_invoke, "memory": memory}
    
def resume_web_search(state:dict)->str:


    print("---resume_web_search---")

    question = state["question"]
    documents = state["documents"]
    web_docs = state["web_docs"]
    memory=state["memory"]
        
    generator_dict = {
        #"question": question,
        "web_docs": web_docs,
        "memory": memory
    }

    resume_web = create_chain(model=MODEL_RESUME_WEBSEARCH, 
                                model_output_format=None,
                                model_temp=0,
                                yaml_file=YAML_RESUME_WEB_PATH, 
                                yaml_var_name="Template",
                                format_dict=generator_dict, 
                                parser=StrOutputParser())
    
    print(question)
    print(resume_web)
    print(memory)

    return {"documents": documents, "question": question, "web_docs": [resume_web], "memory":memory}


## Resume memory LLM

def resume_memory_llm(state:dict)->str:

    
    print("---IN MEMORY WRITING---")

    question = state["question"]
    generation = state["generation"]
    memory = state["memory"]

    if len(memory) > 1:
        memory = state["memory"]
    else:
        memory = ""
        
    generator_dict = {
        "question": question,
        "generation": generation,
        "memory": memory
    }

    summary_invoke = create_chain(model=MODEL_SUMMARY, 
                            model_output_format=None,
                            model_temp=0,
                            yaml_file=YAML_SUMMARY_PATH, 
                            yaml_var_name="Template",
                            format_dict=generator_dict, 
                            parser=StrOutputParser())
    
    return {"memory":summary_invoke}