# llm.py

import os
from functools import wraps, partial
from dotenv import load_dotenv
from langfuse.decorators import observe as langfuse_observe
from langfuse.decorators import langfuse_context
from langsmith import traceable as langsmith_traceable
from langsmith.wrappers import wrap_openai
from langsmith.run_helpers import get_current_run_tree
import inspect
import json
import logging
from llama_index.core.llms import ChatMessage, MessageRole
from llama_index.core.tools import FunctionTool

load_dotenv()
observability_library = os.getenv("LLM_OBSERVABILITY_LIBRARY", 'none').lower()

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s:%(message)s')

def initialize_llm_client():
    logging.info("Initializing LLM client.")
    LLM_API_KEY = os.environ.get('LLM_API_KEY', '')
    LLM_BASE_URL = os.environ.get('LLM_BASE_URL', '')
    LLM_MODEL_ID = os.environ.get('LLM_MODEL_ID', '')
    logging.info("LLM API KEY : ***************")
    logging.info(f"LLM Base URL: {LLM_BASE_URL}")
    logging.info(f"LLM Model ID: {LLM_MODEL_ID}")
    logging.info(f"LLM Observability Library: {observability_library}")

    if not LLM_API_KEY or not LLM_BASE_URL or not LLM_MODEL_ID:
        raise EnvironmentError("LLM_API_KEY or LLM_BASE_URL or LLM_MODEL_ID is not set in the environment variables.")

    if observability_library == "langfuse":
        from langfuse.openai import OpenAI as LangfuseOpenAI
        llm_client = LangfuseOpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL)
    elif observability_library == "langsmith":
        from openai import OpenAI
        llm_client = wrap_openai(OpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL))
    else:
        from openai import OpenAI
        llm_client = OpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL)

    return llm_client

def initialize_async_llm_client():
    logging.info("Initializing LLM client.")
    LLM_API_KEY = os.environ.get('LLM_API_KEY', '')
    LLM_BASE_URL = os.environ.get('LLM_BASE_URL', '')
    LLM_MODEL_ID = os.environ.get('LLM_MODEL_ID', '')
    logging.info("LLM API KEY : ***************")
    logging.info(f"LLM Base URL: {LLM_BASE_URL}")
    logging.info(f"LLM Model ID: {LLM_MODEL_ID}")
    logging.info(f"LLM Observability Library: {observability_library}")

    if not LLM_API_KEY or not LLM_BASE_URL or not LLM_MODEL_ID:
        raise EnvironmentError("LLM_API_KEY or LLM_BASE_URL or LLM_MODEL_ID is not set in the environment variables.")

    if observability_library == "langfuse":
        from langfuse.openai import AsyncOpenAI as LangfuseAsyncOpenAI
        llm_client = LangfuseAsyncOpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL)
    elif observability_library == "langsmith":
        from openai import AsyncOpenAI
        llm_client = wrap_openai(AsyncOpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL))
    else:
        from openai import AsyncOpenAI
        llm_client = AsyncOpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL)

    return llm_client

def noop_decorator(name):
    def decorator(func):
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        wrapper.name = name
        return wrapper
    return decorator

def get_trace_id(observability_library):
    if observability_library == "langfuse":
        return langfuse_context.get_current_trace_id()
    elif observability_library == "langsmith":
        run_tree = get_current_run_tree()
        return run_tree.trace_id if run_tree else ''
    else:
        return ''

