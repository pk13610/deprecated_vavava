#! /usr/bin/python
# -*- coding: utf-8 -*-

import ctypes as ct

def struct2stream(s):
    length  = ct.sizeof(s)
    p       = ct.cast(ct.pointer(s), ct.POINTER(ct.c_char * length))
    return p.contents.raw

def stream2struct(string, stype):
    if not issubclass(stype, ct.Structure):
        raise ValueError('The type of the struct is not a ctypes.Structure')
    length      = ct.sizeof(stype)
    stream      = (ct.c_char * length)()
    stream.raw  = string
    p           = ct.cast(stream, ct.POINTER(stype))
    return p.contents

class VersionStruct(ct.LittleEndianStructure):
    _pack_ = 1
    _fields_ =[('v1', ct.c_uint8),
               ('v2', ct.c_uint8),
               ('v3', ct.c_uint16)
    ]

class Version:
    STRING = 1
    STRUCT = 2
    def __init__(self, version, vtype=STRING):
        if vtype == Version.STRING:
            self.string = version
            v = version.split('.')
            if len(v) != 3:
                raise "invilid version"
            self.v1 = int(v[0])
            self.v2 = int(v[1])
            self.v3 = int(v[2])
            self.struct = VersionStruct(self.v1, self.v2, self.v3)
            self.stream = struct2stream(self.struct)
        elif vtype == Version.STRUCT:
            self.stream = version
            self.struct = stream2struct(version, VersionStruct)
            self.v1 = self.struct.v1
            self.v2 = self.struct.v2
            self.v3 = self.struct.v3
            self.string = '%d.%d.%d' % (self.v1, self.v2, self.v3)
        else:
            raise "Invilad param"


if __name__ == '__main__':
    v = Version(r'1.0.256')
    #v = Version(b'\x01\x02\x03\x00', Version.STRUCT)
    print v.v1
    print v.v2
    print v.v3
    print "%r"%v.stream
    print v.string


