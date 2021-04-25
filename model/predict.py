import torch
from torch import nn
from math import sqrt, ceil
from transformers import RobertaTokenizer, RobertaConfig, RobertaModel
from model.implementation import LangInferModel

ENTAILMENT = 0
NEUTRAL = 1
CONTRADICTION = 2

def load_model(model_path):
    config = RobertaConfig.from_pretrained("roberta-base")
    base_model = RobertaModel(config)
    model = LangInferModel(base_model, config, 6)

    checkpoint = torch.load(model_path, map_location=torch.device('cpu'))
    model.load_state_dict(checkpoint['model_state_dict'])
    model.eval()
    return model


def calculate_prediction(model_result):
    unbatched = model_result.squeeze(0)
    predicted_class = torch.argmax(unbatched, dim=0)
    unbatched = nn.functional.softmax(unbatched, dim=0)
    entailment_percentage = unbatched[0]
    contradiction_percentage = unbatched[0]

    if predicted_class == ENTAILMENT:
        return (2/3) + entailment_percentage * (1/3)
    elif predicted_class == CONTRADICTION:
        return (1/3) - (1/3) * contradiction_percentage
    else:
        return 0.5 + (1/3) * entailment_percentage - (1/3) * contradiction_percentage


class Model:
    def __init__(self, model_path, span_drop=0.85, max_spans=1000):
        self.tokenizer = RobertaTokenizer.from_pretrained("roberta-base")
        self.model = load_model(model_path)
        self.span_drop = span_drop
        self.max_spans = max_spans

    def predict(self, premise, hypothesis):
        encoded_data, start_indexes, end_indexes = self.__encode_input(premise, hypothesis)
        # unsqueeze - the model expects a batch, we pass only a single record, so it needs to be converted to a batch
        # of size of 1
        res = self.model(encoded_data.unsqueeze(0), start_indexes.unsqueeze(0), end_indexes.unsqueeze(0))
        return calculate_prediction(res).item()

    def __encode_input(self, premise, hypothesis):
        sep_token = self.tokenizer.sep_token_id
        start_token = self.tokenizer.bos_token_id
        end_token = self.tokenizer.eos_token_id
        encoded_premise = self.tokenizer(premise, add_special_tokens=False)['input_ids']
        encoded_hypothesis = self.tokenizer(hypothesis, add_special_tokens=False)['input_ids']
        encoded_data = [start_token] + encoded_premise + [sep_token] + encoded_hypothesis + [end_token]
        start_indexes, end_indexes = self.__calculate_spans(len(encoded_premise), len(encoded_hypothesis))
        return torch.LongTensor(encoded_data), torch.LongTensor(start_indexes), torch.LongTensor(end_indexes)

    def __calculate_spans(self, premise_len, hypothesis_len):
        if 0 > self.span_drop or self.span_drop > 1:
            raise ValueError("span_drop valid range is [0,1)")
        elif self.span_drop == 1:
            return [], []
        start_indexes = []
        end_indexes = []
        hypothesis_start_index = 1 + premise_len + 1
        hypothesis_end_index = hypothesis_start_index + hypothesis_len
        premise_step = self.__calculate_step(premise_len)
        hypothesis_step = self.__calculate_step(hypothesis_len)

        for i in range(1, premise_len + 1, premise_step):
            for j in range(i, premise_len + 1, premise_step):
                start_indexes.append(i)
                end_indexes.append(j)

        for i in range(hypothesis_start_index, hypothesis_end_index, hypothesis_step):
            for j in range(i, hypothesis_end_index, hypothesis_step):
                start_indexes.append(i)
                end_indexes.append(j)

        return start_indexes, end_indexes

    def __calculate_step(self, range_len):
        if self.span_drop == 0:
            return 1

        # Arithmetic progression sum
        number_of_spans = (range_len + 1) * (range_len - 1) / 2
        wanted_number_of_spans = min(ceil(number_of_spans * (1 - self.span_drop)), self.max_spans)

        if wanted_number_of_spans == 0:
            return ceil(range_len)
        else:
            return ceil(range_len / sqrt(wanted_number_of_spans))
