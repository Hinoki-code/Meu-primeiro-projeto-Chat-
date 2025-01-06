from flask import Flask, render_template, request, redirect, url_for
from flask_socketio import SocketIO, join_room, leave_room, send, emit
import random
from string import ascii_uppercase

app = Flask(__name__)
app.config['SECRET_KEY'] = '12345'
socketio = SocketIO(app)
salas = {}

def gerar_nome_sala_aleatorio(length=6):
    return ''.join(random.choices(ascii_uppercase, k=length))

@app.route('/')
def inicio():
    return render_template('inicio.html')

@app.route('/chat')
def chat():
    sala = request.args.get('sala')
    nome = request.args.get('nome')
    if sala and sala in salas and nome:
        return render_template('chat.html', sala=sala, nome=nome)
    else:
        return redirect(url_for('inicio'))

@socketio.on('criar_sala')
def criar_sala():
    nome_sala = gerar_nome_sala_aleatorio()
    salas[nome_sala] = []
    emit('sala_criada', {'nome_sala': nome_sala}, to=request.sid)

@socketio.on('entrar_sala')
def entrar_sala(data):
    nome_sala = data['nome_sala']
    nome_usuario = data['nome_usuario']
    if nome_sala in salas:
        join_room(nome_sala)
        salas[nome_sala].append(request.sid)
        send(f'{nome_usuario} entrou na sala {nome_sala}', room=nome_sala)

@socketio.on('sair_sala')
def sair_sala(data):
    nome_sala = data['nome_sala']
    nome_usuario = data['nome_usuario']
    if nome_sala in salas:
        leave_room(nome_sala)
        salas[nome_sala].remove(request.sid)
        if len(salas[nome_sala]) == 0:
            del salas[nome_sala]
        send(f'{nome_usuario} saiu da sala {nome_sala}', room=nome_sala)

@socketio.on('disconnect')
def desconectar():
    for nome_sala in list(salas.keys()):
        if request.sid in salas[nome_sala]:
            salas[nome_sala].remove(request.sid)
            leave_room(nome_sala)
            if len(salas[nome_sala]) == 0:
                del salas[nome_sala]

@socketio.on('enviar_mensagem')
def enviar_mensagem(data):
    nome_sala = data['nome_sala']
    nome_usuario = data['nome_usuario']
    mensagem = f'{nome_usuario}: {data["texto"]}'
    emit('nova_mensagem', {'texto': mensagem}, room=nome_sala)

if __name__ == '__main__':
    socketio.run(app, debug=True)
