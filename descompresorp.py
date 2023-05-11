import time
import sys
from mpi4py import MPI

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

def decompress_file(input_file_path, output_file_path, comm):
    rank = comm.Get_rank()
    size = comm.Get_size()

    with open(input_file_path, "rb") as input_file:
        input_file.seek(0, 2)  # Move to the end of the file
        file_size = input_file.tell()
        block_size = file_size // size
        input_file.seek(rank * block_size)  # Move to the start of the block
        if rank == size - 1:  # Last rank gets the remaining bytes
            block_size = file_size - (rank * block_size)
        data = input_file.read(block_size)

    compressed_text = []
    for i in range(len(data)//4):
        code_byte = data[i*4:(i+1)*4]
        if not code_byte:
            break
        code = int.from_bytes(code_byte, byteorder="big")
        compressed_text.append(code)

    # Decompress the block of data
    text = lzw_decompress(compressed_text)

    # Gather the results from all processes
    all_texts = comm.gather(text, root=0)

    if rank == 0:
        # Concatenate the results from all processes
        all_texts = "".join(all_texts)

        # Write the decompressed text to the output file
        with open(output_file_path, "wb") as output_file:
            output_file.write(all_texts.encode("iso-8859-1"))


if __name__ == "__main__":
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()

    start_time = time.time()
    decompress_file("comprimido.elmejorprofesor", "descomprimido-elmejorprofesor.txt", comm)
    end_time = time.time()

    if rank == 0:
        print(f"El tiempo de ejecución fue: {end_time - start_time:.2f} segundos")