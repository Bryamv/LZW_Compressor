import time
from mpi4py import MPI


def lzw_decompress_chunk(chunk):
    dictionary = {}
    for i in range(256):
        dictionary[i] = bytes([i])

    result = bytearray()
    buffer = bytearray()
    for code in chunk:
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

    return result


def decompress_file(input_file_path, output_file_path):
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    if rank == 0:
        with open(input_file_path, "rb") as input_file:
            compressed_text = []
            while True:
                byte = input_file.read(4)
                if not byte:
                    break
                code = int.from_bytes(byte, byteorder="big")
                compressed_text.append(code)

        chunk_size = (len(compressed_text) + size - 1) // size
        chunks = [compressed_text[i:i+chunk_size] for i in range(0, len(compressed_text), chunk_size)]
    else:
        chunks = None

    chunk = comm.scatter(chunks, root=0)
    chunk_result = lzw_decompress_chunk(chunk)
    chunk_results = comm.gather(chunk_result, root=0)

    if rank == 0:
        text = b"".join(chunk_results).decode("iso-8859-1")

        with open(output_file_path, "wb") as output_file:
            output_file.write(text.encode("iso-8859-1"))


start_time = time.time()
decompress_file("comprimido.elmejorprofesor", "descomprimido-elmejorprofesor.txt")
end_time = time.time()

print(f"El tiempo de ejecución fue: {end_time - start_time:.2f} segundos")
