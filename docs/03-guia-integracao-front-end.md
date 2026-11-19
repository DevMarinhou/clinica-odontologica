# ETAPA 3 — GUIA DE INTEGRAÇÃO COM O FRONT-END

> **Para quem vai fazer o front-end (HTML + CSS + Bootstrap):**
> este documento é o contrato completo da API. Nele você encontra
> todos os endereços, campos, formatos, exemplos de `fetch()` e a
> sugestão de tela por tela. **Não é preciso ler o código Python.**
>
> ⚠️ **Atualização:** a interface também foi construída e integrada a esta
> API (pasta `front-end/`), porque o colega de dupla não pôde entregá-la.
> Este documento continua valendo como **contrato da API** e como referência
> de campos e endpoints; a descrição da interface pronta está em
> [05-guia-do-front-end.md](05-guia-do-front-end.md). Se você for refazer ou
> customize as telas, siga este guia — ele descreve exatamente o que a API
> espera.

---

## 1. Como as duas partes se encaixam

```
┌─────────────────────────────┐        ┌──────────────────────────────┐
│  FRONT-END (você)           │  HTTP  │  BACK-END (já pronto)        │
│  HTML + CSS + Bootstrap     │ <────> │  API Flask  ·  porta 5000    │
│  pasta: front-end/          │  JSON  │  banco: MySQL                │
└─────────────────────────────┘        └──────────────────────────────┘
```

- A API já está pronta e testada (**55 testes automatizados passando**);
- Ela **não tem telas**: devolve apenas dados em JSON;
- Sua função é montar as telas e chamar os endereços da tabela abaixo;
- A API já está configurada com **CORS liberado** — você pode rodar o
  front-end de qualquer forma (arquivo aberto no navegador, Live Server,
  servidor próprio, outra porta) que as chamadas funcionam.

### Para testar a API antes de escrever qualquer linha

1. Duplo clique em `iniciar.bat` (isso sobe a API **e as telas**);
2. Abra <http://127.0.0.1:5000/api/pacientes> no navegador —
   você verá o JSON com os pacientes de teste;
3. Abra <http://127.0.0.1:5000/api/status> — informações da API
   (`{"status": "online", ...}`).

### Onde as telas são servidas

O back-end também entrega o front-end (pasta `front-end/`), para que a
aplicação funcione em **um único endereço**:

| Endereço | Conteúdo |
|---|---|
| `/` | `index.html` (login + painel) |
| `/pacientes.html`, `/dentistas.html`, `/procedimentos.html`, `/consultas.html`, `/usuarios.html` | Demais telas |
| `/assets/...` | CSS, JS, Bootstrap e ícones |
| `/api/...` | A API REST (JSON) |

Se as telas forem movidas para outro servidor (ou abertas direto do
`file://`), use a **URL absoluta** nas chamadas — o CORS já está liberado
para qualquer origem.

---

## 2. Regras gerais de resposta

| Situação | Formato | Código HTTP |
|---|---|---|
| Listagem | `{ "total": 2, "dados": [ {...}, {...} ] }` | 200 |
| Item único | `{ "dados": { ...campos } }` | 200 |
| Criação | `{ "mensagem": "...", "dados": { "id": 7 } }` | 201 |
| Edição | `{ "mensagem": "...", "dados": { ...campos } }` | 200 |
| Exclusão | `{ "mensagem": "..." }` | 200 |
| **Qualquer erro** | `{ "erro": "mensagem em português" }` | 400/401/404/409/503 |

**Padrão de erro — é só mostrar `corpo.erro` ao usuário:**

```js
const resposta = await fetch(url, opcoes);
const corpo = await resposta.json();
if (!resposta.ok) {
  alert(corpo.erro);   // mensagem pronta em português
}
```

### Formatos de valor

| Tipo | Exemplo na resposta | Como colocar no formulário |
|---|---|---|
| Data (`DATE`) | `"1990-05-12"` | `<input type="date">` (valor direto) |
| Data/hora (`DATETIME`) | `"2026-11-19T15:30:00"` | `<input type="datetime-local">` → use `valor.slice(0,16)` |
| Preço (`DECIMAL`) | `150.0` (número) | `<input type="number" step="0.01">` |
| Flag ativa | `1` ou `0` | checkbox → envie `1`/`0` (ou `true`/`false`) |

