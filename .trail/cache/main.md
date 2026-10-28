# main.py

- create_provider_client · function · L32-L33 — def create_provider_client() -> httpx.AsyncClient
- lifespan · function · L37-L41 — async def lifespan(app: FastAPI): # Um pool por aplicação, criado no event loop e fechado no desligamento.
- get_provider_client · function · L44-L45 — async def get_provider_client(request: Request) -> httpx.AsyncClient
- AlertaRede · class · L65-L68 — class AlertaRede(BaseModel)
- consultar_ia · function · L78-L116 — async def consultar_ia(client: httpx.AsyncClient, headers: dict, payload: dict) -> str
- receber_alerta · function · L120-L152 — async def receber_alerta( alerta: AlertaRede, client: Annotated[httpx.AsyncClient, Depends(get_provider_client)], usuario: Annotated[Usuario, Depends(exige_papel("suporte_n1"))], ): # 1. Aplica a anonimização irreversível e fail-closed (Conformidade com a LGPD - RF05)
- obter_status · function · L160-L162 — async def obter_status(usuario: Annotated[Usuario, Depends(exige_papel("suporte_n1"))])
- listar_alertas · function · L166-L168 — async def listar_alertas(usuario: Annotated[Usuario, Depends(exige_papel("suporte_n1"))])
- ver_pacotes · function · L172-L174 — async def ver_pacotes(usuario: Annotated[Usuario, Depends(exige_papel("analista_redes"))])
- listar_incidentes · function · L178-L180 — async def listar_incidentes(usuario: Annotated[Usuario, Depends(exige_papel("analista_redes"))])
- relatorios_gerenciais · function · L184-L186 — async def relatorios_gerenciais(usuario: Annotated[Usuario, Depends(exige_papel("gestor_ti"))])
- listar_usuarios · function · L190-L192 — async def listar_usuarios(usuario: Annotated[Usuario, Depends(exige_papel("gestor_ti"))])
- NovoUsuarioIn · class · L195-L198 — class NovoUsuarioIn(BaseModel)
- criar_usuario · function · L202-L208 — async def criar_usuario( dados: NovoUsuarioIn, usuario: Annotated[Usuario, Depends(exige_papel("gestor_ti"))], )
- rotacionar_chaves · function · L212-L214 — async def rotacionar_chaves(usuario: Annotated[Usuario, Depends(exige_papel("gestor_ti"))])
- acessar_n8n · function · L218-L220 — async def acessar_n8n(usuario: Annotated[Usuario, Depends(exige_papel("gestor_ti"))])
