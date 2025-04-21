import os

from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel
from agents.run import RunConfig
import chainlit as cl
from openai.types.responses import ResponseTextDeltaEvent
from agents.tool import function_tool

gemini_api_key = "AIzaSyAKvIhBxQBGrZXILRUNc-0v62WOCoVzVpI"


@function_tool("population finder")
def population(country:str) -> str:
    """get population for given country"""
    population = int()
    return f"the current population of {country} as of today data is {population} "
# Check if the API key is present; if not, raise an error
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY is not set. Please ensure it is defined in your .env file.")

#Reference: https://ai.google.dev/gemini-api/docs/openai
external_client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=external_client
)

config = RunConfig(
    model=model,
    model_provider=external_client,
    tracing_disabled=True
)

import asyncio

from agents import Agent, Runner



agent = Agent(
        name="Assistant",
        instructions="You only respond in haikus.",
        tools=[population]
    )

@cl.on_chat_start
async def handle_start():
    cl.user_session.set("chat",[])
    cl.Message(content="Hello Hear to Help you!!!").send()
    # print(result.final_output)
@cl.on_message
async def handle_massage(message: cl.Message):
        history = cl.user_session.get("chat")


        msg = cl.Message(content="")
        await msg.send()


        history.append({"role":"user","content":message.content}) 
        result = Runner.run_streamed(
             agent, input=history
             ,run_config=config
             )
        async for even in result.stream_events():
             if even.type =="raw_response_event" and isinstance(even.data, ResponseTextDeltaEvent):
                #   msg.update((even.data.delta))
                  await msg.stream_token(even.data.delta)             
        history.append({"role":"assistant","content": result.final_output}) 
        cl.user_session.set("chat",history)
        # await cl.Message(content=result.final_output).send()
    
    