Ao **enviar** data/hora no formato do `datetime-local`
(`2026-11-19T15:30`), a API aceita direto — não precisa converter.

### Códigos de erro que podem aparecer

| HTTP | Quando | O que fazer na tela |
|---|---|---|
| 400 | Dado inválido (CPF, data, campo faltando) | Mostrar `corpo.erro` no formulário |
| 401 | Usuário/senha errados no login | Mostrar aviso "Usuário ou senha inválidos" |
| 404 | Registro não encontrado | Atualizar a lista |
| 409 | CPF/duplicado **ou** registro com vínculo | Mostrar `corpo.erro` (ex.: "já existe consulta vinculada") |
| 503 | MySQL desligado | Avisar "serviço do banco desligado" |

---

## 3. Endereços (endpoints)

Base: `http://127.0.0.1:5000`

### 3.1 Painel (tela inicial)

| Método | Endereço | O que faz |
|---|---|---|
| GET | `/api/painel/resumo` | Contagens, consultas de hoje, faturamento e próximas 5 consultas |

Resposta:
```json
{
  "dados": {
    "totais": { "pacientes": 6, "dentistas": 5, "procedimentos": 6,
                "consultas": 9, "usuarios": 5 },
    "consultas_hoje": 0,
    "consultas_pendentes": 5,
    "consultas_por_status": [ { "status": "agendada", "quantidade": 5 } ],
    "faturamento_concluido": 920.0,
    "proximas_consultas": [
      { "id": 4, "data_hora": "2026-11-18T11:00:00", "status": "agendada",
        "paciente_nome": "Pedro Santos", "dentista_nome": "Fernando Dias",
        "procedimento_nome": "Extracao" }
    ]
  }
}
```

### 3.2 Login

| Método | Endereço | Corpo |
|---|---|---|
| POST | `/api/auth/login` | `{ "nome_usuario": "admin", "senha": "senha123" }` |

Sucesso (200):
```json
{ "mensagem": "Login realizado com sucesso.",
  "dados": { "id": 1, "nome_usuario": "admin",
             "nome_completo": "Administrador do Sistema",
             "perfil": "admin", "ativo": 1 } }
```
Erro (401): `{ "erro": "Usuario ou senha invalidos." }`

> A API não exige login nas demais rotas (a atividade não pede controle
> de acesso). Sugerimos guardar o usuário logado em `localStorage` só
> para exibir no cabeçalho.

### 3.3 Pacientes

| Método | Endereço | Corpo / parâmetros |
|---|---|---|
| GET | `/api/pacientes` | `?busca=` (pesquisa por nome, cpf, email, telefone) |
| GET | `/api/pacientes/{id}` | — |
| POST | `/api/pacientes` | `nome*`, `cpf*`, `data_nascimento*`, `telefone`, `email`, `endereco` |
| PUT | `/api/pacientes/{id}` | qualquer subconjunto dos campos acima |
| DELETE | `/api/pacientes/{id}` | — |

Item da lista:
```json
{ "id": 1, "nome": "Maria Silva", "cpf": "123.456.789-09",
  "data_nascimento": "1990-05-12", "telefone": "(11) 98888-1010",
  "email": "maria.silva@email.com",
  "endereco": "Rua das Flores, 123 - Sao Paulo/SP",
  "criado_em": "2026-11-17T07:05:00" }
```

Campos obrigatórios marcados com `*`. O CPF é validado com dígitos
verificadores (formato `000.000.000-00`).

### 3.4 Dentistas

| Método | Endereço | Corpo / parâmetros |
|---|---|---|
| GET | `/api/dentistas` | `?busca=` (nome, CRO, especialidade, email) |
| GET | `/api/dentistas/{id}` | — |
| POST | `/api/dentistas` | `nome*`, `cro*`, `especialidade`, `telefone`, `email`, `ativo` |
| PUT | `/api/dentistas/{id}` | qualquer subconjunto |
| DELETE | `/api/dentistas/{id}` | — |

Item: `{ "id": 1, "nome": "Ana Paula Ferreira", "cro": "CRO-SP 12345",
"especialidade": "Ortodontia", "telefone": "(11) 98888-1111",
"email": "ana.ferreira@clinicasorriso.com", "ativo": 1 }`

