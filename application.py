import os

from collections import deque

from flask import Flask, render_template, session, request, redirect
from flask_socketio import SocketIO, send, emit, join_room, leave_room

from helpers import login_required

app = Flask(__name__)
app.config["SECRET_KEY"] = "my secret key"
socketio = SocketIO(app)

# Realice un seguimiento de los canales creados (compruebe el nombre del canal)
channelsCreated = []

# Realizar un seguimiento de los usuarios registrados (comprobar el nombre de usuario)
usersLogged = []

# Instanciar un dict
channelsMessages = dict()

@app.route("/")
@login_required
def index():

    return render_template("index.html", channels=channelsCreated)

@app.route("/signin", methods=['GET','POST'])
def signin():
    ''' Save the username on a Flask session
    after the user submit the sign in form '''

    # Olvida cualquier nombre de usuario
    session.clear()

    username = request.form.get("username")

    # Recuerde la sesión del usuario en una cookie si el navegador está cerrado.
        session.permanent = True

        return redirect("/")
    else:
        return render_template("signin.html")

@app.route("/logout", methods=['GET'])
def logout():
    """ Logout user from list and delete cookie."""

    # Quitar de la lista
    try:
        usersLogged.remove(session['username'])
    except ValueError:
        pass

    # Eliminar cookie
    session.clear()

    return redirect("/")

@app.route("/create", methods=['POST'])
def create():
    """ Create a channel and redirect to its page """

    # Obtener el nombre del canal del formulario
    newChannel = request.form.get("channel")

    if newChannel in channelsCreated:
        return render_template("error.html", message="¡ese canal ya existe!")

    # Agregar canal a la lista global de canales
    channelsCreated.append(newChannel)

    # Agregar canal al dictado global de canales con mensajes
    # Cada canal es una deque para usar el método popleft ()
    # https://stackoverflow.com/questions/1024847/add-new-keys-to-a-dictionary
    channelsMessages[newChannel] = deque()

    return redirect("/channels/" + newChannel)

@app.route("/channels/<channel>", methods=['GET','POST'])
@login_required
def enter_channel(channel):
    """ Show channel page to send and receive messages """

    # Actualiza el canal actual del usuario
    session['current_channel'] = channel

    if request.method == "POST":

        return redirect("/")
    else:
        return render_template("channel.html", channels= channelsCreated, messages=channelsMessages[channel])

@socketio.on("joined", namespace='/')
def joined():
    """ Send message to announce that user has entered the channel """

    # Guardar el canal actual para unirse a la sala
    room = session.get('current_channel')

    join_room(room)

    emit('status', {
        'userJoined': session.get('username'),
        'channel': room,
        'msg': session.get('username') + ' ha entrado al canal'},
        room=room)

@socketio.on("left", namespace='/')
def left():
    """ Send message to announce that user has left the channel """

    room = session.get('current_channel')

    leave_room(room)

    emit('status', {
        'msg': session.get('username') + ' ha salido del canal'},
        room=room)

@socketio.on('send message')
def send_msg(msg, timestamp):
    """ Receive message with timestamp and broadcast on the channel """

    # Transmitir solo a usuarios en el mismo canal.
    room = session.get('current_channel')

    # Guarde 100 mensajes y páselos cuando un usuario se une a un canal específico.

    if len(channelsMessages[room]) > 100:
        # El mensaje mas antigua.
        channelsMessages[room].popleft()

    channelsMessages[room].append([timestamp, session.get('username'), msg])

    emit('announce message', {
        'user': session.get('username'),
        'timestamp': timestamp,
        'msg': msg},
        room=room)
