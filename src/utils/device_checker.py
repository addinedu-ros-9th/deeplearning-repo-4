import torch
import platform

class DeviceChecker:
    def __init__(self):
        self.device = None

    def check_cuda_availability(self):
        if torch.cuda.is_available():
            print("CUDA is available")
            self.device = torch.device("cuda")
        else:
            print("CUDA is NOT available")
            self.device = torch.device("cpu")
        return self.device

    def check_mps_availability(self):
        if torch.backends.mps.is_available():
            print("MPS is available")
            self.device = torch.device("mps")
        else:
            print("MPS is NOT available")
            self.device = torch.device("cpu")
        return self.device

    def determine_device(self):
        if platform.system() == "Darwin":
            print("Your system is macOS")
            self.device = self.check_mps_availability()
        else:
            print("Your system is", platform.system())
            self.device = self.check_cuda_availability()
        print("Using device:", self.device)
        return self.device