### 3.5 Procedimentos

| Método | Endereço | Corpo / parâmetros |
|---|---|---|
| GET | `/api/procedimentos` | `?busca=` (nome, descrição) |
| GET | `/api/procedimentos/{id}` | — |
| POST | `/api/procedimentos` | `nome*`, `preco*`, `descricao`, `duracao_minutos` (mín. 5) |
| PUT | `/api/procedimentos/{id}` | qualquer subconjunto |
| DELETE | `/api/procedimentos/{id}` | — |

Item: `{ "id": 1, "nome": "Profilaxia (Limpeza)",
"descricao": "Remocao de placa e calculo...", "preco": 150.0,
"duracao_minutos": 30 }`

### 3.6 Consultas ⭐ (a que usa JOIN)

| Método | Endereço | Corpo / parâmetros |
|---|---|---|
| GET | `/api/consultas` | filtros: `?busca=`, `?status=`, `?data=AAAA-MM-DD`, `?paciente_id=`, `?dentista_id=` |
| GET | `/api/consultas/{id}` | — |
| POST | `/api/consultas` | `paciente_id*`, `dentista_id*`, `procedimento_id*`, `data_hora*`, `status`, `observacoes` |
| PUT | `/api/consultas/{id}` | qualquer subconjunto (mudar status, remarcar...) |
| DELETE | `/api/consultas/{id}` | — |

**A listagem já vem com os nomes das 3 tabelas resolvidos** — é só
renderizar (é o `JOIN` que a atividade exige):

```json
{ "total": 9,
  "dados": [
    { "id": 4,
      "data_hora": "2026-11-18T11:00:00",
      "status": "agendada",
      "observacoes": "Extracao do dente 48",
      "paciente_id": 4, "paciente_nome": "Pedro Santos",
      "paciente_cpf": "234.567.890-92",
      "dentista_id": 4, "dentista_nome": "Fernando Dias",
      "dentista_cro": "CRO-SP 45678",
      "procedimento_id": 4, "procedimento_nome": "Extracao",
      "procedimento_preco": 350.0,
      "procedimento_duracao_minutos": 40 }
  ] }
```

**Valores de `status`:** `agendada`, `confirmada`, `em_andamento`,
`concluida`, `cancelada`.

### 3.7 Usuários

| Método | Endereço | Corpo / parâmetros |
|---|---|---|
| GET | `/api/usuarios` | `?busca=` (nome de usuário, nome completo) |
| GET | `/api/usuarios/{id}` | — |
| POST | `/api/usuarios` | `nome_usuario*`, `senha*` (mín. 6), `nome_completo*`, `perfil`, `ativo` |
| PUT | `/api/usuarios/{id}` | qualquer subconjunto (`senha` só se quiser trocar) |
| DELETE | `/api/usuarios/{id}` | — |

**A senha nunca aparece nas respostas** (é gravada como hash).

**Valores de `perfil`:** `admin`, `recepcao`, `dentista`, `financeiro`.

---

## 4. Exemplos prontos de `fetch()`

### Listar com pesquisa

```js
async function listarPacientes(busca = '') {
  const url = 'http://127.0.0.1:5000/api/pacientes'
            + (busca ? `?busca=${encodeURIComponent(busca)}` : '');
  const resposta = await fetch(url);
  const corpo = await resposta.json();
  return corpo.dados;          // array de pacientes
}
```

### Criar registro

```js
async function salvarPaciente(dados) {
  const resposta = await fetch('http://127.0.0.1:5000/api/pacientes', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(dados),
  });
  const corpo = await resposta.json();
  if (!resposta.ok) throw new Error(corpo.erro);   // ex.: CPF inválido
  return corpo;                                    // { mensagem, dados: { id } }
}
```

### Editar registro

