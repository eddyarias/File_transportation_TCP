import socket
import os

# Configuraciones generales
BUFFER_SIZE = 4096  # Tamaño del buffer de datos para transmisión
SEPARADOR = "<SEPARADOR>"  # Separador de nombre de archivo y tamaño

# Función para iniciar el nodo en modo servidor (recibe archivos)
def iniciar_servidor(ip, puerto):
    # Crea el socket TCP
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.bind((ip, puerto))
    servidor.listen(1)
    print(f"Servidor escuchando en {ip}:{puerto}...")

    # Acepta conexiones
    cliente_socket, cliente_direccion = servidor.accept()
    print(f"Conexión desde {cliente_direccion}")

    # Recibe la información del archivo
    recibido = cliente_socket.recv(BUFFER_SIZE).decode()
    nombre_archivo, tamano_archivo = recibido.split(SEPARADOR)
    tamano_archivo = int(tamano_archivo)

    # Abre el archivo para escribir los datos que recibe
    with open(nombre_archivo, "wb") as f:
        bytes_recibidos = 0
        while bytes_recibidos < tamano_archivo:
            datos = cliente_socket.recv(BUFFER_SIZE)
            if not datos:
                break
            f.write(datos)
            bytes_recibidos += len(datos)
            print(f"Recibido {bytes_recibidos} de {tamano_archivo} bytes")

    print(f"Archivo {nombre_archivo} recibido con éxito.")
    cliente_socket.close()
    servidor.close()

# Función para iniciar el nodo en modo cliente (envía archivos)
def iniciar_cliente(ip, puerto, nombre_archivo):
    # Verifica que el archivo existe
    if not os.path.exists(nombre_archivo):
        print("El archivo no existe.")
        return

    # Obtiene el tamaño del archivo
    tamano_archivo = os.path.getsize(nombre_archivo)

    # Crea el socket TCP
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(f"Conectando a {ip}:{puerto}")
    cliente.connect((ip, puerto))

    # Envia el nombre y tamaño del archivo
    cliente.send(f"{nombre_archivo}{SEPARADOR}{tamano_archivo}".encode())

    # Envía el archivo
    with open(nombre_archivo, "rb") as f:
        bytes_enviados = 0
        while bytes_enviados < tamano_archivo:
            datos = f.read(BUFFER_SIZE)
            if not datos:
                break
            cliente.sendall(datos)
            bytes_enviados += len(datos)
            print(f"Enviados {bytes_enviados} de {tamano_archivo} bytes")

    print(f"Archivo {nombre_archivo} enviado con éxito.")
    cliente.close()

# Código principal
if __name__ == "__main__":
    # Selecciona el modo: 'enviar' o 'recibir'
    modo = input("Selecciona el modo (enviar/recibir): ").strip().lower()
    ip = input("Ingresa la IP del nodo remoto: ").strip()
    puerto = int(input("Ingresa el puerto: "))

    if modo == "recibir":
        iniciar_servidor(ip, puerto)
    elif modo == "enviar":
        nombre_archivo = input("Ingresa el nombre del archivo a enviar: ").strip()
        iniciar_cliente(ip, puerto, nombre_archivo)
    else:
        print("Modo no válido. Usa 'enviar' o 'recibir'.")
