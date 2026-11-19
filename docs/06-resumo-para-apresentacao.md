# RESUMO PARA APRESENTAÇÃO — Clínica Odontológica
### Sistema Web com Banco de Dados MySQL | Duração: 10 minutos

> Documento de apoio: leia os blocos marcados como **🗣️ FALA** na ordem.
> Os tempos são suggestions — ajuste conforme o ritmo da apresentação.
> Comandos, credenciais e checklist estão nos anexos.

---

## 🖼️ QUADRO 1 — Identificação e problema (30s)

**🗣️ FALA**
> "Bom dia. Nossa dupla sorteou o segmento **Clínica Odontológica** e
> desenvolvemos um sistema web para gerenciar a clínica: pacientes,
> dentistas, procedimentos e a agenda de consultas, com cadastro de
> usuários e senha. O problema real que ele resolve é o controle da
> agenda e do cadastro: sem sistema, essas informações ficam em papel ou
> planilha, gerando erro de digitação, consulta perdida e dificuldade de
> saber quem atendeu quem."

- **Empresa sorteada:** Clínica Odontológica
- **Produto final:** aplicação web integrada ao MySQL
- **Endereço do sistema:** <http://127.0.0.1:5000> (telas + API juntos)

---

## 🖼️ QUADRO 2 — O que foi feito (1 min) — *as DUAS partes*

### 🔧 BACK-END (API + Banco de dados)

| Item | Detalhe |
|---|---|
| Banco de dados | MySQL 8.4, banco `clinica_odontologica`, **5 tabelas** |
| Scripts SQL | `CREATE DATABASE`, `CREATE TABLE`, `INSERT INTO` (31 registros de teste) |
| API REST | **26 rotas** com CRUD completo + login + painel |
| Segurança | senha gravada como **hash**, usuário do banco próprio (não usa root) |
| Qualidade | **55 testes automatizados**, todos passando |

### 🎨 FRONT-END (interface em HTML + CSS + Bootstrap + JavaScript)

| Item | Detalhe |
|---|---|
| Telas | **7 telas**: Login, Painel, Pacientes, Dentistas, Procedimentos, Consultas, Usuários |
| Recursos de cada tela | menu lateral, tabela, **busca**, **cadastro**, **edição**, **exclusão** (com confirmação), avisos |
| Integração | `fetch()` consumindo a API REST (contrato documentado) |
| Extras | painel com indicadores, filtros de status/data, badges coloridos, valores em R$ e data em pt-BR |
| Offline | Bootstrap e ícones **baixados localmente** — funciona sem internet |

> **Observação importante:** o colega de dupla teve um imprevisto e não pôde
> entregar a interface; por isso **as duas etapas foram concluídas** e o
> sistema está **inteiro e funcionando** — é isso que será demonstrado.

---

## 🖼️ QUADRO 3 — Como as tabelas foram organizadas (1 min30)

**🗣️ FALA**
> "Modelamos o problema em **cinco tabelas**, o máximo permitido pela
> atividade. Cada tabela tem chave primária, e os relacionamentos foram
> implementados com chaves estrangeiras."

| Tabela | Guarda | Tipo/Detalhe importante |
|---|---|---|
| `usuarios` | quem acessa o sistema (usuário + senha) | senha em **hash** (não texto puro) |
| `pacientes` | dados dos pacientes | `CPF` com **UNIQUE**; `DATE` para nascimento |
| `dentistas` | profissionais | `CRO` com **UNIQUE**; flag `ativo` |
| `procedimentos` | catálogo de serviços | `DECIMAL(10,2)` no preço (nunca FLOAT, que erra centavos) |
| `consultas` | os agendamentos | **tabela de ligação** + `ENUM` de status + 3 FKs |

**Tipos de dados escolhidos com critério:**
`DATE` (só a data de nascimento) · `DATETIME` (data e hora da consulta) ·
`DECIMAL(10,2)` (dinheiro exato) · `ENUM` (status validado pelo próprio banco) ·
`VARCHAR` com tamanhos realistas · `TINYINT(1)` (situação ativo/inativo) ·
`utf8mb4` (acentos) · `INDEX` na data das consultas (filtro mais usado).

**Onde mostrar:** abrir `database/DER.md` (diagrama ER) ou o MySQL Workbench
com o `DESCRIBE` de cada tabela.

