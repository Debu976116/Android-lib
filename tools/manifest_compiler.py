#!/usr/bin/env python

'''
This program will take truseted application's manifest config JSON file as
input. Processes the JSON config file and creates packed data
mapping to C structures and dumps in binary format.

USAGE:
    manifest_compiler.py --input <input_filename> --output <output_filename>

    Arguments:
    input_filename  - Trusted app manifest config file in JSON format.
    output_filename - Binary file containing packed manifest config data mapped
                      to C structres.

    example:
        manifest_compiler.py --input manifest.json --output output.bin

   Input sample JSON Manifest config file content -
   {
        "uuid": "5f902ace-5e5c-4cd8-ae54-87b88c22ddaf",
        "min_heap": 4096,
        "min_stack": 4096,
        "mem_map":[
            {
                "id": 1,
                "addr": "0x70000000",
                "size": "0x1000"
            },
            {
                "id": 2,
                "addr": "0x70010000",
                "size": "0x100"
            },
            {
                "id": 3,
                "addr": "0x70020000",
                "size": "0x4"
            }
        ]
   }
'''

import argparse
import cStringIO
import json
import optparse
import os.path
import struct
import sys


# Manifest properties
UUID = "uuid"
MIN_HEAP = "min_heap"
MIN_STACK = "min_stack"
MEM_MAP = "mem_map"
MEM_MAP_ID = "id"
MEM_MAP_ADDR = "addr"
MEM_MAP_SIZE = "size"

# CONFIG TAGS
# These values need to be kept in sync with uapi/trusty_app_manifest_types.h
TRUSTY_APP_CONFIG_KEY_MIN_STACK_SIZE = 1
TRUSTY_APP_CONFIG_KEY_MIN_HEAP_SIZE = 2
TRUSTY_APP_CONFIG_KEY_MAP_MEM = 3


class MemIOMap(object):
    def __init__(self, id_, addr, size):
        self.id = id_
        self.addr = addr
        self.size = size


'''
Holds Manifest data to be used for packing
'''
class Manifest(object):
    def __init__(
            self,
            uuid,
            min_heap,
            min_stack,
            mem_io_maps
    ):
        self.uuid = uuid
        self.min_heap = min_heap
        self.min_stack = min_stack
        self.mem_io_maps = mem_io_maps


'''
Tracks errors during manifest compilation
'''
class Log(object):
    def __init__(self):
        self.error_count = 0

    def error(self, msg):
        sys.stderr.write("Error: {}\n".format(msg))
        self.error_count += 1

    def error_occurred(self):
        return self.error_count > 0


'''
Determines whether the value for the given key in dictionary is of type string
and if it is a string then returns the value.
'''
def get_string(manifest_dict, key, log):
    if key not in manifest_dict:
        log.error(
                "Manifest is missing required attribute - {} "
                .format(key))
        return None

    return coerce_to_string(manifest_dict.pop(key), key, log)


def coerce_to_string(value, key, log):
    if not isinstance(value, str) and \
            not isinstance(value, unicode):
        log.error(
                "Invalid value for" +
                " {} - \"{}\", Valid string value is expected"
                .format(key, value))
        return None

    return value


'''
Determines whether the value for the given key in dictionary is of type integer
and if it is int then returns the value
'''
def get_int(manifest_dict, key, log):
    if key not in manifest_dict:
        log.error("Manifest is missing required attribute - {}".format(key))
        return None

    return coerce_to_int(manifest_dict.pop(key), key,log)


def coerce_to_int(value, key, log):
    if isinstance(value, int):
        return value
    elif isinstance(value, basestring):
        try:
            return int(value, 0)
        except ValueError as ex:
            log.error("Invalid value for" +
                      " {} - \"{}\", valid integer or hex string is expected"
                      .format(key, value))
            return None
    else:
        log.error("Invalid value for" +
                  " {} - \"{}\", valid integer value is expected"
                  .format(key, value))
        return None


'''
Determines whether the value for the given key in dictionary is of type List
and if it is List then returns the value
'''
def get_list(manifest_dict, key, log):
    if key not in manifest_dict:
        log.error("Manifest is missing required attribute - {}".format(key))
        return None
    return coerce_to_list(manifest_dict.pop(key), key, log)


def coerce_to_list(value, key, log):
    if not isinstance(value, list):
        log.error("Invalid value for" +
                  " {} - \"{}\", valid list is expected"
                  .format(key, value))
        return None

    return value


'''
Determines whether the value for the given
key in dictionary is of type Dictionary
and if it is Dictionary then returns the value
'''
def get_dict(manifest_dict, key, log):
    if key not in manifest_dict:
        log.error("Manifest is missing required attribute - {}".format(key))
        return None
    return coerce_to_dict(manifest_dict.pop(key), key, log)


