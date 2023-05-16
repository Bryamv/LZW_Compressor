import time
import sys
from mpi4py import MPI
import os
import math
dictionary = {}
for i in range(256):
        dictionary[bytes([i])] = i
def lzw_compress(data):
    
    

    result = []
    buffer = b""
    for byte in data:
        new_buffer = buffer + bytes([byte])
        if new_buffer in dictionary:
            buffer = new_buffer
        else:
            result.append(int.from_bytes(dictionary[buffer], byteorder='big'))
            dictionary[new_buffer] = len(dictionary).to_bytes(2, byteorder='big')
            buffer = bytes([byte])
            if len(dictionary) >= max_dict_size:
                break
    if buffer:
        result.append(int.from_bytes(dictionary[buffer], byteorder='big'))

    return result, dictionary


def compress_file(input_file_path, output_file_path):

    file_size = os.path.getsize(input_file_path)
    part_size = math.ceil(file_size / size)

    file_parts = []
    with open(input_file_path, 'rb') as file:
        for i in range(size):
            data = file.read(part_size)
            # Agrega los n bytes a la lista de fragmentos
            file_parts.append(data)


    # Distribuir la lista entre los procesos
    data = comm.scatter(file_parts, root=0)

    if rank == 0:
        compressed_text, dictionary = lzw_compress(data)
        compressed_data = bytearray()
        for code in compressed_text:
            compressed_data.extend(code.to_bytes(4, byteorder="big"))

        for i in range(1, size):
            comm.send(dictionary, dest=i)

        data = compressed_text

        for i in range(1, size):
            # Recibe los datos de cada proceso
            data += comm.recv(source=i)
            
            # Escribe los datos en el archivo de salida
            with open(output_file_path, "wb") as output_file:
                for code in data:
                    output_file.write(code.to_bytes(4, byteorder="big"))
    else: 
        # Comprime los datos recibidos
        compressed_text = lzw_compress(data)
        # Convierte los datos comprimidos a bytes
        # Envía los datos comprimidos al proceso 0
        print(f"proceso {rank}: {(compressed_text)}")
        comm.send(compressed_text, dest=0)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Debes especificar el nombre del archivo a comprimir y el nombre del archivo de salida")
        sys.exit()
    input_file_path = sys.argv[1]
    output_file_path = sys.argv[2]

    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()


    start_time = MPI.Wtime()

    compress_file(input_file_path, output_file_path)

    end_time = MPI.Wtime()
    if rank == 0:
       print(f"{end_time - start_time:.2f}")

