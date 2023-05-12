from mpi4py import MPI
import time

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
    
    with open(input_file_path, "rb") as input_file:
        compressed_text = []
        while True:
            byte = input_file.read(4)
            if not byte:
                break
            code = int.from_bytes(byte, byteorder="big")
            compressed_text.append(code)
            
    text = lzw_decompress(compressed_text)
    
    with open(output_file_path, "wb") as output_file:
        output_file.write(text.encode("iso-8859-1"))


def main():
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    if rank == 0:
        start_time = time.time()

    # Asume que tienes archivos comprimidos llamados "comprimido_0.elmejorprofesor", "comprimido_1.elmejorprofesor", etc.
    input_file_path = f"comprimido_{rank}.elmejorprofesor"
    output_file_path = f"descomprimido-elmejorprofesor_{rank}.txt"

    decompress_file(input_file_path, output_file_path)

    if rank == 0:
        end_time = time.time()
        print(f'El tiempo de ejecución fue: {end_time-start_time:.2f} segundos')

if __name__ == "__main__":
    main()