```js
async function editarPaciente(id, dadosParciais) {
  const resposta = await fetch(`http://127.0.0.1:5000/api/pacientes/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(dadosParciais),
  });
  const corpo = await resposta.json();
  if (!resposta.ok) throw new Error(corpo.erro);
  return corpo.dados;
}
```

### Excluir registro

```js
async function excluirPaciente(id) {
  if (!confirm('Deseja realmente excluir este paciente?')) return;
  const resposta = await fetch(`http://127.0.0.1:5000/api/pacientes/${id}`, {
    method: 'DELETE',
  });
  const corpo = await resposta.json();
  if (!resposta.ok) { alert(corpo.erro); return; }  // ex.: 409 com consultas
  alert(corpo.mensagem);
  carregarLista();   // recarrega a tabela
}
```

### Preencher os `<select>` do formulário de consulta

```js
async function carregarOpcoes() {
  const [pacientes, dentistas, procedimentos] = await Promise.all([
    fetch('http://127.0.0.1:5000/api/pacientes').then(r => r.json()),
    fetch('http://127.0.0.1:5000/api/dentistas').then(r => r.json()),
    fetch('http://127.0.0.1:5000/api/procedimentos').then(r => r.json()),
  ]);
  // <select id="paciente_id"> ... <option value="${p.id}">${p.nome}</option>
}
```

### Login

```js
async function entrar(usuario, senha) {
  const resposta = await fetch('http://127.0.0.1:5000/api/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ nome_usuario: usuario, senha }),
  });
  const corpo = await resposta.json();
  if (!resposta.ok) throw new Error(corpo.erro);
  localStorage.setItem('usuario', JSON.stringify(corpo.dados));
}
```

---

## 5. Sugestão de tela por tela (mapeamento)

| Tela do menu | Endereços usados | Recursos do Bootstrap sugeridos |
|---|---|---|
| **Painel inicial** | `GET /api/painel/resumo` | cards com números, badges de status, tabela "próximas consultas" |
| **Pacientes** | `GET/POST/PUT/DELETE /api/pacientes` | tabela + modal de cadastro/edição + campo de busca no topo |
| **Dentistas** | `GET/POST/PUT/DELETE /api/dentistas` | igual acima |
| **Procedimentos** | `GET/POST/PUT/DELETE /api/procedimentos` | tabela com preço formatado (`toLocaleString('pt-BR',{style:'currency',currency:'BRL'})`) |
| **Consultas** | `GET/POST/PUT/DELETE /api/consultas` | tabela com JOIN (nome do paciente/dentista/procedimento), filtros (status/data), badge de status |
| **Usuários** | `GET/POST/PUT/DELETE /api/usuarios` + `POST /api/auth/login` | formulário de login inicial; lista sem senha |

### Fluxo mínimo para a apresentação (rode na frente do professor)

1. Painel → mostra os totais;
2. Pacientes → **cadastrar** um novo (o professor pede "como fazer um
   cadastro") → aparece na lista;
3. Consultas → mostrar a **listagem com JOIN** e **filtrar** por status;
4. Editar um registro (mudar telefone/status) → mostrar que gravou;
5. Excluir o que acabou de criar → mostra confirmação;
6. (Opcional) Login com `admin` / `senha123`.

---

## 6. Checklist de integração

- [ ] API ligada (`iniciar.bat`) e `http://127.0.0.1:5000` respondendo;
- [ ] Front-end consegue buscar `/api/pacientes` sem erro de CORS;
- [ ] Listagem renderiza `dados` e mostra `total`;
- [ ] Cadastro envia `POST` e recarrega a lista (o novo registro aparece);
- [ ] Edição envia `PUT` com só os campos alterados;
- [ ] Exclusão pede confirmação e trata o **409** (registro com vínculo);
- [ ] Pesquisa usa `?busca=`;
- [ ] Formulário de consulta usa os 3 `select` carregados por API;
- [ ] Erros exibem `corpo.erro`;
- [ ] Datas no formato AAAA-MM-DD / datetime-local.

---

## 7. Perguntas frequentes

**"Posso rodar o front-end abrindo o arquivo .html direto?"**
Sim — o CORS está liberado para qualquer origem.

**"A API precisa reiniciar quando eu mudo o HTML?"**
Não. O Flask reinicia sozinho ao detectar mudança no Python (debug
ligado no `.env`); mudanças no HTML/CSS não afetam a API.

**"De onde vem o `id` que eu colo no PUT/DELETE?"**
Do próprio item da lista (`dados[i].id`) ou do campo escondido do
formulário de edição.

**"Como sei se um campo é obrigatório?"**
A tabela de cada recurso marca com `*`. Se faltar, a API responde
`400` com `{"erro": "Campo(s) obrigatorio(s): nome, cpf."}` — mostre
essa mensagem no formulário.
