import os
import json
import re
import time
import asyncio
from openai import AsyncOpenAI
from prompts import system_prompt
from actions import available_actions

# Ollama provides an OpenAI-compatible API at localhost:11434
client = AsyncOpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"  # Ollama doesn't require a real API key
)

async def stream_agent(user_input: str):
    """
    Generator that yields events from the agent.
    Events are certain types: 'thought', 'tool', 'answer', 'error', 'info'.
    """
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_input}
    ]

    turn_count = 0
    max_turns = 5  # Reduced to prevent excessive looping
    
    yield {"type": "thought", "content": "Thinking..."}

    yield {"type": "thought", "content": "Thinking..."}

    previous_actions = {} # Map action_str -> result
    first_tool_result = None  # Track first tool result for duplicate fallback
    seen_results = set() # Set of result strings to detect semantic loops
    consecutive_failures = 0  # Track parsing failures

    while turn_count < max_turns:
        turn_count += 1
        
        try:
            response = await client.chat.completions.create(
                model="mistral",  # local Ollama model
                messages=messages,
                temperature=0,
                stop=["Observation:"]
            )
        except Exception as e:
            yield {"type": "error", "content": f"API Error: {e}"}
            return

        result_text = response.choices[0].message.content
        
        # Add the model's reply to history
        messages.append({"role": "assistant", "content": result_text})

        # Check if the model wants to run an action
        if "Action:" in result_text and "PAUSE" in result_text:
            
            # Parse the action
            action_pattern = r'Action:\s*(\{.*?\})\s*PAUSE'
            match = re.search(action_pattern, result_text, re.DOTALL)
            
            if match:
                consecutive_failures = 0  # Reset failure counter
                json_str = match.group(1)
                try:
                    # Normalize JSON for deduplication (ignore whitespace differences)
                    action_data = json.loads(json_str)
                    action_key = json.dumps(action_data, sort_keys=True)
                    
                    # Deduplication check
                    if action_key in previous_actions:
                        # Force the model to answer instead of repeating - hard stop
                        # Use first_tool_result (most likely matches original query) if available
                        cached_result = previous_actions[action_key]
                        answer_result = first_tool_result if first_tool_result else cached_result
                        yield {"type": "thought", "content": "Duplicate tool call detected. Using cached result to answer."}
                        yield {"type": "answer", "content": answer_result}
                        return
                    else:
                        # Will be populated after execution
                        # We temporarily add it with a placeholder or wait until after execution
                        # Better to add it after we get the result, but to be safe against self-loops in same turn (unlikely), 
                        # we can add it now. But we need the result.
                        # unique key for the set was fine, but map needs value.
                        pass # wait to store until we have result
                        action_data = json.loads(json_str)
                        function_name = action_data.get("function_name")
                        function_params = action_data.get("function_params", {})
                        
                        yield {"type": "tool", "content": f"Running {function_name}..."}
                        
                        if function_name in available_actions:
                            # Execute the function
                            tool_function = available_actions[function_name]
                            # Run synchronous tools in a separate thread to prevent blocking
                            action_result = await asyncio.to_thread(tool_function, **function_params)
                        else:
                            action_result = f"Error: Tool '{function_name}' not found."
                        
                        # DETERMINISTIC STOPPING: Force answer after first successful info-retrieval tool
                        # Don't rely on LLM to decide when to stop - enforce it programmatically
                        if function_name in ("web_search", "get_weather") and not action_result.startswith("Error"):
                            yield {"type": "thought", "content": f"Got result. Answering immediately."}
                            yield {"type": "answer", "content": action_result}
                            return
                        
                        # Store result for deduplication (for tools that don't force-stop)
                        previous_actions[action_key] = str(action_result)[:500]
                        
                        # Track first tool result for fallback
                        if first_tool_result is None:
                            first_tool_result = str(action_result)[:500] 
                        
                        # Result-based dedup (semantic loop detection)
                        result_str = str(action_result).strip()
                        if result_str in seen_results:
                            action_result = f"{result_str}\n\n(SYSTEM NOTE: You have received this exact information in a previous turn. It likely did not help then, so it will not help now. If you have the answer, output it immediately using `Answer:`. Otherwise, try a completely different approach or tool.)"
                        else:
                             seen_results.add(result_str)

                except json.JSONDecodeError:
                    action_result = "Error: Failed to decode Action JSON. Please provide an Answer."
                except Exception as e:
                    action_result = f"Error executing tool: {e}"
                
                # Create the observation message
                observation_msg = f"Observation: {action_result}"
                messages.append({"role": "user", "content": observation_msg})
                
                # Yield the observation result as a thought/info
                yield {"type": "thought", "content": f"Observed: {str(action_result)[:200]}..."}

            else:
                # Pattern didn't match - could be malformed, force an answer
                consecutive_failures += 1
                if consecutive_failures >= 2:
                    yield {"type": "error", "content": "Multiple parsing failures. Stopping."}
                    return
                messages.append({"role": "user", "content": "Observation: Error parsing action format. Please provide your Answer directly."})
                yield {"type": "thought", "content": "Error parsing action, retrying..."}

        else:
            # If no Action, assume it's the final answer
            final_content = result_text
            
            if "Answer:" in result_text:
                final_content = result_text.split("Answer:", 1)[1].strip()
            else:
                # Regex to remove "Thought: ..." block at the start
                final_content = re.sub(r'^Thought:.*?\n\n', '', result_text, flags=re.DOTALL).strip()
                if not final_content:
                    final_content = result_text.replace("Thought:", "").strip()

            yield {"type": "answer", "content": final_content}
            return
        
    if turn_count >= max_turns:
        yield {"type": "error", "content": "Max turns reached without final answer."}

async def run_agent_async(user_input: str):
    """
    Wrapper for CLI compatibility using the generator.
    """
    print(f"User: {user_input}")
    
    async for event in stream_agent(user_input):
        etype = event["type"]
        content = event["content"]
        
        if etype == "thought":
            print(f"[Thought] {content}")
        elif etype == "tool":
            print(f"[Tool] {content}")
        elif etype == "answer":
            print(f"\nAnswer: {content}")
        elif etype == "error":
            print(f"\n[Error] {content}")

def run_agent(user_input: str):
    asyncio.run(run_agent_async(user_input))

if __name__ == "__main__":
    while True:
        try:
            user_q = input("\nEnter your question (or 'quit' to exit): ")
            if not user_q.strip():
                continue
            if user_q.lower() in ['quit', 'exit']:
                break
            run_agent(user_q)
        except KeyboardInterrupt:
            break
