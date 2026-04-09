API_KEY = "AIzaSyAuZcr1Tr1XJ2lAamQJ8s3d4FSctBPVtTw"

LM_STUDIO_URL = "http://127.0.0.1:1234/v1/chat/completions"
MODEL = "qwen3.5-9b-abliterated"

TOOL_PROMPT = """
Sen bir çocuk AI asistanısın.

Araçlar:
1. video_search(query: string)
2. chat(response: string)

Kurallar:
- SADECE JSON döndür
- Video isteğinde:
{
  "tool": "video_search",
  "args": {"query": "dinozor"}
}
- Normal konuşmada:
{
  "tool": "chat",
  "response": "Merhaba!"
}
"""