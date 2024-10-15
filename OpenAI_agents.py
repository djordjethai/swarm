# Import necessary modules
from openai import OpenAI  # OpenAI client for API calls
import inspect  # For inspecting function signatures
import json  # For handling JSON data
from pydantic import BaseModel  # For data validation and settings management
from typing import Optional  # For optional type hints

# Initialize the OpenAI API client
client = OpenAI()

def function_to_schema(func) -> dict:
    """
    Generates a JSON schema for a given Python function.

    The schema describes the function's name, parameters, and their types based on Python's type annotations,
    along with other metadata extracted from the function's docstring.

    Args:
        func: The Python function to generate a schema for.

    Returns:
        A dictionary representing the JSON schema of the function.

    Raises:
        ValueError: If the function signature cannot be retrieved.
    """
    # Type mapping from Python types to JSON schema types
    type_map = {
        str: "string",
        int: "integer",
        float: "number",
        bool: "boolean",
        list: "array",
        dict: "object",
        type(None): "null",
    }

    try:
        # Retrieve the signature of the function
        signature = inspect.signature(func)
    except ValueError as e:
        raise ValueError(
            f"Failed to get signature for function {func.__name__}: {str(e)}"
        )

    parameters = {}
    for param in signature.parameters.values():
        # Map parameter type to JSON schema type, defaulting to "string" if not found
        param_type = type_map.get(param.annotation, "string")
        parameters[param.name] = {"type": param_type}

    # Identify required parameters (those without default values)
    required = [
        param.name
        for param in signature.parameters.values()
        if param.default == inspect._empty
    ]

    # Construct the JSON schema dictionary
    return {
        "type": "function",
        "function": {
            "name": func.__name__,
            "description": (func.__doc__ or "").strip(),
            "parameters": {
                "type": "object",
                "properties": parameters,
                "required": required,
            },
        },
    }

class Agent(BaseModel):
    """
    Represents an agent with a name, model, instructions, and tools.

    Attributes:
        name (str): The name of the agent.
        model (str): The OpenAI model to use.
        instructions (str): The system prompt or instructions for the agent.
        tools (list): A list of functions (tools) the agent can use.
    """
    name: str = "Agent"
    model: str = "gpt-4o-mini"
    instructions: str = "You are a helpful Agent"
    tools: list = []

class Response(BaseModel):
    """
    Represents the response from running a full turn with an agent.

    Attributes:
        agent (Optional[Agent]): The agent used in the response (could be a different agent if transferred).
        messages (list): The list of messages exchanged during the turn.
    """
    agent: Optional['Agent']
    messages: list

def execute_tool_call(tool_call, tools, agent_name):
    """
    Executes a tool call by calling the corresponding function with provided arguments.

    Args:
        tool_call: The tool call object containing the function name and arguments.
        tools (dict): A mapping from function names to function objects.
        agent_name (str): The name of the agent executing the tool call.

    Returns:
        The result of executing the tool function.
    """
    # Extract function name and arguments from the tool call
    name = tool_call.function.name
    args = json.loads(tool_call.function.arguments)

    # Print the action being taken by the agent
    print(f"{agent_name}:", f"{name}({args})")

    # Call the corresponding function with provided arguments and return the result
    return tools[name](**args)

def run_full_turn(agent, messages):
    """
    Runs a full conversation turn with the given agent.

    This function handles agent responses, tool calls, and agent transfers.

    Args:
        agent (Agent): The agent to interact with.
        messages (list): The list of messages exchanged so far.

    Returns:
        Response: An object containing the last agent used and new messages generated during the turn.
    """
    current_agent = agent
    num_init_messages = len(messages)
    messages = messages.copy()

    while True:
        # Convert Python functions into tool schemas and create a reverse map
        tool_schemas = [function_to_schema(tool) for tool in current_agent.tools]
        tools = {tool.__name__: tool for tool in current_agent.tools}

        # Get OpenAI completion (the agent's response)
        response = client.chat.completions.create(
            model=current_agent.model,
            messages=[{"role": "system", "content": current_agent.instructions}] + messages,
            tools=tool_schemas or None,
        )
        message = response.choices[0].message
        messages.append(message)

        if message.content:  # Print agent response
            print(f"{current_agent.name}:", message.content)

        if not message.tool_calls:  # If no more tool calls, break the loop
            break

        # Handle tool calls
        for tool_call in message.tool_calls:
            result = execute_tool_call(tool_call, tools, current_agent.name)

            if isinstance(result, Agent):  # If agent transfer, update current agent
                current_agent = result
                result = f"Transferred to {current_agent.name}. Adopt persona immediately."

            # Append the result of the tool call to the messages
            result_message = {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result,
            }
            messages.append(result_message)

    # Return the last agent used and new messages
    return Response(agent=current_agent, messages=messages[num_init_messages:])

