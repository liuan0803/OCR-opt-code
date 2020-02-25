# -*- coding: utf-8 -*-
# @Time    : 2020/1/8 20:57
# @Author  : liuan0803
# @Email   : liuan0803@126.com
# @File    : resnetCBAM.py
# @Software: PyCharm
import torch
import torch.nn as nn
import torch.utils.model_zoo as model_zoo


class ChannelAttention(nn.Module):
    def __init__(self, in_planes, ratio=16):##尤其注意这里的通道数，可能输入的通道数和输出的就对不上，之前就出在这个问题
        super(ChannelAttention, self).__init__()
        #特征图先经过最大池化和平均池化，转化为1*1*channels的tensor
        self.avg_pool = nn.AdaptiveAvgPool2d(1)
        self.max_pool = nn.AdaptiveMaxPool2d(1)
        #在经过尺寸为1的卷积核相当于全连接层，先降低维度再升高维度，进行特征融合，并未改变通道数
        #参数为，输入通道数，输出通道数，卷积核大小，步长
        self.fc1 = nn.Conv2d(in_planes, in_planes // 16, 1, bias=False)
        self.relu1 = nn.ReLU()
        self.fc2 = nn.Conv2d(in_planes // 16, in_planes, 1, bias=False)

        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        avg_out = self.fc2(self.relu1(self.fc1(self.avg_pool(x))))
        max_out = self.fc2(self.relu1(self.fc1(self.max_pool(x))))
        out = avg_out + max_out
        return self.sigmoid(out)

class SpatialAttention(nn.Module):
    def __init__(self, kernel_size=7):
        super(SpatialAttention, self).__init__()

        assert kernel_size in (3, 7), 'kernel size must be 3 or 7'
        padding = 3 if kernel_size == 7 else 1

        self.conv1 = nn.Conv2d(2, 1, kernel_size, padding=padding, bias=False)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        avg_out = torch.mean(x, dim=1, keepdim=True)
        max_out, _ = torch.max(x, dim=1, keepdim=True)#返回结果元素的值和对应位置的index信息
        x = torch.cat([avg_out, max_out], dim=1)
        x = self.conv1(x)
        return self.sigmoid(x)

class BasicBlock(nn.Module):
    extend = 1

    def __init__(self, in_channel, out_channel, stride=1, shortcut=None):
        super(BasicBlock, self).__init__()# 等价于nn.Module.__init__(self)
        # 输入输出格式input(N, C, H, W)
        # output(N, C, H, W) N是batch的大小，C是通道数量，H为输入高度，W为输入的宽度
        self.layer = nn.Sequential(
            nn.Conv2d(in_channel, out_channel, kernel_size=3, stride=stride, padding=1),
            nn.BatchNorm2d(out_channel),
            nn.ReLU(True),
            nn.Conv2d(out_channel, out_channel, kernel_size=3, stride=stride, padding=1),
            nn.BatchNorm2d(out_channel)
        )

        self.shrotcut = shortcut
        self.Relu = nn.ReLU(True)

    def forward(self, input):
        tmp = input
        out = self.layer(input)

        if self.shrotcut is not None:
            tmp = self.shrotcut(input)
        out = out + tmp
        out = self.Relu(out)

        return out

#----在这里加入了CBAM模块，注意因为resnet用的101所以这部分就相当于bottleneck
class HighBlock(nn.Module):
    extend = 4

    def __init__(self, in_channel, out_channel, stride=1, shortcut=None):
        super(HighBlock, self).__init__()

        self.layer = nn.Sequential(
            nn.Conv2d(in_channel, out_channel, kernel_size=1, padding=0, bias=False),
            nn.BatchNorm2d(out_channel),
            nn.Conv2d(out_channel, out_channel, kernel_size=3, stride=stride, padding=1, bias=False),
            nn.BatchNorm2d(out_channel),
            nn.Conv2d(out_channel, out_channel * 4, kernel_size=1, padding=0, bias=False),#改一下输出通道
            nn.BatchNorm2d(out_channel * 4),
            nn.ReLU(True)
        )

        self.ca = ChannelAttention(in_channel)#放入的in_channel
        self.sa = SpatialAttention()

        self.shortcut = shortcut
        self.Relu = nn.ReLU(True)

    def forward(self, input):
        tmp = input
        out = self.layer(input)
        out = self.ca(out) * out  # 先经过通道显著性模块
        out = self.sa(out) * out  # 再经过空间显著性模块

        if self.shortcut is not None:
            tmp = self.shortcut(input)
        out = out + tmp
        out = self.Relu(out)

        return out


class ResNet(nn.Module):
    def __init__(self, block, block_num):
        super(ResNet, self).__init__()
        self.in_channel = 64

        self.layer1 = nn.Sequential(
            nn.Conv2d(3, 64, kernel_size=7, stride=2, padding=3, bias=False),
            nn.BatchNorm2d(64),
            nn.ReLU(True),
            nn.MaxPool2d(kernel_size=3, stride=2, padding=1)
        )

        self.layer2 = self.build_block(block, 64, block_num[0])
        self.layer3 = self.build_block(block, 128, block_num[1], 2)
        self.layer4 = self.build_block(block, 256, block_num[2], 2)
        self.layer5 = self.build_block(block, 512, block_num[3], 2)

        self.size = [128 * block.extend, 256 * block.extend, 512 * block.extend]

    def forward(self, input):
        C1 = self.layer1(input)
        C2 = self.layer2(C1)
        C3 = self.layer3(C2)
        C4 = self.layer4(C3)
        C5 = self.layer5(C4)

        return [C3, C4, C5]

    def build_block(self, block, out_channel, block_num, stride=1):
        shortcut =  None
        if stride != 1 or self.in_channel != out_channel * block.extend:
            shortcut = nn.Sequential(
                nn.Conv2d(self.in_channel, out_channel * block.extend, kernel_size=1, stride=stride, bias=False),
                nn.BatchNorm2d(out_channel * block.extend)
            )
        layers = []

        layers.append(block(self.in_channel, out_channel, stride, shortcut))
        self.in_channel = out_channel * block.extend
        for i in range(block_num-1):
            layers.append(block(self.in_channel, out_channel))

        return nn.Sequential(*layers)

    def get_size(self):
        return self.size


model_urls = {
    'resnet18': 'https://download.pytorch.org/models/resnet18-5c106cde.pth',
    'resnet34': 'https://download.pytorch.org/models/resnet34-333f7ec4.pth',
    'resnet50': 'https://download.pytorch.org/models/resnet50-19c8e357.pth',
    'resnet101': 'https://download.pytorch.org/models/resnet101-5d3b4d8f.pth',
    'resnet152': 'https://download.pytorch.org/models/resnet152-b121ed2d.pth',
}


def resnet18(pretrained=False):
    model = ResNet(BasicBlock, [2, 2, 2, 2])
    if pretrained:
        model.load_state_dict(model_zoo.load_url(model_urls['resnet18'], model_dir='.'), strict=False)
    return model


def resnet34(pretrained=False):
    model = ResNet(BasicBlock, [3, 4, 6, 3])
    if pretrained:
        model.load_state_dict(model_zoo.load_url(model_urls['resnet34'], model_dir='.'), strict=False)
    return model


def resnet50(pretrained=False):
    model = ResNet(HighBlock, [3, 4, 6, 3])
    if pretrained:
        model.load_state_dict(model_zoo.load_url(model_urls['resnet50'], model_dir='.'), strict=False)
    return model

def resnet101(pretrained=False):
    model = ResNet(HighBlock, [3, 4, 23, 3])
    if pretrained:
        model.load_state_dict(model_zoo.load_url(model_urls['resnet101'], model_dir='.'), strict=False)
    return model


def resnet152(pretrained=False):
    model = ResNet(HighBlock, [3, 8, 36, 3])
    if pretrained:
        model.load_state_dict(model_zoo.load_url(model_urls['resnet152'], model_dir='.'), strict=False)
    return model


def SetUpNet(net_size, pretrained=False):
    if net_size == 18:
        return resnet18(pretrained)
    elif net_size == 34:
        return  resnet34(pretrained)
    elif net_size == 50:
        return resnet50(pretrained)
    elif net_size == 101:
        return resnet101(pretrained)
    elif net_size == 152:
        return resnet152(pretrained)
    else:
        print('Net size must be one of 18, 34, 50, 101, 152')
        return None
