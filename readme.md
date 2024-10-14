# Positive Swarm Agents

## Overview

Swarm is an implementation of orchestrating multiple agents using routines and handoffs, designed for flexible and dynamic agent interactions. This project demonstrates how language models can handle complex workflows by dynamically selecting tools and agents based on the conversation flow.

## Features

**Routines:** Predefined steps for an agent to follow, including tasks like refunds, item lookups, etc.
**Handoffs:** Seamless transitions between agents based on user needs (e.g., customer service to refund).
**Tool Integration:** Utilize custom Python functions within the language model flow.
**Memory:** Messages are passed from agent to agent
**Human in the loop:** Intreaction is enabled.

### The core flow involves

Initializing agents with tools (e.g., refund, lookup).
Processing user input and passing it through the relevant agent.
Handling function calls based on agent actions.
Swapping agents if necessary (handoff).
It uses conversational logic between the user and the assistant.

## Extending

Add new tools or agents by defining them and incorporating into the routine or handoff logic.
Add frontend and cloud deployment as needed.

License
MIT
