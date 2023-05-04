import time
import sys


def lzw_compress(text):
    dictionary = {}
    for i in range(256):
        dictionary[chr(i)] = 

    result = []
    buffer = ""
    for char in text:
        new_buffer = buffer + char
        if new_buffer in dictionary:
            buffer = new_buffer
        else:
            result.append(dictionary[buffer])
            dictionary[new_buffer] = len(dictionary)
            buffer = char
    if buffer:
        result.append(dictionary[buffer])

    return result


def compress_file(input_file_path, output_file_path):
    with open(input_file_path, "r", encoding="iso-8859-1") as input_file:
        text = input_file.read()

    compressed_text = lzw_compress(text)

    with open(output_file_path, "wb") as output_file:
        for code in compressed_text:
            output_file.write(code.to_bytes(4, byteorder="big"))


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
