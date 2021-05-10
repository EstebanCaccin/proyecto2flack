document.addEventListener('DOMContentLoaded', () => {

    // Conectarse a websocket
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);


     // Cuando esté conectada, configure el botón
    socket.on('connect', () => {


         // Notificar a la usuario del servidor se ha unido
        socket.emit('joined');


        // Olvídese del último canal del usuario cuando haga clic en '+ Canal'
        document.querySelector('#newChannel').addEventListener('click', () => {
            localStorage.removeItem('last_channel');
        });

        // Cuando el usuario abandona el canal, se redirige a '/'
        document.querySelector('#leave').addEventListener('click', () => {

            // Notificar al usuario del servidor que se ha ido
            socket.emit('left');

            localStorage.removeItem('last_channel');
            window.location.replace('/');
        })

        // Olvidar el último canal del usuario cuando se desconecta
        document.querySelector('#logout').addEventListener('click', () => {
            localStorage.removeItem('last_channel');
        });


         // La tecla 'Enter' en textarea también envía un mensaje
        // https://developer.mozilla.org/en-US/docs/Web/Events/keydown
        document.querySelector('#comment').addEventListener("keydown", event => {
            if (event.key == "Enter") {
                document.getElementById("send-button").click();
            }
        });

        // El botón Enviar emite un evento de "mensaje enviado"
        document.querySelector('#send-button').addEventListener("click", () => {

            // Ahorre tiempo en formato HH: MM: SS
            let timestamp = new Date;
            timestamp = timestamp.toLocaleTimeString();

            // Guardar la entrada del usuario
            let msg = document.getElementById("comment").value;

            socket.emit('send message', msg, timestamp);

            // Borrar entrada
            document.getElementById("comment").value = '';
        });
    });


     // Cuando el usuario se une a un canal, agregue un mensaje y los usuarios conectados.
    socket.on('status', data => {


        // Mensaje de difusión del usuario unido.
        let row = '<' + `${data.msg}` + '>'
        document.querySelector('#chat').value += row + '\n';


         // Guardar el canal actual del usuario en localStorage
        localStorage.setItem('last_channel', data.channel)
    })

    // Cuando se anuncie un mensaje, agréguelo al área de texto.
    socket.on('announce message', data => {

        // Dar formato al mensaje
        let row = '<' + `${data.timestamp}` + '> - ' + '[' + `${data.user}` + ']:  ' + `${data.msg}`
        document.querySelector('#chat').value += row + '\n'
    })


});
