import torch
from torch import nn
from math import sqrt, ceil
from transformers import RobertaTokenizer, RobertaConfig, RobertaModel
from models.inference.implementation import LangInferModel
from transformers import AutoTokenizer, AutoModelForSequenceClassification

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
    predicted_class = torch.argmax(model_result, dim=0)
    model_result = nn.functional.softmax(model_result, dim=0)
    entailment_percentage = model_result[ENTAILMENT]
    contradiction_percentage = model_result[CONTRADICTION]

    if predicted_class == ENTAILMENT:
        return (2 / 3) + entailment_percentage * (1 / 3)
    elif predicted_class == CONTRADICTION:
        return (1 / 3) - (1 / 3) * contradiction_percentage
    else:
        return 0.5 + (1 / 3) * entailment_percentage - (1 / 3) * contradiction_percentage


class LangInferModelWrapper:
    def __init__(self, model_path, span_drop=0.6, max_spans=1000):
        self.tokenizer = RobertaTokenizer.from_pretrained("roberta-base")
        self.model = load_model(model_path)
        self.span_drop = span_drop
        self.max_spans = max_spans

    def predict(self, batch):
        encoded_data, start_indexes, end_indexes, span_masks = self.__encode_input(batch)
        # res = self.model(encoded_data, start_indexes, end_indexes, span_masks)
        res = self.model(encoded_data, start_indexes, end_indexes, span_masks)
        return list(map(lambda single_result: calculate_prediction(single_result).item(), res))

    def __encode_input(self, batch):
        encoded = list((map(lambda sample: self.__encode_sample(sample), batch)))
        return self.__collate(encoded)

    def __encode_sample(self, sample):
        sep_token = self.tokenizer.sep_token_id
        start_token = self.tokenizer.bos_token_id
        end_token = self.tokenizer.eos_token_id
        encoded_premise = self.tokenizer(sample["premise"], add_special_tokens=False)['input_ids']
        encoded_hypothesis = self.tokenizer(sample["hypothesis"], add_special_tokens=False)['input_ids']
        input_ids = torch.LongTensor([start_token] + encoded_premise + [sep_token] + encoded_hypothesis + [end_token])
        return {
            "input_ids": input_ids,
            "premise_len": len(encoded_premise),
            "hypothesis_len": len(encoded_hypothesis)
        }

    def __collate(self, batch):
        max_text_len = max([len(sample['input_ids']) for sample in batch])
        text_tensor = self.__padd_and_and_collect([sample['input_ids'] for sample in batch],
                                                  max_text_len,
                                                  self.tokenizer.pad_token_id)

        sentence_start_indexes = []
        sentence_end_indexes = []
        span_masks = []

        for sample in batch:
            premise_len = sample['premise_len']
            hypothesis_len = sample['hypothesis_len']

            start_indexes, end_indexes = self.__calculate_spans(premise_len, hypothesis_len)
            sentence_start_indexes.append(torch.LongTensor(start_indexes))
            sentence_end_indexes.append(torch.LongTensor(end_indexes))

        max_span_num = max([len(span) for span in sentence_start_indexes])

        if self.span_drop != 1:
            sentence_start_indexes = self.__padd_and_and_collect(sentence_start_indexes, max_span_num, max_text_len - 1)
            sentence_end_indexes, span_masks = self.__padd_and_and_collect(sentence_end_indexes, max_span_num,
                                                                           max_text_len - 1, True)
        else:
            sentence_start_indexes = torch.stack(sentence_start_indexes)
            sentence_end_indexes = torch.stack(sentence_end_indexes)

        return [
            text_tensor,
            sentence_start_indexes,
            sentence_end_indexes,
            span_masks,
        ]

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

    def __padd_and_and_collect(self, data, max_data_len, padding_token_id, with_masks=False):
        masks = torch.zeros([len(data), max_data_len])
        data_tensor = torch.full([len(data), max_data_len],
                                 fill_value=padding_token_id,
                                 dtype=data[0][0].dtype)
        for i, sample in enumerate(data):
            data_tensor[i][:len(sample)] = sample
            masks[i][len(sample):] = 1e6

        if with_masks:
            return data_tensor, masks
        else:
            return data_tensor
