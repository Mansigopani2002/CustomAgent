# CustomAgent 🤖

A **ReAct (Reasoning + Acting) AI Agent** built with Python that can answer questions, search the web, check weather, calculate math, and generate code — all running locally using Ollama.

## What is This Project?

CustomAgent is an autonomous AI assistant that uses the ReAct pattern to reason through problems and take actions using tools. Unlike simple chatbots that just generate text, this agent can:

1. **Think** about what it needs to do
2. **Act** by calling tools (web search, weather, calculator)
3. **Observe** the results
4. **Answer** based on the information gathered

The agent includes **deterministic flow control** to prevent common issues like infinite loops and irrelevant responses.

## Base Model

- **Model**: [Mistral 7B](https://mistral.ai/) via [Ollama](https://ollama.ai/)
- **API**: OpenAI-compatible API endpoint at `localhost:11434`
- **Temperature**: 0 (deterministic outputs)

### Why Mistral?
- Runs locally (no API costs)
- Good instruction-following capabilities
- Fast inference on consumer hardware

## Features

| Feature | Description |
|---------|-------------|
| 🔍 **Web Search** | Search Wikipedia for information using keywords |
| 🌤️ **Weather** | Get current weather for any city worldwide |
| 🧮 **Calculator** | Evaluate mathematical expressions safely |
| 💻 **Code Generation** | Generate Python code with explanations |
| 🌐 **Chat UI** | Web-based interface at `http://localhost:8000` |
| 🔄 **Streaming** | Real-time thought/action streaming |

## Available Tools

### 1. `web_search(query)`
Searches Wikipedia and returns summaries of the top 3 matching results.
```
Example: "who is elon musk" → Returns Wikipedia summary
```

### 2. `get_weather(city)`
Gets current weather conditions using wttr.in API.
```
Example: "London" → "Current weather in London: Partly cloudy +50°F"
```

### 3. `calculate(expression)`
Safely evaluates mathematical expressions.
```
Example: "2 * 3.5 + 10" → "17.0"
```

### 4. `get_response_time(url)`
Measures website response latency.
```
Example: "google.com" → "0.25 seconds"
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         User Input                          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    ReAct Agent Loop                         │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐  │
│  │ Thought │ → │ Action  │ → │Observation│ → │ Answer  │  │
│  └─────────┘    └─────────┘    └─────────┘    └─────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
        ┌──────────┐   ┌──────────┐   ┌──────────┐
        │web_search│   │get_weather│   │calculate │
        └──────────┘   └──────────┘   └──────────┘
```

## Quick Start

### Prerequisites
- Python 3.10+
- [Ollama](https://ollama.ai/) installed with Mistral model

### Installation

```bash
# Clone the repository
git clone https://github.com/Mansigopani2002/CustomAgent.git
cd CustomAgent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Pull Mistral model (if not already)
ollama pull mistral
```

### Running

**CLI Mode:**
```bash
python main.py
```

**Web UI Mode:**
```bash
uvicorn server:app --host 0.0.0.0 --port 8000 --reload
# Open http://localhost:8000
```

## Example Interactions

```
User: What's the weather in New York?
[Tool] Running get_weather...
Answer: Current weather in New York: Cloudy +45°F

User: Who is Rakhi Sawant?
[Tool] Running web_search...
Answer: Rakhi Sawant is an Indian media personality, actress, dancer and politician...

User: Calculate 15% of 250
Answer: 37.5

User: Explain the difference between PostgreSQL and DynamoDB
Answer: PostgreSQL is a traditional RDBMS that uses SQL... DynamoDB is a NoSQL database service by AWS...
```

## Limitations

| Limitation | Description |
|------------|-------------|
| 🧠 **Model Quality** | Mistral 7B is capable but may occasionally misunderstand complex queries |
| 📚 **Wikipedia Only** | Web search is limited to Wikipedia; no real-time news or social media |
| 🌐 **Local Only** | Requires Ollama running locally; no cloud deployment out of the box |
| ⏱️ **Response Time** | Can be slow on CPU-only machines (GPU recommended) |
| 🔁 **Single Tool per Query** | Agent stops after first successful tool call. This is a workaround for reliability — intelligent stopping logic based on query context is yet to be implemented. |
| 📝 **Context Length** | Limited by Mistral's context window (~8K tokens) |

## Key Design Decisions

### Deterministic Stopping
Instead of relying on the LLM to decide when to stop, the agent programmatically forces an answer after the first successful `web_search` or `get_weather` result. This prevents:
- Infinite loops
- Tangential searches
- Parsing failures

### Duplicate Detection
If the agent tries to call the same tool with the same parameters twice, it immediately returns the cached result instead of re-executing.

## Project Structure

```
CustomAgent/
├── main.py           # Agent loop and CLI
├── prompts.py        # System prompt with ReAct instructions
├── actions.py        # Tool implementations
├── server.py         # FastAPI web server
├── static/
│   └── index.html    # Chat UI
├── requirements.txt  # Dependencies
└── README.md         # This file
```

## Contributing

Contributions are welcome! Some ideas:
- Add more tools (e.g., email, calendar, code execution)
- Support for other LLMs (Llama, Phi, etc.)
- Improve the chat UI
- Add conversation memory

---

Built with ❤️ using Python, Ollama, and FastAPI
