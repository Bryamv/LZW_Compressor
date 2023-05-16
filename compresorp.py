import time
import sys
from mpi4py import MPI
import os
import math
dictionary = {}
for i in range(256):
        dictionary[bytes([i])] = i

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

def lzw_compress(data):
    
    

    result = []
    buffer = b""
    for byte in data:
        new_buffer = buffer + bytes([byte])
        if new_buffer in dictionary:
            buffer = new_buffer
        else:
            result.append(dictionary[buffer])
            dictionary[new_buffer] = len(dictionary)
            buffer = bytes([byte])
    if buffer:
        result.append(dictionary[buffer])

    return result


def compress_file(input_file_path, output_file_path):

    file_size = os.path.getsize(input_file_path)

    # Calcula el tamaño de cada parte en bytes
    part_size = math.ceil(file_size / size)

    file_parts = []
    with open(input_file_path, 'rb') as file:
        for i in range(size):
            # Lee n bytes del archivo
            data = file.read(part_size)
            
            # Agrega los n bytes a la lista de fragmentos
            file_parts.append(data)

    
    # Distribuir la lista entre los procesos
    data = comm.scatter(file_parts, root=0)
    
    
    if rank == 0:
        compressed_text = lzw_compress(data)

        data = compressed_text
        with open(f'comprimido_{rank}.bin', "wb") as output_file:
                for code in data:
                    output_file.write(code.to_bytes(4, byteorder="big"))
        
        comm.barrier()

        if os.path.exists(output_file_path):
            os.remove(output_file_path)
        for i in range(size):
            
            with open(f'comprimido_{rank}.bin', "rb") as input_file, open(output_file_path, "ab") as output_file:
                while True:
                    # Lee 4 bytes del archivo
                    code = input_file.read(4)
                    if not code:
                        break
                    # Convierte los 4 bytes a un número entero
                    code = int.from_bytes(code, byteorder="big")
                    # Convierte el número entero a 4 bytes
                    output_file.write(code.to_bytes(4, byteorder="big"))

        for i in range(size):
            if os.path.exists(f'comprimido_{i}.bin'):
                    os.remove(f'comprimido_{i}.bin')
    else: 
        # Comprime los datos recibidos
        compressed_text = lzw_compress(data)
        # Convierte los datos comprimidos a bytes
        # Envía los datos comprimidos al proceso 0
       # print(f"proceso {rank}: {(compressed_text)}")

        with open(f'comprimido_{rank}.bin', "wb") as output_file:
                for code in compressed_text:
                    output_file.write(code.to_bytes(4, byteorder="big"))

        comm.barrier()

   
        #comm.send(compressed_text, dest=0)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Debes especificar el nombre del archivo a comprimir")
        sys.exit()
    input_file_path = sys.argv[1]
    output_file_path = "comprimido.elmejorprofesor"

    start_time = time.time()
    compress_file(input_file_path, output_file_path)
    end_time = time.time()
    print(f"El tiempo de ejecución fue: {end_time - start_time:.2f} segundos")

