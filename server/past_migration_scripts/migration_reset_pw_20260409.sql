-- Reset de senha: user_id=92, username=Anthony001
-- Data: 2026-04-09
-- Motivo: hash anterior inválido
-- Executado diretamente via docker exec no container flashcard_server

UPDATE users SET password_hash='$2b$12$gUAZbR.e7sbEZITrSlff1OV5DbK4/dfi/mBfv7KMf12FU5tMZo77q' WHERE user_id=92;
