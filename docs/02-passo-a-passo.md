# ETAPA 2 — PASSO A PASSO

> Este documento registra, na ordem exata, **tudo o que foi feito e como
> fazer de novo**. É o seu guia de bolso: siga da seção 1 à 5 e o sistema
> inteiro sobe do zero.
>
> O sistema completo (telas + API) é servido em **um único endereço**:
> <http://127.0.0.1:5000>

---

## Credenciais rápidas (anote!)

| O que | Valor |
|---|---|
| Usuário root do MySQL | `admin123` |
| Usuário da aplicação | `clinica_app` / `clinica2026` |
| Usuário de teste do sistema | `admin` / `senha123` |
| Endereço da API | `http://127.0.0.1:5000` |
| Banco de dados | `clinica_odontologica` |
| Serviço do Windows | `MySQL84` |

---

## PARTE 1 — Instalação do ambiente (feita uma única vez)

### Passo 1.1 — Instalar o Python (já instalado: 3.14)

Verifique com `python --version` no terminal.

### Passo 1.2 — Instalar o MySQL Server

```powershell
winget install Oracle.MySQL --silent --accept-package-agreements
```

> ⚠️ O instalador silencioso do MySQL só copia os arquivos: ele **não**
> cria o serviço nem a pasta de dados. Por isso é preciso o passo 1.3.

### Passo 1.3 — Criar o serviço do Windows (precisa de administrador)

Abra o PowerShell **como administrador** e rode:

```powershell
& 'C:\Users\Dev Marinho\clinica-odontologica\database\instalar_servico_mysql.ps1'
```

O script faz 3 coisas:
1. Grava o `my.ini` (com `utf8mb4` para aceitar acentos);
2. Inicializa a pasta de dados (`mysqld --initialize-insecure`);
3. Instala e inicia o serviço **MySQL84**.

Confira que funcionou:

```powershell
Get-Service MySQL84        # deve aparecer "Running"
```

> **No projeto foi exatamente isso que fizemos**, com o aviso de
> Controle de Conta de Usuário (UAC) aprovado. O log ficou em
> `database/init_estado.log`.

### Passo 1.4 — Criar o usuário da aplicação

```powershell
cd C:\Users\Dev Marinho\clinica-odontologica
mysql -u root -p < database\00_configuracao_inicial.sql
# senha do root: admin123
```

Esse script define a senha do root e cria o usuário `clinica_app`
(usado pela aplicação — **nunca** root no dia a dia).

### Passo 1.5 — Criar as tabelas

```powershell
mysql -u root -p < database\01_criar_banco_e_tabelas.sql
```

O que esse script contém (comandos obrigatórios da atividade):
- `CREATE DATABASE clinica_odontologica`
- `DROP DATABASE IF EXISTS` (para poder rodar de novo do zero)
- 5 × `CREATE TABLE` com `PRIMARY KEY`
- 3 × `FOREIGN KEY` em `consultas`
- `GRANT` de permissões para o usuário da aplicação

### Passo 1.6 — Inserir os dados de teste

```powershell
mysql -u root -p clinica_odontologica < database\02_dados_de_teste.sql
```

Resultado esperado (≥ 5 registros em cada tabela):

| Tabela | Registros |
|---|---|
| usuarios | 5 |
| pacientes | 6 |
| dentistas | 5 |
| procedimentos | 6 |
| consultas | 9 |

Conferência rápida:

```powershell
mysql -u clinica_app -pclinica2026 clinica_odontologica -e "SELECT COUNT(*) FROM pacientes;"
```

### Passo 1.7 — Criar o ambiente virtual Python e instalar dependências

```powershell
cd C:\Users\Dev Marinho\clinica-odontologica
python -m venv venv
venv\Scripts\pip install -r requirements.txt
```

Dependências: `flask`, `flask-cors`, `mysql-connector-python`, `python-dotenv`.

---

## PARTE 2 — Rodar o sistema no dia a dia

### Passo 2.1 — Ligar o MySQL

```powershell
Start-Service MySQL84
```
(ou `services.msc` → MySQL84 → Iniciar)

### Passo 2.2 — Ligar a aplicação (API + telas)

Duplo clique em **`iniciar.bat`** — ou no terminal:

```powershell
cd C:\Users\Dev Marinho\clinica-odontologica
venv\Scripts\python run.py
```

O Flask sobe **as telas e a API** no mesmo endereço:

