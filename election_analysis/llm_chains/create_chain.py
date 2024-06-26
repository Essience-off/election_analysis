from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import ChatPromptTemplate

import asyncio

import yaml

def load_yaml_file(file_path):
    try:
        with open(file_path) as stream:
            data = yaml.safe_load(stream)
            return data
    except yaml.YAMLError as exc:
        print(f"Error loading YAML: {exc}")
        return None

def create_chain(model:str, 
                 model_output_format:str,
                 model_temp:int,
                 yaml_file:str, 
                 yaml_var_name:str,
                 format_dict:dict, 
                 parser,
                 ):
    
    prompt = load_yaml_file(yaml_file)[yaml_var_name]

    llm = ChatOllama(model=model, 
                            format=model_output_format, 
                            temperature=model_temp,)

    prompt = ChatPromptTemplate.from_messages([
        ("system", prompt['sys']),
        ("user", prompt['user'])
    ])


    if parser:
        chain = prompt | llm | parser
    else:
        chain = prompt | llm

    result = invoke_chain(chain, format_dict)

    result = asyncio.run(result)

    return result


async def invoke_chain(chain, format_dict):
    return await chain.ainvoke(format_dict) 