import mysql.connector

def conectar_bd():
    try:
        db_connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='Root',
            database='bd'
        )
        print('Conectado')
        return db_connection
    except mysql.connector.Error as error:
        if error.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
            print('Banco de dados não existe')
        elif error.errno == mysql.connector.errorcode.ER_ACCESS_DENIED_ERROR:
            print('Usuário ou senha incorretos')
        else:
            print(error)
        return None

def registrar_usuario(nickname, email, senha, num):
    db_connection = conectar_bd()
    if db_connection:
        try:
            cursor = db_connection.cursor()
            cursor.execute("INSERT INTO usuarios (nickname, email, senha, num) VALUES (%s, %s, %s, %s)", (nickname, email, senha, num))
            db_connection.commit()
            cursor.close()
            print('Cadastro realizado com sucesso!')
        except mysql.connector.Error as error:
            print(f'Erro ao registrar: {error}')
        finally:
            db_connection.close()
            print('Conexão fechada')

def verificar_login(email, senha):
    db_connection = conectar_bd()
    if db_connection:
        try:
            cursor = db_connection.cursor()
            cursor.execute("SELECT nickname FROM usuarios WHERE email = %s AND senha = %s", (email, senha))
            usuario = cursor.fetchone()
            cursor.close()
            if usuario:
                return usuario[0]  # Retorna o nickname
        except mysql.connector.Error as error:
            print(f'Erro ao verificar login: {error}')
        finally:
            db_connection.close()
            print('Conexão fechada')
    return None