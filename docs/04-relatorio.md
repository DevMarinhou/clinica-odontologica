# ETAPA 4 — RELATÓRIO DO PROJETO
## Sistema Web para Clínica Odontológica

**Atividade:** Desenvolvimento de uma Aplicação WEB com Banco de Dados
**Segmento sorteado:** Clínica Odontológica
**Modalidade:** Trabalho em dupla
**Etapas deste relatório:** Back-end (API + Banco de Dados) **e Front-end**
**Data da apresentação:** 19/11/2026

> **Sobre a divisão do trabalho:** o colega de dupla teve um imprevisto e não
> pôde entregar a interface. Para não comprometer a entrega, **todo o sistema
> foi concluído**: banco de dados, API REST e a interface web (HTML + CSS +
> Bootstrap), já integradas e funcionando juntas em um único endereço.
> A documentação segue dividida por etapa (02 = passo a passo,
> 03 = contrato da API, 05 = guia do front-end) para facilitar a leitura.

---

## 1. Qual problema a aplicação resolve

Uma clínica odontológica precisa controlar, no dia a dia:

- **quem** é o paciente (dados de contato, CPF, nascimento);
- **quem** é o dentista que atende (com registro no conselho — CRO);
- **quais** procedimentos a clínica oferece e quanto custam;
- **quando** cada consulta acontece, com quem e para quê;
- **quem** pode acessar o sistema (usuário e senha).

Antes disso, essas informações costumam viver em cadernos, planilhas ou
agenda de papel — o que gera erro de digitação, consulta perdida,
paciente esquecido e dificuldade de saber "quem atendeu quem".

O sistema entregue resolve isso com **cadastro completo (CRUD),
pesquisa, agendamento com validação de dados e um painel com os
números da clínica**, gravando tudo efetivamente em um banco MySQL.

---

## 2. O que foi feito (entregáveis)

| # | Entregável da atividade | Onde está | Status |
|---|---|---|---|
| 1 | Script SQL de criação do banco e das tabelas | `database/00_*.sql`, `01_criar_banco_e_tabelas.sql`, `02_dados_de_teste.sql` | ✅ |
| 2 | Modelo lógico / diagrama ER | `database/DER.md` | ✅ |
| 3 | Aplicação web funcionando | `iniciar.bat` → <http://127.0.0.1:5000> (telas + API) | ✅ |
| 4 | Operações CRUD implementadas | 5 recursos completos (pacientes, dentistas, procedimentos, consultas, usuários) | ✅ |
| 5 | Registros de teste inseridos | 5–9 por tabela (31 no total) | ✅ |
| 6 | Apresentação (10 min) | Roteiro na seção 8 deste relatório | ✅ a fazer em 19/11 |

### Resumo técnico da entrega

- **Banco:** `clinica_odontologica` com **5 tabelas** (limite máximo),
  todas com `PRIMARY KEY`, 3 `FOREIGN KEY` e tipos de dados adequados;
- **API REST:** 26 rotas cobrindo listagem, busca, cadastro, edição,
  exclusão, login e painel;
- **Interface web:** 7 telas em HTML/CSS/Bootstrap/JavaScript puro,
  servidas pelo próprio Flask no mesmo endereço da API;
- **Testes:** script automatizado com **55 verificações — todas
  passando** (`testes/testar_api.py`) + verificação manual de cada tela
  no navegador (login, CRUD completo, busca e filtros);
- **Documentação:** plano de execução, passo a passo, contrato da API,
  guia do front-end e este relatório.

---

## 3. Como foi feito (o processo)

### 3.1 Etapas percorridas

1. **Leitura da atividade** e extração dos requisitos obrigatórios
   (checklist reproduzido na seção 7);
2. **Planejamento** em `docs/01-plano-de-execucao.md`: escopo, modelo
   de dados, arquitetura, estrutura de pastas e critérios de aceite;
3. **Passo a passo** registrado em `docs/02-passo-a-passo.md`, na ordem
   exata em que tudo foi executado (reproduzível do zero);
4. **Instalação e configuração do ambiente:** MySQL 8.4 (via `winget`),
   serviço `MySQL84` do Windows, usuário da aplicação e ambiente
   virtual Python com as dependências;
