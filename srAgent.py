import requests
import json
import re
import ast
import os
import subprocess
import sys

# Your configuration
API_KEY = "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"
MODEL = "google/gemini-3-flash-preview"
MAX_ITERATIONS = 5

##GLOBAL VARIABLES
TOOLS = {}
SYSTEM_PROMPT = ""
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

#Decorator to register tools
def tool(name, params, description, example):
    def decorator(func):
        TOOLS[name] = {
            "function": func,
            "parameters": params,
            "description": description,
            "example": example
        }
        return func
    return decorator

#Add the tools to the system prompt
def buildSystemPrompt():
    # Build system prompt with dynamic tool documentation
    with open(os.path.join(SCRIPT_DIR, "agent.md"), "r") as f:
        base_prompt = f.read()

    tools_docs = ""
    for tool_name, tool_info in TOOLS.items():
        tools_docs += f"- {tool_name}({', '.join(tool_info['parameters'])})\n"
        tools_docs += f"    Description: {tool_info['description']}\n"
        tools_docs += f"    Example: {tool_info['example']}\n"

    return base_prompt.replace("{{{INSERT_TOOL_DESCRIPTION_HERE}}}", tools_docs)

def call_llm(messages):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": MODEL,
        "messages": messages,
        "response_format": {"type": "json_object"}
    }
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    
    if response.status_code == 200:
        result = response.json()
        return result['choices'][0]['message']['content']
    else:
        return f"Error: {response.status_code} - {response.text}"

def parse_response(response):
    try:
        data = json.loads(response)
        return data.get("actions", [])
    except Exception as e:
        return [{"type": "thought", "content": f"Failed to parse response: {e}"}]

def execute_tool(tool_content):
    #Extract the tool name and parameters from the tool_content and execute the corresponding function from TOOLS
    match = re.match(r"(\w+)\((.*)\)", tool_content, re.DOTALL)
    if not match:
        return "Error: Invalid tool format."
    
    tool_name, params_str = match.group(1), match.group(2)
    if tool_name not in TOOLS:
        return f"Error: Tool '{tool_name}' not found."
    
    try:
        params = ast.literal_eval(f"({params_str},)")  # wrap in tuple for safe eval
    except Exception as e:
        return f"Error parsing parameters: {e}"
    
    return TOOLS[tool_name]["function"](*params)

def agent_loop(messages, user_input):
    messages.append({"role": "user", "content": user_input})

    iters = 0 
    while iters < MAX_ITERATIONS:
        print(f"\n[Iteration {iters + 1}/{MAX_ITERATIONS}] Calling LLM...")
        response = call_llm(messages)
        response = response.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        messages.append({"role": "assistant", "content": response})
        parsed_response = parse_response(response)
        
        tool_results = []
        
        for item in parsed_response:
            if item["type"] == "thought":
                print(f"[Thought] {item['content']}")
            elif item["type"] == "tool":
                confirm = input(f"\n[Tool Call] {item['content']}\nAllow? (y/n): ").strip().lower()
                if confirm != "y":
                    tool_result = "Tool call denied by user."
                    print("[Denied]")
                else:
                    tool_result = execute_tool(item["content"])
                    print(f"[Tool Result] {tool_result[:200]}{'...' if len(tool_result) > 200 else ''}")
                tool_results.append(f"RESULT OF {item['content']}:\n{tool_result}")
            elif item["type"] == "complete":
                print(f"\n[Complete]\n{item['content']}")
                return
        
        if tool_results:
            messages.append({"role": "user", "content": "\n\n".join(tool_results)})
        
        iters += 1
    print("[Max iterations reached]")

class Tools:
    @staticmethod
    @tool("read_file", ["path", "start_line", "end_line"],
          "Read a file's contents. Optionally pass start_line and end_line (1-indexed, inclusive) to read a specific range. Pass empty strings to read the whole file.",
          'read_file("notes.txt", "", "") or read_file("notes.txt", "10", "20")')
    def read_file(path, start_line="", end_line=""):
        try:
            with open(path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            if start_line or end_line:
                s = int(start_line) - 1 if start_line else 0
                e = int(end_line) if end_line else len(lines)
                lines = lines[s:e]
            return "".join(lines)
        except Exception as e:
            return f"Error [{type(e).__name__}]: {e}"

    @staticmethod
    @tool("list_dir", ["path"],
          "List files and directories at the given path. Directories are suffixed with /.",
          'list_dir("C:/Users/salvo/project")')
    def list_dir(path):
        try:
            entries = []
            for name in os.listdir(path):
                entries.append(name + "/" if os.path.isdir(os.path.join(path, name)) else name)
            return "\n".join(entries)
        except Exception as e:
            return f"Error [{type(e).__name__}]: {e}"

    @staticmethod
    @tool("python_tool", ["code", "filepath"],
          "Execute a Python code snippet or a script file. Pass code as a string and leave filepath empty, or pass an empty string for code and provide a filepath to run a script.",
          'python_tool("print(1 + 1)", "") or python_tool("", "C:/scripts/run.py")')
    def python_tool(code, filepath=""):
        try:
            cmd = [sys.executable, filepath] if filepath else [sys.executable, "-c", code]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            output = result.stdout
            if result.stderr:
                output += "\nSTDERR:\n" + result.stderr
            return output.strip() or "(no output)"
        except Exception as e:
            return f"Error [{type(e).__name__}]: {e}"

    @staticmethod
    @tool("edit_file", ["path", "new_content", "old_string"],
          "Edit a file. If old_string is provided, replaces the first occurrence with new_content. If old_string is empty, overwrites the entire file.",
          'edit_file("notes.txt", "new text here", "old text here") or edit_file("notes.txt", "full file content", "")')
    def edit_file(path, new_content, old_string=""):
        try:
            if old_string:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                if old_string not in content:
                    return "Error: old_string not found in file."
                content = content.replace(old_string, new_content, 1)
            else:
                content = new_content
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            return "File updated successfully."
        except Exception as e:
            return f"Error [{type(e).__name__}]: {e}"

    @staticmethod
    @tool("code_search", ["pattern", "path"],
          "Search for a regex pattern across all files under a directory. Returns matching file paths, line numbers, and lines.",
          'code_search("def agent_loop", "C:/Users/salvo/project")')
    def code_search(pattern, path):
        matches = []
        for root, _, files in os.walk(path):
            for fname in files:
                fpath = os.path.join(root, fname)
                try:
                    with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                        for i, line in enumerate(f, 1):
                            if re.search(pattern, line):
                                matches.append(f"{fpath}:{i}: {line.rstrip()}")
                except Exception:
                    continue
        return "\n".join(matches) or "No matches found."

def main():
    global TOOLS, SYSTEM_PROMPT
    SYSTEM_PROMPT = buildSystemPrompt()

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    print("srAgent ready. Type your request, or 'exit' to quit.\n")
    while True:
        user_input = input("You: ").strip()
        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit"):
            break
        agent_loop(messages, user_input)

main()