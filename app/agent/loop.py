from app.agent.tool_schemas import LOOKUP_OFFERING_SCHEMA
from app.agent.tools import lookup_offering
import json

def request_model_step(
    client,
    model_name: str,
    question: str
):
    internation=client.interactions.create(
        model=model_name,
        input=question,
        tools=[LOOKUP_OFFERING_SCHEMA]
    )
    return internation

def get_function_calls(interaction) -> list:
    return [
        step
        for step in interaction.steps
        if step.type == "function_call"
    ]

def dispatch_tool(call)->dict:
    if call.name=="lookup_offering":
        return lookup_offering(call.arguments)
    else:
        return {"status":"unknown_tool"}

def run_agent(client, model_name: str, question: str):
    model_calls=0
    tool_steps=0
    
    interaction=request_model_step(client,model_name,question)
    model_calls+=1
    while True:
        calls=get_function_calls(interaction)
        if len(calls) == 0:
            return {
                "status": "final",
                "interaction": interaction
            }
        if len(calls) > 1:
            return {"status": "unsupported_multiple_calls"}
        call = calls[0]
        if tool_steps >= 2:
            return {"status": "tool_budget_exhausted"}
        if model_calls >= 3:
            return {"status": "model_budget_exhausted"}
        result=build_function_result(call)
        tool_steps+=1
        interaction=continue_after_tool(client,model_name,interaction,result)
        model_calls+=1


def build_function_result(call) -> dict:
    result=dispatch_tool(call)
    return {
        
    "type": "function_result",
    "name": call.name,
    "call_id": call.id,
    "result": [
        {
            "type": "text",
            "text": json.dumps(result)
        }
    ],

    }
def continue_after_tool(
    client,
    model_name: str,
    interaction,
    function_result: dict
):
    return client.client.interactions.create(
        model=model_name,
        previous_interaction_id=interaction.id,
        input=[function_result],
        tools=[LOOKUP_OFFERING_SCHEMA]
    )
