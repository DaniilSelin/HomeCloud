import os
from .connection import connection
from sqlalchemy import text


with open(
        os.path.join(os.path.dirname(__file__), "sql/trigger-limiting-UserReqToken.sql")
) as trigger_file:
    connection.execute(text(trigger_file.read()))