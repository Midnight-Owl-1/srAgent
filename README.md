This is a very simple LLM powered agent system that uses tools to complete a task. Inspiration was from [here](https://ghuntley.com/agent/)

It's a general purpose tool-using (or Coding) agent that you can invoke from any directory on your computer.
Although the primary purpose is for learning and understanding how tools like Claude Code CLI work.

It's called srAgent (**s**elf **r**ecursive) because I thought it would be a cool idea to have the agent iteratively self improve the same system that it runs on.

## Installation for Windows
1. Make a directory anywhere on your computer, and add 'agent.md' and 'srAgent.py' to it.
2. Create a 'srAgent.bat' file with the following content
```shell
@echo off
python "{PATH_TO_YOUR_FILE}\srAgent.py" %*
```
3. Add the srAgent.bat to your PATH (Windows button -> search 'Edit the System Environmental Variables'-> 'Environment Variables' -> double click 'Path' -> Add an entry including the same {PATH_TO_YOUR_FILE} -> OK)

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

