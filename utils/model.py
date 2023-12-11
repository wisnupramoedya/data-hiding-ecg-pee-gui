import pickle
from models.constant import Constant


def get_model(index: int = 0):
    with open(f'models/regressions/{Constant.model_paths[index]}', 'rb') as model_file:
        model = pickle.load(model_file)

    return model