def transfer_to_sales_agent():
    """
    Used for anything sales or buying related.

    Returns:
        Agent: The sales agent to handle sales-related queries.
    """
    return sales_agent

def transfer_to_issues_and_repairs():
    """
    Used for issues, repairs, or refunds.

    Returns:
        Agent: The issues and repairs agent to handle support-related queries.
    """
    return issues_and_repairs_agent

def transfer_back_to_triage():
    """
    Call this if the user brings up a topic outside of your purview,
    including escalating to a human.

    Returns:
        Agent: The triage agent to re-evaluate the user's needs.
    """
    return triage_agent

def escalate_to_human(summary):
    """
    Escalates the conversation to a human agent.

    Args:
        summary (str): A brief summary of the issue to be provided to the human agent.

    Note:
        This function will print an escalation report and exit the program.
    """
    print("Escalating to human agent...")
    print("\n=== Escalation Report ===")
    print(f"Summary: {summary}")
    print("=========================\n")
    exit()

def execute_order(product, price: int):
    """
    Processes an order for a product at a given price.

    Args:
        product (str): The name of the product to order.
        price (int): The price of the product in USD.

    Returns:
        str: A message indicating the result of the order execution.
    """
    print("\n\n=== Order Summary ===")
    print(f"Product: {product}")
    print(f"Price: ${price}")
    print("=================\n")
    confirm = input("Confirm order? y/n: ").strip().lower()
    if confirm == "y":
        print("Order execution successful!")
        return "Success"
    else:
        print("Order cancelled!")
        return "User cancelled order."

def look_up_item(search_query):
    """
    Finds an item ID based on a search query.

    Args:
        search_query (str): A description or keywords to search for the item.

    Returns:
        str: The item ID found.
    """
    item_id = "item_132612938"  # In a real application, this would search a database
    print("Found item:", item_id)
    return item_id

def execute_refund(item_id, reason="not provided"):
    """
    Processes a refund for a given item ID and reason.

    Args:
        item_id (str): The ID of the item to refund.
        reason (str, optional): The reason for the refund.

    Returns:
        str: A message indicating the result of the refund execution.
    """
    print("\n\n=== Refund Summary ===")
    print(f"Item ID: {item_id}")
    print(f"Reason: {reason}")
    print("=================\n")
    print("Refund execution successful!")
    return "success"

# Define the Triage Agent, responsible for initial customer interaction and directing them to the right department
triage_agent = Agent(
    name="Triage Agent",
    instructions=(
        "You are a customer service bot for ACME Inc. "
        "Introduce yourself. Always be very brief. "
        "Gather information to direct the customer to the right department. "
        "But make your questions subtle and natural."
    ),
    tools=[transfer_to_sales_agent, transfer_to_issues_and_repairs, escalate_to_human],
)

# Define the Sales Agent, responsible for selling products to the customer
sales_agent = Agent(
    name="Sales Agent",
    instructions=(
        "You are a sales agent for ACME Inc."
        " Always answer in a sentence or less."
        " Follow the following routine with the user:"
        "1. Ask them about any problems in their life related to catching roadrunners.\n"
        "2. Casually mention one of ACME's crazy made-up products can help.\n"
        " - Don't mention price.\n"
        "3. Once the user is bought in, drop a ridiculous price.\n"
        "4. Only after everything, and if the user says yes, "
        "tell them a crazy caveat and execute their order.\n"
    ),
    tools=[execute_order, transfer_back_to_triage],
)

# Define the Issues and Repairs Agent, responsible for handling customer issues and refunds
issues_and_repairs_agent = Agent(
    name="Issues and Repairs Agent",
    instructions=(
        "You are a customer support agent for ACME Inc."
        " Always answer in a sentence or less."
        " Follow the following routine with the user:"
        "1. First, ask probing questions and understand the user's problem deeper.\n"
        " - Unless the user has already provided a reason.\n"
        "2. Propose a fix (make one up).\n"
        "3. ONLY if not satisfied, offer a refund.\n"
        "4. If accepted, search for the ID and then execute refund."
    ),
    tools=[execute_refund, look_up_item, transfer_back_to_triage],
)

# Start with the triage agent
agent = triage_agent
messages = []

# Main interaction loop
while True:
    user = input("User: ")  # Get user input
    messages.append({"role": "user", "content": user})

    # Run a full conversation turn with the current agent
    response = run_full_turn(agent, messages)
    agent = response.agent  # Update the agent in case of agent transfer
    messages.extend(response.messages)  # Add new messages to the conversation history

