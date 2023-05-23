import time
from mpi4py import MPI
import sys

def lzw_decompress(compressed_text):
    dictionary = {}
    for i in range(256):
        dictionary[i] = bytes([i])

    result = bytearray()
    buffer = bytearray()
    for code in compressed_text:
        if code in dictionary:
            new_buffer = dictionary[code]
        elif code == len(dictionary):
            new_buffer = buffer + bytes([buffer[0]])
        else:
            raise ValueError("Invalid LZW code")

        result += new_buffer
        if buffer:
            dictionary[len(dictionary)] = buffer + bytes([new_buffer[0]])
        buffer = new_buffer

    return result.decode("iso-8859-1")


def decompress_file(input_file_path, output_file_path):


    if rank == 0:
        with open(input_file_path, "rb") as input_file:
            compressed_text = []
            while True:
                byte = input_file.read(4)
                if not byte:
                    break
                code = int.from_bytes(byte, byteorder="big")
                compressed_text.append(code)
    else:
        compressed_text = None

    compressed_text = comm.bcast(compressed_text, root=0)

    # Divide los códigos comprimidos entre los procesos
    chunk_size = len(compressed_text) // size
    start = rank * chunk_size
    end = start + chunk_size if rank < size - 1 else len(compressed_text)
    local_compressed_text = compressed_text[start:end]

    # Descomprime la parte de los códigos asignada al proceso actual
    local_text = lzw_decompress(local_compressed_text)

    # Junta los resultados de los procesos en un solo archivo de salida
    all_text = comm.gather(local_text, root=0)

    if rank == 0:
        text = "".join(all_text)

        with open(output_file_path, "wb") as output_file:
            output_file.write(text.encode("iso-8859-1"))


if __name__ == "__main__":
    if len(sys.argv) != 2:
            print("Debes especificar el nombre del archivo a comprimir")
            sys.exit()
    input_file_path = sys.argv[1]

    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()


    start_time = MPI.Wtime()
    decompress_file(input_file_path, "descomprimidop-elmejorprofesor.txt")
    end_time = MPI.Wtime()
    if rank == 0:
     print(f"{end_time - start_time}")