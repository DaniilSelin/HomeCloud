CREATE OR REPLACE FUNCTION check_user_limit()
RETURNS TRIGGER AS $$
DECLARE
    user_count INTEGER;
    max_users INTEGER;
BEGIN
    -- Проверяем, существует ли указанный RegistrationToken
    SELECT max_users INTO max_users FROM "RegistrationToken" WHERE "regToken_id" = NEW."regToken_id";

    IF NOT FOUND THEN
        RAISE EXCEPTION 'RegistrationToken does not exist';
    END IF;

    -- Подсчитываем количество пользователей, связанных с этим RegistrationToken
    SELECT COUNT(*) INTO user_count FROM "Users" WHERE "regToken_id" = NEW."regToken_id";

    -- Проверяем, превышает ли количество пользователей максимальное значение
    IF user_count >= max_users THEN
        RAISE EXCEPTION 'Maximum number of users for this token reached';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER user_limit_trigger
BEFORE INSERT ON "Users"
FOR EACH ROW EXECUTE FUNCTION check_user_limit();