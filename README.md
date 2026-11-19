# 🦷 Clínica Odontológica — Sistema Web

> **Projeto acadêmico** — Atividade "Aplicação WEB integrada com Banco de Dados"  
> **Tema sorteado:** Clínica Odontológica  
> **Dupla:** Dev Marinhou (back-end) + 01morais (front-end)  
> **Curso/Disciplina:** Análise é desenvolvimento de sistemas / Banco de Dados

Aplicação WEB completa integrada ao banco de dados MySQL. **Sistema pronto e funcionando:** banco de dados, API REST e interface web (HTML + CSS + Bootstrap + JavaScript), servidos juntos em um único endereço.

## ⚡ Iniciar em 3 passos

```powershell
# 1) Garantir que o MySQL está ligado
Start-Service MySQL84

# 2) Subir o sistema (telas + API) — ou duplo clique em iniciar.bat
iniciar.bat

# 3) Abrir no navegador
#    http://127.0.0.1:5000
```

**Login:** `admin` / `senha123`

## 🖥️ Telas do sistema

| Tela | Endereço | O que faz |
|---|---|---|
| Login + Painel | `/` | Autenticação e indicadores da clínica |
| Pacientes | `/pacientes.html` | CRUD + busca |
| Dentistas | `/dentistas.html` | CRUD + busca |
| Procedimentos | `/procedimentos.html` | CRUD + busca + preços |
| Consultas | `/consultas.html` | Agenda com JOIN + filtros |
| Usuários | `/usuarios.html` | CRUD de usuários e perfis |

API REST em `/api/...` — contrato completo em
[docs/03-guia-integracao-front-end.md](docs/03-guia-integracao-front-end.md).

## 📚 Documentação

| Documento | O que é |
|---|---|
| [docs/01-plano-de-execucao.md](docs/01-plano-de-execucao.md) | Planejamento: o que fazer e como |
| [docs/02-passo-a-passo.md](docs/02-passo-a-passo.md) | Passo a passo de instalação e execução |
| [docs/03-guia-integracao-front-end.md](docs/03-guia-integracao-front-end.md) | **Contrato da API** (endpoints, campos, exemplos) |
| [docs/04-relatorio.md](docs/04-relatorio.md) | Relatório: o que, como e por que foi feito |
| [docs/05-guia-do-front-end.md](docs/05-guia-do-front-end.md) | **Guia da interface** (telas, estrutura, personalização) |
| [database/DER.md](database/DER.md) | Diagrama entidade-relacionamento |

## 🗄️ Banco de dados

`clinica_odontologica` — 5 tabelas: `usuarios`, `pacientes`,
`dentistas`, `procedimentos`, `consultas` (3 foreign keys + JOIN na
listagem de consultas). Scripts em [`database/`](database/).

## 🧪 Testes

```powershell
venv\Scripts\python testes\testar_api.py
# Resultado: 55 testes aprovados, 0 falhas
```

## 📁 Estrutura

```
├── run.py / iniciar.bat      # ponto de entrada (API + telas)
├── .env                      # credenciais do banco
├── database/                 # scripts SQL + DER
├── app/
│   ├── banco.py              # pool + SQL
│   ├── validacao.py          # validação das entradas
│   ├── erros.py              # respostas de erro padronizadas
│   └── rotas/                # um módulo por recurso + web.py (serve as telas)
├── front-end/                # interface (HTML + CSS + Bootstrap + JS puro)
├── testes/testar_api.py      # 55 testes automatizados
└── docs/                     # documentação completa
```

## 🔑 Credenciais

| O que | Valor |
|---|---|
| MySQL root | `admin123` |
| Usuário da aplicação | `clinica_app` / `clinica2026` |
| Login do sistema | `admin` / `senha123` |
