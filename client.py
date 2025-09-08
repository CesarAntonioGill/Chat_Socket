import socket

HOST = "127.0.0.1"
PORT = 5000

def main():
    print("Cliente de chat (escribí mensajes y Enter; escribí 'exito' para terminar)\n")
    try:
        with socket.create_connection((HOST, PORT)) as s:
            while True:
                mensaje = input("> ").strip()
                if mensaje.lower() in ("éxito", "exito"):
                    print("Saliendo del cliente...")
                    break

                try:
                    s.sendall((mensaje + "\n").encode('utf-8'))
                except BrokenPipeError:
                    print("El servidor cerró la conexión.")
                    break

                data = s.recv(1024)
                if not data:
                    print("Servidor sin respuesta, cerrando...")
                    break
                print(data.decode('utf-8', errors='replace').strip())
    except ConnectionRefusedError:
        print(f"No se pudo conectar con el servidor en {HOST}:{PORT}. ¿Está ejecutándose?")
    except Exception as e:
        print(f"Error de cliente: {e}")

if __name__ == "__main__":
    main()

