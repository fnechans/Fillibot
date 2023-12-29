from openai import OpenAI
from typing import List
from dotenv import load_dotenv
from .utils import get_log, omluva
log = get_log()

load_dotenv()
gpt_client = OpenAI()

messages = [ {"role": "system", "content": "You are a intelligent assistant."} ]

def get_reply(content: List[str]) -> str:

    messages.append( 
        {"role": "user", "content": ' '.join(content)}, 
    ) 
    reply = gpt_client.chat.completions.create( 
        model="gpt-3.5-turbo", messages=messages 
    ) 

    reply = reply.choices[0].message
    messages.append({"role": "assistant", "content": str(reply)})            

    return str(reply)