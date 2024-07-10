download all requirements using 
    pip3 install -r requirements.txt
and
    sudo apt install python3-pyaudio
setup CUDA drivers and CuDNN
    https://developer.nvidia.com/cuda-downloads

    https://developer.nvidia.com/cudnn
    
download absent files from the standalone faster-whisper
    https://github.com/Purfview/whisper-standalone-win/releases
set path:
    # Add system library paths first
    export LD_LIBRARY_PATH=/lib:/usr/lib:/usr/local/lib:${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}

    # Add CUDA bin and library paths
    export PATH=/usr/local/cuda-12.5/bin${PATH:+:${PATH}}
    export LD_LIBRARY_PATH=/usr/local/cuda-12.5/lib64${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}

    # Optional: Add the NVCC compiler path
    export CUDA_HOME=/usr/local/cuda-12.5

    # Add cuDNN library paths
    export CUDNN_PATH=/usr/local/cuda-12.5/lib64
    export LD_LIBRARY_PATH=$CUDNN_PATH:$LD_LIBRARY_PATH
install absent cublass/cudnn files from https://github.com/Purfview/whisper-standalone-win/releases and unzip:
    cd ~/Downloads/Whisper-Faster-XXL/_xxl_data
    sudo cp libcudnn_ops_infer.so.8 /usr/local/cuda-12.5/lib64
    sudo cp libcudnn_cnn_infer.so.8 /usr/local/cuda-12.5/lib64/
    sudo cp libcublasLt.so.11 /usr/local/cuda-12.5/lib64/
    sudo cp libcublas.so.11 /usr/local/cuda-12.5/lib64/