def coerce_to_dict(value, key, log):
    if not isinstance(value, dict):
        log.error("Invalid value for" +
                  " {} - \"{}\", valid dict is expected"
                  .format(key, value))
        return None

    return value


'''
Validate and arrange UUID byte order
If its valid UUID then returns 16 byte UUID
'''
def parse_uuid(uuid, log):
    if uuid is None:
        return None

    # Example UUID: "5f902ace-5e5c-4cd8-ae54-87b88c22ddaf"
    if len(uuid) != 36:
        log.error(
                "Invalid UUID " +
                "{}, uuid should be of length 16 bytes of hex values"
                .format(uuid))
        return None

    uuid_data = uuid.split("-")
    if len(uuid_data) != 5:
        log.error(
                "Invalid UUID {}".format(uuid) +
                "uuid should be of length 16 bytes of hex divided into 5 groups"
                )
        return None

    try:
        uuid_data = [part.decode("hex") for part in uuid_data]
    except TypeError as ex:
        log.error("Invalid UUID {}, {}".format(uuid, ex))
        return None

    if len(uuid_data[0]) != 4 or \
            len(uuid_data[1]) != 2 or \
            len(uuid_data[2]) != 2 or \
            len(uuid_data[3]) != 2 or \
            len(uuid_data[4]) != 6:
        log.error("Wrong grouping of UUID - {}".format(uuid))
        return None

    return "".join(uuid_data)


'''
Validate memory size value.
if success return memory size value else return None
'''
def parse_memory_size(memory_size, log):
    if memory_size is None:
        return None

    if memory_size <= 0 or memory_size % 4096 != 0:
        log.error(
                "{}: {}, Minimum memory size should be "
                .format(MIN_STACK, memory_size) +
                "non-negative multiple of 4096")
        return None

    return memory_size


def parse_mem_map(mem_maps, key, log):
    if mem_maps is None:
        return None

    mem_io_maps = []
    for mem_map_entry in mem_maps:
        mem_map_entry = coerce_to_dict(mem_map_entry, key, log)
        if mem_map_entry is None:
            continue
        mem_map = MemIOMap(
                get_int(mem_map_entry, MEM_MAP_ID, log),
                get_int(mem_map_entry, MEM_MAP_ADDR, log),
                get_int(mem_map_entry, MEM_MAP_SIZE, log))
        if mem_map_entry:
            log.error("Unknown atributes in mem_map entries in manifest: {} "
                      .format(mem_map_entry))
        mem_io_maps.append(mem_map)

    return mem_io_maps


'''
validate the manifest config and extract key, values
'''
def parse_manifest_config(manifest_dict, log):
    # UUID
    uuid = parse_uuid(get_string(manifest_dict, UUID, log), log)

    # MIN_HEAP
    min_heap = parse_memory_size(get_int(manifest_dict, MIN_HEAP, log), log)

    # MIN_STACK
    min_stack = parse_memory_size(get_int(manifest_dict, MIN_STACK, log), log)

    # MEM_MAP
    mem_io_maps = []
    if MEM_MAP in manifest_dict:
        mem_io_maps = parse_mem_map(
                get_list(manifest_dict, MEM_MAP, log),
                MEM_MAP,
                log)

    # look for any extra attributes
    if manifest_dict:
        log.error("Unknown atributes in manifest: {} ".format(manifest_dict))

    if log.error_occurred():
        return None

    return Manifest(uuid, min_heap, min_stack, mem_io_maps)


'''
This script represents UUIDs in a purely big endian order.
Trusty stores the first three components of the UUID in little endian order.
Rearrange the byte order accordingly by doing inverse
on first three components of UUID
'''
def swap_uuid_bytes(uuid):
    return uuid[3::-1] + uuid[5:3:-1] + uuid[7:5:-1] + uuid[8:]


'''
Creates Packed data from extracted manifest data
Writes the packed data to binary file
'''
def pack_manifest_data(manifest, log):
    # PACK {
    #        uuid,
    #        TRUSTY_APP_CONFIG_KEY_MIN_HEAP_SIZE, min_heap,
    #        TRUSTY_APP_CONFIG_KEY_MIN_STACK_SIZE, min_stack,
    #        TRUSTY_APP_CONFIG_KEY_MAP_MEM, id, addr, size
    #        TRUSTY_APP_CONFIG_KEY_MAP_MEM, id, addr, size
    #      }
    out = cStringIO.StringIO()

    uuid = swap_uuid_bytes(manifest.uuid)
    out.write(uuid)

    if manifest.min_heap is not None:
        out.write(struct.pack("II",TRUSTY_APP_CONFIG_KEY_MIN_HEAP_SIZE,
                              manifest.min_heap))

    if manifest.min_stack is not None:
        out.write(struct.pack("II", TRUSTY_APP_CONFIG_KEY_MIN_STACK_SIZE,
                              manifest.min_stack))

    for memio_map in manifest.mem_io_maps:
        out.write(struct.pack("IIII",
                              TRUSTY_APP_CONFIG_KEY_MAP_MEM,
                              memio_map.id,
                              memio_map.addr,
                              memio_map.size))

    return out.getvalue()


