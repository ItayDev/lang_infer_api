from models.inference.predict import LangInferModelWrapper
from models.pattern.PatternModel import PatternModel
from models.pattern import Parameters, SaveLoad
from os.path import join, dirname, abspath

modules_location = join(dirname(abspath(__file__)), "models", "saved_models")
inference_model_location = join(modules_location, "inference_model.pt")
pattern_model_location = join(modules_location, "patternModel.pt")


def load_inference_model():
    model = LangInferModelWrapper(inference_model_location)
    return model


def load_pattern_model():
    model = PatternModel().to(Parameters.DEVICE)
    SaveLoad.load_checkpoint(load_path=pattern_model_location, model=model)
    return model
