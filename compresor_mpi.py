import time
import sys
from mpi4py import MPI

def lzw_compress(data):
    dictionary = {}
    for i in range(256):
        dictionary[bytes([i])] = i

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


def compress_file(input_file_path, output_file_path, comm):
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

    compressed_text = lzw_compress(data)

    # Gather compressed text sizes from all processes
    compressed_sizes = comm.gather(len(compressed_text), root=0)

    if rank == 0:
        # Compute the total size of the compressed text
        total_size = sum(compressed_sizes)

        # Write the total size to the output file
        with open(output_file_path, "wb") as output_file:
            output_file.write(total_size.to_bytes(4, byteorder="big"))

    # Gather compressed text from all processes
    compressed_texts = comm.gather(compressed_text, root=0)

    if rank == 0:
        # Write the compressed text to the output file
        with open(output_file_path, "ab") as output_file:
            for text in compressed_texts:
                for code in text:
                    output_file.write(code.to_bytes(4, byteorder="big"))

if __name__ == "__main__":
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()

    if rank == 0:
        if len(sys.argv) != 2:
            print("Debes especificar el nombre del archivo a comprimir")
            sys.exit()
        input_file_path = sys.argv[1]
        output_file_path = "comprimido.elmejorprofesor"
    else:
        input_file_path = None
        output_file_path = None

    # Broadcast input and output file paths to all processes
    input_file_path = comm.bcast(input_file_path, root=0)
    output_file_path = comm.bcast(output_file_path, root=0)

    start_time = time.time()
    compress_file(input_file_path, output_file_path, comm)
    end_time = time.time()

    if rank == 0:
        print(f"El tiempo de ejecución fue: {end_time - start_time:.2f} segundos")
