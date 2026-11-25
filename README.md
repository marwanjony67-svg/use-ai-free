# BudgieOS AI 1.0

A Claude-inspired, BudgieOS Blue chat interface with a small local Python server. It can connect to a local **Ollama** model or an **OpenAI-compatible API** that you configure.

> This project does not unlock Claude, ChatGPT, or paid services for free. Provider access, pricing, rate limits, and terms are controlled by each provider.

## Features

- Responsive dark chat interface with conversation reset and prompt suggestions.
- Local Ollama integration (default; no cloud API key required).
- Optional OpenAI-compatible chat completions endpoint.
- API keys are read from server environment variables and never placed in browser JavaScript.
- No third-party Python packages required.

## Run with Ollama (local AI)

1. Install Python 3.10+ and [Ollama](https://ollama.com/).
2. In a terminal, download a model, for example:

   ```powershell
   ollama pull llama3.2
   ```

3. Start Ollama, then in this project folder run:

   ```powershell
   python server.py
   ```

4. Open http://127.0.0.1:8765 in your browser.

Choose a model in the top bar that you have already pulled with Ollama. For example: `llama3.2`, `qwen2.5`, or `mistral`.

## Use an OpenAI-compatible provider

Set these environment variables before starting the server. Use a provider and model that you are authorized to access.

PowerShell:

```powershell
$env:BUDGIE_PROVIDER = "openai"
$env:AI_BASE_URL = "https://api.openai.com/v1"
$env:AI_API_KEY = "YOUR_API_KEY"
$env:AI_MODEL = "gpt-4o-mini"
python server.py
```

For another compatible provider, set `AI_BASE_URL` to its documented API base URL and `AI_MODEL` to a model available to your account. Never commit real API keys to GitHub.

## Configuration

| Variable | Default | Purpose |
|---|---|---|
| `BUDGIE_HOST` | `127.0.0.1` | Local bind address |
| `BUDGIE_PORT` | `8765` | Web server port |
| `BUDGIE_PROVIDER` | `ollama` | `ollama` or `openai` |
| `OLLAMA_URL` | `http://127.0.0.1:11434` | Ollama server |
| `AI_BASE_URL` | `https://api.openai.com/v1` | Compatible API base |
| `AI_API_KEY` | empty | Server-side provider key |
| `AI_MODEL` | `gpt-4o-mini` | Cloud model name |

## Notes

- The default server binds to localhost only. Do not expose it to the public internet without adding authentication, HTTPS, request limits, and appropriate security controls.
- Chat history currently lives in browser memory and is cleared when you start a new chat or reload the page.
- This is a starter project, not a packaged Windows installer yet.

## License

No license has been selected. Add a license file before redistributing the project.
