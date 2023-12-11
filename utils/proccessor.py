import numpy as np


def preproccess_signal(original_data: np.ndarray) -> np.ndarray:
    return (np.round(original_data * 1000.0).flatten()).astype(np.int64)


def postproccess_signal(original_data: np.ndarray) -> np.ndarray:
    output_array = original_data / 1000.0
    output_array = output_array.reshape(-1, 1)
    return output_array


def string_to_bits(text: str) -> str:
    # Encode the text as bytes using UTF-8 encoding
    encoded_bytes = text.encode('utf-8')

    # Convert each byte to a binary string representation
    binary_strings = [format(byte, '08b') for byte in encoded_bytes]

    # Join the binary strings to get a single string of bits
    bit_string = ''.join(binary_strings)

    return bit_string


def bits_to_string(bit_string: str) -> str:
    # Split the bit string into 8-bit chunks
    bit_chunks = [bit_string[i:i+8] for i in range(0, len(bit_string), 8)]

    # Convert each 8-bit chunk to an integer
    bytes_list = [int(chunk, 2) for chunk in bit_chunks]

    # Convert the list of integers to bytes
    byte_array = bytearray(bytes_list)

    # Decode the bytes using UTF-8 encoding to get the original string
    string = byte_array.decode('utf-8')

    return string
