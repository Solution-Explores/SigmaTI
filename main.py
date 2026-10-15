from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import re
import requests

from config import load_settings

settings = load_settings()

app = FastAPI(title="SIGMA - Mini MVP Integrado")

# Origens do painel configuradas separadamente em cada ambiente.
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.cors_origins),
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
    
    # 2. Chamada ao OpenRouter com chave e modelo definidos no ambiente.
    
    headers = {
        "Authorization": f"Bearer {settings.openrouter_api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": settings.llm_model,
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