5. **Banco de dados:** scripts SQL em 3 arquivos (configuração →
   estrutura → dados), executados e conferidos;
6. **Desenvolvimento da API** em camadas, seguindo a estrutura da
   seção 3.3;
7. **Testes automatizados** cobrindo CRUD, JOIN, login, pesquisa,
   filtros e todos os erros esperados;
8. **Construção da interface web** (7 telas) seguindo exatamente o
   contrato da API documentado, e **integração real** com o back-end;
9. **Validação no navegador** de cada tela (login, CRUD completo,
   busca, filtros e preenchimento dos selects da agenda);
10. **Documentação** dividida por etapa: plano de execução, passo a
    passo, contrato da API, guia do front-end e este relatório.

### 3.2 Como a aplicação se comunica com o banco

```
 Navegador (front-end)          API Flask (Python)              MySQL
 ─────────────────────          ──────────────────              ─────
 fetch('/api/pacientes')  ──►  app/rotas/pacientes.py
                                │ valida os dados recebidos
                                │ monta o SQL com parâmetros (%s)
                                ▼
                              app/banco.py
                                │ pega uma conexão do pool
                                │ cursor.execute(SELECT ...)  ──►  clinica_odontologica
                                │ ◄── linhas do banco ◄──────────  (tabela pacientes)
                                │ converte datas/números p/ JSON
                                ▼
 JSON { total: 6, dados:[…] } ◄── resposta devolvida ao front-end
```

Ponto-chave: **todo o SQL vive em `app/banco.py` e nos arquivos de
rota** (SELECT, INSERT, UPDATE, DELETE e o JOIN das consultas). Os
parâmetros são sempre passados com `%s` (nunca concatenados na
string), o que impede SQL Injection.

### 3.3 Estrutura do código (organizada em arquivos e pastas)

```
clinica-odontologica/
├── run.py                  # sobe a API + as telas
├── iniciar.bat             # inicia com duplo clique
├── requirements.txt        # dependências
├── .env                    # usuário/senha do banco (fora do código)
├── database/               # scripts SQL + DER + script do serviço
├── app/
│   ├── __init__.py         # fábrica da aplicação
│   ├── config.py           # lê o .env
│   ├── banco.py            # pool + todo o SQL
│   ├── validacao.py        # validação das entradas
│   ├── erros.py            # respostas de erro padronizadas
│   └── rotas/              # um módulo por recurso (Blueprints)
│       ├── auth.py  pacientes.py  dentistas.py
│       ├── procedimentos.py  consultas.py  usuarios.py
│       ├── painel.py        # resumo com contagens
│       └── web.py           # serve as telas do front-end
├── front-end/             # INTERFACE (HTML + CSS + Bootstrap + JS puro)
│   ├── index.html  pacientes.html  dentistas.html
│   ├── procedimentos.html  consultas.html  usuarios.html
│   └── assets/            # css, js e Bootstrap local (funciona offline)
├── testes/testar_api.py    # 55 testes automatizados
└── docs/                   # esta documentação
```

---

## 4. Por que foi feito de tal maneira (justificativas)

Esta é a parte que costuma ser perguntada na apresentação. Cada decisão
técnica e o motivo dela:

### 4.1 Sobre o banco de dados

**Por que exatamente 5 tabelas?**
A atividade permite de 3 a 5. Usamos as 5 para cobrir todos os cadastros
do segmento (pacientes, dentistas, procedimentos) **mais** o cadastro de
usuários exigido por toda a atividade — sem exagerar em tabelas que não
seriam usadas.

**Por que existe a tabela `consultas`?**
Ela materializa o relacionamento **N:N**: um paciente é atendido por
vários dentistas e um dentista atende vários pacientes. Sem essa tabela
de ligação, seria preciso duplicar dados nas duas pontas. Ela também
guarda **data/hora, status e observações** — informações que só fazem
sentido no encontro entre as três entidades.

**Por que separar `procedimentos` das consultas?**
Para não repetir nome, preço e duração em cada agendamento. O preço
muda no catálogo e **não retroage** para consultas antigas — mantendo o
histórico fiel (quem pagou R$ 150 na limpeza em novembro continua com
R$ 150 no registro, mesmo que o preço suba).

