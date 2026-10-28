# routers/auth.py

- LoginIn · class · L21-L23 — class LoginIn(BaseModel)
- LoginOut · class · L26-L31 — class LoginOut(BaseModel)
- LogoutOut · class · L34-L36 — class LogoutOut(BaseModel)
- UsuarioMeOut · class · L39-L41 — class UsuarioMeOut(BaseModel)
- login · function · L45-L103 — def login(dados: LoginIn, request: Request) -> dict
- logout · function · L107-L119 — def logout(usuario: Usuario = Depends(obter_usuario_atual)) -> dict
- me · function · L123-L127 — def me(usuario: Usuario = Depends(obter_usuario_atual)) -> dict
