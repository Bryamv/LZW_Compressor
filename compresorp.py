from mpi4py import MPI
import time
import sys


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


def compress_file(input_file_path, output_file_path):
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    if rank == 0:
        with open(input_file_path, "rb") as input_file:
            text = input_file.read()
        block_size = len(text) // size
        remainder = len(text) % size
        block_sizes = [block_size] * size
        block_sizes[-1] += remainder
    else:
        text = None
        block_size = None
        block_sizes = None

    block_size = comm.bcast(block_size, root=0)
    block_sizes = comm.scatter(block_sizes, root=0)
    block_start = rank * block_size
    block_end = block_start + block_sizes

    block_data = text[block_start:block_end] if text is not None else b""
    compressed_text = lzw_compress(block_data)

    compressed_data = bytearray(compressed_text)
    compressed_size = len(compressed_data)
    compressed_sizes = comm.gather(compressed_size, root=0)

    if rank == 0:
        total_compressed_size = sum(compressed_sizes)
        compressed_text = bytearray(total_compressed_size)
        offsets = [0] + compressed_sizes[:-1]
        offsets = [sum(offsets[:i+1]) for i in range(len(offsets))]
    else:
        offsets = None

    comm.Gatherv(sendbuf=compressed_data, recvbuf=(compressed_text, compressed_sizes, offsets), root=0)

    if rank == 0:
        with open(output_file_path, "wb") as output_file:
            output_file.write(compressed_text)


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