**Por que `DECIMAL(10,2)` no preço e não `FLOAT`?**
Ponto flutuante em binário não representa decimal exatamente
(0,1 + 0,2 ≠ 0,3) e causa erro de centavos. `DECIMAL` guarda o valor
exato — padrão para dinheiro em qualquer banco.

**Por que `ENUM` no status?**
O próprio banco passa a recusar valores fora da lista
(`agendada/confirmada/em_andamento/concluida/cancelada`), mesmo que
alguém tente gravar direto por SQL — uma barreira a mais além da
validação da API.

**Por que `UNIQUE` em CPF, CRO e nome de usuário?**
A unicidade fica garantida pelo banco, não só pela aplicação. Se duas
telas tentarem cadastrar o mesmo CPF ao mesmo tempo, quem chegar
depois recebe o erro 409 — o banco é a última palavra na integridade.

**Por que `ON DELETE RESTRICT` nas chaves estrangeiras?**
Para não deixar apagar um paciente, dentista ou procedimento que tenha
consultas vinculadas — isso apagaria o histórico da clínica. O MySQL
bloqueia a exclusão e a API devolve um erro amigável (409) explicando
o motivo.

**Por que `utf8mb4`?**
Para acentos (ã, ç, é) e até emojis nos dados — configurado tanto no
`CREATE DATABASE` quanto no `my.ini` do servidor e na conexão.

**Por que inserir os dados de teste por script (`02_dados_de_teste.sql`)?**
A atividade exige ≥ 5 registros por tabela. Um script garante que os
dados são reprodutíveis em qualquer máquina e pode ser reexecutado
(limpa e reinsere na ordem correta).

### 4.2 Sobre a aplicação

**Por que Flask (Python)?**
É a tecnologia sugerida na atividade, é leve e direta: em poucas
linhas expõe rotas HTTP. Nada de framework pesado para um sistema
simples.

**Por que uma API REST em JSON (e não telas Jinja2)?**
Para **separar o trabalho da dupla**: este relatório é a etapa
back-end; a pessoa do front-end monta as telas em HTML/CSS/Bootstrap
de forma independente, seguindo apenas o guia
`docs/03-guia-integracao-front-end.md`, sem tocar no Python. É
também como funciona o mercado (front-end e back-end conversam por
HTTP/JSON). Bônus: a API pode ser testada antes de existir qualquer
tela — foi exatamente o que fizemos (55 testes).

**Por que SQL puro e não um ORM?**
A atividade exige **demonstrar** `CREATE TABLE`, `INSERT`, `SELECT`,
`UPDATE`, `DELETE` e `JOIN`. Com SQL explícito no código, os comandos
ficam visíveis e fáceis de apontar na apresentação. Um ORM esconderia
justamente o que o professor quer ver.

**Por que um "pool" de conexões?**
Abrir e fechar conexão a cada requisição é lento. O pool mantém
conexões prontas e as reutiliza — melhora de desempenho com quase
nenhuma linha de código.

**Por que validar tudo na camada de entrada?**
Nunca se confia no cliente. Cada dado passa por `app/validacao.py`
(CPF com dígitos verificadores, data, e-mail, preço, status...). O
erro sai como `{"erro": "mensagem clara"}` com HTTP 400 — em vez de
uma mensagem técnica do MySQL que o usuário não entenderia.

**Por que a senha nunca fica em texto puro?**
A atividade pede apenas "armazenar usuário e senha", mas guardar a
senha visível seria uma falha grave. Usamos `generate_password_hash`
(Werkzeug — o mesmo do Flask): no banco fica um hash irreversible, e
na comparação usamos `check_password_hash`. As respostas da API nunca
devolvem a senha nem o hash.

**Por que um usuário do banco diferente do root?**
`clinica_app` só enxerga o banco da clínica. Se o código da aplicação
for comprometido, o estrago fica limitado — prática padrão de segurança.

**Por que CORS?**
O front-end (futuro) rodará em outra pasta/porta que a API. O
`flask-cors` libera as chamadas `/api/*` de qualquer origem, evitando
o bloqueio padrão dos navegadores.

**Por que separar as rotas em módulos (Blueprints)?**
Um arquivo por recurso (`pacientes.py`, `consultas.py`...) mantém o
código organizado — uma exigência das regras gerais — e facilita
encontrar e alterar qualquer funcionalidade.

