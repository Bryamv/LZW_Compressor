import time
import sys
import os
from mpi4py import MPI

dictionary = {}
for i in range(256):
    dictionary[i] = bytes([i])

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

def lzw_decompress(data):
    dictionary_size = 256
    dictionary = dict((i, bytes([i])) for i in range(dictionary_size))
    result = []
    buffer = bytes([data[0]])
    result.append(buffer)
    for code in data[1:]:
        if code in dictionary:
            entry = dictionary[code]
        elif code == dictionary_size:
            entry = buffer + bytes([buffer[0]])
        else:
            raise ValueError("Código inválido")
        result.append(entry)
        dictionary[dictionary_size] = buffer + bytes([entry[0]])
        dictionary_size += 1
        buffer = entry
    return b"".join(result)

def decompress_file(input_file_path, output_file_path):
    with open(input_file_path, "rb") as input_file:
        data = input_file.read()

    file_size = len(data) // 4
    part_size = file_size // size

    comm.barrier()

    if rank == 0:
        for i in range(size):
            start = i * part_size * 4
            end = start + part_size * 4
            if i == size - 1:
                end = len(data)
            part_data = data[start:end]
            comm.send(part_data, dest=i)
    else:
        part_data = None

    part_data = comm.scatter(None if rank == 0 else part_data, root=0)

    decompressed_text = lzw_decompress(struct.unpack(f">{len(part_data)//4}I", part_data))
    decompressed_data = struct.pack(f">{len(decompressed_text)}B", *decompressed_text)

    gathered_data = comm.gather(decompressed_data, root=0)

    if rank == 0:
        with open(output_file_path, "wb") as output_file:
            for data in gathered_data:
                output_file.write(data)

if __name__ == "__main__":
    if len(sys.argv) != 2:
            print("Debes especificar el nombre del archivo a comprimir")
            sys.exit()
    input_file_path = sys.argv[1] # Ruta del archivo de entrada
    output_file_path = "descomprimido-elmejorprofesor.txt"  # Ruta del archivo de salida

    start_time = time.time()

    
    start_time = MPI.Wtime()
    decompress_file(input_file_path, output_file_path)
    end_time = MPI.Wtime()
    if rank == 0:
     print(f"{end_time - start_time}")
