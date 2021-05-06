import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision.models import resnet18


class ProjectionNet(nn.Module):
    def __init__(self, pretrained=True, head_layers=[512,512,512,512,512,512,512,512,128]):
        super(ProjectionNet, self).__init__()
        #self.resnet18 = torch.hub.load('pytorch/vision:v0.9.0', 'resnet18', pretrained=pretrained)
        self.resnet18 = resnet18(pretrained=pretrained)

        # create MPL head as seen in the code in: https://github.com/uoguelph-mlrg/Cutout/blob/master/util/cutout.py
        # TODO: check if this is really the right architecture
        last_layer = 512
        sequential_layers = []
        for num_neurons in head_layers[:-1]:
            sequential_layers.append(nn.Linear(last_layer, num_neurons))
            #TODO: use Batchnormalization?
            sequential_layers.append(nn.ReLU(inplace=True))
            last_layer = num_neurons
        
        #the last layer without activation
        sequential_layers.append(nn.Linear(last_layer, head_layers[-1]))
        last_layer = head_layers[-1]

        head = nn.Sequential(
            *sequential_layers
          )
        self.resnet18.fc = head
        self.out = nn.Linear(last_layer, 2)
    
    def forward(self, x):
        embeds = self.resnet18(x)
        logits = self.out(embeds)
        return embeds, logits