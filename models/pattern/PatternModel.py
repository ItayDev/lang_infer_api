from transformers import BertForSequenceClassification
import torch
import torch.nn as nn
from models.pattern import Parameters


class PatternModel(nn.Module):

    def __init__(self):
        super(PatternModel, self).__init__()
        self.bert = BertForSequenceClassification.from_pretrained(Parameters.BERT_TOKENIZER_NAME)
        for param in self.bert.parameters():
            param.requires_grad = False
        self.bert.classifier = nn.Linear(in_features=768, out_features=512)
        self.bert.classifier.requires_grad = True
        self.fc = nn.Linear(in_features=512, out_features=2)
        self.fc.requires_grad = True

    def forward(self, text):
        cls_hs = self.bert(text)[0]
        x = torch.sigmoid(cls_hs)
        x = self.fc(x)
        x = torch.softmax(x, dim=1)
        return x
