from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory
from flask_socketio import SocketIO, join_room, leave_room, emit
import random
from string import ascii_uppercase
import os
from werkzeug.utils import secure_filename
import base64
from banco import verificar_login, registrar_usuario

app = Flask(__name__)
app.config['SECRET_KEY'] = '12345'
socketio = SocketIO(app)
salas = {}



UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'txt'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)



def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



def gerar_nome_sala_aleatorio(length=6):
    return ''.join(random.choices(ascii_uppercase, k=length))


@app.route('/')
def login():
    return render_template('login.html')



@app.route('/inicio')
def inicio():
    if 'nickname' in session:
        return render_template('inicio.html', nickname=session['nickname'])
    return redirect(url_for('login'))



@app.route('/login', methods=['POST'])
def login_post():
    email = request.form['email']
    senha = request.form['senha']

    nickname = verificar_login(email, senha)
    if nickname:
        session['nickname'] = nickname
        return redirect(url_for('inicio'))
    flash('E-mail ou senha incorretos.', 'danger')
    return redirect(url_for('login'))



@app.route('/cadastro')
def cadastro():
    return render_template('cadastro.html')



@app.route('/registrar', methods=['POST'])
def registrar():
    nickname = request.form['nickname']
    email = request.form['mail']
    senha = request.form['senha']
    num = request.form['num']

    registrar_usuario(nickname, email, senha, num)
    flash('Cadastro realizado com sucesso!', 'success')
    return redirect(url_for('login'))



@app.route('/chat')
def chat():
    sala = request.args.get('sala')
    if sala and sala in salas and 'nickname' in session:
        return render_template('chat.html', sala=sala, nome=session['nickname'])
    return redirect(url_for('inicio'))



@socketio.on('criar_sala')
def criar_sala():
    nome_sala = gerar_nome_sala_aleatorio()
    salas[nome_sala] = []
    emit('sala_criada', {'nome_sala': nome_sala}, to=request.sid)



@socketio.on('entrar_sala')
def entrar_sala(data):
    nome_sala = data['nome_sala']
    nome_usuario = session.get('nickname')
    if nome_sala in salas:
        join_room(nome_sala)
        salas[nome_sala].append(nome_usuario)
        emit('nova_mensagem', {'texto': f'{nome_usuario} entrou na sala!'}, to=nome_sala)




@socketio.on('sair_sala')
def sair_sala(data):
    nome_sala = data['nome_sala']
    nome_usuario = session.get('nickname')
    if nome_sala in salas and nome_usuario in salas[nome_sala]:
        leave_room(nome_sala)
        salas[nome_sala].remove(nome_usuario)
        emit('nova_mensagem', {'texto': f'{nome_usuario} saiu da sala!'}, to=nome_sala)




@socketio.on('enviar_mensagem')
def enviar_mensagem(data):
    nome_sala = data['nome_sala']
    texto = data['texto']
    nome_usuario = session.get('nickname')
    if nome_sala in salas:
        mensagem = f"{nome_usuario}: {texto}"
        emit('nova_mensagem', {'texto': mensagem}, to=nome_sala)




@socketio.on('enviar_arquivo')
def enviar_arquivo(data):
    nome_sala = data['nome_sala']
    nome_usuario = data['nome_usuario']
    arquivo = data['arquivo']
    nome_arquivo = data['nome_arquivo']

    arquivo_decodificado = base64.b64decode(arquivo.split(",")[1])
    caminho_arquivo = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(nome_arquivo))

    with open(caminho_arquivo, "wb") as f:
        f.write(arquivo_decodificado)

    mensagem = f"{nome_usuario} enviou um arquivo: {nome_arquivo}"
    file_url = f"/uploads/{secure_filename(nome_arquivo)}"
    emit('nova_mensagem', {'texto': mensagem, 'file_url': file_url}, room=nome_sala)




@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    socketio.run(app, debug=True)
