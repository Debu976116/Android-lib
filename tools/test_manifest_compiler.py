#!/usr/bin/env python

'''
Command to run tests:
  python2 -m unittest -v test_manifest_compiler
'''

import unittest

import manifest_compiler

class TestManifest(unittest.TestCase):
    '''
    Test with integer value as input to get_string
    '''
    def test_get_string_1(self):
        log = manifest_compiler.Log()
        config_data  = {"data": 1234}
        data = manifest_compiler.get_string(config_data, "data", log)
        self.assertEqual(len(config_data), 0)
        self.assertTrue(log.error_occurred())
        self.assertIsNone(data)

    '''
    Test with valid uuid value as input to get_string
    '''
    def test_get_string_2(self):
        log = manifest_compiler.Log()
        uuid = "5f902ace-5e5c-4cd8-ae54-87b88c22ddaf"
        config_data  = {"data": uuid}
        data = manifest_compiler.get_string(config_data, "data", log)
        self.assertEqual(len(config_data), 0)
        self.assertFalse(log.error_occurred())
        self.assertEqual(data, uuid)

    '''
    Test with empty string
    '''
    def test_get_string_3(self):
        log = manifest_compiler.Log()
        config_data  = {"data": ""}
        data = manifest_compiler.get_string(config_data, "data", log)
        self.assertEqual(len(config_data), 0)
        self.assertFalse(log.error_occurred())
        self.assertEqual(data, "")

    '''
    Test with empty config data and non optional field
    '''
    def test_get_string_4(self):
        log = manifest_compiler.Log()
        config_data  = {}
        data = manifest_compiler.get_string(config_data, "data", log)
        self.assertEqual(len(config_data), 0)
        self.assertTrue(log.error_occurred())
        self.assertIsNone(data)

    '''
    Test with non-existing attribute which is optional
    '''
    def test_get_string_5(self):
        log = manifest_compiler.Log()
        config_data  = {}
        data = manifest_compiler.get_string(config_data, "data",
                                            log, optional=True, default="")
        self.assertFalse(log.error_occurred())
        self.assertEqual(data, "")

    '''
    Test with empty config with required field
    '''
    def test_get_string_6(self):
        log = manifest_compiler.Log()
        config_data  = {}
        data = manifest_compiler.get_string(config_data, "data", log)
        self.assertTrue(log.error_occurred())
        self.assertIsNone(data)

    '''
    Test with empty string for get_int
    '''
    def test_get_int_1(self):
        log = manifest_compiler.Log()
        config_data  = {"data": ""}
        data = manifest_compiler.get_int(config_data, "data", log)
        self.assertEqual(len(config_data), 0)
        self.assertTrue(log.error_occurred())
        self.assertIsNone(data)

    '''
    Test with string of integers
    '''
    def test_get_int_2(self):
        log = manifest_compiler.Log()
        config_data  = {"data": "4096"}
        data = manifest_compiler.get_int(config_data, "data", log)
        self.assertEqual(len(config_data), 0)
        self.assertFalse(log.error_occurred())
        self.assertEqual(data, 4096)

    '''
    Test with integer value
    '''
    def test_get_int_3(self):
        log = manifest_compiler.Log()
        config_data  = {"data": 4096}
        data = manifest_compiler.get_int(config_data, "data", log)
        self.assertEqual(len(config_data), 0)
        self.assertFalse(log.error_occurred())
        self.assertEqual(data, 4096)

    '''
    Test with empty config data and non optional field
    '''
    def test_get_int_4(self):
        log = manifest_compiler.Log()
        config_data  = {}
        data = manifest_compiler.get_int(config_data, "data", log)
        self.assertTrue(log.error_occurred())
        self.assertIsNone(data)

    '''
    Test with valid hex string
    '''
    def test_get_int_5(self):
        log = manifest_compiler.Log()
        config_data  = {"data": "0X7f010000"}
        data = manifest_compiler.get_int(config_data, "data", log)
        self.assertFalse(log.error_occurred())
        self.assertEqual(data, 0X7f010000)

    '''
    Test with invalid hex string
    '''
    def test_get_int_6(self):
        log = manifest_compiler.Log()
        config_data  = {"data": "0X7k010000"}
        data = manifest_compiler.get_int(config_data, "data", log)
        self.assertTrue(log.error_occurred())
        self.assertIsNone(data)

    '''
    Test with string containing non-integers
    '''
    def test_get_int_7(self):
        log = manifest_compiler.Log()
        config_data  = {"data": "123A7"}
        data = manifest_compiler.get_int(config_data, "data", log)
        self.assertTrue(log.error_occurred())
        self.assertIsNone(data)

    '''
    Test with boolean value
    '''
    def test_get_int_8(self):
        log = manifest_compiler.Log()
        config_data  = {"data": True}
        data = manifest_compiler.get_int(config_data, "data", log)
        self.assertTrue(log.error_occurred())
        self.assertIsNone(data)

    '''
    Test with non-existing attribute which is optional field
    '''
    def test_get_int_9(self):
        log = manifest_compiler.Log()
        config_data  = {}
        data = manifest_compiler.get_int(config_data, "data", log,
                                         optional=True)
        self.assertFalse(log.error_occurred())
        self.assertIsNone(data)

    '''
    Test with non-existing attribute which is optional field
    '''
    def test_get_int_10(self):
        log = manifest_compiler.Log()
        config_data  = {}
        data = manifest_compiler.get_int(config_data, "data", log,
                                         optional=True, default=0)
        self.assertFalse(log.error_occurred())
        self.assertEqual(data, 0)

    '''
    Test with valid boolean values
    '''
    def test_get_boolean_1(self):
        log = manifest_compiler.Log()
        config_data  = {"data": True}
        data = manifest_compiler.get_boolean(config_data, "data", log)
        self.assertFalse(log.error_occurred())
        self.assertTrue(data)

    '''
    Test with invalid values
    '''
    def test_get_boolean_2(self):
        log = manifest_compiler.Log()
        config_data  = {"data": "True"}
        data = manifest_compiler.get_boolean(config_data, "data", log)
        self.assertTrue(log.error_occurred())
        self.assertIsNone(data)

    '''
    Test with invalid values
    '''
    def test_get_boolean_3(self):
        log = manifest_compiler.Log()
        config_data  = {"data": 1}
        data = manifest_compiler.get_boolean(config_data, "data", log)
        self.assertTrue(log.error_occurred())
        self.assertIsNone(data)

    '''
    Test with empty config data with non optional field
    '''
    def test_get_boolean_4(self):
        log = manifest_compiler.Log()
        config_data  = {}
        data = manifest_compiler.get_boolean(config_data, "data", log)
        self.assertTrue(log.error_occurred())
        self.assertIsNone(data)

    '''
    Test with non-existing attribute which is optional
    '''
    def test_get_boolean_5(self):
        log = manifest_compiler.Log()
        config_data  = {}
        data = manifest_compiler.get_boolean(config_data, "data", log,
                                             optional=True, default=False)
        self.assertFalse(log.error_occurred())
        self.assertFalse(data)

    '''
    Test with valid value as list
    '''
    def test_get_list_1(self):
        log = manifest_compiler.Log()
        sample_list = [1, 2, 3]
        config_data  = {"data": sample_list}
        data = manifest_compiler.get_list(config_data, "data", log)
        self.assertFalse(log.error_occurred())
        self.assertEqual(data, sample_list)

    '''
    Test with non-existing attribute with optional field
    '''
    def test_get_list_2(self):
        log = manifest_compiler.Log()
        config_data  = {}
        data = manifest_compiler.get_list(config_data, "data", log,
                                          optional=True, default=[])
        self.assertFalse(log.error_occurred())
        self.assertEqual(data, [])

    '''
    Test with empty config data with required field
    '''
    def test_get_list_3(self):
        log = manifest_compiler.Log()
        config_data  = {}
        data = manifest_compiler.get_list(config_data, "data", log)
        self.assertTrue(log.error_occurred())
        self.assertIsNone(data)

    '''
    Test with invalid value
    '''
    def test_get_list_4(self):
        log = manifest_compiler.Log()
        config_data  = {"data": 123}
        data = manifest_compiler.get_list(config_data, "data", log,
                                          optional=True)
        self.assertTrue(log.error_occurred())

    '''
    Test with valid value as dict
    '''
    def test_get_dict_1(self):
        log = manifest_compiler.Log()
        sample_dict = {"attr": 1}
        config_data  = {"data": sample_dict}
        data = manifest_compiler.get_dict(config_data, "data", log)
        self.assertFalse(log.error_occurred())
        self.assertEqual(data, sample_dict)

    '''
    Test with non-existing attribute with optional field
    '''
    def test_get_dict_2(self):
        log = manifest_compiler.Log()
        config_data  = {}
        data = manifest_compiler.get_dict(config_data, "data", log,
                                          optional=True, default={})
        self.assertFalse(log.error_occurred())
        self.assertEqual(data, {})

    '''
    Test with empty config data with required field
    '''
    def test_get_dict_3(self):
        log = manifest_compiler.Log()
        config_data  = {}
        data = manifest_compiler.get_dict(config_data, "data", log)
        self.assertTrue(log.error_occurred())
        self.assertIsNone(data)

    '''
    Test with invalid value
    '''
    def test_get_dict_4(self):
        log = manifest_compiler.Log()
        config_data  = {"data": 123}
        data = manifest_compiler.get_dict(config_data, "data",
                                          log, optional=True)
        self.assertTrue(log.error_occurred())

    '''
    Test with valid UUID with hex values
    '''
    def test_validate_uuid_1(self):
        log = manifest_compiler.Log()
        uuid_in = "5f902ace-5e5c-4cd8-ae54-87b88c22ddaf"
        data = manifest_compiler.parse_uuid(uuid_in, log)
        self.assertFalse(log.error_occurred())
        self.assertEqual(data.encode("hex"), uuid_in.replace("-", ""))

    '''
    Test with invalid UUID containing one byte less
    '''
    def test_validate_uuid_2(self):
        log = manifest_compiler.Log()
        uuid  = "902ace-5e5c-4cd8-ae54-87b88c22ddaf"
        data = manifest_compiler.parse_uuid(uuid, log)
        self.assertTrue(log.error_occurred())
        self.assertIsNone(data)

    '''
    Test with invalid number of bytes in uuid groups
    '''
    def test_validate_uuid_3(self):
        log = manifest_compiler.Log()
        uuid  = "5f902ace5e-5c-4cd8-ae54-87b88c22ddaf"
        data = manifest_compiler.parse_uuid(uuid, log)
        self.assertTrue(log.error_occurred())
        self.assertIsNone(data)

    '''
    Test with valid UUID value but ungrouped
    '''
    def test_validate_uuid_6(self):
        log = manifest_compiler.Log()
        uuid  = "5f902ace5e5c4cd8ae5487b88c22ddaf"
        data = manifest_compiler.parse_uuid(uuid, log)
        self.assertTrue(log.error_occurred())
        self.assertIsNone(data)

    '''
    Test with invalid UUID value
    '''
    def test_validate_uuid_7(self):
        log = manifest_compiler.Log()
        uuid  = "12345678-9111-1222-3333-222111233222"
        data = manifest_compiler.parse_uuid(uuid, log)
        self.assertTrue(log.error_occurred())
        self.assertIsNone(data)

    '''
    Test with invalid UUID value
    '''
    def test_validate_uuid_7(self):
        log = manifest_compiler.Log()
        uuid  = ""
        data = manifest_compiler.parse_uuid(uuid, log)
        self.assertTrue(log.error_occurred())
        self.assertIsNone(data)

    '''
    Test with valid memory size
    '''
    def test_validate_memory_size_1(self):
        log = manifest_compiler.Log()
        data = manifest_compiler.parse_memory_size(4096, log)
        self.assertFalse(log.error_occurred())
        self.assertEqual(data, 4096)

    '''
    Test with valid memory size
    '''
    def test_validate_memory_size_2(self):
        log = manifest_compiler.Log()
        data = manifest_compiler.parse_memory_size(8192, log)
        self.assertFalse(log.error_occurred())
        self.assertEqual(data, 8192)

    '''
    Test with invalid memory size
    '''
    def test_validate_memory_size_3(self):
        log = manifest_compiler.Log()
        data = manifest_compiler.parse_memory_size(0, log)
        self.assertTrue(log.error_occurred())
        self.assertIsNone(data)

    '''
    Test with invalid memory size
    '''
    def test_validate_memory_size_4(self):
        log = manifest_compiler.Log()
        data = manifest_compiler.parse_memory_size(-4096, log)
        self.assertTrue(log.error_occurred())
        self.assertIsNone(data)

    '''
    Test with invalid memory size
    '''
    def test_validate_memory_size_5(self):
        log = manifest_compiler.Log()
        data = manifest_compiler.parse_memory_size(4095, log)
        self.assertTrue(log.error_occurred())
        self.assertIsNone(data)

    '''
    Test with invalid memory size
    '''
    def test_validate_memory_size_6(self):
        log = manifest_compiler.Log()
        data = manifest_compiler.parse_memory_size(16777217, log)
        self.assertTrue(log.error_occurred())
        self.assertIsNone(data)

    '''
    Test with invalid memory size
    '''
    def test_validate_memory_size_7(self):
        log = manifest_compiler.Log()
        data = manifest_compiler.parse_memory_size(1024, log)
        self.assertTrue(log.error_occurred())
        self.assertIsNone(data)

    '''
    Test with valid large integer value (2**32) as memory size
    '''
    def test_validate_memory_size_8(self):
        log = manifest_compiler.Log()
        data = manifest_compiler.parse_memory_size(4294967296, log)
        self.assertFalse(log.error_occurred())
        self.assertEqual(data, 4294967296)

    '''
    Test with a single memory mapping
    '''
    def test_validate_mem_map_1(self):
        mem_map_ref_data = [{"id": 1, "addr": 0x70000000, "size": 0x1000}]

        mem_map_json_data = [{"id": 1, "addr": "0x70000000", "size": "0x1000"}]

        log = manifest_compiler.Log()
        mem_io_map_list = manifest_compiler.parse_mem_map(
                mem_map_json_data, manifest_compiler.MEM_MAP, log)
        self.assertFalse(log.error_occurred())

        for (memio_map, memio_ref_data) in zip(
                mem_io_map_list, mem_map_ref_data):
            self.assertEqual(memio_map.id, memio_ref_data["id"])
            self.assertEqual(memio_map.addr, memio_ref_data["addr"])
            self.assertEqual(memio_map.size, memio_ref_data["size"])

    '''
    Test with multiple memory mapping
    '''
    def test_validate_mem_map_2(self):
        mem_map_ref_data = [{"id": 1, "addr": 0x70000000, "size": 0x1000},
                            {"id": 2, "addr": 0x70010000, "size": 0x100},
                            {"id": 3, "addr": 0x70020000, "size": 0x4}]

        mem_map_json_data = [{"id": 1, "addr": "0x70000000", "size": "0x1000"},
                             {"id": 2, "addr": "0x70010000", "size": "0x100"},
                             {"id": 3, "addr": "0x70020000", "size": "0x4"}]

        log = manifest_compiler.Log()
        mem_io_map_list = manifest_compiler.parse_mem_map(
                mem_map_json_data, manifest_compiler.MEM_MAP, log)
        self.assertFalse(log.error_occurred())

        for (memio_map, memio_ref_data) in zip(
                mem_io_map_list, mem_map_ref_data):
            self.assertEqual(memio_map.id, memio_ref_data["id"])
            self.assertEqual(memio_map.addr, memio_ref_data["addr"])
            self.assertEqual(memio_map.size, memio_ref_data["size"])

    '''
    Test with a unknown entry in memory mapping
    '''
    def test_validate_mem_map_3(self):
        mem_map_json_data = [{"id": 1, "addr": "0x70000000", "size": "0x1000",
                              "offset": "0x70001000"}]

        log = manifest_compiler.Log()
        mem_io_map_list = manifest_compiler.parse_mem_map(
                mem_map_json_data, manifest_compiler.MEM_MAP, log)
        self.assertTrue(log.error_occurred())

    '''
    Test with a empty memory mapping entry
    '''
    def test_validate_mem_map_4(self):
        mem_map_json_data = []

        log = manifest_compiler.Log()
        mem_io_map_list = manifest_compiler.parse_mem_map(
                mem_map_json_data, manifest_compiler.MEM_MAP, log)
        self.assertFalse(log.error_occurred())
        self.assertFalse(mem_io_map_list)

    '''
    Test with a memory mapping entry with missing "size"
    '''
    def test_validate_mem_map_5(self):
        mem_map_json_data = [{"id": 1, "addr": "0x70000000"}]

        log = manifest_compiler.Log()
        mem_io_map_list = manifest_compiler.parse_mem_map(
                mem_map_json_data, manifest_compiler.MEM_MAP, log)
        self.assertTrue(log.error_occurred())

    '''
    Test with a memory mapping entry with invalid JSON format
    Pass invalid list of JSON attributes
    '''
    def test_validate_mem_map_6(self):
        mem_map_json_data = ["id", 1, "addr", "0x70000000"]

        log = manifest_compiler.Log()
        mem_io_map_list = manifest_compiler.parse_mem_map(
                mem_map_json_data, manifest_compiler.MEM_MAP, log)
        self.assertTrue(log.error_occurred())

    '''
    Test with a memory mapping entry with invalid JSON format
    Pass a MEM_MAP JSON object instead of list of MEM_MAP JSON objects.
    '''
    def test_validate_mem_map_7(self):
        config_data = {manifest_compiler.MEM_MAP:
                       {"id": 1, "addr": "0x70000000"}}

        log = manifest_compiler.Log()
        mem_io_map_list = manifest_compiler.parse_mem_map(
                manifest_compiler.get_list(
                        config_data, manifest_compiler.MEM_MAP, log,
                        optional=True),
                manifest_compiler.MEM_MAP, log)
        self.assertTrue(log.error_occurred())

    '''
    Test with a valid management flags
    '''
    def test_validate_mgmt_flags_1(self):
        mgmt_flags_ref_data = {
                manifest_compiler.MGMT_FLAG_RESTART_ON_EXIT: True,
                manifest_compiler.MGMT_FLAG_DEFERRED_START: True}
        mgmt_flags_data = {
                manifest_compiler.MGMT_FLAG_RESTART_ON_EXIT: True,
                manifest_compiler.MGMT_FLAG_DEFERRED_START: True}

        log = manifest_compiler.Log()
        mgmt_flags = manifest_compiler.parse_mgmt_flags(
            mgmt_flags_data, log)
        self.assertFalse(log.error_occurred())
        self.assertEqual(mgmt_flags.restart_on_exit,
                         mgmt_flags_ref_data[
                             manifest_compiler.MGMT_FLAG_RESTART_ON_EXIT])
        self.assertEqual(mgmt_flags.deferred_start,
                         mgmt_flags_ref_data[
                             manifest_compiler.MGMT_FLAG_DEFERRED_START])

    '''
    Test with a valid management flags
    '''
    def test_validate_mgmt_flags_2(self):
        mgmt_flags_ref_data = {
                manifest_compiler.MGMT_FLAG_RESTART_ON_EXIT: False,
                manifest_compiler.MGMT_FLAG_DEFERRED_START: False}
        mgmt_flags_data = {
                manifest_compiler.MGMT_FLAG_RESTART_ON_EXIT: False,
                manifest_compiler.MGMT_FLAG_DEFERRED_START: False}

        log = manifest_compiler.Log()
        mgmt_flags = manifest_compiler.parse_mgmt_flags(
            mgmt_flags_data, log)
        self.assertFalse(log.error_occurred())
        self.assertEqual(mgmt_flags.restart_on_exit,
                         mgmt_flags_ref_data[
                             manifest_compiler.MGMT_FLAG_RESTART_ON_EXIT])
        self.assertEqual(mgmt_flags.deferred_start,
                         mgmt_flags_ref_data[
                             manifest_compiler.MGMT_FLAG_DEFERRED_START])

    '''
    Test with a valid management flags
    '''
    def test_validate_mgmt_flags_3(self):
        mgmt_flags_ref_data = {
                manifest_compiler.MGMT_FLAG_RESTART_ON_EXIT: False,
                manifest_compiler.MGMT_FLAG_DEFERRED_START: True}
        mgmt_flags_data = {
                manifest_compiler.MGMT_FLAG_RESTART_ON_EXIT: False,
                manifest_compiler.MGMT_FLAG_DEFERRED_START: True}

        log = manifest_compiler.Log()
        mgmt_flags = manifest_compiler.parse_mgmt_flags(
            mgmt_flags_data, log)
        self.assertFalse(log.error_occurred())
        self.assertEqual(mgmt_flags.restart_on_exit,
                         mgmt_flags_ref_data[
                             manifest_compiler.MGMT_FLAG_RESTART_ON_EXIT])
        self.assertEqual(mgmt_flags.deferred_start,
                         mgmt_flags_ref_data[
                             manifest_compiler.MGMT_FLAG_DEFERRED_START])

    '''
    Test with a management flags missing
    manifest_compiler.MGMT_FLAG_RESTART_ON_EXIT
    '''
    def test_validate_mgmt_flags_4(self):
        mgmt_flags_data = {manifest_compiler.MGMT_FLAG_DEFERRED_START: True}

        log = manifest_compiler.Log()
        mgmt_flags = manifest_compiler.parse_mgmt_flags(
            mgmt_flags_data, log)
        self.assertTrue(log.error_occurred())
        self.assertIsNone(mgmt_flags.restart_on_exit)
        self.assertTrue(mgmt_flags.deferred_start)

    '''
    Test with a empty management flags"
    '''
    def test_validate_mgmt_flags_5(self):
        mgmt_flags_data = {}

        log = manifest_compiler.Log()
        mgmt_flags = manifest_compiler.parse_mgmt_flags(
            mgmt_flags_data, log)
        self.assertTrue(log.error_occurred())
        self.assertIsNone(mgmt_flags.restart_on_exit)
        self.assertIsNone(mgmt_flags.deferred_start)

    '''
    Test with a mgmt_flags as array of flags
    '''
    def test_validate_mgmt_flags_6(self):
        config_data = {manifest_compiler.MGMT_FLAGS: [{
                manifest_compiler.MGMT_FLAG_RESTART_ON_EXIT: True,
                manifest_compiler.MGMT_FLAG_DEFERRED_START: True}]}

        log = manifest_compiler.Log()
        mgmt_flags = manifest_compiler.parse_mgmt_flags(
            manifest_compiler.get_dict(
                    config_data, manifest_compiler.MGMT_FLAGS, log,
                    optional=True),
            log)
        self.assertTrue(log.error_occurred())

    '''
    Test with a  single start_ports entry
    '''
    def test_validate_start_port_1(self):
        ref_data = [{
            manifest_compiler.START_PORT_NAME: \
                "com.android.trusty.appmgmt.loadable.start",
            manifest_compiler.START_PORT_FLAGS: {
                manifest_compiler.START_PORT_ALLOW_TA_CONNECT: True,
                manifest_compiler.START_PORT_ALLOW_NS_CONNECT: False}}]

        port_conf_data = [{
            manifest_compiler.START_PORT_NAME: \
                "com.android.trusty.appmgmt.loadable.start",
            manifest_compiler.START_PORT_FLAGS: {
                manifest_compiler.START_PORT_ALLOW_TA_CONNECT: True,
                manifest_compiler.START_PORT_ALLOW_NS_CONNECT: False}}]

        log = manifest_compiler.Log()
        start_ports_list = manifest_compiler.parse_app_start_ports(
                port_conf_data, manifest_compiler.START_PORTS, log)
        self.assertFalse(log.error_occurred())

        for (start_port, ref_port) in zip(
                start_ports_list, ref_data):
            self.assertEqual(start_port.name,
                             ref_port[manifest_compiler.START_PORT_NAME])
            ref_flags = ref_port[manifest_compiler.START_PORT_FLAGS]
            self.assertEqual(
                start_port.start_port_flags.allow_ta_connect,
                ref_flags[manifest_compiler.START_PORT_ALLOW_TA_CONNECT])
            self.assertEqual(
                start_port.start_port_flags.allow_ns_connect,
                ref_flags[manifest_compiler.START_PORT_ALLOW_NS_CONNECT])

    '''
    Test with a  multiple start_ports entry
    '''
    def test_validate_start_port_2(self):
        ref_data = [
            {
                manifest_compiler.START_PORT_NAME: \
                    "com.android.trusty.appmgmt.loadable.start",
                manifest_compiler.START_PORT_FLAGS: {
                    manifest_compiler.START_PORT_ALLOW_TA_CONNECT: True,
                    manifest_compiler.START_PORT_ALLOW_NS_CONNECT: False
                }
            },
            {
                manifest_compiler.START_PORT_NAME: \
                    "com.android.trusty.appmgmt.portstartsrv.shutdown",
                manifest_compiler.START_PORT_FLAGS: {
                    manifest_compiler.START_PORT_ALLOW_TA_CONNECT: True,
                    manifest_compiler.START_PORT_ALLOW_NS_CONNECT: True
                }
            }]

        port_conf_data = [
            {
                manifest_compiler.START_PORT_NAME: \
                    "com.android.trusty.appmgmt.loadable.start",
                manifest_compiler.START_PORT_FLAGS: {
                    manifest_compiler.START_PORT_ALLOW_TA_CONNECT: True,
                    manifest_compiler.START_PORT_ALLOW_NS_CONNECT: False}
            },
            {
                manifest_compiler.START_PORT_NAME: \
                        "com.android.trusty.appmgmt.portstartsrv.shutdown",
                manifest_compiler.START_PORT_FLAGS: {
                    manifest_compiler.START_PORT_ALLOW_TA_CONNECT: True,
                    manifest_compiler.START_PORT_ALLOW_NS_CONNECT: True}
            }]

        log = manifest_compiler.Log()
        start_ports_list = manifest_compiler.parse_app_start_ports(
                port_conf_data, manifest_compiler.START_PORTS, log)
        self.assertFalse(log.error_occurred())

        for (start_port, ref_port) in zip(
                start_ports_list, ref_data):
            self.assertEqual(start_port.name,
                    ref_port[manifest_compiler.START_PORT_NAME])
            ref_port_flags = ref_port[manifest_compiler.START_PORT_FLAGS]
            self.assertEqual(
                start_port.start_port_flags.allow_ta_connect,
                ref_port_flags[manifest_compiler.START_PORT_ALLOW_TA_CONNECT])
            self.assertEqual(
                start_port.start_port_flags.allow_ns_connect,
                ref_port_flags[manifest_compiler.START_PORT_ALLOW_NS_CONNECT])

    '''
    Test with a zero start_ports
    '''
    def test_validate_start_port_3(self):
        start_ports_json_data = []

        log = manifest_compiler.Log()
        start_ports_list = manifest_compiler.parse_app_start_ports(
                start_ports_json_data, manifest_compiler.START_PORTS, log)
        self.assertFalse(log.error_occurred())
        self.assertEqual(len(start_ports_list), 0)

    '''
    Test with a unknown attribute in start_port entry
    '''
    def test_validate_start_port_4(self):
        start_ports_json_data = [
            {
                manifest_compiler.START_PORT_NAME: \
                        "com.android.trusty.appmgmt.loadable.start",
                manifest_compiler.START_PORT_ALLOW_TA_CONNECT: True,
                manifest_compiler.START_PORT_FLAGS: {
                    manifest_compiler.START_PORT_ALLOW_TA_CONNECT: True,
                    manifest_compiler.START_PORT_ALLOW_NS_CONNECT: False}
            }]

        log = manifest_compiler.Log()
        start_ports_list = manifest_compiler.parse_app_start_ports(
                start_ports_json_data, manifest_compiler.START_PORTS, log)
        self.assertTrue(log.error_occurred())

    '''
    Test with a flags missing in start_port entry
    '''
    def test_validate_start_port_5(self):
        start_ports_json_data = [
            {
                manifest_compiler.START_PORT_NAME: \
                        "com.android.trusty.appmgmt.loadable.start",
            }]

        log = manifest_compiler.Log()
        start_ports_list = manifest_compiler.parse_app_start_ports(
                start_ports_json_data, manifest_compiler.START_PORTS, log)
        self.assertTrue(log.error_occurred())

    '''
    Test with valid UUID with hex values and
    valid values for min_heap and min_stack.
    '''
    def test_manifest_valid_dict_1(self):
        uuid_in = "5f902ace-5e5c-4cd8-ae54-87b88c22ddaf"
        min_heap = 4096
        min_stack = 4096
        id_ = 1
        addr = "0x70000000"
        size = "0x1000"
        mem_map_data = [{"id": id_, "addr": addr, "size": size}]
        log = manifest_compiler.Log()

        config_data  = {
                "uuid": uuid_in,
                "min_heap": min_heap,
                "min_stack": min_stack,
                "mem_map": mem_map_data
        }
        manifest = manifest_compiler.parse_manifest_config(config_data, log)
        self.assertFalse(log.error_occurred())
        self.assertIsNotNone(manifest)
        self.assertEqual(manifest.uuid.encode("hex"), uuid_in.replace("-", ""))
        self.assertEqual(manifest.min_heap, min_heap)
        self.assertEqual(manifest.min_stack, min_stack)
        for memio_map in manifest.mem_io_maps:
            self.assertEqual(memio_map.id, id_)
            self.assertEqual(memio_map.addr, int(addr, 0))
            self.assertEqual(memio_map.size, int(size, 0))
        self.assertFalse(manifest.mgmt_flags.restart_on_exit)
        self.assertFalse(manifest.mgmt_flags.deferred_start)

    '''
    Test with invalid value in config,
    UUID with integer value and string values for min_stack.
    '''
    def test_manifest_invalid_dict_2(self):
        log = manifest_compiler.Log()
        config_data  = {"uuid": 123, "min_heap": "4096", "min_stack": "8192"}
        manifest = manifest_compiler.parse_manifest_config(config_data, log)
        self.assertEqual(len(config_data), 0)
        self.assertTrue(log.error_occurred())
        self.assertIsNone(manifest)

    '''
    Test with empty config.
    '''
    def test_manifest_invalid_dict_3(self):
        log = manifest_compiler.Log()
        config_data  = {}
        manifest = manifest_compiler.parse_manifest_config(config_data, log)
        self.assertTrue(log.error_occurred())
        self.assertIsNone(manifest)

    '''
    Test with unknown entries
    '''
    def test_manifest_invalid_dict_4(self):
        log = manifest_compiler.Log()
        config_data  = {"uuid": "5f902ace-5e5c-4cd8-ae54-87b88c22ddaf",
                         "min_heap": 4096, "min_stack": 4096, "max_heap": 234}
        manifest = manifest_compiler.parse_manifest_config(config_data, log)
        self.assertNotEqual(len(config_data), 0)
        self.assertTrue(log.error_occurred())
        self.assertIsNone(manifest)

    '''
    Test with valid UUID with hex values and
    valid values for min_heap and min_stack.
    Pack the manifest config data and unpack it and
    verify it with the expected values
    '''
    def test_manifest_valid_pack_1(self):
        # PLZ DON'T EDIT VALUES
        log = manifest_compiler.Log()

        # Reference JSON manifest data structure
        config_ref_data  = {
                manifest_compiler.UUID: "5f902ace-5e5c-4cd8-ae54-87b88c22ddaf",
                manifest_compiler.MIN_HEAP: 8192,
                manifest_compiler.MIN_STACK: 4096,
                manifest_compiler.MGMT_FLAGS: {
                        manifest_compiler.MGMT_FLAG_RESTART_ON_EXIT: False,
                        manifest_compiler.MGMT_FLAG_DEFERRED_START: False
                }
        }

        # JSON manifest data structure
        config_data  = {
                manifest_compiler.UUID: "5f902ace-5e5c-4cd8-ae54-87b88c22ddaf",
                manifest_compiler.MIN_HEAP: 8192,
                manifest_compiler.MIN_STACK: 4096
        }

        '''
        Pack manifest config_data
        Unpack the binary packed data to JSON text
        Validate unpacked JSON text
        '''
        self.assertEqual(
                manifest_compiler.manifest_data_to_json(config_ref_data),
                manifest_compiler.unpack_binary_manifest_to_json(
                        pack_manifest_config_data(self, config_data, log)))

    '''
    Test with valid manifest config containing
      - UUID
      - min_heap and min_stack
      - memory mapping entries
    Pack the manifest config data and unpack it and
    verify it with the expected values
    '''
    def test_manifest_valid_pack_2(self):
        log = manifest_compiler.Log()

        # Reference JSON manifest data structure
        ref_config_data  = {
                manifest_compiler.UUID: "5f902ace-5e5c-4cd8-ae54-87b88c22ddaf",
                manifest_compiler.MIN_HEAP: 8192,
                manifest_compiler.MIN_STACK: 4096,
                manifest_compiler.MEM_MAP: [
                        {"id": 1, "addr": "0x70000000", "size": "0x1000"},
                        {"id": 2, "addr": "0x70010000", "size": "0x100"},
                        {"id": 3, "addr": "0x70020000", "size": "0x4"}],
                manifest_compiler.MGMT_FLAGS: {
                        manifest_compiler.MGMT_FLAG_RESTART_ON_EXIT: False,
                        manifest_compiler.MGMT_FLAG_DEFERRED_START: False
                }
        }

        # JSON manifest data structure
        config_data  = {
                manifest_compiler.UUID: "5f902ace-5e5c-4cd8-ae54-87b88c22ddaf",
                manifest_compiler.MIN_HEAP: 8192,
                manifest_compiler.MIN_STACK: 4096,
                manifest_compiler.MEM_MAP: [
                        {"id": 1, "addr": "0x70000000", "size": "0x1000"},
                        {"id": 2, "addr": "0x70010000", "size": "0x100"},
                        {"id": 3, "addr": "0x70020000", "size": "0x4"}]
        }

        '''
        Pack manifest config_data
        Unpack the binary packed data to JSON text
        Validate unpacked JSON text
        '''
        self.assertEqual(
                manifest_compiler.manifest_data_to_json(ref_config_data),
                manifest_compiler.unpack_binary_manifest_to_json(
                        pack_manifest_config_data(self, config_data, log)))

    '''
    Test with valid manifest config containing
      - UUID
      - min_heap and min_stack
      - Management flags
    Pack the manifest config data and unpack it and
    verify it with the expected values
    '''
    def test_manifest_valid_pack_3(self):
        log = manifest_compiler.Log()

        # JSON manifest data structure
        config_data  = {
                manifest_compiler.UUID: "5f902ace-5e5c-4cd8-ae54-87b88c22ddaf",
                manifest_compiler.MIN_HEAP: 8192,
                manifest_compiler.MIN_STACK: 4096,
                manifest_compiler.MGMT_FLAGS: {
                        manifest_compiler.MGMT_FLAG_RESTART_ON_EXIT: True,
                        manifest_compiler.MGMT_FLAG_DEFERRED_START: False
                }
        }

        '''
        Pack manifest config_data
        Unpack the binary packed data to JSON text
        Validate unpacked JSON text
        '''
        self.assertEqual(
                manifest_compiler.manifest_data_to_json(config_data),
                manifest_compiler.unpack_binary_manifest_to_json(
                        pack_manifest_config_data(self, config_data, log)))


    '''
    Test with valid manifest config containing
      - UUID
      - min_heap and min_stack
      - start_ports
    Pack the manifest config data and unpack it and
    verify it with the expected values
    '''
    def test_manifest_valid_pack_4(self):
        log = manifest_compiler.Log()

        # Reference manifest data structure
        ref_config_data  = {
                manifest_compiler.UUID: "5f902ace-5e5c-4cd8-ae54-87b88c22ddaf",
                manifest_compiler.MIN_HEAP: 8192,
                manifest_compiler.MIN_STACK: 4096,
                manifest_compiler.START_PORTS: [
                    {
                        manifest_compiler.START_PORT_NAME: \
                                "com.android.trusty.appmgmt.loadable.start",
                        manifest_compiler.START_PORT_FLAGS: {
                            manifest_compiler.START_PORT_ALLOW_TA_CONNECT: True,
                            manifest_compiler.START_PORT_ALLOW_NS_CONNECT: False
                        }
                    }
                ],
                manifest_compiler.MGMT_FLAGS: {
                        manifest_compiler.MGMT_FLAG_RESTART_ON_EXIT: False,
                        manifest_compiler.MGMT_FLAG_DEFERRED_START: False
                }
        }

        # JSON manifest data structure
        config_data  = {
                manifest_compiler.UUID: "5f902ace-5e5c-4cd8-ae54-87b88c22ddaf",
                manifest_compiler.MIN_HEAP: 8192,
                manifest_compiler.MIN_STACK: 4096,
                manifest_compiler.START_PORTS: [
                    {
                        manifest_compiler.START_PORT_NAME: \
                                "com.android.trusty.appmgmt.loadable.start",
                        manifest_compiler.START_PORT_FLAGS: {
                            manifest_compiler.START_PORT_ALLOW_TA_CONNECT: True,
                            manifest_compiler.START_PORT_ALLOW_NS_CONNECT: False
                        }
                    }
                ]
        }

        '''
        Pack manifest config_data
        Unpack the binary packed data to JSON text
        Validate unpacked JSON text
        '''
        self.assertEqual(
                manifest_compiler.manifest_data_to_json(ref_config_data),
                manifest_compiler.unpack_binary_manifest_to_json(
                        pack_manifest_config_data(self, config_data, log)))


def pack_manifest_config_data(self, config_data, log):
    # parse manifest JSON data
    manifest = manifest_compiler.parse_manifest_config(config_data, log)
    self.assertFalse(log.error_occurred())

    # pack manifest config data
    packed_data = manifest_compiler.pack_manifest_data(manifest, log)
    self.assertEqual(len(config_data), 0)
    self.assertFalse(log.error_occurred())
    self.assertIsNotNone(packed_data)

    return packed_data

'''
START - Test start point
'''
if __name__ == "__main__":
    unittest.main()