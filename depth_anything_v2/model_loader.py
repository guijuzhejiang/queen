import cv2
import torch
import sys
import os
dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.abspath(os.path.join(dir_path, os.pardir)))

from midas.dpt_depth import DPTDepthModel
from midas.transforms import Resize, NormalizeImage, PrepareForNet

from torchvision.transforms import Compose


def load_model(device, model_path, optimize=True, height=None):
    """Load the specified network.

    Args:
        device (device): the torch device used
        model_path (str): path to saved model
        optimize (bool): optimize the model to half-integer on CUDA?
        height (int): inference encoder image height

    Returns:
        The loaded network, the transform which prepares images as input to the network and the dimensions of the
        network input
    """
    model = DPTDepthModel(
        path=model_path,
        backbone="beitl16_512",
        non_negative=True,
    )
    net_w, net_h = 512, 512
    resize_mode = "minimal"
    normalization = NormalizeImage(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])

    if height is not None:
        net_w, net_h = height, height

    transform = Compose(
        [
            Resize(
                net_w,
                net_h,
                resize_target=None,
                keep_aspect_ratio=True,
                ensure_multiple_of=32,
                resize_method=resize_mode,
                image_interpolation_method=cv2.INTER_CUBIC,
            ),
            normalization,
            PrepareForNet(),
        ]
    )

    model.eval()

    if optimize and (device == torch.device("cuda")):
        model = model.to(memory_format=torch.channels_last)
        model = model.half()

    model.to(device)

    return model, transform, net_w, net_h
