import time
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


    
    
if __name__ == "__main__":
    

    if len(sys.argv) != 2:
            print("Debes especificar el nombre del archivo a comprimir")
            sys.exit()
    input_file_path = sys.argv[1]
    
    start_time = time.time()
    decompress_file(input_file_path, "descomprimido-elmejorprofesor.txt")
    end_time = time.time()

    print(f'El tiempo de ejecución fue: {end_time-start_time:.2f} segundos')
