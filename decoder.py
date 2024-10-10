import os
import sys
import cv2
import struct
import numpy as np

from project2.encode.encoder import calculate_crc


def decode_frame(frame):
    """解析帧数据"""
    # 将帧转换为字节流
    frame_bytes = frame.tobytes()

    if frame_bytes[0] != 0xCA or frame_bytes[-1] != 0xCA:
        return None, False  # 定界符不匹配

    address_dest = frame_bytes[1]
    address_src = frame_bytes[2]
    length = struct.unpack('>H', frame_bytes[3:5])[0]
    payload = frame_bytes[5:-2]  # 去掉 CRC

    # 校验 CRC
    if calculate_crc(frame_bytes[:-1]) != frame_bytes[-1]:
        return None, False  # CRC 校验失败

    return payload, True


def decode(video_file, output_dir):
    """解码器主函数"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)  # 创建输出目录

    cap = cv2.VideoCapture(video_file)
    if not cap.isOpened():
        print("无法打开视频文件。")
    frame_count = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("未能读取帧，可能是视频结束。")
            break

        print(f"处理帧: {frame_count}")  # 打印当前处理的帧数
        decoded_frame = decode_frame(frame)

        if decoded_frame[1]:  # 如果有效
            payload = decoded_frame[0]
            bin_filename = os.path.join(output_dir, f"{frame_count}.bin")
            val_filename = os.path.join(output_dir, f"{frame_count}.val")

            with open(bin_filename, 'wb') as bin_file:
                bin_file.write(payload)
            print(f"成功写入: {bin_filename}")

            with open(val_filename, 'wb') as val_file:
                val_file.write(b'\x01')  # 标记有效
            print(f"成功写入: {val_filename}")
        else:
            print(f"帧 {frame_count} 解码失败。")  # 输出解码失败的信息

        frame_count += 1

    cap.release()
    print(f"解码完成，总共处理了 {frame_count} 帧。")


if __name__ == "__main__":
    # 定义输入文件和输出目录
    input_file = r"C:\Users\Administrator\PycharmProjects\pythonProject\project2\decode\input.mp4"
    output_dir = r"C:\Users\Administrator\PycharmProjects\pythonProject\project2\decode\output_bin"

    # 调用解码函数
    decode(input_file, output_dir)
