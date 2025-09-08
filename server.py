import socket
import sqlite3
from datetime import datetime
import threading

HOST = "127.0.0.1"   
PORT = 5000          

DB_NAME = "chat.db"

# --- Base de datos ---
def init_db():
    """Crea la tabla si no existe."""
    try:
        with sqlite3.connect(DB_NAME) as conn:
            conn.execute(
                """CREATE TABLE IF NOT EXISTS mensajes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    contenido TEXT NOT NULL,
                    fecha_envio TEXT NOT NULL,
                    ip_cliente TEXT NOT NULL
                )"""
            )
    except sqlite3.Error as e:
        print(f"[DB] Error inicializando la base: {e}")
        raise

def save_message(contenido: str, ip_cliente: str):
    """Guarda un mensaje en la DB con timestamp ISO y la IP del cliente."""
    try:
        fecha = datetime.now().isoformat(timespec='seconds')
        with sqlite3.connect(DB_NAME) as conn:
            conn.execute(
                """INSERT INTO mensajes (contenido, fecha_envio, ip_cliente)
                   VALUES (?, ?, ?)""",
                (contenido, fecha, ip_cliente)
            )
    except sqlite3.Error as e:
        print(f"[DB] Error al guardar el mensaje: {e}")
        raise

# --- Socket ---
def init_socket(host: str = HOST, port: int = PORT) -> socket.socket:
    """Configura el socket TCP/IP del servidor."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((host, port))
        s.listen(5)
        print(f"Servidor escuchando en {host}:{port}")
        return s
    except OSError as e:
        print(f"[Socket] No se pudo iniciar el servidor en {host}:{port}: {e}")
        raise

def handle_client(conn: socket.socket, addr):
    """Atiende a un cliente: recibe mensajes, guarda y responde."""
    ip, _ = addr
    print(f"[+] Conexión de {ip}")
    with conn:
        while True:
            try:
                data = conn.recv(1024)
                if not data:
                    print(f"[-] {ip} cerró la conexión.")
                    break
                mensaje = data.decode('utf-8', errors='replace').strip()

                # Si el cliente envía 'exito', cerramos este cliente.
                if mensaje.lower() in ("éxito", "exito"):
                    print(f"[~] Señal de fin recibida de {ip}")
                    break

                save_message(mensaje, ip)  # Guardar en Base de Datos

                ts = datetime.now().isoformat(timespec='seconds')
                respuesta = f"Mensaje recibido: {ts}\n"
                conn.sendall(respuesta.encode('utf-8'))
            except ConnectionResetError:
                print(f"[!] Conexión reseteada por {ip}")
                break
            except Exception as e:
                print(f"[!] Error atendiendo a {ip}: {e}")
                break
    print(f"[x] Conexión finalizada con {ip}")

def accept_loop(server_sock: socket.socket):
    """Acepta conexiones entrantes y lanza un hilo por cliente."""
    try:
        while True:
            conn, addr = server_sock.accept()
            thr = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
            thr.start()
    except KeyboardInterrupt:
        print("\n[CTRL+C] Servidor detenido por el usuario.")
    except Exception as e:
        print(f"[!] Error en el bucle de aceptación: {e}")
    finally:
        server_sock.close()

if __name__ == "__main__":
    init_db()
    print("Iniciando servidor...")
    sock = init_socket()
    accept_loop(sock)