### 4.3 Sobre a interface (Front-end)

Como o colega de dupla não pôde entregar a interface, ela foi construída
também. As decisões e seus porquês:

**Por que HTML + CSS + JavaScript puro, sem React ou Vue?**
A atividade sugere HTML, CSS e Bootstrap. Sem framework, não há build, nem
`npm install`, nem servidor de front-end: o professor executa `iniciar.bat` e
tudo funciona. Para um CRUD com 7 telas, JavaScript puro é suficiente e mais
fácil de explicar na apresentação.

**Por que o Bootstrap foi baixado para a pasta `assets/vendor`?**
O sistema precisa funcionar **sem internet** — inclusive na apresentação na
escola. Com o CSS/JS do Bootstrap e os ícones salvos localmente, nada depende
de CDN externo.

**Por que o Flask serve as telas (e não um segundo servidor)?**
Entregar a aplicação completa em **um único endereço**
(`http://127.0.0.1:5000`) simplifica a demonstração: um comando, um
endereço, sem configurar portas nem CORS na prática. As telas continuam
sendo arquivos estáticos independentes — trocá-las é só editar HTML/CSS.

**Por que a sessão fica no `localStorage`?**
O back-end desta atividade não exige autenticação obrigatória em todas as
rotas; o login existe para demonstrar o cadastro de usuário e senha. Guardar
o usuário no navegador permite mostrar "quem está usando" e evitar acesso
acidental às telas, sem introduzir tokens ou cookies (complexidade
desnecessária para o escopo).

**Por que validar em dois lugares (navegador e back-end)?**
No navegador (HTML5) o usuário recebe retorno imediato; no back-end
(`validacao.py`) porque **nunca se confia no cliente** — é a validação do
servidor que protege o banco. O back-end é a referência; a validação do
front-end é só conforto.

**Por que `fetch` e não formulários HTML tradicional?**
A API devolve JSON e exige `Content-Type: application/json`. Com `fetch` o
front-end controla cabeçalhos, corpo e tratamento de erro — e a mesma função
serve para listar, criar, editar e excluir.

**Quais telas foram construídas?** Login, Painel, Pacientes, Dentistas,
Procedimentos, Consultas (com filtros e agenda do JOIN) e Usuários —
detalhes em [05-guia-do-front-end.md](05-guia-do-front-end.md).

---

## 5. Requisitos da atividade × onde foram atendidos

| Requisito | Onde |
|---|---|
| Banco com nome relacionado à empresa | `clinica_odontologica` (script 01) |
| 3 a 5 tabelas | 5 tabelas (script 01) |
| PRIMARY KEY em todas | `id INT AUTO_INCREMENT PRIMARY KEY` em todas |
| FOREIGN KEY onde houver relacionamento | 3 FKs em `consultas` |
| Tipos de dados adequados | `DATE`, `DATETIME`, `DECIMAL(10,2)`, `ENUM`, `VARCHAR`, `TINYINT` |
| ≥ 5 registros por tabela | 5/6/5/6/9 (script 02) |
| Tela inicial / painel | `front-end/index.html` + `GET /api/painel/resumo` (totais, hoje, próximas, faturamento) |
| Menu de navegação | `front-end/assets/js/layout.js` (menu lateral com item ativo) |
| Cadastro / listagem / pesquisa / edição / exclusão | Telas em `front-end/` + CRUD nas 5 rotas + `?busca=` |
| Integração funcional com o banco | Interface → `fetch` → API → MySQL (verificado no navegador e nos 55 testes) |
| `CREATE DATABASE` / `CREATE TABLE` | script 01 |
| `INSERT INTO` | script 02 (31 registros) |
| `SELECT` / `UPDATE` / `DELETE` | endpoints GET/PUT/DELETE |
| `JOIN` entre tabelas | `GET /api/consultas` (JOIN de 3 tabelas) — exibido na tela Consultas |
| Cadastro de usuários com usuário e senha | tabela `usuarios` + `POST /api/auth/login` + tela de login |
| Código organizado em arquivos e pastas | estrutura da seção 3.3 |
| Dados efetivamente no MySQL | ✅ MySQL 8.4 como serviço `MySQL84` |