---

## 🖼️ QUADRO 4 — Quais relacionamentos foram implementados (1 min)

**🗣️ FALA**
> "A tabela `consultas` é a central do sistema: é ela que materializa o
> relacionamento **muitos para muitos** entre paciente e dentista — um
> paciente é atendido por vários dentistas e um dentista atende vários
> pacientes. As três chaves estrangeiras usam `ON DELETE RESTRICT`, ou
> seja, o banco **impede** que se apague um paciente que já tem consultas:
> o histórico da clínica fica preservado."

| De → Para | Cardinalidade | Regra |
|---|---|---|
| `pacientes` → `consultas` | 1 : N | `ON DELETE RESTRICT` + `ON UPDATE CASCADE` |
| `dentistas` → `consultas` | 1 : N | `ON DELETE RESTRICT` + `ON UPDATE CASCADE` |
| `procedimentos` → `consultas` | 1 : N | `ON DELETE RESTRICT` + `ON UPDATE CASCADE` |

**Na prática:** a API devolve **409** com a mensagem
*"Operacao nao permitida: o registro esta vinculado a outros dados"*.

---

## 🖼️ QUADRO 5 — Como a aplicação se comunica com o banco de dados (1 min)

**🗣️ FALA**
> "A comunicação acontece em três níveis. O front-end **nunca** fala com o
> MySQL: ele chama a API por `fetch`, a API valida os dados e executa o SQL
> com parâmetros, e o MySQL devolve as linhas, que a API transforma em JSON."

```
NAVEGADOR (front-end)        API FLASK (back-end)           MySQL
───────────────────          ────────────────────          ──────────────────
fetch('/api/pacientes') ──►  app/rotas/pacientes.py
                            │ valida (validacao.py)
                            │ monta SQL com %s  ──────────►  clinica_odontologica
                            │ ◄──── linhas do banco ──────
                            │ converte data/DECIMAL p/ JSON
JSON { total, dados } ◄───  resposta
```

**Pontos para destacar (perguntas certas):**
- Todo SQL está **visível no código** (a atividade pede demonstrar os comandos);
- Os parâmetros usam `%s` — **nunca** concatenação de string (evita SQL Injection);
- **Pool de conexões** (fila de conexões prontas) em `app/banco.py` → mais velocidade;
- `commit` automático e `rollback` se algo falhar no meio da operação.

---

## 🖼️ QUADRO 6 — Como realizar um cadastro (1 min) — *demonstração ao vivo*

**🗣️ FALA + ação na tela**
> "Vou cadastrar um paciente agora. Vou em **Pacientes → Novo paciente**."

**Passos (mostrar na tela):**
1. Menu lateral → **Pacientes**;
2. Botão **+ Novo paciente** (abre um modal);
3. Preencher: nome, CPF, data de nascimento, telefone, e-mail, endereço;
   → o CPF é validado **com dígitos verificadores** (o back-end recusa CPF inválido);
4. **Salvar** → a API executa o `INSERT`, devolve o `id` e a lista é recarregada;
5. O paciente **aparece na tabela na hora** (confirme que está no MySQL).

**O que acontece por trás (diga isto):**
`POST /api/pacientes` → validação → `INSERT INTO pacientes (...)` → `201 Created`.

---

## 🖼️ QUADRO 7 — Como consultar, editar e excluir (1 min30) — *demonstração ao vivo*

| Ação | Como fazer na tela | O que o back-end executa |
|---|---|---|
| **Consultar / pesquisar** | Digitar no campo de busca da tabela (filtra enquanto digita) | `GET /api/pacientes?busca=maria` → `SELECT ... WHERE nome LIKE %s` |
| **Consultar (agenda)** | Tela **Consultas** → filtros por texto, status e data | `GET /api/consultas?status=agendada` → `SELECT` com **JOIN** |
| **Editar** | Botão ✏️ na linha → o modal abre **preenchido** → alterar → Salvar | `PUT /api/pacientes/<id>` → `UPDATE ... WHERE id = %s` (envia só o que mudou) |
| **Excluir** | Botão 🗑️ → modal de confirmação → **Excluir** | `DELETE /api/pacientes/<id>` → `DELETE FROM ... WHERE id = %s` |

**Destaques para falar:**
- A listagem de **Consultas** é o exemplo do **JOIN**: mostra paciente + CPF,
  dentista + CRO, procedimento + preço **na mesma linha**, sem 3 requisições;