'''
Creates manifest JSON string from packed manifest data
'''
def unpack_binary_manifest_to_json(packed_data):
    return manifest_data_to_json(unpack_binary_manifest_to_data(packed_data))


def manifest_data_to_json(manifest):
    return json.dumps(manifest, sort_keys=True, indent=4)


'''
This method can be used for extracting manifest data from packed binary.
UUID should be present in packed data.
'''
def unpack_binary_manifest_to_data(packed_data):
    manifest = {}

    # Extract UUID
    uuid, packed_data = packed_data[:16], packed_data[16:]
    uuid = swap_uuid_bytes(uuid)
    uuid = uuid.encode("hex")
    uuid = uuid[:8] + "-" \
            + uuid[8:12] + "-" \
            + uuid[12:16] + "-" \
            + uuid[16:20] + "-" \
            + uuid[20:]

    manifest[UUID] = uuid

    # Extract remaining app configurations
    while len(packed_data) > 0:
        (tag,), packed_data = struct.unpack(
                "I", packed_data[:4]), packed_data[4:]

        if tag == TRUSTY_APP_CONFIG_KEY_MIN_HEAP_SIZE:
            assert MIN_HEAP not in manifest
            (manifest[MIN_HEAP],), packed_data = struct.unpack(
                    "I", packed_data[:4]), packed_data[4:]
        elif tag == TRUSTY_APP_CONFIG_KEY_MIN_STACK_SIZE:
            assert MIN_STACK not in manifest
            (manifest[MIN_STACK],), packed_data = struct.unpack(
                    "I", packed_data[:4]), packed_data[4:]
        elif tag == TRUSTY_APP_CONFIG_KEY_MAP_MEM:
            if MEM_MAP not in manifest:
                manifest[MEM_MAP] = []
            mem_map_entry = {}
            (id_,), packed_data = struct.unpack(
                    "I", packed_data[:4]), packed_data[4:]
            (addr,), packed_data = struct.unpack(
                    "I", packed_data[:4]), packed_data[4:]
            (size,), packed_data = struct.unpack(
                    "I", packed_data[:4]), packed_data[4:]
            mem_map_entry[MEM_MAP_ID] = id_
            mem_map_entry[MEM_MAP_ADDR] = hex(addr)
            mem_map_entry[MEM_MAP_SIZE] = hex(size)
            manifest[MEM_MAP].append(mem_map_entry)
        else:
            raise Exception("Unknown tag: {}".format(tag))

    return manifest


def write_packed_data_to_bin_file(packed_data, output_file, log):
    # Write packed data to binary file
    try:
        with open(output_file, "wb") as out_file:
            out_file.write(packed_data)
            out_file.close()
    except IOError as ex:
        log.error(
                "Unable to write to output file: {}"
                .format(output_file) + "\n" + str(ex))


def read_manifest_config_file(input_file, log):
    try:
       read_file = open(input_file, "r")
    except IOError as ex:
        log.error(
                "Unable to open input file: {}"
                .format(input_file) + "\n" + str(ex))
        return None

    try:
        manifest_dict = json.load(read_file)
        return manifest_dict
    except ValueError as ex:
        log.error(
                "Unable to parse manifest config JSON - {}"
                .format(str(ex)))
        return None


'''
START OF THE PROGRAM
Handles the command line arguments
Parses the given manifest input file and creates packed data
Writes the packed data to binary output file.
'''
def main(argv):
    parser = argparse.ArgumentParser();
    parser.add_argument(
            "-i", "--input",
            dest="input_filename",
            required=True,
            type=str,
            help="It should be trust app manifest config JSON file"
    )
    parser.add_argument(
            "-o", "--output",
            dest="output_filename",
            required=True,
            type=str,
            help="It will be binary file with packed manifest data"
    )
    # Parse the command line arguments
    args = parser.parse_args()

    log = Log()

    if not os.path.exists(args.input_filename):
        log.error(
                "Manifest config JSON file doesn't exist: {}"
                .format(args.input_filename))
        return 1

    manifest_dict = read_manifest_config_file(args.input_filename, log)
    if log.error_occurred():
        return 1

    # parse the manifest config
    manifest = parse_manifest_config(manifest_dict, log)
    if log.error_occurred():
        return 1

    # Pack the data as per c structures
    packed_data = pack_manifest_data(manifest, log)
    if log.error_occurred():
        return 1

    # Write to file.
    write_packed_data_to_bin_file(packed_data, args.output_filename, log)
    if log.error_occurred():
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