---

## 6. Como demonstrar a aplicação (passo a passo da apresentação)

1. Mostrar o **DER** (`database/DER.md`) — 2 minutos: as tabelas e os
   relacionamentos;
2. Abrir o **MySQL Workbench** e rodar um `SELECT` com `JOIN` ao vivo;
3. Abrir <http://127.0.0.1:5000> e **fazer login** (`admin` / `senha123`)
   — mostrar o **painel** com os totais, o faturamento e as próximas
   consultas;
4. Ir em **Pacientes → Novo paciente**, cadastrar alguém e mostrar que
   ele **aparece na tabela na hora** (gravou no MySQL);
5. **Pesquisar** pelo nome, **editar** o telefone e **excluir** o registro
   criado (com a confirmação);
6. Ir em **Consultas** — mostrar a listagem com **JOIN** (paciente +
   dentista + procedimento na mesma linha), o **filtro por status** e o
   **agendamento de uma nova consulta**;
7. Em **Usuários**, mostrar o cadastro e explicar que a senha fica em
   **hash** no banco;
8. Mostrar o **código**: `app/rotas/consultas.py` (o JOIN em SQL puro) e
   `front-end/assets/js/api.js` (a camada de comunicação);
9. Rodar ao vivo `venv\Scripts\python testes\testar_api.py` e mostrar
   os **55 testes passando**.

### Perguntas prováveis do professor (e a resposta curta)

- **"Por que 5 tabelas?"** — limite máximo, e cobrem todos os
  cadastros do segmento + usuários;
- **"Por que a senha não aparece?"** — gravamos o hash, não a senha;
- **"E se eu tentar apagar um paciente com consultas?"** — o
  `ON DELETE RESTRICT` bloqueia e a API responde 409 com a explicação;
- **"O que é o JOIN?"** — junta as 3 tabelas numa listagem só, para a
  tela mostrar nome do paciente + dentista + procedimento sem precisar
  de 3 requisições;
- **"Como o front-end conversa com o banco?"** — o JavaScript chama a
  API por `fetch`, a API executa o SQL e devolve JSON; o front-end nunca
  fala com o MySQL diretamente;
- **"Por que a senha do banco não está no código?"** — está no `.env`,
  que fica fora do versionamento;
- **"Funciona sem internet?"** — sim, o Bootstrap está salvo localmente
  na pasta `assets/vendor`.

---

## 7. Distribuição do trabalho na dupla

| Etapa | Responsável | Situação |
|---|---|---|
| Banco de dados + scripts SQL | Back-end | ✅ concluído |
| API REST (todas as rotas CRUD) | Back-end | ✅ concluído |
| Validações, erros e testes | Back-end | ✅ concluído (55 testes) |
| Documentação (plano, passo a passo, contrato da API, guia do front-end, relatório) | Back-end | ✅ concluído |
| HTML/CSS/Bootstrap + chamadas `fetch()` | ~~Front-end (colega de dupla)~~ → assumido pelo Back-end | ✅ concluído e integrado |
| Apresentação em 10 min (19/11/2026) | Dupla | ⏳ |

> **Como fica a divisão de responsabilidade na apresentação:** o
> colega de dupla pode apresentar a **interface** (telas, navegação e
> demonstração do CRUD) usando o guia
> [05-guia-do-front-end.md](05-guia-do-front-end.md), que explica tela por
> tela o que cada uma faz e como ela se comunica com a API. Assim a dupla
> divide a apresentação sem que nenhum dos dois precise explicar partes
> que não conhece.

---

## 8. Próximos passos e possíveis melhorias

**Para apresentar:** ensaiar o roteiro da seção 6 com o sistema ligado
(`iniciar.bat`) e os dados de teste carregados.

**Se houver tempo, evoluções possíveis (fora do escopo obrigatório):**

- Exigir login em todas as rotas (token/JWT);
- Paginação nas listagens (`?pagina=1`);
- Relatórios (atendimentos por mês, faturamento por dentista);
- Agendamento com conflito de horário do dentista (verificar livre);
- Exclusão lógica (`ativo = 0`) em vez de exclusão física;
- Upload de radiografias por paciente.