- Se o paciente tiver consultas, a exclusão é **bloqueada** (409) — é a
  integridade referencial protegendo o histórico;
- Toda resposta de erro chega no formato `{"erro": "mensagem em português"}`
  e aparece para o usuário como um aviso (toast) na tela.

---

## 🖼️ QUADRO 8 — Decisões técnicas (o "porquê") — *para perguntas do professor*

| Decisão | Por quê |
|---|---|
| Flask + Python | Tecnologia sugerida; leve e simples para um CRUD |
| **SQL puro, sem ORM** | A atividade pede **demonstrar** SELECT/INSERT/UPDATE/DELETE/JOIN — com ORM eles ficariam escondidos |
| **API REST em JSON** | Separou o back do front; o front pôde ser escrito/testado contra um contrato claro; é o padrão do mercado |
| 5 tabelas | Máximo permitido, cobrindo todos os cadastros + o de usuários |
| Tabela `consultas` como ligação | Resolve o N:N entre paciente e dentista sem duplicar dados |
| `DECIMAL` no preço | Ponto flutuante perde precisão em dinheiro (0,1 + 0,2 ≠ 0,3) |
| `ENUM` no status | O próprio banco recusa valores inválidos |
| `UNIQUE` em CPF/CRO/login | Integridade garantida pelo banco, mesmo com dois cadastros simultâneos |
| `ON DELETE RESTRICT` | Não deixa apagar registros que fazem parte do histórico |
| **Senha em hash** | A atividade pede guardar usuário e senha; guardar em texto puro seria falha grave de segurança |
| Usuário do banco diferente do root | Se o código for comprometido, o dano fica limitado ao banco da clínica |
| Pool de conexões | Reaproveitar conexões é bem mais rápido que abrir uma a cada requisição |
| Validação em duas camadas | Navegador dá retorno rápido; **servidor** é quem protege o banco |
| Front sem framework e Bootstrap local | Sem `npm install` nem build: abre e funciona; e **funciona offline** na apresentação |
| Flask servindo as telas | Sistema completo em **um único endereço**: um comando, uma URL |

---

## 🖼️ QUADRO 9 — Roteiro dos 10 minutos (divisão de fala)

| Tempo | Quem | O quê |
|---|---|---|
| 0:00–0:30 | **A** | Identificação, problema e o que foi feito (Quadros 1 e 2) |
| 0:30–2:00 | **A** | Banco de dados: 5 tabelas, tipos e relacionamentos (Quadros 3 e 4) |
| 2:00–3:00 | **A** | Como a aplicação fala com o banco (Quadro 5) |
| 3:00–6:00 | **B** | **Demonstração ao vivo**: login → painel → cadastrar paciente → pesquisar → editar → excluir → agenda de consultas com JOIN e filtros |
| 6:00–7:00 | **A** | Mostrar o código: `app/rotas/consultas.py` (o JOIN em SQL) e `front-end/assets/js/api.js` (a comunicação) |
| 7:00–8:00 | **B** | Tela de Usuários e explicar o hash da senha |
| 8:00–9:00 | **A** | Rodar os **55 testes** ao vivo (`testes\testar_api.py`) |
| 9:00–10:00 | **A + B** | Conclusão e perguntas (Quadro 10) |

> **A = quem fez o back-end · B = colega de dupla (apresenta as telas)**
> Se o colega não puder apresentar, use o Quadro 9 inteiro sozinho — o
> roteiro de fala está escrito para isso.

---

## 🖼️ QUADRO 10 — Perguntas prováveis (e a resposta curta)

