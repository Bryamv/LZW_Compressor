import time
import sys
from mpi4py import MPI
import os
import math


def lzw_compress(data, max_dict_size=2**16):
    dictionary = {}
    for i in range(256):
        dictionary[bytes([i])] = i.to_bytes(4, byteorder='big')
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
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    file_size = os.path.getsize(input_file_path)
    part_size = math.ceil(file_size / size)

    file_parts = []
    with open(input_file_path, 'rb') as file:
        for i in range(size):
            data = file.read(part_size)
            file_parts.append(data)

    data = comm.scatter(file_parts, root=0)

    if rank == 0:
        compressed_text, dictionary = lzw_compress(data)
        compressed_data = bytearray()
        for code in compressed_text:
            compressed_data.extend(code.to_bytes(4, byteorder="big"))

        for i in range(1, size):
            comm.send(dictionary, dest=i)

        final_data = compressed_data

        for i in range(1, size):
            received_data = comm.recv(source=i)
            final_data.extend(received_data)

        with open(output_file_path, "wb") as output_file:
            output_file.write(final_data)

    else:
        dictionary = comm.bcast(None, root=0)
        compressed_text, _ = lzw_compress(data, max_dict_size=len(dictionary))

        compressed_data = bytearray()
        for code in compressed_text:
            compressed_data.extend(code.to_bytes(4, byteorder="big"))

        comm.send(compressed_data, dest=0)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Debes especificar el nombre del archivo a comprimir y el nombre del archivo de salida")
        sys.exit()
    input_file_path = sys.argv[1]
    output_file_path = sys.argv[2]

    start_time = time.time()
    compress_file(input_file_path, output_file_path)
    end_time = time.time()

    print(f"El tiempo de ejecución fue: {end_time - start_time:.2f} segundos")
