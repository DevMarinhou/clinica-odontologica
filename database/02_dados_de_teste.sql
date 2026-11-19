-- ============================================================
-- CLINICA ODONTOLOGICA - Script 02 - Dados de teste
-- (INSERT INTO - minimo 5 registros por tabela)
-- Executar:
--   mysql -u root -p clinica_odontologica < 02_dados_de_teste.sql
-- ============================================================
USE clinica_odontologica;

-- Limpeza para poder reexecutar sem erro de chave duplicada
-- (ordem importa: consultas referenciam as outras tabelas)
DELETE FROM consultas;
DELETE FROM usuarios;
DELETE FROM pacientes;
DELETE FROM dentistas;
DELETE FROM procedimentos;

-- ------------------------------------------------------------
-- USUARIOS (5) - todos com a senha: senha123
-- A coluna senha recebe o HASH gerado pelo Flask/Werkzeug,
-- nunca a senha em texto puro.
-- ------------------------------------------------------------
INSERT INTO usuarios (nome_usuario, senha, nome_completo, perfil, ativo) VALUES
('admin',       'scrypt:32768:8:1$UkYe4e3l07ThqMT2$30093764d6cbc8101e1475513f87352d251b73d9cf9b53e66396644c1dbc66c8f36d5384662978ec9fd337aff9161c3eebc7ea6d82ad6fc6b631cad94e3e62ff', 'Administrador do Sistema', 'admin',       1),
('marina.recep','scrypt:32768:8:1$ClYeOXaU1t1v8vgr$267d2cef928e7781283a2057893b9da2c13713215d67ad333809d16b4ca1b759ab45ba923bd484dc3e7bdc65d76cf7f43371667e60ddc043b32c4eae15d5f2f3', 'Marina Souza',           'recepcao',   1),
('carlos.recep','scrypt:32768:8:1$ss0IXp2k7j2JEcOW$3633d770844c9d2957754b809de9da7fb308da0f8370c080a2604347fd7e3134291558a9d89ac243ebf65152b7e6de5a6616d09d2690ad5b6f4c0b25f01f9e43', 'Carlos Lima',            'recepcao',   1),
('dra.ana',     'scrypt:32768:8:1$aIWSVpFeDPHEjQTx$546813b016ff32844eab7e23349ee6280054a76e53b6d0c717bc7db7b76f0a9f6ea66060a35dccd442e9d6dbc47c0b53f6dd8cab670a7a7dbbfb516a5d77e36e', 'Ana Paula Ferreira',     'dentista',   1),
('financeiro',  'scrypt:32768:8:1$itdr2yR1WD3zMtaf$08f67ff96881ab520d515a0488da774487b7e4b3ddf3d8428be0b2d4771411234c371bdf446d5c24fe0365f0cd38ee9e2319e57e737ec687294caebe7b77e88c', 'Joao Pedro Alves',       'financeiro', 1);

-- ------------------------------------------------------------
-- PACIENTES (6)
-- ------------------------------------------------------------
INSERT INTO pacientes (nome, cpf, data_nascimento, telefone, email, endereco) VALUES
('Maria Silva',        '123.456.789-09', '1990-05-12', '(11) 98888-1010', 'maria.silva@email.com',    'Rua das Flores, 123 - Sao Paulo/SP'),
('Joao Oliveira',      '987.654.321-00', '1985-11-30', '(11) 97777-2020', 'joao.oliveira@email.com',  'Avenida Brasil, 456 - Sao Paulo/SP'),
('Ana Costa',          '456.789.012-49', '2000-03-25', '(11) 96666-3030', 'ana.costa@email.com',      'Rua Aurora, 789 - Sao Paulo/SP'),
('Pedro Santos',       '234.567.890-92', '1978-07-15', '(11) 95555-4040', 'pedro.santos@email.com',   'Rua do Sol, 321 - Sao Paulo/SP'),
('Carla Rodrigues',    '770.123.456-08', '1995-01-08', '(11) 94444-5050', 'carla.rodrigues@email.com','Avenida Paulista, 1000 - Sao Paulo/SP'),
('Lucas Ferreira',     '102.030.405-70', '2010-09-20', '(11) 93333-6060', 'lucas.ferreira@email.com', 'Rua Verde, 55 - Sao Paulo/SP');

-- ------------------------------------------------------------
-- DENTISTAS (5)
-- ------------------------------------------------------------
INSERT INTO dentistas (nome, cro, especialidade, telefone, email, ativo) VALUES
('Ana Paula Ferreira', 'CRO-SP 12345', 'Ortodontia',              '(11) 98888-1111', 'ana.ferreira@clinicasorriso.com',   1),
('Roberto Almeida',    'CRO-SP 23456', 'Endodontia',              '(11) 98888-2222', 'roberto.almeida@clinicasorriso.com',1),
('Camila Nunes',       'CRO-SP 34567', 'Odontopediatria',         '(11) 98888-3333', 'camila.nunes@clinicasorriso.com',   1),
('Fernando Dias',      'CRO-SP 45678', 'Periodontia',             '(11) 98888-4444', 'fernando.dias@clinicasorriso.com',  1),
('Juliana Prado',      'CRO-SP 56789', 'Protese Dentaria',        '(11) 98888-5555', 'juliana.prado@clinicasorriso.com',  1);

-- ------------------------------------------------------------
-- PROCEDIMENTOS (6)
-- ------------------------------------------------------------
INSERT INTO procedimentos (nome, descricao, preco, duracao_minutos) VALUES
('Profilaxia (Limpeza)', 'Remocao de placa e calculo + aplicacao de fluoreto', 150.00, 30),
('Restauracao',          'Restauracao em resina composta (dente com carie)',   200.00, 45),
('Tratamento de Canal',  'Endodontia com instrumentacao mecanica',            650.00, 90),
('Extracao',             'Remocao simples de dente',                           350.00, 40),
('Clareamento',          'Clareamento dental a laser',                         800.00, 60),
('Aplicacao de Fluoreto','Aplicacao topica de fluoreto (prevencao)',          120.00, 20);

-- ------------------------------------------------------------
-- CONSULTAS (9) - relaciona paciente + dentista + procedimento
-- ------------------------------------------------------------
INSERT INTO consultas (paciente_id, dentista_id, procedimento_id, data_hora, status, observacoes) VALUES
(1, 1, 1, '2026-11-10 09:00:00', 'concluida',  'Paciente sem queixas'),
(2, 2, 3, '2026-11-12 14:00:00', 'concluida',  'Canal do dente 36 finalizado'),
(3, 3, 6, '2026-11-16 10:00:00', 'concluida',  'Aplicacao sem intercorrencias'),
(4, 4, 4, '2026-11-18 11:00:00', 'agendada',   'Extracao do dente 48'),
(5, 1, 5, '2026-11-19 15:30:00', 'agendada',   'Avaliacao previa do clareamento'),
(6, 3, 1, '2026-11-20 09:30:00', 'confirmada', 'Paciente confirmou por telefone'),
(1, 5, 2, '2026-11-25 16:00:00', 'agendada',   'Restauracao do dente 26'),
(2, 4, 2, '2026-11-11 10:30:00', 'cancelada',  'Paciente desmarcou'),
(3, 2, 3, '2026-11-27 08:00:00', 'agendada',   'Inicio do tratamento de canal 11');

SELECT 'Dados de teste inseridos com sucesso' AS resultado;