def observability_decorator(name=None):
    if observability_library == "langfuse":
        decorator = partial(langfuse_observe, name=name) if name else langfuse_observe
    elif observability_library == "langsmith":
        decorator = partial(langsmith_traceable, name=name) if name else langsmith_traceable
    else:
        decorator = partial(noop_decorator, name=name) if name else noop_decorator

    def wrapper(func):
        @wraps(func)
        def wrapped_func(*args, **kwargs):
            logging.info(f"Entering observability decorator with observability library '{observability_library}' for function: {func.__name__}")
            decorated_func = decorator()(func)
            
            if inspect.isasyncgenfunction(func):
                async def async_gen_wrapper(*args, **kwargs):
                    async for item in decorated_func(*args, **kwargs):
                        trace_id = get_trace_id(observability_library)
                        logging.info(f"Trace ID associated: {trace_id}")
                        yield item
                return async_gen_wrapper(*args, **kwargs)
            elif inspect.iscoroutinefunction(func):
                async def async_wrapper(*args, **kwargs):
                    result = await decorated_func(*args, **kwargs)
                    trace_id = get_trace_id(observability_library)
                    logging.info(f"Trace ID associated: {trace_id}")
                    return result
                return async_wrapper(*args, **kwargs)
            else:
                result = decorated_func(*args, **kwargs)
                trace_id = get_trace_id(observability_library)
                logging.info(f"Trace ID associated: {trace_id}")
                return result
        return wrapped_func
    return wrapper

@observability_decorator(name="json_fixer")
async def json_fixer(text):
    try:
        messages = [
            {
                "role": "system",
                "content": 
                    "Your job is to fix all syntax errors in the JSON data provided and put it into proper JSON. "
                    "You should change nothing about the structure of the output, only fix syntax mistakes."
                    "Always use the same underscores or dashes in the keys of the input JSON."
            },
            {
                "role": "user",
                "content": text
            }
        ]
        llm_client = initialize_llm_client()
        LLM_MODEL_ID_JSON_FIXER = os.environ.get('LLM_MODEL_ID_JSON_FIXER', '')
        response = await llm_client.chat.completions.create(
            model=LLM_MODEL_ID_JSON_FIXER,
            messages=messages,
            temperature=0.9,
            response_format={ "type": "json_object" },
        )
        json_text = json.loads(response.choices[0].message.content)
    except Exception as e:
        logging.error(f"Error in json_fixer: {e}")
        raise e
    return json_text

def openai_message_to_llama_index(message: dict):
    if message['role'] == "assistant" and 'tool_calls' not in message.keys():
        return ChatMessage(
            role=MessageRole.ASSISTANT,
            content=message['content']
        )
    elif message['role'] == "user":
        return ChatMessage(
            role=MessageRole.USER,
            content=message['content']
        )
    elif message['role'] == "assistant" and 'tool_calls' in message.keys():
        return ChatMessage(
            role=MessageRole.ASSISTANT,
            content=None,
            additional_kwargs={
                "tool_calls": [
                    {'id': call['id'], 'function': call['function'], 'type': call['type']}
                    for call in message['tool_calls']
                ]
            }
        )
    elif message['role'] == "tool":
        return ChatMessage(
            role=MessageRole.TOOL,
            content=message['content'],
            additional_kwargs={
                "tool_call_id": message['tool_call_id'],
                "name": message['name'],
            }
        )
    raise Exception(f'Unknown message role "{message["role"]}" was encountered.')

def llama_index_message_to_openai(message: ChatMessage):
    if message.role == "assistant" and message.content is None:
        return {
            "role": message.role,
            'tool_calls': message.additional_kwargs['tool_calls']
        }
    elif message.role == "assistant" and message.content is not None:
        return {
            "role": message.role,
            "content": message.content
        }
    elif message.role == "user":
        return {
            "role": message.role,
            "content": message.content
        }
    elif message.role == "tool":
        return {
            "role": message.role,
            "content": message.content,
            **message.additional_kwargs
        }
    raise Exception(f'Unknown message role "{message.role}" was encountered.')

def make_tools_description(tool_base_functions: list) -> tuple:
    tools = {}
    for func in tool_base_functions:
        tools[func.__name__] = FunctionTool.from_defaults(fn=func)
    
    tool_param_desc = {}
    for func in tool_base_functions:
        tool_param_desc[func.__name__] = inspect.signature(func).parameters 

    tools_desc = ""
    for name, tool in tools.items():
        tools_desc += "\n\n" + tool.metadata.description

    return tools_desc, tools, tool_param_desc
