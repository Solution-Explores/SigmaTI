from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import re
import requests

app = FastAPI(title="SIGMA - Mini MVP Integrado")

# --- LIBERAÇÃO DE SEGURANÇA DO NAVEGADOR (CORS) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Autoriza o painel React a comunicar com a API
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# --------------------------------------------------

class AlertaRede(BaseModel):
    equipamento: str
    ip_origem: str
    descricao_erro: str

def anonimizar_dados(texto: str) -> str:
    texto_limpo = re.sub(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', '[IP_MASCARADO]', texto)
    texto_limpo = texto_limpo.replace("dr.joao", "[USUARIO_MEDICO]")
    return texto_limpo

@app.post("/api/alertas")
async def receber_alerta(alerta: AlertaRede):
    # 1. Aplica a anonimização irreversível (Conformidade com a LGPD)
    erro_anonimizado = anonimizar_dados(alerta.descricao_erro)
    
    prompt_enviado = f"Equipamento: {alerta.equipamento} | Erro: {erro_anonimizado}. Forneça um diagnóstico de rede curto e direto."
    
    # 2. Chamada real ao OpenRouter (Modelo Llama 3 Gratuito)
    OPENROUTER_API_KEY = "" 
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "qwen/qwen3.8-27b:free",
        "messages": [
            {"role": "system", "content": "És um engenheiro de redes sénior de um hospital oncológico. Responde de forma técnica e concisa."},
            {"role": "user", "content": prompt_enviado}
        ]
    }
    
    try:
        resposta_api = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
        dados_resposta = resposta_api.json()
        
        if resposta_api.status_code == 200:
            diagnostico_ia = dados_resposta['choices'][0]['message']['content']
        else:
            erro_msg = dados_resposta.get("error", {}).get("message", "Erro desconhecido")
            diagnostico_ia = f"Recusa da OpenRouter (Erro {resposta_api.status_code}): {erro_msg}"
            
    except Exception as e:
        diagnostico_ia = f"Erro no código Python: {str(e)}"
    
    # 3. Retorno para o Frontend (O bloco que devolve a resposta)
    return {
        "status": "Incidente Registrado",
        "dados_enviados_nuvem": prompt_enviado,
        "diagnostico_ia": diagnostico_ia
    }