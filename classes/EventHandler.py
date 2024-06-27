from typing_extensions import override
from openai import AssistantEventHandler
import time

class EventHandler(AssistantEventHandler): 
  start_time = time.time()

  def get_time_diff(self):
    return time.time() - self.start_time
  
  @override
  def on_text_created(self, text) -> None:
    print(f"\nassistant > ", end="", flush=True)
    print("\n---TEXT CREATED---\n")
    print(f"\nt to create first text: {self.get_time_diff()}\n")
      
  @override
  def on_text_delta(self, delta, snapshot):
    # print(delta.value, end="", flush=True)
    yield delta.value
    
  def on_tool_call_created(self, tool_call):
    print(f"\nassistant > {tool_call.type}\n", flush=True)
    # print("\n---TOOL CALL CREATED---\n")
  
  def on_tool_call_delta(self, delta, snapshot):
    # print("\n---TOOL DELTA---\n")
    if delta.type == 'code_interpreter':
      if delta.code_interpreter.input:
        print(delta.code_interpreter.input, end="", flush=True)
      if delta.code_interpreter.outputs:
        print(f"\n\noutput >", flush=True)
        for output in delta.code_interpreter.outputs:
          if output.type == "logs":
            print(f"\n{output.logs}", flush=True)