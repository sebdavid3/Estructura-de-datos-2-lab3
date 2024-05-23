import socket
import threading
import hashlib

def buscar_password(pwd, salt, possible_passwords):
    for i,password in enumerate(possible_passwords):
        for pepper in range (256):
            H = hashlib.sha3_512()
            password_b = bytes(password, 'utf-8')
            H.update(password_b)
            
            pepper_b = pepper.to_bytes(1,'big')
            H.update(pepper_b)
            
            salt_b = bytes.fromhex(salt)
            H.update(salt_b)
            
            pwd_h = H.hexdigest()
            if pwd == pwd_h:
                return i
            
    return -1        

# Codigos de respuesta -4: no se leyo tamano, -3: no se leyo mensaje,  -2: size <= 2, -1: no encontro en la lista, >= 0 encontrado
def handle_client(client_socket):
    respuesta = -2 # No se recibio lista
    # leer encabezado de 4 bytes que contiene el tamano total del mensaje
    buffer = client_socket.recv(8)
    if not buffer or len (buffer) < 8:
        print('No recibio counter')
        client_socket.sendall('-4'.encode('utf-8'))
        client_socket.close()
        return
    
    # leer mensaje
    tamano = int(buffer.decode('utf-8'))
    message_buffer = bytearray(0)
    leido = 0
    while leido < tamano:
        buffer = client_socket.recv(tamano - leido)
        if not buffer:
            print(f'No recibio mensaje, leidos {leido} de {tamano} bytes')
            client_socket.sendall('-3'.encode('utf-8'))
            client_socket.close()
            return
        leido = leido + len(buffer)
        message_buffer = message_buffer + buffer

    message = message_buffer.decode('utf-8')
    lineas = message.split("\n")
    size = len(lineas)
    if size > 2:
        pwd = lineas[0]
        salt = lineas[1]
        lineas = lineas[2:size]
        print('Procesando')
        respuesta = buscar_password(pwd, salt, lineas)
        print(f'Procesado respuesta: {respuesta}')
        
    client_socket.sendall(f'{respuesta}'.encode('utf-8'))
    client_socket.close()

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('0.0.0.0', 9999))
server.listen(100)
print('Server listening on port 9999')

while True:
    client_socket, addr = server.accept()
    client_handler = threading.Thread(target=handle_client, args=(client_socket,))
    client_handler.start()
