import torch
import Models.Pattern.Parameters
from Models.Pattern import Parameters


# Save and Load Functions


def load_checkpoint(load_path, model):
    if load_path is None:
        return

    state_dict = torch.load(load_path, map_location=Parameters.DEVICE)
    print(f'Model loaded from <== {load_path}')

    model.load_state_dict(state_dict['model_state_dict'])
    return state_dict['test_loss']
