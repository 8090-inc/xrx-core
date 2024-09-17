---
sidebar_position: 4
---

# Build Your Own Reasoning Application

In this tutorial, we will explore how to create an application with a custom reasoning agent using the xRx framework. The beauty of xRx is that it can accommodate any reasoning agent built in Python, offering flexibility and power for your AI applications.

We'll use xRx's simple reasoning app as our starting point. This app serves as an excellent foundation, showcasing basic functionalities that you can build upon to create your own sophisticated reasoning agent.

Let's dive into the process of adapting and expanding this simple app to suit your specific needs.

## Clone the repository

First, let's get the code onto your local machine:

```bash
git clone --recursive https://github.com/8090-inc/xrx-sample-apps.git
cd xrx-sample-apps/
```

> **Note:** The --recursive flag is crucial here. It ensures that you also clone the xrx-core submodule, which contains the fundamental building blocks of the xRx framework. Without this, your project won't have access to the core functionalities it needs.

If you need to update the submodule later (for instance, if there have been updates to the core framework), you can use:

```bash
git submodule update --init --recursive
```

## Rename the simple app directory

The simple app code resides in the simple-app directory. However, as you're building your own agent, it's a good idea to give it a more descriptive name. This helps in organizing your projects, especially if you plan to create multiple agents.

For example, if you're building a customer support agent:

```bash
mv simple-app customer-support-agent
```

## Implement your reasoning agent

The heart of your agent lives in the file `customer-support-agent/app/agent/executor.py`. This is where you'll implement the core logic of your reasoning agent.

The key function here is `single_turn_agent`. It's called each time a request is sent to your reasoning agent, forming the backbone of your agent's interaction loop.

Here's a simplified version of what this function might look like:

```python
from agent.utils.llm import initialize_llm_client

llm_client = initialize_llm_client()

def single_turn_agent(messages: List[dict]) -> str:
    resp = llm_client.chat.completions.create(
        model=os.environ['LLM_MODEL_ID'],
        messages=messages,
        temperature=0.0,
    )
    message = {
        "role": "assistant",
        "content": resp.choices[0].message.content
    }
    out = {
        "messages": [message],
        "node": "CustomerResponse",
        "output": message['content'],
    }
    return out
```

This function takes in a list of message dictionaries, sends them to a language model, and returns the model's response. The `out` dictionary is crucial - it contains the response message, specifies the node type (in this case, "CustomerResponse"), and provides the output content.

## Creating a Custom Tool

xRx allows you to create custom tools that extend your agent's capabilities. These tools enable your agent to perform specific tasks or access particular information sources, greatly enhancing its functionality. This feature is one of the most powerful aspects of the xRx framework.

Let's walk through the process of creating a custom tool, using a simple calculator as an example. This tool will allow your agent to perform basic arithmetic operations.

First, we'll create the tool function:

```python
from agent_framework import observability_decorator

@observability_decorator(name="calculator")
def calculator(operation: str, x: float, y: float) -> str:
    """
    Perform a basic arithmetic operation.
    
    Args:
    operation (str): The operation to perform (add, subtract, multiply, divide)
    x (float): The first number
    y (float): The second number
    
    Returns:
    str: A string containing the result of the operation
    """
    if operation == "add":
        result = x + y
    elif operation == "subtract":
        result = x - y
    elif operation == "multiply":
        result = x * y
    elif operation == "divide":
        if y != 0:
            result = x / y
        else:
            return "Error: Division by zero"
    else:
        return "Error: Invalid operation"
    
    return f"The result of {x} {operation} {y} is {result}"
```

This function takes an operation and two numbers as input, performs the specified operation, and returns the result as a string. The `@observability_decorator` is a special feature of xRx that allows for monitoring and logging of tool usage.

Now, to make this tool available to your agent, you need to add it to the `tools_dict` in the `single_turn_agent` function:

```python
tools_dict = {
    "get_current_weather": get_current_weather,
    "get_current_time": get_current_time,
    "get_stock_price": get_stock_price,
    "calculator": calculator, # Add your new tool here
}
```

By adding the calculator to this dictionary, you're telling your agent that it has access to this new capability. The language model can now use this tool when it determines that a calculation is necessary to answer a query.

This is just a simple example, but it illustrates the power and flexibility of the tool system in xRx. You could create tools to access databases, call external APIs, process images, or perform any other task that Python can handle. The key is to think about what specific capabilities would enhance your agent's ability to assist users in your particular domain.

Remember, when creating tools, it's important to:
1. Clearly define the tool's purpose and inputs
2. Handle potential errors gracefully
3. Return results in a format that's easy for the agent to interpret and use
4. Use the `@observability_decorator` for monitoring and debugging

As you develop your agent, you'll likely find yourself creating a variety of custom tools to handle different tasks. This modular approach allows you to continually expand and refine your agent's capabilities over time.

## Test your reasoning agent

Once you've implemented your agent and added any custom tools, it's time to test it. You can do this by building and running a Docker container:

```bash
cd customer-support-agent
docker build -t customer-support-agent:latest .
docker run -p 8003:8003 --env-file .env customer-support-agent:latest
```

Your agent will now be accessible at http://localhost:8003.

## Build a custom UI

While the agent works fine via API calls, you might want to create a custom user interface. For information on how to build custom widgets for your UI, refer to the tutorial Create your own Widgets.

## Create your .env file

Your agent will need certain environment variables to function correctly. Create a `.env` file in your project directory based on the provided `.env.example`. Here's a minimal example:

```
LLM_API_KEY="<your Api Key>"
LLM_BASE_URL="https://api.groq.com/openai/v1"
LLM_MODEL_ID="llama3-70b-8192"
```

Make sure to replace the placeholder values with your actual API keys and preferred model ID.

## Deploy the xRx system

With your agent implemented and environment variables set, you're ready to deploy the full xRx system. From your project directory, run:

```bash
docker-compose up --build
```

This command builds and starts all the necessary containers for your xRx application.

## Project Structure

Here's a quick overview of the key components in your project:

- `app/`: Contains the main application code
  - `agent/`: Agent logic
    - `executor.py`: Main agent execution logic
  - `tools/`: Folder containing agent tools
  - `main.py`: FastAPI application setup and endpoint definition
- `test/`: Contains test files
- `xrx-core/`: Core xRx framework (submodule)
- `Dockerfile`: Docker configuration for containerization
- `requirements.txt`: Python dependencies
- `docker-compose.yaml`: Docker Compose configuration file

## API Usage

Your agent exposes a single endpoint via FastAPI:

- `POST /run-reasoning-agent`: Submit a query to the reasoning agent and receive streaming responses.

Here's an example of how to use this endpoint with curl:

```bash
curl -X POST http://localhost:8003/run-reasoning-agent \
-H "Content-Type: application/json" \
-H "Accept: text/event-stream" \
-d '{
"session": {
"id": "1234567890"
},
"messages": [
{"role": "user", "content": "What is the weather like in Paris?"}
]
}'
```

This setup provides a solid foundation for building and customizing your own reasoning agent within the xRx framework. As you continue to develop your agent, remember that the key to creating a powerful and effective AI assistant lies in thoughtfully designing its capabilities, carefully implementing its logic, and thoroughly testing its performance across a wide range of scenarios.

Happy building!