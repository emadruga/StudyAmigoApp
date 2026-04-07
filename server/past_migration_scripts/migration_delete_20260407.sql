-- Deleção de contas duplicadas
-- Gerado em: 2026-04-07 10:24:35 por manage_users.py
-- Revise cuidadosamente antes de aplicar.
--
-- user_id=53  username=Rogério🚲  nome=Rogério Gabriel Barros dos Santos Simões
-- user_id=66  username=Rogério 🚲  nome=Rogério Gabriel Barros dos Santos Simões
-- user_id=70  username=Rogério  nome=Rogério Gabriel Barros dos Santos Simões
-- user_id=73  username=Rogerio  nome=Rogério Gabriel Barros dos Santos Simões
-- user_id=87  username=Rogerio G  nome=Rogério Gabriel Barros dos Santos Simões

DELETE FROM users WHERE user_id IN (53, 66, 70, 73, 87);

-- Remover arquivos de banco individual:
-- rm user_dbs/user_53.db
-- rm user_dbs/user_66.db
-- rm user_dbs/user_70.db
-- rm user_dbs/user_73.db
-- rm user_dbs/user_87.db
