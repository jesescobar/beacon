import logging

import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from app.config import settings
from app.rag.pipeline import search
from app.tools.search_kb import mcp

logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

app = FastAPI(title="Beacon")


class AskRequest(BaseModel):
    question: str


@app.post("/ask")
async def ask(body: AskRequest):
    answer = search(body.question)
    return {"answer": answer}


EXAMPLE_QUESTIONS = [
    "¿Cuáles son los horarios de entrega?",
    "¿Qué pasa si me falta un producto?",
    "¿Qué medios de pago aceptan?",
    "¿Cómo sé si mi dirección tiene cobertura?",
    "¿Puedo usar dos cupones en el mismo pedido?",
]


@app.get("/", response_class=HTMLResponse)
async def index():
    example_buttons = "\n".join(
        f'<button class="example" onclick="useExample({q!r})">{q}</button>'
        for q in EXAMPLE_QUESTIONS
    )
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Beacon</title>
<style>
  :root {{
    color-scheme: light;
    --accent: #4f46e5;
    --accent-dark: #4338ca;
    --ink: #1a1b24;
    --muted: #6b7280;
    --border: #e5e7eb;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    background:
      radial-gradient(900px 500px at 15% -10%, rgba(79,70,229,0.10), transparent 60%),
      radial-gradient(700px 500px at 100% 0%, rgba(79,70,229,0.06), transparent 55%),
      #f4f5f8;
    color: var(--ink);
    display: flex;
    justify-content: center;
    min-height: 100vh;
    padding: 56px 16px;
  }}
  .container {{
    width: 100%;
    max-width: 680px;
  }}
  .header {{
    display: flex;
    align-items: center;
    gap: 14px;
    margin-bottom: 32px;
  }}
  .logo {{
    width: 44px;
    height: 44px;
    flex-shrink: 0;
    border-radius: 12px;
    background: linear-gradient(135deg, var(--accent), #7c3aed);
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 6px 16px rgba(79,70,229,0.35);
  }}
  .logo svg {{ width: 24px; height: 24px; }}
  h1 {{
    margin: 0;
    font-size: 26px;
    font-weight: 700;
    letter-spacing: -0.02em;
  }}
  .subtitle {{
    margin: 2px 0 0;
    color: var(--muted);
    font-size: 14px;
  }}
  .card {{
    background: #fff;
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 28px;
    box-shadow: 0 10px 30px rgba(17, 24, 39, 0.06);
  }}
  .section-label {{
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: var(--muted);
    margin: 0 0 10px;
  }}
  .examples {{
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-bottom: 24px;
  }}
  .example {{
    background: #f6f6fb;
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 8px 14px;
    font-size: 13px;
    cursor: pointer;
    color: #374151;
    transition: background 0.15s ease, border-color 0.15s ease, transform 0.1s ease;
  }}
  .example:hover {{
    background: #ececfb;
    border-color: #d3d3f5;
    transform: translateY(-1px);
  }}
  .input-row {{
    display: flex;
    gap: 10px;
    margin-bottom: 24px;
  }}
  #question {{
    flex: 1;
    padding: 13px 16px;
    border: 1px solid var(--border);
    border-radius: 10px;
    font-size: 15px;
    outline: none;
    transition: border-color 0.15s ease, box-shadow 0.15s ease;
  }}
  #question:focus {{
    border-color: var(--accent);
    box-shadow: 0 0 0 3px rgba(79,70,229,0.12);
  }}
  #ask-btn {{
    background: linear-gradient(135deg, var(--accent), var(--accent-dark));
    color: #fff;
    border: none;
    border-radius: 10px;
    padding: 0 22px;
    font-size: 15px;
    font-weight: 600;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 8px;
    transition: filter 0.15s ease, transform 0.1s ease;
  }}
  #ask-btn:hover:not(:disabled) {{ filter: brightness(1.08); }}
  #ask-btn:active:not(:disabled) {{ transform: scale(0.98); }}
  #ask-btn:disabled {{
    opacity: 0.6;
    cursor: default;
  }}
  .spinner {{
    width: 14px;
    height: 14px;
    border: 2px solid rgba(255,255,255,0.4);
    border-top-color: #fff;
    border-radius: 50%;
    animation: spin 0.7s linear infinite;
    display: none;
  }}
  #ask-btn.loading .spinner {{ display: inline-block; }}
  @keyframes spin {{ to {{ transform: rotate(360deg); }} }}

  #answer-wrap {{ min-height: 20px; }}
  .placeholder {{
    color: #9ca3af;
    font-size: 14px;
    padding: 4px 2px;
  }}
  .loading-row {{
    display: flex;
    align-items: center;
    gap: 10px;
    color: var(--muted);
    font-size: 14px;
    padding: 4px 2px;
  }}
  .loading-dot {{
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: var(--accent);
    animation: pulse 1s ease-in-out infinite;
  }}
  @keyframes pulse {{
    0%, 100% {{ opacity: 0.3; transform: scale(0.85); }}
    50% {{ opacity: 1; transform: scale(1); }}
  }}
  .error-text {{
    color: #b91c1c;
    font-size: 14px;
  }}
  .result-block {{
    background: #fafaff;
    border: 1px solid #ececf7;
    border-left: 3px solid var(--accent);
    border-radius: 10px;
    padding: 16px 18px;
    margin-bottom: 12px;
  }}
  .result-block:last-child {{ margin-bottom: 0; }}
  .result-block h3, .result-block h4, .result-block h5 {{
    margin: 0 0 8px;
    color: var(--ink);
    font-weight: 700;
  }}
  .result-block h3 {{ font-size: 17px; }}
  .result-block h4 {{ font-size: 15px; }}
  .result-block h5 {{ font-size: 14px; }}
  .result-block p {{
    margin: 0 0 8px;
    font-size: 14px;
    line-height: 1.6;
    color: #333640;
  }}
  .result-block ul {{
    margin: 0 0 8px;
    padding-left: 20px;
    font-size: 14px;
    line-height: 1.6;
    color: #333640;
  }}
  .result-block p:last-child, .result-block ul:last-child {{ margin-bottom: 0; }}
  .source-badge {{
    display: inline-block;
    margin-top: 6px;
    font-size: 11px;
    font-weight: 600;
    color: var(--accent-dark);
    background: #ece9fe;
    border-radius: 6px;
    padding: 3px 8px;
    letter-spacing: 0.01em;
  }}
