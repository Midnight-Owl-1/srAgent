This simple LLM-powered agent system, inspired by [here](https://ghuntley.com/agent/), is a general-purpose tool-using (or coding) agent that can be invoked from any directory on your computer.

While it can be useful, It's primary purpose is for learning and understanding how tools like Claude Code CLI work. See blog post [here](https://lucasalvo.com/post/building-a-simple-coding-agent-on-a-raspberry-pi-zero) for the motivation behind this project.

It uses a [OpenRouter](https://openrouter.ai/) API calls for LLM usage.

It's called srAgent (**s**elf **r**ecursive) because I thought it would be a cool idea to have the agent iteratively self improve the same system that it runs on.

![Image of app usage in command prompt](https://lucasalvo.com/images/21Mar2026/srAgent-example.png)

## Installation for Windows
1. Make a directory anywhere on your computer, and add 'agent.md' and 'srAgent.py' to it.
2. Open srAgent.py, and add your OpenRouter API key to it
- To make a new one, log into your OpenRouter account -> navigate to [here](https://openrouter.ai/workspaces/default/keys) -> Create -> Give it a name, and a credit limit (try 25 cents to start), no expiration -> copy key
3. You can also change the model here if you want to (try out some different ones!)
4. Create a 'srAgent.bat' file with the following content
```shell
@echo off
python "{PATH_TO_YOUR_FILE}\srAgent.py" %*
```
5. Add the srAgent.bat to your PATH (Windows button -> search 'Edit the System Environmental Variables'-> 'Environment Variables' -> double click 'Path' -> Add an entry including the same {PATH_TO_YOUR_FILE} -> OK)

Once this is done, its ready to use!

## Usage

* Type `srAgent` into command prompt from *any* working directory, then explain to the agent what you want it to do
* You will be prompted for permission for each tool use

## Tools that the Agent can use:

* read\_tool - read the contents of a file (even specific lines)
* list\_tool - lists all of the files and directories in a given path
* python\_tool - lets the agent use an interactive python interpreter to run code, or run a python script on disk
* edit\_tool - lets the agent edit a specific file (either write out fully, or replace sections)
* code\_search - lets the agent search for code patterns similar to using ripgrep (rg)

## Note

This kind of system is inherently dangerous - The agent can (if it wants to) do *anything* with python (including sending your data to random APIs, deleting files or folders, and much more).
Having the permission prompts for each tool use is a safeguard for anything dangerous.
In general though, models have good behaviour. Unless it ingests a prompt injection, it should be fine to run on your system.

