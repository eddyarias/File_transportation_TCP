import socket
import os
import tqdm
import time

# Configuraciones generales
BUFFER_SIZE = 64 * 1024  # Tamaño del buffer (64 KB para mayor velocidad)
SEPARADOR = "<SEPARADOR>"  # Separador para el nombre y tamaño del archivo

# Función para iniciar el nodo en modo servidor (recibe archivos)
def iniciar_servidor(ip, puerto):
    try:
        servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        servidor.bind((ip, puerto))
        servidor.listen(1)
        print(f"Servidor esperando conexión en {ip}:{puerto}...")

        while True:
            cliente_socket, cliente_direccion = servidor.accept()
            print(f"Conexión establecida con {cliente_direccion}")

            # Recibe información sobre el archivo
            recibido = cliente_socket.recv(BUFFER_SIZE).decode()
            nombre_archivo, tamano_archivo = recibido.split(SEPARADOR)
            tamano_archivo = int(tamano_archivo)

            # Si el archivo existe y está incompleto, permite la reanudación
            bytes_recibidos = 0
            modo_escritura = "wb" if not os.path.exists(nombre_archivo) else "ab"
            if modo_escritura == "ab":
                bytes_recibidos = os.path.getsize(nombre_archivo)
                print(f"Reanudando descarga de {nombre_archivo}, {bytes_recibidos} bytes ya recibidos.")

            # Informar al cliente sobre el punto de reanudación
            cliente_socket.send(f"{bytes_recibidos}".encode())

            # Inicializar la barra de progreso
            barra_progreso = tqdm.tqdm(range(bytes_recibidos, tamano_archivo), f"Recibiendo {nombre_archivo}", unit="B", unit_scale=True, unit_divisor=1024)

            # Recibir y escribir datos al archivo
            with open(nombre_archivo, modo_escritura) as f:
                while bytes_recibidos < tamano_archivo:
                    try:
                        datos = cliente_socket.recv(BUFFER_SIZE)
                        if not datos:
                            break
                        f.write(datos)
                        bytes_recibidos += len(datos)
                        barra_progreso.update(len(datos))
                    except Exception as e:
                        print(f"Error durante la recepción: {e}")
                        cliente_socket.close()
                        time.sleep(2)  # Esperar antes de intentar reconectar
                        break
            barra_progreso.close()
            print(f"Archivo '{nombre_archivo}' recibido exitosamente.")
            cliente_socket.close()
    except Exception as e:
        print(f"Error en el servidor: {e}")
    finally:
        servidor.close()
        print("Servidor cerrado.")

# Función para iniciar el nodo en modo cliente (envía archivos)
def iniciar_cliente(ip, puerto, nombre_archivo):
    if not os.path.exists(nombre_archivo):
        print("El archivo no existe.")
        return

    tamano_archivo = os.path.getsize(nombre_archivo)

    while True:
        try:
            cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print(f"Conectando a {ip}:{puerto}...")
            cliente.connect((ip, puerto))
            print(f"Conexión establecida con {ip}:{puerto}")

            # Enviar nombre y tamaño del archivo
            cliente.send(f"{nombre_archivo}{SEPARADOR}{tamano_archivo}".encode())

            # Esperar respuesta del servidor sobre el punto de reanudación
            bytes_enviados = int(cliente.recv(BUFFER_SIZE).decode())
            print(f"Reanudando desde {bytes_enviados} bytes.")

            # Inicializar barra de progreso
            barra_progreso = tqdm.tqdm(range(bytes_enviados, tamano_archivo), f"Enviando {nombre_archivo}", unit="B", unit_scale=True, unit_divisor=1024)

            # Enviar el archivo desde el punto de reanudación
            with open(nombre_archivo, "rb") as f:
                f.seek(bytes_enviados)
                while bytes_enviados < tamano_archivo:
                    try:
                        datos = f.read(BUFFER_SIZE)
                        if not datos:
                            break
                        cliente.sendall(datos)
                        bytes_enviados += len(datos)
                        barra_progreso.update(len(datos))
                    except Exception as e:
                        print(f"Error durante el envío: {e}")
                        cliente.close()
                        time.sleep(2)  # Esperar antes de intentar reconectar
                        break
            barra_progreso.close()
            print(f"Archivo '{nombre_archivo}' enviado exitosamente.")
            cliente.close()
            break
        except Exception as e:
            print(f"Error en la conexión con el servidor: {e}")
            time.sleep(2)  # Esperar antes de intentar reconectar
        finally:
            cliente.close()

# Código principal
if __name__ == "__main__":
    print("Bienvenido al sistema de transferencia de archivos nodo a nodo")
    modo = input("¿Quieres enviar o recibir un archivo? (enviar/recibir): ").strip().lower()
    ip = input("Ingresa la IP del nodo remoto: ").strip()
    puerto = int(input("Ingresa el puerto (ej. 8000): "))

    if modo == "recibir":
        iniciar_servidor(ip, puerto)
    elif modo == "enviar":
        nombre_archivo = input("Ingresa el nombre del archivo a enviar: ").strip()
        iniciar_cliente(ip, puerto, nombre_archivo)
    else:
        print("Modo no válido. Usa 'enviar' o 'recibir'.")
