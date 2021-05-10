from Models.Hypothesis.predict import HypothesisModel
from Models.Pattern.PatternModel import PatternModel
from Models.Pattern import Parameters, SaveLoad
from os.path import join, dirname, abspath

modules_location = join(dirname(abspath(__file__)), "Models", "SavedModels")
hypothesis_model_location = join(modules_location, "hypothesisModel.pt")
pattern_model_location = join(modules_location, "patternModel.pt")


def load_hypothesis_model():
    model = HypothesisModel(hypothesis_model_location)
    return model


def load_pattern_model():
    model = PatternModel().to(Parameters.DEVICE)
    SaveLoad.load_checkpoint(load_path=pattern_model_location, model=model)
    return model



