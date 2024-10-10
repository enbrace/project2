import os
import sys
import cv2
import numpy as np
import struct

def calculate_crc(data):
    """计算CRC校验"""
    return sum(data) % 256

def frame_data(address_dest, address_src, payload):
    """构建帧数据"""
    START_DELIMITER = 0xCA
    end_delimiter = 0xCA
    length = len(payload)

    # 处理数据以避免定界符冲突
    payload = bytearray(payload)
    payload = payload.replace(b'\xCA', b'\xCC\xCA')
    payload = payload.replace(b'\xCC', b'\xCC\xCC')

    # 构造帧
    frame = bytearray()
    frame.append(START_DELIMITER)
    frame.append(address_dest)
    frame.append(address_src)
    frame.extend(struct.pack('>H', length))  # 2 bytes for length
    frame.extend(payload)
    frame.extend(struct.pack('>B', calculate_crc(frame)))  # CRC 1 byte
    frame.append(end_delimiter)

    return frame

def encode(directory, mtu, output_file, duration):
    """编码器主函数"""
    frames = []
    for filename in os.listdir(directory):
        if filename.endswith('.bin'):
            with open(os.path.join(directory, filename), 'rb') as f:
                data = f.read()
                address_dest = 0x01  # 示例地址
                address_src = 0x02   # 示例地址
                payload = data[:mtu-6]  # 减去其他字段的大小
                frame = frame_data(address_dest, address_src, payload)
                frames.append(frame)

    # 将帧写入视频文件
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_file, fourcc, 30, (640, 480))

    for frame in frames:
        img = np.zeros((480, 640, 3), dtype=np.uint8)  # 创建空图像
        out.write(img)  # 写入空图像作为占位
        # 实际编码过程可以将 frame 数据转化为视频流

    out.release()

if __name__ == "__main__":
    encode('bin_files', 1500, 'output/output_video.mp4', 500)

