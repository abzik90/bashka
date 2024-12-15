# This is a local voice assistant project implemented using Faster-Whisper, LLaMa 3.1, and xTTSv2
Here's the simplified flow of the app:

User speaks to the app -> \
Speech detection function writes the speech into .wav file ->  \
.wav file is fed into LM Studio's endpoint -> \
Text result is fed into xTTSv2 along with the original .wav file -> \
xTTS reads the LLaMa's response with the user's voice. \
 \
Note: Speech detection dynamically changes the threshold to consider ambient noise. \
 \
## To replicate this project you might first want to
## Download all requirements using 
    pip3 install -r requirements.txt
## and
    sudo apt install python3-pyaudio
## Setup CUDA drivers and CuDNN
    https://developer.nvidia.com/cuda-downloads
    https://developer.nvidia.com/cudnn
    
## Download absent files from the standalone faster-whisper
  https://github.com/Purfview/whisper-standalone-win/releases
## Set path:
    ## Add system library paths first
    ```
    export LD_LIBRARY_PATH=/lib:/usr/lib:/usr/local/lib:${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}
    ```
    ### Add CUDA bin and library paths
    export PATH=/usr/local/cuda-12.5/bin${PATH:+:${PATH}}
    export LD_LIBRARY_PATH=/usr/local/cuda-12.5/lib64${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}
    ```

    ### Optional: Add the NVCC compiler path
    ```
    export CUDA_HOME=/usr/local/cuda-12.5
    ```
    ### Add cuDNN library paths
    ```
    export CUDNN_PATH=/usr/local/cuda-12.5/lib64
    export LD_LIBRARY_PATH=$CUDNN_PATH:$LD_LIBRARY_PATH
    ```
### Install absent cublass/cudnn files from https://github.com/Purfview/whisper-standalone-win/releases and unzip:
    ```cd ~/Downloads/Whisper-Faster-XXL/_xxl_data
    sudo cp libcudnn_ops_infer.so.8 /usr/local/cuda-12.5/lib64
    sudo cp libcudnn_cnn_infer.so.8 /usr/local/cuda-12.5/lib64/
    sudo cp libcublasLt.so.11 /usr/local/cuda-12.5/lib64/
    sudo cp libcublas.so.11 /usr/local/cuda-12.5/lib64/
    sudo cp libcudnn.so.8 /usr/local/cuda-12.5/lib64/

## Run main.py
    sudo cp libcufft.so.10 /usr/local/cuda-12.5/lib64/
    sudo cp libcudart.so.11.0 /usr/local/cuda-12.5/lib64/
    ```
