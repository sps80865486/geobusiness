This repository connects to strava for obtaining segments information for a marketing purpose.

It use Flask for accesing strava web and obtaining the access token for accesing segments information.

Follow the nex steps for launching the app:

1- Lanzamos el server.py, desde consola : python server.py
2- Desde el navegador ponemos la url de login: http:127.0.0.1:5000/
3- Nos logeamos con el usuario strava y nos devuelte el token de acceso
4- La aplicacion usa el token de acceso para realizar varias queries
5- El resultado se muestra en la pagina creada a partir de los templates en directorio: templates
