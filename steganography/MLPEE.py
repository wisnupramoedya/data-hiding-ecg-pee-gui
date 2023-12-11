import numpy as np
import warnings
from typing import Literal
import math

# Disable only the specific NumPy deprecation warning
warnings.filterwarnings("ignore", category=DeprecationWarning)


class MLPEEStego:
    """
    Add model
    """

    def __init__(self, model):
        self.model = model

    """
    Embed data for PEE
    """

    def embed(self, original_data: np.ndarray[np.any, np.int64], secret_data: str, threshold: int = 3):
        watermarked_data = original_data.copy()
        bit_index = 0
        errors = []

        # Check whether all secret data has been inserted
        full_loop = 0
        while bit_index < len(secret_data):
            for phase in range(1, 4):
                for i in self.get_phase_indexes(phase, len(watermarked_data)):
                    if i + 4 >= len(watermarked_data):
                        break
                    # Get error from predicted value and original value
                    original_value = watermarked_data[i+2]
                    predicted_value = int(self.model.predict(
                        [[watermarked_data[i], watermarked_data[i+1], watermarked_data[i+3], watermarked_data[i+4]]]))
                    error_embedding = original_value - predicted_value

                    errors.append(error_embedding)

                    expanded_error = 0
                    # check threshold
                    if abs(error_embedding) < threshold:
                        bit = 1 if bit_index < len(
                            secret_data) and secret_data[bit_index] == '1' else 0
                        bit_index += 1
                        expanded_error = 2*error_embedding + bit
                    else:
                        if error_embedding > 0:
                            expanded_error = error_embedding + threshold
                        else:
                            expanded_error = error_embedding - threshold + 1

                    watermarked_value = predicted_value + expanded_error
                    watermarked_data[i+2] = watermarked_value

                # print(watermarked_data[0: 10])

            print(f"{bit_index} from {len(secret_data)}")
            full_loop += 1
            if full_loop >= 8:
                print("Sorry the full_loop got out of range, break the system")
                break
        # print("Full loop", full_loop)

        # Inserting the full loop
        bit_reverse_full_loop_index = 0
        reversed_bit_full_loop = str(bin(full_loop)[2:])[::-1]
        print(reversed_bit_full_loop)
        for phase in range(1, 4):
            for i in self.get_phase_indexes(phase, len(watermarked_data)):
                if i + 4 >= len(watermarked_data):
                    break
                # Get error from predicted value and original value
                original_value = watermarked_data[i+2]
                predicted_value = int(self.model.predict(
                    [[watermarked_data[i], watermarked_data[i+1], watermarked_data[i+3], watermarked_data[i+4]]]))
                error_embedding = original_value - predicted_value

                errors.append(error_embedding)

                expanded_error = 0
                # check threshold
                if abs(error_embedding) < threshold:
                    bit = 1 if bit_reverse_full_loop_index < len(
                        reversed_bit_full_loop) and reversed_bit_full_loop[bit_reverse_full_loop_index] == '1' else 0
                    bit_reverse_full_loop_index += 1
                    expanded_error = 2*error_embedding + bit
                else:
                    if error_embedding > 0:
                        expanded_error = error_embedding + threshold
                    else:
                        expanded_error = error_embedding - threshold + 1

                watermarked_value = predicted_value + expanded_error
                watermarked_data[i+2] = watermarked_value

        return watermarked_data, full_loop if full_loop < 8 else -1

    def extract(self, watermarked_data: np.ndarray[np.any, np.int64], threshold: int = 3):
        original_data = watermarked_data.copy()

        # Get the full loop
        reversed_bit_full_loop = ''
        for phase in reversed(range(1, 4)):
            for i in reversed(self.get_phase_indexes(phase, len(original_data))):
                if i + 4 >= len(original_data):
                    continue

                # Get error from predicted value and watermarked value
                watermarked_value = original_data[i+2]
                predicted_value = int(self.model.predict(
                    [[original_data[i], original_data[i+1], original_data[i+3], original_data[i+4]]]))
                error_extraction = watermarked_value - predicted_value

                # Check threshold
                if error_extraction >= 2*threshold:
                    original_value = watermarked_value - threshold
                elif error_extraction <= -2*threshold + 1:
                    original_value = watermarked_value + threshold - 1
                else:
                    # Extract the watermark bit
                    bit = error_extraction - 2 * \
                        math.floor(error_extraction / 2)

                    # Get the original value and the bit
                    original_value = watermarked_value - \
                        math.floor(error_extraction / 2) - bit
                    reversed_bit_full_loop = reversed_bit_full_loop + (
                        '1' if bit else '0')

                # Repack the ECG and secret data
                original_data[i+2] = original_value

            print(reversed_bit_full_loop)
            # print(original_data[0: 10])
        print(reversed_bit_full_loop, reversed_bit_full_loop !=
              '', len(reversed_bit_full_loop) > 3)
        full_loop = int(reversed_bit_full_loop,
                        2) if reversed_bit_full_loop != '' and (len(reversed_bit_full_loop) > 3 and int(reversed_bit_full_loop[:-3], 2) == 0) else 8
        print("Reverse full loop", full_loop)

        # Get the secret data
        if full_loop == 8:
            original_data = watermarked_data.copy()
            full_loop = 7
        secret_data = ''
        while full_loop != 0:
            for phase in reversed(range(1, 4)):
                for i in reversed(self.get_phase_indexes(phase, len(original_data))):
                    if i + 4 >= len(original_data):
                        continue

                    # Get error from predicted value and watermarked value
                    watermarked_value = original_data[i+2]
                    predicted_value = int(self.model.predict(
                        [[original_data[i], original_data[i+1], original_data[i+3], original_data[i+4]]]))
                    error_extraction = watermarked_value - predicted_value

                    # Check threshold
                    if error_extraction >= 2*threshold:
                        original_value = watermarked_value - threshold
                    elif error_extraction <= -2*threshold + 1:
                        original_value = watermarked_value + threshold - 1
                    else:
                        # Extract the watermark bit
                        bit = error_extraction - 2 * \
                            math.floor(error_extraction / 2)

                        # Get the original value
                        original_value = watermarked_value - \
                            math.floor(error_extraction / 2) - bit
                        secret_data = ('1' if bit else '0') + secret_data

                    # Repack the ECG and secret data
                    original_data[i+2] = original_value

                # print(original_data[0: 10])

            full_loop -= 1

        return original_data, secret_data

    def get_phase_indexes(self, phase: Literal[1, 2, 3], max_len: int = 3_600):
        return range(phase - 1, max_len, 3)
