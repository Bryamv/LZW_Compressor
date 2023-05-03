import time

def lzw_decompress(compressed_text):
    dictionary = {}
    for i in range(256):
        dictionary[i] = chr(i)
        
    result = ""
    buffer = ""
    for code in compressed_text:
        if code in dictionary:
            new_buffer = dictionary[code]
        elif code == len(dictionary):
            new_buffer = buffer + buffer[0]
        else:
            raise ValueError("Invalid LZW code")
        
        result += new_buffer
        if buffer:
            dictionary[len(dictionary)] = buffer + new_buffer[0]
        buffer = new_buffer
        
    return result


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
    
    with open(output_file_path, "w", encoding="iso-8859-1") as output_file:
        output_file.write(text)

    
    
start_time = time.time()
decompress_file("comprimido.elmejorprofesor", "descomprimido-elmejorprofesor.txt")
end_time = time.time()

print(f'El tiempo de ejecución fue: {end_time-start_time:.2f} segundos')