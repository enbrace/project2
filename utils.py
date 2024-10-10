import struct
import zlib


class Utils:
    @staticmethod
    def crc32(data: bytes) -> int:
        """计算给定数据的 CRC32 校验值"""
        return zlib.crc32(data) & 0xffffffff

    @staticmethod
    def create_frame(data: bytes, frame_type: int, seq_number: int) -> bytes:
        """创建数据帧"""
        # 假设帧结构为：帧头(1字节) + 帧类型(1字节) + 序列号(2字节) + 数据长度(2字节) + 数据 + CRC(4字节)
        frame_header = b'\x7E'  # 帧头
        length = len(data)
        length_bytes = struct.pack('>H', length)  # 大端字节序
        seq_bytes = struct.pack('>H', seq_number)

        crc = Utils.crc32(data)
        crc_bytes = struct.pack('>I', crc)

        return frame_header + bytes([frame_type]) + seq_bytes + length_bytes + data + crc_bytes

    @staticmethod
    def parse_frame(frame: bytes):
        """解析数据帧"""
        if frame[0] != 0x7E:
            raise ValueError("Invalid frame header.")

        frame_type = frame[1]
        seq_number = struct.unpack('>H', frame[2:4])[0]
        length = struct.unpack('>H', frame[4:6])[0]
        data = frame[6:6 + length]
        crc_received = struct.unpack('>I', frame[6 + length:10 + length])[0]

        # 验证 CRC
        crc_calculated = Utils.crc32(data)
        if crc_received != crc_calculated:
            raise ValueError("CRC check failed.")

        return {
            'frame_type': frame_type,
            'seq_number': seq_number,
            'data': data
        }


# 使用示例
if __name__ == "__main__":
    # 创建帧
    data = b'Hello, World!'
    frame = Utils.create_frame(data, frame_type=1, seq_number=1)
    print("Created Frame:", frame)

    # 解析帧
    parsed_frame = Utils.parse_frame(frame)
    print("Parsed Frame:", parsed_frame)
