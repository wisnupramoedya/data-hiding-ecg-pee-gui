import os


def split_file_path_without_extension(file_path):
    # Split the file path into root and extension
    root, ext = os.path.splitext(file_path)
    return root


def split_path_for_saving(file_path) -> (str, str):
    directory, filename = os.path.split(file_path)
    return directory, filename
