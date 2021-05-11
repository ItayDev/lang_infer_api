import torch

# data parameters:
MODEL_FILE_NAME = "model.pt"

# Model Parameters:
BERT_TOKENIZER_NAME = "bert-base-uncased"
BATCH_SIZE = 64 if torch.cuda.is_available() else 4
LR = 1e-3
TRUE_LABEL_INDEX = 1

# Read only first 128 tokens
MAX_SEQ_LEN = 128

# Running environment Parameters
DEVICE = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
print(f'Running over {DEVICE}')
