import torch
print(torch.version.cuda)
print(torch.cuda.get_device_properties(0).total_memory)