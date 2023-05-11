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
        input_file.seek(0, 2)  
        file_size = input_file.tell()
        block_size = file_size // size
        input_file.seek(rank * block_size) 
        if rank == size - 1:  
            block_size = file_size - (rank * block_size)
        data = input_file.read(block_size)

    compressed_text = lzw_compress(data)

 
    compressed_sizes = comm.gather(len(compressed_text), root=0)

    if rank == 0:
       
        total_size = sum(compressed_sizes)

       
        with open(output_file_path, "wb") as output_file:
            output_file.write(total_size.to_bytes(4, byteorder="big"))

    
    compressed_texts = comm.gather(compressed_text, root=0)

    if rank == 0:
      
        with open(output_file_path, "wb") as output_file:
            for text in compressed_texts:
                for code in text:
                    output_file.write(code.to_bytes(4, byteorder="big"))

if __name__ == "__main__":
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()

    if rank == 0:
        if len(sys.argv) != 2:
            print("Por favor especifica el nombre del archivo a comprimir")
            sys.exit()
        input_file_path = sys.argv[1]
        output_file_path = "comprimido.elmejorprofesor"
    else:
        input_file_path = None
        output_file_path = None

    
    input_file_path = comm.bcast(input_file_path, root=0)
    output_file_path = comm.bcast(output_file_path, root=0)

    start_time = time.time()
    compress_file(input_file_path, output_file_path, comm)
    end_time = time.time()

    if rank == 0:
        print(f"El tiempo de ejecución fue: {end_time - start_time:.2f} segundos")
