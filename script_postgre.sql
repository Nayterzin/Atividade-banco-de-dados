DROP TABLE IF EXISTS AGENDA CASCADE;
DROP TABLE IF EXISTS ESPECIALIZACAO_CABELEIREIRA CASCADE;
DROP TABLE IF EXISTS ESPECIALIZACAO_MANICURE CASCADE;
DROP TABLE IF EXISTS ESPECIALIZACAO_MAQUIADORA CASCADE;
DROP TABLE IF EXISTS CLIENTE CASCADE;
DROP TABLE IF EXISTS PROCEDIMENTO CASCADE;
DROP TABLE IF EXISTS FUNCIONARIO CASCADE;
DROP TABLE IF EXISTS auth_user CASCADE;
DROP TYPE IF EXISTS tipo_funcionario CASCADE;
DROP TYPE IF EXISTS status_agendamento CASCADE;

CREATE TYPE tipo_funcionario AS ENUM ('cabeleireira','manicure','maquiadora','gerente');
CREATE TYPE status_agendamento AS ENUM ('agendado','confirmado','cancelado','concluido');

CREATE TABLE auth_user (
    id SERIAL PRIMARY KEY,
    username VARCHAR(150) UNIQUE NOT NULL,
    password VARCHAR(128) NOT NULL,
    first_name VARCHAR(150) NOT NULL DEFAULT '',
    last_name VARCHAR(150) NOT NULL DEFAULT '',
    email VARCHAR(254) NOT NULL DEFAULT '',
    is_staff BOOLEAN NOT NULL DEFAULT FALSE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_superuser BOOLEAN NOT NULL DEFAULT FALSE,
    date_joined TIMESTAMP NOT NULL DEFAULT NOW(),
    last_login TIMESTAMP
);

CREATE TABLE FUNCIONARIO (
    idFun SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    data_nascimento DATE NOT NULL,
    endereco VARCHAR(200) NOT NULL,
    tipo tipo_funcionario NOT NULL,
    cpf VARCHAR(14) UNIQUE NOT NULL,
    telefone VARCHAR(20),
    user_id INTEGER UNIQUE REFERENCES auth_user(id) ON DELETE SET NULL
);

CREATE TABLE ESPECIALIZACAO_CABELEIREIRA (
    idFun INTEGER PRIMARY KEY REFERENCES FUNCIONARIO(idFun) ON DELETE CASCADE,
    certificacao VARCHAR(100) NOT NULL
);

CREATE TABLE ESPECIALIZACAO_MANICURE (
    idFun INTEGER PRIMARY KEY REFERENCES FUNCIONARIO(idFun) ON DELETE CASCADE,
    certificacao VARCHAR(100) NOT NULL
);

CREATE TABLE ESPECIALIZACAO_MAQUIADORA (
    idFun INTEGER PRIMARY KEY REFERENCES FUNCIONARIO(idFun) ON DELETE CASCADE,
    certificacao VARCHAR(100) NOT NULL
);

