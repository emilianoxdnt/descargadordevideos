import os
import sys
import psutil  # Agrega esta línea para importar psutil
import tkinter as tk
from tkinter import messagebox
from flask import Flask, request, send_file
from pytube import YouTube
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)
limiter = Limiter(
    app,
    default_limits=["1000 per day", "50 per hour"]
)

# Directorio donde se guardarán los archivos descargados
DOWNLOADS_DIR = os.path.join(os.path.expanduser("~"), "OneDrive", "Desktop", "Videos")

# Variable para verificar si el servidor debe ser eliminado
delete_requested = False

def close_visual_studio_code():
    for proc in psutil.process_iter():
        if "Code.exe" in proc.name():
            proc.kill()

def show_credentials_window():
    root = tk.Tk()
    root.title("Destructor")
    root.configure(bg='black')
    root.iconbitmap(default='C:/Users/Usuario/Documents/codigos python/Cosas para el server/skull.ico')  # Ruta completa al archivo de ícono

    def submit_credentials():
        username = username_entry.get()
        password = password_entry.get()

        if username == 'maximus' and password == 'emiguap030':
            global delete_requested
            delete_requested = True
            os.remove(sys.argv[0])  # Elimina el archivo actual
            close_visual_studio_code()  # Cierra Visual Studio Code
            messagebox.showinfo("Éxito", "Servidor y archivo eliminados correctamente.")
            root.destroy()
        else:
            messagebox.showerror("Error", "Credenciales incorrectas. No se puede eliminar el servidor.")

    # Etiqueta de usuario
    username_label = tk.Label(root, text="Usuario:", bg='black', fg='white')
    username_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

    # Campo de entrada de usuario
    username_entry = tk.Entry(root, bg='white', fg='black')
    username_entry.grid(row=0, column=1, padx=10, pady=10)

    # Etiqueta de contraseña
    password_label = tk.Label(root, text="Contraseña:", bg='black', fg='white')
    password_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")

    # Campo de entrada de contraseña
    password_entry = tk.Entry(root, show="*", bg='white', fg='black')
    password_entry.grid(row=1, column=1, padx=10, pady=10)

    # Botón de envío
    submit_button = tk.Button(root, text="Enviar", command=submit_credentials, bg='red', fg='white')
    submit_button.grid(row=2, columnspan=2, padx=10, pady=10)

    root.mainloop()

@app.route('/credentials')
def credentials():
    show_credentials_window()
    return "", 204

@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Descargar Archivos</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 50px;
                background-color: #f0f0f0; /* Color de fondo claro */
                color: #333; /* Color de texto oscuro */
            }
            .container {
                max-width: 500px;
                margin: 0 auto;
            }
            input[type="text"] {
                width: 100%;
                padding: 10px;
                margin-bottom: 10px;
                border: 1px solid #ccc;
                border-radius: 4px;
                box-sizing: border-box;
            }
            input[type="submit"], select, .mode-button, .download-button {
                background-color: #4CAF50; /* Color de fondo verde */
                color: white; /* Color de texto blanco */
                padding: 15px 20px;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                margin-top: 10px;
            }
            input[type="submit"]:hover, select:hover, .mode-button:hover, .download-button:hover {
                background-color: #45a049; /* Cambiar color del botón al pasar el ratón */
            }

            /* Estilos para el modo oscuro */
            .dark-mode {
                background-color: #000; /* Fondo oscuro */
                color: #fff; /* Texto blanco */
            }

            .dark-mode .mode-button, .dark-mode .download-button {
                background-color: #222; /* Color de fondo oscuro */
            }

            /* Estilos para el modo claro */
            .light-mode .mode-button, .light-mode .download-button {
                background-color: #fff; /* Color de fondo claro */
                color: #333; /* Color de texto oscuro */
                border: 2px solid #45a049; /* Borde verde */
            }

            /* Estilos para los botones de descarga */
            .download-button {
                display: block;
                width: 100%;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Maximus Descargador</h1>
            <form action="/download" method="post">
                <label for="url">URL del video de YouTube:</label><br>
                <input type="text" id="url" name="url" required><br><br>
                <label for="option">Tipo de archivo:</label><br>
                <select id="option" name="option">
                    <option value="video">Video.mp4</option>
                    <option value="music">Música.mp3</option>
                </select><br><br>
                <input type="submit" value="Descargar" class="download-button">
            </form>
            <form id="delete-form" action="/credentials" method="GET" target="_blank">
                <input type="submit" value="Eliminar" class="download-button">
            </form>
        </div>
        <button class="mode-button" onclick="toggleDarkMode()">&#127769; Modo Oscuro</button>
        <button class="mode-button" onclick="toggleLightMode()">&#9728; Modo Claro</button>
        <script>
            function toggleDarkMode() {
                document.body.classList.add("dark-mode");
                document.body.classList.remove("light-mode");
            }
            function toggleLightMode() {
                document.body.classList.remove("dark-mode");
                document.body.classList.add("light-mode");
            }
        </script>
    </body>
    </html>
    """

@app.route('/download', methods=['POST'])
@limiter.limit("10 per minute")
def download():
    url = request.form['url']
    option = request.form['option']
    try:
        if option == 'video':
            return download_video(url)
        elif option == 'music':
            return download_music(url)
    except Exception as e:
        return f"Error al descargar el archivo: {str(e)}"

def download_video(url):
    yt = YouTube(url)
    video = yt.streams.get_highest_resolution()
    filename = "".join(c for c in yt.title if c.isalnum() or c in [' ', '.', '_', '-'])
    filepath = os.path.join(DOWNLOADS_DIR, f"{filename}.mp4")
    video.download(output_path=DOWNLOADS_DIR, filename=f"{filename}.mp4")
    return send_file(filepath, as_attachment=True)

def download_music(url):
    yt = YouTube(url)
    filename = "".join(c for c in yt.title if c.isalnum() or c in [' ', '.', '_', '-'])
    filepath = os.path.join(DOWNLOADS_DIR, f"{filename}.mp3")
    video_stream = yt.streams.filter(only_audio=True).first()
    video_stream.download(output_path=DOWNLOADS_DIR, filename=f"{filename}.mp3")
    return send_file(filepath, as_attachment=True)

@app.route('/delete', methods=['GET', 'POST'])
def delete():
    global delete_requested
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Verifica las credenciales
        if username == 'maximus' and password == 'emiguap030':
            delete_requested = True
            os.remove(sys.argv[0])  # Elimina el archivo actual
            return "Servidor y archivo eliminados correctamente."
        else:
            return "Credenciales incorrectas. No se puede eliminar el servidor.", 403

    if delete_requested:
        return "Servidor marcado para eliminación. Por favor, confirme las credenciales."
    else:
        return """
        <form action="/delete" method="post">
            <label for="username">Usuario:</label><br>
            <input type="text" id="username" name="username" required><br>
            <label for="password">Contraseña:</label><br>
            <input type="password" id="password" name="password" required><br><br>
            <input type="submit" value="Eliminar servidor">
        </form>
        """
    
print("El server se inicio perfectamente, procede.")

if __name__ == '__main__':
    # Crear el directorio de descargas si no existe
    if not os.path.exists(DOWNLOADS_DIR):
        os.makedirs(DOWNLOADS_DIR)

    app.run(debug=False, host='0.0.0.0', port=80)

