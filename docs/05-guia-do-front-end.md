# ETAPA 5 — GUIA DO FRONT-END (entregue e integrado)

> Este documento descreve a **interface** do sistema que foi construída e
> integrada ao back-end. Ele é o complemento do
> [03-guia-integracao-front-end.md](03-guia-integracao-front-end.md) (que é
> o **contrato da API**) e do
> [04-relatorio.md](04-relatorio.md) (que explica o trabalho como um todo).

---

## 1. O que foi entregue

Uma interface web completa em **HTML + CSS + Bootstrap 5 + JavaScript puro**
(sem frameworks, sem build, sem instalação), com **7 telas**:

| # | Tela | Arquivo | O que faz |
|---|---|---|---|
| 1 | **Login** | `index.html` | Autentica o usuário (`POST /api/auth/login`) e guarda a sessão |
| 2 | **Painel principal** | `index.html` | Totais, consultas de hoje/pendentes, faturamento, status e próximas consultas |
| 3 | **Pacientes** | `pacientes.html` | CRUD + busca |
| 4 | **Dentistas** | `dentistas.html` | CRUD + busca |
| 5 | **Procedimentos** | `procedimentos.html` | CRUD + busca + preço em R$ |
| 6 | **Consultas** | `consultas.html` | CRUD + filtros (texto, status, data) e agenda com JOIN |
| 7 | **Usuários** | `usuarios.html` | CRUD de usuários e perfis |

Requisitos da atividade atendidos pela interface:

- ✅ **Tela inicial / painel principal** (com indicadores do banco);
- ✅ **Menu de navegação** (lateral, com o item ativo destacado);
- ✅ **Cadastro** (formulário em modal, com validação);
- ✅ **Listagem** (tabelas com total de registros);
- ✅ **Consulta / pesquisa** (campo de busca com filtro automático);
- ✅ **Edição** (modal pré-preenchido);
- ✅ **Exclusão** (modal de confirmação em português);
- ✅ **Integração funcional com o banco** (tudo via API REST, gravando no MySQL).

---

## 2. Como executar

```powershell
# 1) ligar o banco de dados
Start-Service MySQL84

# 2) subir a aplicação (telas + API no mesmo endereço)
iniciar.bat
```

3. Abra **<http://127.0.0.1:5000>** e entre com **`admin` / `senha123`**.

> O Flask serve **as telas e a API** no mesmo endereço: `/` entrega a interface
> e `/api/...` entrega os dados. Não existe servidor extra para configurar.

---

## 3. Estrutura de arquivos do front-end

```
front-end/
├── index.html            # login + painel principal
├── pacientes.html        # CRUD de pacientes
├── dentistas.html        # CRUD de dentistas
├── procedimentos.html    # CRUD de procedimentos
├── consultas.html        # agenda de consultas (JOIN)
├── usuarios.html         # CRUD de usuários
└── assets/
    ├── css/estilo.css    # layout (menu lateral, cards, tabelas) e paleta
    ├── js/
    │   ├── api.js        # camada de comunicação com a API (fetch + erros)
    │   ├── layout.js     # menu, topo, sessão, avisos, modal, formatação
    │   ├── painel.js     # login + indicadores
    │   ├── pacientes.js  # CRUD de pacientes
    │   ├── dentistas.js  # CRUD de dentistas
    │   ├── procedimentos.js
    │   ├── consultas.js
    │   └── usuarios.js
    └── vendor/           # Bootstrap 5.3.3 + Bootstrap Icons 1.11.3 (locais)
        ├── bootstrap/css|js
        └── bootstrap-icons/css|fonts
```

**O que mexer em cada arquivo**

| Arquivo | Responsabilidade |
|---|---|
| `api.js` | Único lugar que fala com a API. Se a porta/URL mudar, muda só aqui |
| `layout.js` | Menu lateral, cabeçalho, login/sessão, toasts, modal de confirmação, formatação de data/hora/moeda |
| `estilo.css` | Cores, menu lateral, cards, tabelas, responsividade |
| `*-*.js` (uma por tela) | Carrega os dados, monta a tabela, trata o formulário |
| `*.html` | Estrutura da tela e do formulário (sem lógica) |

---

## 4. Tela a tela

### 4.1 Login (`index.html`)

- Card centralizado com a marca da clínica;
- Campos **usuário** e **senha**;
- Erro da API exibido no próprio formulário (`corpo.erro`);
- Em caso de sucesso, o usuário é gravado em `localStorage` (chave
  `clinica_usuario`) e o painel é carregado;
