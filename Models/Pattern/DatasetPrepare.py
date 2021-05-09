from torchtext.legacy.data import Field, TabularDataset, BucketIterator
from transformers import BertTokenizer
import torch
from transformers.tokenization_utils_base import PaddingStrategy

# Use BERT tokenizer (the method to use words the same way they are used in BERT model)
from Models.Pattern import Parameters

tokenizer = BertTokenizer.from_pretrained(Parameters.BERT_TOKENIZER_NAME)

# Define padding token and unknown word token
PAD_INDEX = tokenizer.convert_tokens_to_ids(tokenizer.pad_token)
UNK_INDEX = tokenizer.convert_tokens_to_ids(tokenizer.unk_token)

int_field = Field(sequential=False,
                  use_vocab=False,
                  batch_first=True,
                  dtype=torch.int)

long_field = Field(sequential=False,
                   use_vocab=False,
                   batch_first=True,
                   dtype=torch.long)

float_field = Field(sequential=False,
                    use_vocab=False,
                    batch_first=True,
                    dtype=torch.float)

text_field = Field(use_vocab=False,
                   tokenize=tokenizer.encode,
                   lower=False,
                   include_lengths=False,
                   batch_first=True,
                   fix_length=Parameters.MAX_SEQ_LEN,
                   pad_token=PAD_INDEX,
                   unk_token=UNK_INDEX)

# label is required to be long field by Net
fields = [('title', text_field), ('label', long_field)]
#
# test = TabularDataset(path=Parameters.SOURCE_4_FOLDER + "/" + "output.tsv",
#                       format=Parameters.DATASET_FORMAT,
#                       fields=fields,
#                       skip_header=True)
#
#
# train_iter = BucketIterator(test,
#                             batch_size=Parameters.BATCH_SIZE,
#                             device=Parameters.DEVICE,
#                             train=True,
#                             shuffle=True)


def create_iterators(data_file_location, split_to_train_and_test=True):

    if split_to_train_and_test:

        train, test = TabularDataset(path=data_file_location,
                                     format="TSV",
                                     fields=fields,
                                     skip_header=True).split()

        train_iter = BucketIterator(train,
                                    batch_size=Parameters.BATCH_SIZE,
                                    device=Parameters.DEVICE,
                                    train=True,
                                    shuffle=True)

        test_iter = BucketIterator(test,
                                   batch_size=Parameters.BATCH_SIZE,
                                   device=Parameters.DEVICE,
                                   train=True,
                                   shuffle=True,
                                   sort=False)
        answer = train_iter, test_iter
    else:
        dataset = TabularDataset(path=data_file_location,
                                 format="TSV",
                                 fields=fields,
                                 skip_header=True)
        answer = BucketIterator(dataset,
                                    batch_size=Parameters.BATCH_SIZE,
                                    device=Parameters.DEVICE,
                                    train=True,
                                    shuffle=True,
                                    sort=False)

    print("Finish dataset prepare")
    return answer


def encode_bert(human_text):
    encoding = tokenizer._batch_encode_plus(human_text,
                                     add_special_tokens=True,
                                     truncation=True,
                                     padding_strategy=PaddingStrategy.LONGEST,
                                     return_attention_mask=True,
                                     return_tensors="pt")
    return encoding.data["input_ids"]