</style>
</head>
<body>
  <div class="container">
    <div class="header">
      <div class="logo">
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M12 2L4 8v3c0 5 3.4 9.4 8 11 4.6-1.6 8-6 8-11V8l-8-6z" fill="white" fill-opacity="0.95"/>
          <circle cx="12" cy="11" r="3" fill="#4f46e5"/>
        </svg>
      </div>
      <div>
        <h1>Beacon</h1>
        <p class="subtitle">Knowledge base assistant</p>
      </div>
    </div>

    <div class="card">
      <p class="section-label">Preguntas frecuentes</p>
      <div class="examples">
{example_buttons}
      </div>
      <div class="input-row">
        <input id="question" type="text" placeholder="Escribí tu pregunta..." />
        <button id="ask-btn" onclick="ask()">
          <span class="spinner"></span>
          <span class="btn-label">Preguntar</span>
        </button>
      </div>
      <p class="section-label">Respuesta</p>
      <div id="answer-wrap">
        <p class="placeholder" id="placeholder">Elegí una pregunta de ejemplo o escribí la tuya para ver la respuesta acá.</p>
      </div>
    </div>
  </div>

<script>
function useExample(q) {{
  document.getElementById('question').value = q;
  document.getElementById('question').focus();
}}

function escapeHtml(str) {{
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
}}

function inlineFormat(str) {{
  return str.replace(/\\*\\*(.+?)\\*\\*/g, '<strong>$1</strong>');
}}

function formatMarkdownLite(text) {{
  const lines = escapeHtml(text).split('\\n');
  let html = '';
  let inList = false;
  const closeList = () => {{ if (inList) {{ html += '</ul>'; inList = false; }} }};
  for (const raw of lines) {{
    const line = raw.trim();
    if (!line) {{ closeList(); continue; }}
    if (line.startsWith('### ')) {{ closeList(); html += `<h5>${{inlineFormat(line.slice(4))}}</h5>`; }}
    else if (line.startsWith('## ')) {{ closeList(); html += `<h4>${{inlineFormat(line.slice(3))}}</h4>`; }}
    else if (line.startsWith('# ')) {{ closeList(); html += `<h3>${{inlineFormat(line.slice(2))}}</h3>`; }}
    else if (line.startsWith('- ')) {{
      if (!inList) {{ html += '<ul>'; inList = true; }}
      html += `<li>${{inlineFormat(line.slice(2))}}</li>`;
    }}
    else {{ closeList(); html += `<p>${{inlineFormat(line)}}</p>`; }}
  }}
  closeList();
  return html;
}}

function renderAnswer(raw) {{
  const wrap = document.getElementById('answer-wrap');
  if (!raw || !raw.trim()) {{
    wrap.innerHTML = '<p class="placeholder">No encontré una respuesta para esa pregunta.</p>';
    return;
  }}
  const hasSources = /\\[Fuente:/.test(raw);
  if (!hasSources) {{
    wrap.innerHTML = `<p class="placeholder" style="color:#374151;">${{escapeHtml(raw).replace(/\\n/g, '<br>')}}</p>`;
    return;
  }}
  const blocks = raw.split(/\\n\\n---\\n\\n/);
  wrap.innerHTML = blocks.map(block => {{
    const match = block.match(/\\[Fuente:\\s*([^\\]]+)\\]\\s*$/);
    const source = match ? match[1].trim() : null;
    const body = match ? block.slice(0, match.index).trim() : block.trim();
    const content = formatMarkdownLite(body);
    const badge = source ? `<span class="source-badge">Fuente: ${{escapeHtml(source)}}</span>` : '';
    return `<div class="result-block">${{content}}${{badge}}</div>`;
  }}).join('');
}}

async function ask() {{
  const input = document.getElementById('question');
  const wrap = document.getElementById('answer-wrap');
  const btn = document.getElementById('ask-btn');
  const question = input.value.trim();
  if (!question) return;

  btn.disabled = true;
  btn.classList.add('loading');
  wrap.innerHTML = `
    <div class="loading-row">
      <span class="loading-dot"></span>
      Consultando...
    </div>
  `;

  try {{
    const res = await fetch('/ask', {{
      method: 'POST',
      headers: {{ 'Content-Type': 'application/json' }},
      body: JSON.stringify({{ question }})
    }});
    if (!res.ok) throw new Error('bad status');
    const data = await res.json();
    renderAnswer(data.answer);
  }} catch (err) {{
    wrap.innerHTML = '<p class="error-text">Ocurrió un error al consultar. Intentá de nuevo.</p>';
  }} finally {{
    btn.disabled = false;
    btn.classList.remove('loading');
  }}
}}

document.getElementById('question').addEventListener('keydown', (e) => {{
  if (e.key === 'Enter') ask();
}});
</script>
</body>
</html>"""


# Monta el server MCP (SSE) en las mismas rutas que ya usa el demo agent
# (GET /sse, POST /messages), sin romper mcp_server_url existente.
app.mount("/", mcp.sse_app())


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=settings.port)
