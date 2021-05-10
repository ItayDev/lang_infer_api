from transformers import BertTokenizer
from transformers.tokenization_utils_base import PaddingStrategy

# Use BERT tokenizer (the method to use words the same way they are used in BERT model)
from Models.Pattern import Parameters

tokenizer = BertTokenizer.from_pretrained(Parameters.BERT_TOKENIZER_NAME)


def encode_bert(human_text):
    encoding = tokenizer._batch_encode_plus(human_text,
                                     add_special_tokens=True,
                                     padding_strategy=PaddingStrategy.LONGEST,
                                     return_attention_mask=True,
                                     return_tensors="pt")
    return encoding.data["input_ids"]
