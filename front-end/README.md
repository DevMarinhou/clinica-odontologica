# Front-end — Clínica Odontológica

Interface do sistema em **HTML + CSS + Bootstrap 5 + JavaScript puro**.
Consome a API REST do back-end por `fetch` (nunca fala com o MySQL
diretamente).

## Como usar

As telas são servidas pelo próprio Flask:

```powershell
iniciar.bat          # na raiz do projeto
# abra http://127.0.0.1:5000
```

Se quiser servi-las separadamente (apenas para desenvolvimento):

```powershell
cd front-end
python -m http.server 5500
# as chamadas continuam apontando para http://127.0.0.1:5000 (CORS liberado)
```

## Arquivos

```
front-end/
├── index.html            # login + painel principal
├── pacientes.html        # CRUD de pacientes
├── dentistas.html        # CRUD de dentistas
├── procedimentos.html    # CRUD de procedimentos
├── consultas.html        # agenda de consultas (JOIN)
├── usuarios.html         # CRUD de usuários
└── assets/
    ├── css/estilo.css    # layout e paleta
    ├── js/api.js         # comunicação com a API (fetch + erros)
    ├── js/layout.js      # menu, topo, sessão, avisos, modal, formatação
    ├── js/*.js           # um script por tela
    └── vendor/           # Bootstrap 5.3.3 + ícones (locais, funciona offline)
```

## Documentação completa

- [Guia do front-end](../docs/05-guia-do-front-end.md) — telas, decisões técnicas e personalização
- [Contrato da API](../docs/03-guia-integracao-front-end.md) — endpoints, campos e formatos