| Endereço | O que entrega |
|---|---|
| <http://127.0.0.1:5000> | Tela de login + painel (Front-end) |
| <http://127.0.0.1:5000/pacientes.html> | Tela de pacientes |
| <http://127.0.0.1:5000/consultas.html> | Agenda de consultas (com JOIN) |
| <http://127.0.0.1:5000/api/pacientes> | A API em JSON |
| <http://127.0.0.1:5000/api/status> | Informações da API |

### Passo 2.3 — Conferir que está no ar

Abra <http://127.0.0.1:5000> — deve aparecer a **tela de login** da clínica.
Entre com **`admin` / `senha123`** e o painel carrega com os totais do banco.

Para conferir só a API: <http://127.0.0.1:5000/api/status> deve responder
`{"sistema": "API Clinica Odontologica", "status": "online", ...}`.

### Passo 2.4 — Rodar os testes automatizados

Com a API ligada, em **outro terminal**:

```powershell
venv\Scripts\python testes\testar_api.py
```

Resultado obtido nesta entrega: **55 testes aprovados, 0 falhas**
(cobre CRUD das 5 tabelas, login, JOIN, pesquisa e todos os erros
esperados: 400, 401, 404, 409).

---

## PARTE 3 — Como testar na mão (curl/PowerShell)

```powershell
# Listar pacientes (SELECT)
Invoke-RestMethod http://127.0.0.1:5000/api/pacientes

# Pesquisar (SELECT + LIKE)
Invoke-RestMethod "http://127.0.0.1:5000/api/pacientes?busca=Maria"

# Consultas com JOIN nas 3 tabelas
Invoke-RestMethod http://127.0.0.1:5000/api/consultas

# Criar paciente (INSERT)
$body = @{ nome='Fulano'; cpf='111.444.777-35'; data_nascimento='1995-04-04' } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:5000/api/pacientes `
  -ContentType 'application/json' -Body $body

# Editar (UPDATE)
Invoke-RestMethod -Method Put -Uri http://127.0.0.1:5000/api/pacientes/7 `
  -ContentType 'application/json' -Body '{ "telefone": "(11) 91234-5678" }'

# Excluir (DELETE)
Invoke-RestMethod -Method Delete http://127.0.0.1:5000/api/pacientes/7

# Login
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:5000/api/auth/login `
  -ContentType 'application/json' -Body '{"nome_usuario":"admin","senha":"senha123"}'

# Painel (dados da tela inicial)
Invoke-RestMethod http://127.0.0.1:5000/api/painel/resumo
```

---

## PARTE 4 — Como fazer tudo do zero em outra máquina

1. Instalar Python e `winget install Oracle.MySQL`;
2. Executar como admin: `database\instalar_servico_mysql.ps1`;
3. `mysql -u root -p < database\00_configuracao_inicial.sql`;
4. `mysql -u root -p < database\01_criar_banco_e_tabelas.sql`;
5. `mysql -u root -p clinica_odontologica < database\02_dados_de_teste.sql`;
6. `python -m venv venv` + `venv\Scripts\pip install -r requirements.txt`;
7. Ajustar `.env` se a senha do root/usuário for outra;
8. `iniciar.bat` e testar com `venv\Scripts\python testes\testar_api.py`.

---

## PARTE 5 — Solução de problemas

| Sintoma | Causa provável | Solução |
|---|---|---|
| API responde 503 "Não foi possível conectar ao banco" | Serviço MySQL parado | `Start-Service MySQL84` |
| `Port already in use` na porta 5000 | Outra API aberta | Feche a outra janela ou mude `PORTA` no `.env` |
| `Access denied for user` | Senha errada no `.env` | Confira `MYSQL_USER`/`MYSQL_PASSWORD` no `.env` |
| Acentos aparecem errados (Ç, ã) | Cliente sem utf8mb4 | Use `mysql --default-character-set=utf8mb4` |
| Erro "chave duplicada" ao rodar o script 02 duas vezes | Não limpa os dados | O script já faz `DELETE` na ordem certa — rode ele inteiro |
| `mysql` não é reconhecido no terminal | Binário fora do PATH | Use o caminho completo: `C:\Program Files\MySQL\MySQL Server 8.4\bin\mysql.exe` |
| UAC / permissão negada ao instalar serviço | Não abriu como administrador | Abra o PowerShell como admin e rode o script do passo 1.3 |
| Testes falham com "API offline" | API desligada | Ligue com `iniciar.bat` antes de rodar os testes |
