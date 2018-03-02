# -*- coding: UTF-8 -*-
import sys
import struct
import socket
import csv

_unpack_S = lambda s: struct.unpack("12s", s)
_unpack_L = lambda l: struct.unpack("<L", l)
_unpack_Q = lambda q: struct.unpack("Q", q)
BASE_LENGTH = 124

with open(sys.argv[1]) as f:
    meta_data = f.read(16)
    offset_info = f.read()

offset_addr, = _unpack_Q(meta_data[:8])
offset_owner, = _unpack_Q(meta_data[8:])
record_max = int(offset_addr / BASE_LENGTH) - 1

print(offset_addr, offset_owner, record_max)


header = ['min IP', 'max IP', '大洲', '国家编码', '行政区划码', '国家', '省', '市', '区', 'BD09坐标系经度', 'BD09坐标系纬度', 'WGS09坐标系经度', 'WGS09坐标系纬度',
          '区域半径', '应用场景', '地理位置精度', 'IP 拥有者名']
out_file = open('{}.csv'.format(sys.argv[1]), mode='wb+')
csv_writer = csv.writer(out_file, quoting=csv.QUOTE_ALL)
csv_writer.writerow(header)

out_file_cn = open('{}-CN.csv'.format(sys.argv[1]), mode='wb+')
csv_writer_cn = csv.writer(out_file_cn, quoting=csv.QUOTE_ALL)
csv_writer_cn.writerow(header)

for i in range(record_max):
    minip, = _unpack_L(offset_info[i * BASE_LENGTH: i * BASE_LENGTH + 4])
    maxip, = _unpack_L(offset_info[i * BASE_LENGTH + 4: i * BASE_LENGTH + 8])
    addr_begin, = _unpack_Q(offset_info[i * BASE_LENGTH + 8: i * BASE_LENGTH + 16])
    addr_length, = _unpack_Q(offset_info[i * BASE_LENGTH + 16: i * BASE_LENGTH + 24])
    owner_begin, = _unpack_Q(offset_info[i * BASE_LENGTH + 24: i * BASE_LENGTH + 32])
    owner_length, = _unpack_Q(offset_info[i * BASE_LENGTH + 32: i * BASE_LENGTH + 40])
    bd_lon, = _unpack_S(offset_info[i * BASE_LENGTH + 40: i * BASE_LENGTH + 52])
    bd_lat, = _unpack_S(offset_info[i * BASE_LENGTH + 52: i * BASE_LENGTH + 64])
    wgs_lon, = _unpack_S(offset_info[i * BASE_LENGTH + 64: i * BASE_LENGTH + 76])
    wgs_lat, = _unpack_S(offset_info[i * BASE_LENGTH + 76: i * BASE_LENGTH + 88])
    radius, = _unpack_S(offset_info[i * BASE_LENGTH + 88: i * BASE_LENGTH + 100])
    scene, = _unpack_S(offset_info[i * BASE_LENGTH + 100: i * BASE_LENGTH + 112])
    accuracy, = _unpack_S(offset_info[i * BASE_LENGTH + 112: i * BASE_LENGTH + 124])
    addr = offset_info[addr_begin:addr_begin + addr_length].split("|")
    owner = offset_info[owner_begin:owner_begin + owner_length]

    ip_info = [socket.inet_ntoa(struct.pack('!I', minip)), socket.inet_ntoa(struct.pack('!I', maxip)), addr[0], addr[1], addr[2], addr[3], addr[4], addr[5], addr[6],
               bd_lon.replace('\x00', ''), bd_lat.replace('\x00', ''), wgs_lon.replace('\x00', ''), wgs_lat.replace('\x00', ''), radius.replace('\x00', ''),
               scene.replace('\x00', ''), accuracy.replace('\x00', ''), owner.replace('\x00', '')]
    csv_writer.writerow(ip_info)
    if ip_info[3] == 'CN':
        csv_writer_cn.writerow(ip_info)