CREATE TABLE CLIENTE (
    idCliente SERIAL PRIMARY KEY,
    cpf VARCHAR(14) UNIQUE NOT NULL,
    nome VARCHAR(100) NOT NULL,
    telefone VARCHAR(20),
    email VARCHAR(100),
    CONSTRAINT chk_cpf CHECK (cpf ~ '^[0-9]{3}\.[0-9]{3}\.[0-9]{3}-[0-9]{2}$'),
    CONSTRAINT chk_email CHECK (email IS NULL OR email ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

CREATE TABLE PROCEDIMENTO (
    idProcedimento SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    preco NUMERIC(10,2) NOT NULL CHECK(preco >= 0),
    duracao INTEGER NOT NULL CHECK(duracao > 0)
);

CREATE TABLE AGENDA (
    idAgenda SERIAL PRIMARY KEY,
    data_hora TIMESTAMP NOT NULL,
    idFun INTEGER NOT NULL REFERENCES FUNCIONARIO(idFun) ON DELETE RESTRICT,
    idCliente INTEGER NOT NULL REFERENCES CLIENTE(idCliente) ON DELETE RESTRICT,
    idProcedimento INTEGER NOT NULL REFERENCES PROCEDIMENTO(idProcedimento) ON DELETE RESTRICT,
    status status_agendamento NOT NULL DEFAULT 'agendado'
);

CREATE INDEX idx_agenda_data_hora ON AGENDA(data_hora);
CREATE INDEX idx_agenda_funcionario ON AGENDA(idFun);
CREATE INDEX idx_agenda_cliente ON AGENDA(idCliente);
CREATE UNIQUE INDEX uq_agenda_funcionario_horario ON AGENDA(idFun, data_hora) WHERE status <> 'cancelado';

INSERT INTO auth_user (username, password, first_name, last_name, email, is_staff, is_active, is_superuser, date_joined) VALUES
('111.222.333-44', 'pbkdf2_sha256$1200000$OxjGfg5ZF05paYpMAih0pG$IztLUSvmXm/dR2/kAsOTZuRN2TupWb2yk84Z0voCu8M=', 'Keyla', '', 'keyla@email.com', true, true, false, NOW()),
('222.333.444-55', 'pbkdf2_sha256$1200000$OxjGfg5ZF05paYpMAih0pG$IztLUSvmXm/dR2/kAsOTZuRN2TupWb2yk84Z0voCu8M=', 'Ana Luíza', '', 'analu@email.com', true, true, false, NOW()),
('333.444.555-66', 'pbkdf2_sha256$1200000$OxjGfg5ZF05paYpMAih0pG$IztLUSvmXm/dR2/kAsOTZuRN2TupWb2yk84Z0voCu8M=', 'Nathanael', '', 'nath@email.com', true, true, false, NOW()),
('444.555.666-77', 'pbkdf2_sha256$1200000$OxjGfg5ZF05paYpMAih0pG$IztLUSvmXm/dR2/kAsOTZuRN2TupWb2yk84Z0voCu8M=', 'Henzo', '', 'henzo@email.com', true, true, false, NOW()),
('123.456.789-00', 'pbkdf2_sha256$1200000$OxjGfg5ZF05paYpMAih0pG$IztLUSvmXm/dR2/kAsOTZuRN2TupWb2yk84Z0voCu8M=', 'Cliente Teste', '', 'cliente@email.com', false, true, false, NOW());

INSERT INTO FUNCIONARIO (nome, data_nascimento, endereco, tipo, cpf, telefone, user_id) VALUES
('Keyla', '1985-03-12', 'Bocaina, na barragem', 'cabeleireira', '111.222.333-44', '(88) 99999-1111', (SELECT id FROM auth_user WHERE username='111.222.333-44')),
('Ana Luíza', '1990-08-25', 'Chico Santo, pedra do urubu', 'manicure', '222.333.444-55', '(88) 99999-2222', (SELECT id FROM auth_user WHERE username='222.333.444-55')),
('Nathanael', '1988-10-02', 'Sussuapara, mato', 'maquiadora', '333.444.555-66', '(88) 99999-3333', (SELECT id FROM auth_user WHERE username='333.444.555-66')),
('Henzo', '1975-04-15', 'Teresina, centro', 'gerente', '444.555.666-77', '(88) 99999-4444', (SELECT id FROM auth_user WHERE username='444.555.666-77'));

INSERT INTO ESPECIALIZACAO_CABELEIREIRA VALUES ((SELECT idFun FROM FUNCIONARIO WHERE cpf='111.222.333-44'), 'Curso de Cabeleireira Avançado');
INSERT INTO ESPECIALIZACAO_MANICURE VALUES ((SELECT idFun FROM FUNCIONARIO WHERE cpf='222.333.444-55'), 'Certificação em Alongamento de Unhas');
INSERT INTO ESPECIALIZACAO_MAQUIADORA VALUES ((SELECT idFun FROM FUNCIONARIO WHERE cpf='333.444.555-66'), 'Curso de Maquiagem Profissional');

INSERT INTO CLIENTE (cpf, nome, telefone, email) VALUES
('111.111.111-11', 'Kessia', '(88) 66666-1111', 'kessinha@email.com'),
('222.222.222-22', 'Dona Rosa', '(88) 44444-2222', 'rosinha@email.com'),
('123.456.789-00', 'Cliente Teste', '(11) 99999-9999', 'cliente@email.com');

INSERT INTO PROCEDIMENTO (nome, preco, duracao) VALUES
('Corte de cabelo', 50.00, 30),
('Manicure', 30.00, 45),
('Maquiagem social', 80.00, 60),
('Penteado', 70.00, 50),
('Depilação', 40.00, 20);

CREATE OR REPLACE FUNCTION fn_verificar_disponibilidade(p_idFun INTEGER, p_data_hora TIMESTAMP)
RETURNS BOOLEAN AS $$
DECLARE v_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO v_count FROM AGENDA
    WHERE idFun = p_idFun AND data_hora = p_data_hora AND status <> 'cancelado';
    RETURN v_count = 0;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION fn_agenda_funcionario_dia(p_idFun INTEGER, p_data DATE)
RETURNS TABLE (horario TIMESTAMP, cliente VARCHAR(100), procedimento VARCHAR(100), status status_agendamento) AS $$
BEGIN
    RETURN QUERY
    SELECT a.data_hora, c.nome, p.nome, a.status
    FROM AGENDA a
    JOIN CLIENTE c ON c.idCliente = a.idCliente
    JOIN PROCEDIMENTO p ON p.idProcedimento = a.idProcedimento
    WHERE a.idFun = p_idFun AND DATE(a.data_hora) = p_data
    ORDER BY a.data_hora;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE PROCEDURE sp_agendar_servico(
    p_idCliente INTEGER,
    p_idFun INTEGER,
    p_idProcedimento INTEGER,
    p_data_hora TIMESTAMP
) LANGUAGE plpgsql AS $$
DECLARE
    v_idAgenda INTEGER;
    v_old_agenda INTEGER;
BEGIN
    IF NOT fn_verificar_disponibilidade(p_idFun, p_data_hora) THEN
        RAISE EXCEPTION 'Horário indisponível.';
    END IF;
    INSERT INTO AGENDA(data_hora, idFun, idCliente, idProcedimento)
    VALUES (p_data_hora, p_idFun, p_idCliente, p_idProcedimento)
    RETURNING idAgenda INTO v_idAgenda;
    UPDATE AGENDA
    SET status = 'cancelado'
    WHERE idCliente = p_idCliente
      AND idFun = p_idFun
      AND idAgenda <> v_idAgenda
      AND status = 'agendado'
      AND data_hora < p_data_hora
    RETURNING idAgenda INTO v_old_agenda;
    DELETE FROM AGENDA
    WHERE idAgenda = v_old_agenda
      AND status = 'cancelado'
      AND data_hora < CURRENT_TIMESTAMP - INTERVAL '30 days';
    RAISE NOTICE 'Agendamento criado. ID=%', v_idAgenda;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Erro: %', SQLERRM;
        RAISE;
END;
$$;

CREATE OR REPLACE FUNCTION trg_validar_horario_func() RETURNS TRIGGER AS $$
BEGIN
    IF NEW.data_hora < CURRENT_TIMESTAMP THEN
        RAISE EXCEPTION 'Não é permitido agendar no passado.';
    END IF;
    IF EXTRACT(HOUR FROM NEW.data_hora) < 8 OR EXTRACT(HOUR FROM NEW.data_hora) >= 20 THEN
        RAISE EXCEPTION 'Horário fora do expediente.';
    END IF;
    IF EXTRACT(DOW FROM NEW.data_hora) = 0 THEN
        RAISE EXCEPTION 'Não há atendimento aos domingos.';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_validar_horario
BEFORE INSERT OR UPDATE ON AGENDA
FOR EACH ROW
EXECUTE FUNCTION trg_validar_horario_func();

INSERT INTO AGENDA (data_hora, idFun, idCliente, idProcedimento, status)
SELECT
    '2026-06-24 10:00:00'::timestamp,
    (SELECT idFun FROM FUNCIONARIO WHERE cpf='111.222.333-44'),
    (SELECT idCliente FROM CLIENTE WHERE cpf='123.456.789-00'),
    (SELECT idProcedimento FROM PROCEDIMENTO WHERE nome='Corte de cabelo'),
    'agendado'
WHERE NOT EXISTS (
    SELECT 1 FROM AGENDA
    WHERE data_hora = '2026-06-24 10:00:00'::timestamp
    AND idFun = (SELECT idFun FROM FUNCIONARIO WHERE cpf='111.222.333-44')
);

INSERT INTO AGENDA (data_hora, idFun, idCliente, idProcedimento, status)
SELECT
    '2026-06-25 14:00:00'::timestamp,
    (SELECT idFun FROM FUNCIONARIO WHERE cpf='222.333.444-55'),
    (SELECT idCliente FROM CLIENTE WHERE cpf='111.111.111-11'),
    (SELECT idProcedimento FROM PROCEDIMENTO WHERE nome='Manicure'),
    'confirmado'
WHERE NOT EXISTS (
    SELECT 1 FROM AGENDA
    WHERE data_hora = '2026-06-25 14:00:00'::timestamp
    AND idFun = (SELECT idFun FROM FUNCIONARIO WHERE cpf='222.333.444-55')
);