- Botão **Sair** no topo apaga a sessão e volta ao login.

### 4.2 Painel (`index.html`)

Consome `GET /api/painel/resumo` e mostra:

- 5 indicadores: pacientes, dentistas, procedimentos, consultas, usuários;
- consultas de hoje, consultas pendentes e faturamento concluído (R$);
- lista de **consultas por status** (com badges coloridos);
- tabela de **próximas 5 consultas agendadas** (com dados do JOIN).

### 4.3 Pacientes / Dentistas / Procedimentos / Usuários

Mesmo padrão em todas:

1. Cabeçalho com **total de registros** + **campo de busca** + botão **novo**;
2. Tabela com os dados e botões **editar** / **excluir**;
3. **Modal de cadastro/edição** com validação do navegador (`required`,
   `type="email"`, `type="date"`, `minlength`);
4. Ao salvar: `POST` (novo) ou `PUT` (edição) e a lista é recarregada;
5. Ao excluir: modal de confirmação → `DELETE` → aviso de sucesso.

Detalhes por tela:

| Tela | Campos do formulário | Observações |
|---|---|---|
| Pacientes | nome\*, cpf\*, data_nascimento\*, telefone, email, endereco | CPF validado com dígitos verificadores pelo back-end |
| Dentistas | nome\*, cro\*, especialidade, telefone, email, ativo | "Ativo" em switch; badge verde/cinza na tabela |
| Procedimentos | nome\*, preço\*, descrição, duração | Preço exibido em **R$**; aceita vírgula ou ponto |
| Usuários | nome_usuario\*, nome_completo\*, senha\*, perfil, ativo | Na edição a senha é **opcional**; nunca é exibida |

### 4.4 Consultas (a tela do JOIN)

- **Filtros**: texto livre, status (select) e data (date) — todos enviados à
  API (`?busca=`, `?status=`, `?data=`);
- **Tabela** com paciente + CPF, dentista + CRO, procedimento + preço,
  status (badge colorido) e observações — tudo já resolvido pelo `JOIN`;
- **Formulário** com três `<select>` preenchidos pela API
  (`/api/pacientes`, `/api/dentistas`, `/api/procedimentos`) e campo
  `datetime-local` para a data/hora.

---

## 5. Como o front conversa com o back

```
Usuário clica em "Salvar"
        │
        ▼
   <form> do navegador  ── validação HTML5 (required, email, date...)
        │  submit
        ▼
  pacientes.js / consultas.js ...  ── monta o JSON com os campos
        │
        ▼
      api.js  ── fetch(POST /api/pacientes) + Content-Type: application/json
        │
        ▼
    Flask (back-end)  ── valida (validacao.py) → executa o SQL → MySQL
        │
        ▼
   resposta JSON  { "mensagem": "...", "dados": { "id": 7 } }
        │
        ▼
  api.js devolve o objeto → a tela mostra o toast e recarrega a lista
```

Regras seguidas (as mesmas do contrato da API):

| Situação | Tratamento no front |
|---|---|
| Sucesso | Toast verde com `mensagem` da API |
| Erro (400/401/404/409) | Toast vermelho com o texto de `corpo.erro` |
| API fora do ar | Mensagem amigável pedindo para ligar o back-end |
| Sessão expirada/ausente | Redireciona para o login |

O `api.js` escolhe a URL sozinho: se as telas estão sendo servidas pelo Flask
(porta 5000) usa caminho relativo (`/api/...`); se forem servidas por outro
servidor estático, usa `http://127.0.0.1:5000/api/...` (o CORS já está
liberado no back-end).

---

## 6. Mapeamento campo a campo (tela → API → banco)

