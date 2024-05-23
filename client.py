import socket
import hashlib
import threading

username, salt, pwd = ('sdibanez', 'd188a8a09d7b2993cf9f1fceaa1e6d81', '4103daa86952d92444ad2f1238c761cc2779908c04ebedbcd9ebbeb1c5403d9b12fe45a5baaf0b9c671c534997937348ad711f49bb3fa29f125d32b7fe85dd38')
encontrado = False

def process_passwords(start, end, possible_passwords, thread_id):
    global encontrado
    inicio = start
    primerIndex = start
    total = end - start
    while not encontrado and inicio < end:
        cadena = pwd + "\n" + salt
        while (inicio < end) and (len(cadena) < 8130):
            cadena = cadena + "\n" + possible_passwords[inicio]
            inicio = inicio + 1
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect(('localhost', 9999))
        except Exception as e:
            print(f'Thread {thread_id} - Error connecting to server: {e}')
            return
        
        try:
            buffer = cadena.encode('utf-8')
            tamano = len(buffer)
            client.sendall(f'{tamano:08d}'.encode('utf-8'))
            client.sendall(buffer)
            respuesta = client.recv(10).decode('utf-8')
            percent = (inicio - start) *100.0 / total;
            print(f'Thread {thread_id}: {percent:0.2f}% Enviados {tamano} bytes al servidor desde la linea {primerIndex} hasta la linea {inicio - 1}. Respuesta {respuesta}')
            iresp = int(respuesta)
            if (iresp >= 0):
                posicion = primerIndex + iresp
                passwd = possible_passwords[posicion]
                print(f'Thread {thread_id}: El password esta en la posicion {posicion}: {passwd}')
                encontrado = True
        except Exception as e:
            print(f'Thread {thread_id} - unexpected error: {e}')
            return
        finally:
            client.close() 
        primerIndex = inicio

def main():
    try:
        possible_passwords = []
         
        with open('rockyou.txt', 'r', encoding='utf-8', errors='ignore') as file:
            possible_passwords = [line.strip() for line in file]

        total_passwords = len(possible_passwords)
        num_threads = 59  # Puedes ajustar esto según tus necesidades
        chunk_size = total_passwords // num_threads

        threads = []
        for i in range(num_threads):
            start = i * chunk_size
            end = (i + 1) * chunk_size if i != num_threads - 1 else total_passwords
            thread = threading.Thread(target=process_passwords, args=(start, end, possible_passwords, i))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()
    except Exception as e:
        print(f'Error in main function: {e}')

if __name__ == '__main__':
    main()