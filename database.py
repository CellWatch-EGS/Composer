# import psycopg2

# # Conectar ao banco de dados PostgreSQL (substitua os valores conforme necessário)
# conn = psycopg2.connect(
#     dbname="nome_do_banco_de_dados",
#     user="nome_do_usuario",
#     password="senha",
#     host="localhost"
# )
# cursor = conn.cursor()

# Código SQL para criar a tabela users
# create_users_table = """
# CREATE TABLE IF NOT EXISTS users (
#     id SERIAL PRIMARY KEY,
#     username VARCHAR(255) NOT NULL UNIQUE,
#     password VARCHAR(255) NOT NULL
# );
# """

# # Código SQL para criar a tabela schedule
# create_schedule_table = """
# CREATE TABLE IF NOT EXISTS schedule (
#     id SERIAL PRIMARY KEY,
#     guardID INTEGER NOT NULL,
#     schedule_id VARCHAR(255) NOT NULL,
#     locationID INTEGER NOT NULL
# );
# """

# # Executa o código SQL
# cursor.execute(create_users_table)
# cursor.execute(create_schedule_table)

# # Commit e fecha a conexão
# conn.commit()
# conn.close()