| Tela | Campo na tela | Campo na API | Coluna no MySQL |
|---|---|---|---|
| Pacientes | Nome completo | `nome` | `pacientes.nome` |
| | CPF | `cpf` | `pacientes.cpf` |
| | Nascimento | `data_nascimento` | `pacientes.data_nascimento` |
| | Telefone / E-mail / Endereço | `telefone` / `email` / `endereco` | idem |
| Dentistas | Nome / CRO / Especialidade | `nome` / `cro` / `especialidade` | `dentistas.*` |
| | Ativo | `ativo` (1/0) | `dentistas.ativo` |
| Procedimentos | Nome / Preço / Duração | `nome` / `preco` / `duracao_minutos` | `procedimentos.*` |
| Consultas | Paciente (select) | `paciente_id` | `consultas.paciente_id` (FK) |
| | Dentista (select) | `dentista_id` | `consultas.dentista_id` (FK) |
| | Procedimento (select) | `procedimento_id` | `consultas.procedimento_id` (FK) |
| | Data e hora | `data_hora` (`2026-11-19 15:30`) | `consultas.data_hora` |
| | Status | `status` | `consultas.status` (ENUM) |
| Usuários | Usuário / Senha / Perfil | `nome_usuario` / `senha` / `perfil` | `usuarios.*` |

---

## 7. Decisões técnicas do front-end (o "porquê")

**Por que HTML/CSS/JavaScript puro, sem React/Vue?**
A atividade sugere HTML, CSS e Bootstrap. Sem framework, não há build, nem
`npm install`, nem servidor de front-end: o professor abre `iniciar.bat` e a
aplicação funciona. Para um CRUD com 7 telas, o JavaScript puro é suficiente
e mais fácil de explicar.

**Por que o Bootstrap foi baixado para a pasta `assets/vendor`?**
O sistema precisa funcionar **sem internet** — inclusive na apresentação na
escola. Com o CSS e o JS do Bootstrap salvos localmente, nada depende de CDN.

**Por que o Flask serve as telas?**
Entregar a aplicação completa em **um único endereço** (`http://127.0.0.1:5000`)
simplifica a demonstração: um comando, um endereço, sem configuração de portas
ou de CORS. As telas continuam sendo arquivos estáticos independentes — se
outra pessoa quiser trocar o layout, basta editar o HTML/CSS.

**Por que a sessão fica no `localStorage`?**
O back-end desta atividade não exige autenticação obrigatória nas rotas; o
login serve para demonstrate o cadastro de usuários e senha. Guardar o usuário
no navegador permite mostrar "quem está usando" e proteger as telas contra
acesso acidental, sem introduzir tokens ou cookies (complexidade desnecessária
para o escopo).

**Por que as validações existem em dois lugares?**
No navegador (HTML5) para dar retorno imediato ao usuário; no back-end
(`validacao.py`) porque **nunca se confia no cliente** — é a validação do
servidor que protege o banco. O back-end é a referência; a validação do
front-end é só conforto.

**Por que usar `fetch` e não formulários HTML tradicional?**
A API devolve JSON e exige `Content-Type: application/json`; com `fetch` o
front-end controla cabeçalhos, corpo e tratamento de erro — e a mesma função
serve para listar, criar, editar e excluir.

---

## 8. Verificações realizadas

- ✅ Todas as 7 telas carregam sem erro de console;
- ✅ Login com `admin`/`senha123` e recusa de senha errada;
- ✅ **Cadastro pela interface** → registro aparece na tabela e no banco;
- ✅ **Edição pela interface** → alteração persiste (telefone conferido);
- ✅ **Exclusão pela interface** → modal de confirmação → registro removido;
- ✅ **Busca** por nome (paciente) e **filtros** de status/data (consultas);
- ✅ `<select>` da agenda populados com dados reais das 3 tabelas;
- ✅ Valores do banco aparecendo formatados (data, data/hora, R$);
- ✅ Back-end continua com **55 testes automatizados passando**.

---

## 9. Como personalizar (para quem quiser evoluir)

| Objetivo | Onde mexer |
|---|---|
| Trocar as cores da clínica | `assets/css/estilo.css` → variáveis `--clinica-*` |
| Trocar o nome/logo | `index.html` (card de login), `assets/js/layout.js` (menu) |
| Adicionar um campo novo | 1) `database/01_criar_banco_e_tabelas.sql` (ALTER) 2) `app/rotas/xxx.py` (CAMPOS + validação) 3) `front-end/xxx.html` (input) 4) `front-end/assets/js/xxx.js` (montar o JSON) |
| Trocar a paleta do Bootstrap | `assets/vendor/bootstrap/css/bootstrap.min.css` ou as variáveis em `estilo.css` |
| Exigir senha para abrir o sistema | `layout.js` → função `exigirLogin()` já é chamada por todas as telas |

> ⚠️ Regra de ouro ao mexer: **campo novo = banco + back-end + front-end**.
> O front-end sozinho não cria coluna; o back-end sozinho não mostra o campo.