| Pergunta | Resposta |
|---|---|
| Por que 5 tabelas? | Limite máximo da atividade, cobrindo todos os cadastros do segmento + o de usuários. |
| Qual a diferença entre chave primária e estrangeira? | A primária identifica o registro (`id`); a estrangeira liga uma tabela a outra (a consulta aponta para paciente, dentista e procedimento). |
| O que o JOIN faz aqui? | Junta as 3 tabelas numa listagem só, para a tela mostrar nome do paciente + dentista + procedimento sem 3 requisições. |
| Por que a senha não aparece no banco? | Guardamos o **hash** (irreversível), gerado pelo Werkzeug; na tela de edição, a senha só muda se for digitada uma nova. |
| E se apagar um paciente com consultas? | O banco bloqueia (`ON DELETE RESTRICT`) e a API responde 409 explicando o motivo. |
| Como o front-end usa o banco? | Não usa diretamente: chama a API por `fetch`; a API valida e executa o SQL. |
| Tem teste automatizado? | Sim — 55 verificações cobrindo CRUD, JOIN, login, busca e todos os erros (400, 401, 404, 409). |
| Dá para rodar sem internet? | Sim — o Bootstrap e os ícones estão salvos localmente na pasta `assets/vendor`. |
| Onde ficam as senhas do banco? | No arquivo `.env`, fora do código (e fora do versionamento). |

---

## 🖼️ QUADRO 11 — Requisitos da atividade: checklist final

| Requisito | ✅ | Onde |
|---|---|---|
| Banco com nome da empresa | ✅ | `clinica_odontologica` |
| 3 a 5 tabelas | ✅ | 5 tabelas |
| PRIMARY KEY em todas | ✅ | `id INT AUTO_INCREMENT` |
| FOREIGN KEY nos relacionamentos | ✅ | 3 FKs em `consultas` |
| Tipos de dados adequados | ✅ | DATE, DATETIME, DECIMAL, ENUM, VARCHAR, TINYINT |
| ≥ 5 registros por tabela | ✅ | 5 / 6 / 5 / 6 / 9 |
| Tela inicial / painel | ✅ | painel com indicadores do banco |
| Menu de navegação | ✅ | menu lateral em todas as telas |
| Cadastro | ✅ | modais de cadastro em todos os recursos |
| Listagem | ✅ | tabelas com total de registros |
| Consulta / pesquisa | ✅ | busca com filtro + filtros de status/data |
| Edição | ✅ | modal preenchido (PUT) |
| Exclusão | ✅ | modal de confirmação (DELETE) |
| Integração funcional com o banco | ✅ | API grava/lê no MySQL (testado na tela e nos testes) |
| CREATE DATABASE / CREATE TABLE | ✅ | `database/01_criar_banco_e_tabelas.sql` |
| INSERT INTO | ✅ | `database/02_dados_de_teste.sql` |
| SELECT / UPDATE / DELETE | ✅ | endpoints GET / PUT / DELETE |
| JOIN | ✅ | `GET /api/consultas` |
| Cadastro de usuários (usuário e senha) | ✅ | tabela `usuarios` + tela de login |
| Código organizado em pastas | ✅ | `app/`, `front-end/`, `database/`, `testes/`, `docs/` |
| Dados no MySQL de verdade | ✅ | MySQL 8.4 como serviço Windows (`MySQL84`) |

---

## 📎 ANEXO A — Comandos do dia da apresentação

```powershell
# 1) ligar o banco (se estiver parado)
Start-Service MySQL84

# 2) subir o sistema (telas + API)
iniciar.bat          # ou: venv\Scripts\python run.py

# 3) abrir no navegador
start http://127.0.0.1:5000

# 4) (opcional, impressiona) rodar os testes
venv\Scripts\python testes\testar_api.py
```

## 📎 ANEXO B — Credenciais

| O que | Valor |
|---|---|
| Login do sistema | `admin` / `senha123` |
| MySQL root | `admin123` |
| Usuário da aplicação | `clinica_app` / `clinica2026` |
| Endereço | <http://127.0.0.1:5000> |

## 📎 ANEXO C — Arquivos para abrir durante a apresentação

| Mostrar | Caminho |
|---|---|
| Diagrama ER | `database/DER.md` |
| Script do banco | `database/01_criar_banco_e_tabelas.sql` |
| Dados de teste | `database/02_dados_de_teste.sql` |
| SQL do JOIN | `app/rotas/consultas.py` |
| Comunicação do front | `front-end/assets/js/api.js` |
| Layout do sistema | `front-end/assets/css/estilo.css` |
| Testes | `testes/testar_api.py` |
| Documentação completa | `docs/01` a `docs/06` |

---

> **Dica final:** ensaie o roteiro uma vez antes de apresentar, com o sistema
> ligado e os dados de teste carregados. A demonstração ao vivo (Quadros 6 e 7)
> é o que mais impressiona — leve o DELETE para o final, depois de mostrar
> o registro criado na mesma sessão.
