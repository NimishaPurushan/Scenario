from os import path
from os.path import *
from os import remove, rename, chdir
from subprocess import check_output
import subprocess
import json
from re import search
from dateutil.parser import parse
from .logger import ScenarioLogger

sc_log = ScenarioLogger(__name__)


class PcapAnalyser:

    tshark_path = "C:\\Program Files\\Wireshark"

    @classmethod
    def set_tshark_patch(cls, path):
        cls.tshark_path = path

    def get_packet_info(self, pcap_filename: str = None, pcap_filter: str = None,
                        dual_pass=True, protocol: str = None):
        # Storing the paths
        print("called function........................")
        exec_dir = abspath(curdir)
        tshark_path = abspath(self.tshark_path)
        pcap_filename = abspath(pcap_filename)
        # setting-up for dual pass
        if dual_pass:
            dual_pass = -2
        else:
            dual_pass = ''

        # Setting the current path
        chdir(exec_dir)
        if not isfile(''.join([tshark_path, '\\', 'tshark.exe'])):
            raise FileNotFoundError(f"Unable to locate tshark executable in the path : {tshark_path}")
        elif not isfile(pcap_filename):
            raise FileNotFoundError(f"Unable to locate pcap file in the path : {pcap_filename}")
        tshark_parse_command = f'tshark.exe -r {pcap_filename} {dual_pass} -R "{pcap_filter}" -T json'
        print(f"{tshark_parse_command}")
        # Setting the execution directory from tshark path
        chdir(tshark_path)
        # Execute command
        try:
            result = subprocess.run(tshark_parse_command, stdout=subprocess.PIPE)
            chdir(exec_dir)
            data = []
            packets = json.loads(result.stdout)
            for packet in packets:
                data.append({packet["_source"]["layers"]["frame"]["frame.time"]:
                                 packet["_source"]["layers"][protocol]})
            return data
        except KeyError:
            print(f"Check protocol")

    def tshark_validate(self, pcap_filename: str = None, pcap_filter: str = None, dual_pass: str = True,
                        condition: str = None):
        # Storing the paths
        exec_dir = abspath(curdir)
        tshark_path = abspath(self.tshark_path)
        pcap_filename = abspath(pcap_filename)
        # setting-up for dual pass
        if dual_pass:
            dual_pass = -2
        else:
            dual_pass = ''

        # Setting the current path
        chdir(exec_dir)
        if not isfile(''.join([tshark_path, '\\', 'tshark.exe'])):
            raise FileNotFoundError(f"Unable to locate tshark executable in the path : {tshark_path}")
        elif not isfile(pcap_filename):
            raise FileNotFoundError(f"Unable to locate pcap file in the path : {pcap_filename}")
        try:
            # Command-palette
            if isinstance(pcap_filter, str):
                read_filter = pcap_filter.strip()
                # Return packet content without checking condition
                tshark_parse_command = f'tshark.exe -r {pcap_filename} {dual_pass} -R "{read_filter}"'
                # Setting the execution directory from tshark path
                chdir(tshark_path)
                # Execute command
                result = [output for output in check_output(tshark_parse_command).decode('utf-8').split('\n') if
                          output != '']
                if not result:
                    chdir(exec_dir)
                    self._check_condition(condition, len(result), read_filter, pcap_filename)
                for filter_result in result:
                    sc_log.console(f"Filter output : {filter_result}")
                # Reset the current working directory
                chdir(exec_dir)
                self._check_condition(condition, len(result), read_filter, pcap_filename)
            elif isinstance(pcap_filter, list):
                for _filter in pcap_filter:
                    if not isinstance(_filter, dict):
                        raise ValueError("Every filter passed must be a dictionary of format '{'filter_name: count'}'")
                    for filter_name, count in _filter.items():
                        filter_name = filter_name.strip()
                        tshark_parse_command = f'tshark.exe -r {pcap_filename} {dual_pass} -R "{filter_name}"'
                        # Setting the execution directory from tshark path
                        chdir(tshark_path)
                        # Execute command
                        result = [output for output in
                                  check_output(tshark_parse_command).decode('utf-8').split('\n') if output != '']
                        # SRTOOL-790 BUGFIX : Handling case of 0 result
                        if not result:
                            chdir(exec_dir)
                            self._check_condition(count, len(result), _filter, pcap_filename)
                        for filter_result in result:
                            sc_log.console(f"Filter output : {filter_result}")
                            # Reset the current working directory
                            chdir(exec_dir)
                            self._check_condition(count, len(result), _filter, pcap_filename)
        except Exception as err:
            sc_log.error(f"Could not validate the pcap because of the error {err}")
            # Reset the current working directory
            chdir(exec_dir)
            raise err

    def verify_msg(self, message_info: list = None, pcap_filename: str = None, pcap_filter: str = None,
                   protocol: str = None, sync=True):
        packets = self.get_packet_info(pcap_filename=pcap_filename, pcap_filter=pcap_filter, dual_pass=True,
                                       protocol=protocol)
        index = 0
        # print("message_info",message_info)
        for msg in message_info:
            # print("msg",msg)
            if not sync:
                index = 0
            msg_found = False
            while index < len(packets):
                if self._check_message(packets[index], msg):
                    msg_found = True
                    sc_log.console(f"MSG: {msg} found at {list(packets[index].keys())[0]}")
                    index += 1
                    break
                index += 1
            if not msg_found:
                sc_log.console(f"MSG: {msg} not found")
                return False
        sc_log.console(f"PACKETS ARE IN CORRECT ORDER")
        return True

    def check_timing(self, pcap_packets: list = None, message: dict = None, start_message: dict = None,
                     stop_message: dict = None, time_interval: int = None):
        index = 0
        msg_found = False
        date_format = r"((.*?)\d+:\d+:\d+.\d+)"
        first = True
        timestamp_list = []
        previous_timestamp = 0
        current_timestamp = 0
        first_timestamp = 0
        start = False
        stop = True
        while index < len(pcap_packets):
            if not start:
                if self._check_message(pcap_packets[index], start_message):
                    start = True
                index += 1
                continue
            if self._check_message(pcap_packets[index], message):
                msg_found = True
                datetime_str = list(pcap_packets[index].keys())[0]
                datetime_str = search(date_format, datetime_str).groups()[0]
                current_timestamp = parse(datetime_str).timestamp()
                if first:
                    first_timestamp = current_timestamp
                    first = False
                else:
                    interval = current_timestamp-previous_timestamp
                    timestamp_list.append(current_timestamp-previous_timestamp)
                previous_timestamp = current_timestamp
            elif self._check_message(pcap_packets[index], stop_message):
                break

            index += 1
        if not msg_found:
            return False
        print(current_timestamp - first_timestamp)
        print(timestamp_list)
        for _interval in timestamp_list:
            if _interval > int(time_interval):
                sc_log.console(f"time interval is greater, expected:{time_interval},  observed:{interval}")
                return
        sc_log.console(f"time_interval list between packets: {timestamp_list}")
        return True

    def verify_parameter(self, pcap_packets: list = None, message: dict = None, parameter=None, expected_value=None):
        for message in pcap_packets:
            self._verify_values(None, message, parameter, expected_value)

    def _verify_values(self, message_key, message_value, parameter, expected_value):
        try:
            if isinstance(message_value, dict):
                for _key, _value in message_value.items():
                    self._verify_values(_key, _value, parameter, expected_value)
            else:
                if parameter == message_key and message_value == expected_value:
                    sc_log.console(f"Value matches")
                    return True
        except AttributeError:
            print("Attribute error")
            return False

    @staticmethod
    def _check_message(pkt_msg, msg2):
        try:
            for msg in pkt_msg.values():
                for val in msg.values():
                    if isinstance(val, dict):
                        if msg2.items() <= val.items():
                            return True
            return False

        except AttributeError:
            print("Attribute error")
            return False

    @staticmethod
    def _check_condition(condition, count, read_filter, pcap_filename):
        if not eval(f"{count}{condition}"):
            sc_log.console(f"Found {count} packet(s) instead of {condition} packet(s) matching {read_filter} in {pcap_filename}.")
            return False
        else:
            sc_log.console(
                f"Found {count} packet(s) for {read_filter} in {pcap_filename}.")
            return True


if __name__ == "__main__":
    r = PcapAnalyser()
    packets = r.get_packet_info("C:\\users\\nipur\\downloads\\wireshark_parsing_tool\\wireshark_parsing_tool\\silentcall.pcapng",
                                read_filter='(fxl-5.0.0.msgType)',
                                dual_pass=True, protocol="fxl-5.0.0")
    r.verify_parameter(packets,'fxl-5.0.0.rsrp','-13.2185')
    message_list = [{'fxl-5.0.0.msgType': '409'}, {'fxl-5.0.0.msgType': '413'}, {'fxl-5.0.0.msgType': '405'}]
    #message_list = [{'fxl-5.0.0.msgType': '111'},{'fxl-5.0.0.msgType': '111'}]
    r.verify_msg(message_list,"C:\\users\\nipur\\downloads\\wireshark_parsing_tool\\wireshark_parsing_tool\\silentcall.pcapng",
                                read_filter='(fxl-5.0.0.msgType)', protocol="fxl-5.0.0")
    #r.check_timing(packets, {"fxl-5.0.0.msgType": '413'}, start_message={"fxl-5.0.0.msgType": '409'},stop_message={"fxl-5.0.0.msgType": '405'})
