-- ============================================================
-- CLINICA ODONTOLOGICA - Script 00 - Configuracao de acessos
-- Executar UMA UNICA VEZ, como root, apos instalar o MySQL:
--   mysql -u root -p < 00_configuracao_inicial.sql
-- (na instalacao deste projeto a senha do root e: admin123)
-- ============================================================

-- 1) Define a senha do root (instalada com senha vazia)
ALTER USER 'root'@'localhost' IDENTIFIED BY 'admin123';

-- 2) Cria o usuario EXCLUSIVO da aplicacao.
-- Por que nao usar root no dia a dia?
-- Porque root tem poder total sobre todos os bancos. O usuario da
-- aplicacao so enxerga o banco clinica_odontologica - se o codigo
-- da web for comprometido, o estrago fica limitado.
CREATE USER IF NOT EXISTS 'clinica_app'@'localhost'
    IDENTIFIED BY 'clinica2026';

FLUSH PRIVILEGES;

SELECT 'Script 00 executado com sucesso' AS resultado;
