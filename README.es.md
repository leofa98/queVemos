[Read in English](README.md)

# QuéVemos
**Demo:** https://quevemos.pythonanywhere.com

QuéVemos es una aplicación web para decidir qué ver en grupo. Es un proyecto personal en el que trabajo de vez en cuando. Lo uso para practicar.

Cada usuario guarda en su biblioteca lo que quiere ver y lo que ya ha visto. Para elegir en grupo, un usuario crea una sala y comparte el código. La app compara las bibliotecas de los miembros, sugiere títulos que tienen pendientes y descarta los que alguien ya ha visto. Después los miembros votan y el anfitrión cierra la sala con el ganador.

## Qué se puede hacer

**Cuenta**
- Registrarse, iniciar sesión y cerrar sesión

**Biblioteca**
- Añadir películas y series y marcarlas como pendientes, vistas o abandonadas
- Poner nota del 1 al 10 a lo que has visto y escribir un comentario
- Buscar, filtrar por estado y pasar de página sin recargar

**Salas**
- Crear una sala y compartir el código
- Unirse a una sala con el código
- Pedir sugerencias a partir de las bibliotecas de los miembros
- Proponer títulos a mano
- Votar a favor o en contra, cambiar el voto o quitarlo
- Cerrar la sala y elegir el ganador (solo el anfitrión)

## Cómo funcionan las sugerencias

1. Se cogen todos los miembros de la sala.
2. Para cada título se cuenta cuántos miembros lo tienen pendiente.
3. Si la sala no permite títulos vistos, se quitan los que alguien ya ha visto.
4. Se ordenan por el número de miembros que los tienen pendientes y se quedan los cinco primeros.
5. Cada sugerencia guarda un motivo, por ejemplo "Lo tenéis pendiente todos".

Si no se puede sugerir nada, la app explica por qué: nadie tiene pendientes, todo lo pendiente ya lo ha visto alguien o ya están todas las sugerencias en la sala.

## Tecnologías

- Django 5.2
- SQLite
- JavaScript sin frameworks
- Bootstrap 5 y Bootstrap Icons

## Lo que he practicado

- Separar el proyecto en varias apps de Django (`accounts`, `catalog`, `library`, `rooms` y `core`) y relacionar sus modelos
- Consultas con el ORM usando `annotate`, `Count` con filtros, `F`, `Q`, `Exists` y `OuterRef`
- Restricciones únicas en la base de datos para no duplicar entradas, miembros, candidatos ni votos
- Comprobar permisos en el servidor: solo los miembros ven la sala y solo el anfitrión la cierra
- Hacer peticiones con `fetch` y CSRF, y recargar trozos de HTML renderizados por Django sin recargar la página
- Delegación de eventos para elementos que se pintan una y otra vez
- Cambiar las variables de Bootstrap para usar mi propia paleta de colores
- Diseño adaptado al móvil

## Estado

Está en desarrollo. Todo lo de arriba funciona, pero quedan cosas por hacer:

- Buscar títulos con la API de TMDb. Ahora salen de un catálogo pequeño y fijo.
- Que la sala se actualice sola cuando votan los demás.
- Tener en cuenta los títulos abandonados en las sugerencias.
- Usar géneros y notas para afinar las sugerencias.
- Ordenar algunas vistas que se han quedado largas.
- Tests.
- Desplegarla.

## Cómo ejecutarla

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py loaddata catalog.json demo_users.json demo_entries.json
python manage.py runserver
```

En Linux o macOS el entorno se activa con `source .venv/bin/activate`.

Después abre `http://127.0.0.1:8000`, crea una cuenta y empieza a añadir títulos a tu biblioteca.

## Datos de prueba
Puedes probar la demo con los usuarios de abajo o crear tu propia cuenta. Los datos de la demo pueden reiniciarse de vez en cuando.

El comando `loaddata` carga un catálogo de 50 títulos y tres usuarios de ejemplo: `marta`, `luis` y `ana`, con la contraseña `quevemos2026`. Sus bibliotecas tienen títulos en común, así que sirven para probar las salas sin tener que crear varias cuentas y rellenarlas a mano. Si solo quieres el catálogo, carga únicamente `catalog.json`.

Para probar una sala con varios usuarios, usa un navegador distinto o una ventana privada para cada uno.