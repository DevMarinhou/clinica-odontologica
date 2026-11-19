-- ============================================================
-- CLINICA ODONTOLOGICA - Script 01 - Banco e tabelas
-- (CREATE DATABASE + CREATE TABLE + FOREIGN KEY)
-- Executar:
--   mysql -u root -p < 01_criar_banco_e_tabelas.sql
-- ============================================================

-- Apaga o banco antigo para permitir reexecutar o script do zero
DROP DATABASE IF EXISTS clinica_odontologica;

-- CREATE DATABASE: nome relacionado a empresa sorteada
CREATE DATABASE clinica_odontologica
    CHARACTER SET utf8mb4        -- aceita acentos e emojis (Ç, ã, é...)
    COLLATE utf8mb4_general_ci;

USE clinica_odontologica;

-- ------------------------------------------------------------
-- TABELA 1: usuarios  (obrigatoria em toda a atividade:
--                     "armazenar o usuario e senha")
-- ------------------------------------------------------------
CREATE TABLE usuarios (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    nome_usuario  VARCHAR(50)  NOT NULL UNIQUE,   -- login unico
    senha         VARCHAR(255) NOT NULL,          -- guarda o HASH, nao a senha em texto
    nome_completo VARCHAR(100) NOT NULL,
    perfil        VARCHAR(20)  NOT NULL DEFAULT 'recepcao',
    ativo         TINYINT(1)   NOT NULL DEFAULT 1,
    criado_em     DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- TABELA 2: pacientes
-- ------------------------------------------------------------
CREATE TABLE pacientes (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    nome            VARCHAR(100) NOT NULL,
    cpf             VARCHAR(14)  NOT NULL UNIQUE, -- CPF unico no sistema
    data_nascimento DATE         NOT NULL,        -- tipo DATE: so a data
    telefone        VARCHAR(20)  NULL,
    email           VARCHAR(100) NULL,
    endereco        VARCHAR(150) NULL,
    criado_em       DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- TABELA 3: dentistas
-- ------------------------------------------------------------
CREATE TABLE dentistas (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    nome          VARCHAR(100) NOT NULL,
    cro           VARCHAR(20)  NOT NULL UNIQUE,   -- registro no conselho, unico
    especialidade VARCHAR(60)  NULL,
    telefone      VARCHAR(20)  NULL,
    email         VARCHAR(100) NULL,
    ativo         TINYINT(1)   NOT NULL DEFAULT 1,
    criado_em     DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- TABELA 4: procedimentos (catalogo de servicos da clinica)
-- ------------------------------------------------------------
CREATE TABLE procedimentos (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    nome            VARCHAR(80)   NOT NULL,
    descricao       VARCHAR(200)  NULL,
    preco           DECIMAL(10,2) NOT NULL, -- DECIMAL e nao FLOAT: dinheiro!
    duracao_minutos INT           NOT NULL DEFAULT 30,
    criado_em       DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- TABELA 5: consultas (tabela de LIGACAO - junta as outras 3)
-- ------------------------------------------------------------
CREATE TABLE consultas (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    paciente_id     INT NOT NULL,
    dentista_id     INT NOT NULL,
    procedimento_id INT NOT NULL,
    data_hora       DATETIME NOT NULL,
    status          ENUM('agendada','confirmada','em_andamento',
                         'concluida','cancelada')
                    NOT NULL DEFAULT 'agendada',
    observacoes     VARCHAR(255) NULL,
    criado_em       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- RELACIONAMENTOS (FOREIGN KEY)
    CONSTRAINT fk_consulta_paciente
        FOREIGN KEY (paciente_id) REFERENCES pacientes(id)
        ON UPDATE CASCADE ON DELETE RESTRICT,   -- nao apaga paciente com consulta
    CONSTRAINT fk_consulta_dentista
        FOREIGN KEY (dentista_id) REFERENCES dentistas(id)
        ON UPDATE CASCADE ON DELETE RESTRICT,   -- nao apaga dentista com consulta
    CONSTRAINT fk_consulta_procedimento
        FOREIGN KEY (procedimento_id) REFERENCES procedimentos(id)
        ON UPDATE CASCADE ON DELETE RESTRICT,   -- nao apaga procedimento em uso

    INDEX idx_consulta_data (data_hora)         -- acelera filtro por data
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- Permissao do usuario da aplicacao (feito AQUI, depois de criar
-- o banco: apagar um banco apaga tambem as permissaoes sobre ele)
-- ------------------------------------------------------------
GRANT ALL PRIVILEGES ON clinica_odontologica.* TO 'clinica_app'@'localhost';
FLUSH PRIVILEGES;

SELECT 'Banco e 5 tabelas criados com sucesso' AS resultado;
