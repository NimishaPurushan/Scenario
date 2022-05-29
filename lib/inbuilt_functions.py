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

    def tshark_validate(self, pcap_filename: str = None, read_filter: str = None,
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
        tshark_parse_command = f'tshark.exe -r {pcap_filename} {dual_pass} -R "{read_filter}" -T json'
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

    def verify_order(self, message_info, pcap_filename: str = None, read_filter: str = None,
                     dual_pass=True, protocol: str = None):
        packets = self.tshark_validate(pcap_filename=pcap_filename, read_filter=read_filter, dual_pass=True,
                                       protocol=protocol)
        index = 0
        # print("message_info",message_info)
        for msg in eval(message_info):
            # print("msg",msg)
            msg_found = False
            while index <= len(packets):
                if self._check_message(packets[index], msg):
                    index += 1
                    msg_found = True
                    break
            if not msg_found:
                return False
        return True

    def check_timing(self, pcap_packets, message, start_message, stop_message):
        index = 0
        msg_found = False
        date_format = r"((.*?)\d+:\d+:\d+.\d+)"
        first = True
        #print(pcap_packets)
        timestamp_list = []
        previous_timestamp = 0
        current_timestamp = 0
        first_timestamp = 0
        start = False
        stop = True
        print(type(pcap_packets))
        print(type(message))
        print(start_message, type(start_message))
        print(stop_message, type(stop_message))
        while index < len(pcap_packets):
            if not start:
                print("came here")
                if self._check_message(pcap_packets[index], start_message):
                    start = True
                index += 1
                continue
            print("index", index)
            if self._check_message(pcap_packets[index], message):
                msg_found = True
                datetime_str = list(pcap_packets[index].keys())[0]
                datetime_str = search(date_format, datetime_str).groups()[0]
                current_timestamp = parse(datetime_str).timestamp()
                print(current_timestamp)
                if first:
                    first_timestamp = current_timestamp
                    first = False
                else:
                    timestamp_list.append(current_timestamp-previous_timestamp)
                previous_timestamp = current_timestamp
            elif self._check_message(pcap_packets[index], stop_message):
                break

            index += 1
        if not msg_found:
            return False
        print(current_timestamp - first_timestamp)
        print(timestamp_list)

    @staticmethod
    def _check_message(pkt_msg, msg2):
        try:
            for msg in pkt_msg.values():
                for val in msg.values():
                    if isinstance(val, dict):
                        if msg2.items() <= val.items():
                            print("PACKET FOUND")
                            print(val.items())
                            return True
            return False

        except AttributeError:
            print("Attribute error")
            exit()
            return False


if __name__ == "__main__":
    r = PcapAnalyser("", "C:\\Program Files\\Wireshark")
    packets = r.tshark_validate("C:\\users\\nipur\\downloads\\wireshark_parsing_tool\\wireshark_parsing_tool\\silentcall.pcapng",
                                read_filter='(fxl-5.0.0.msgType)',
                                dual_pass=True, protocol="fxl-5.0.0")
    r.check_timing(packets, {"fxl-5.0.0.msgType": '413'}, start_message={"fxl-5.0.0.msgType": '409'},stop_message={"fxl-5.0.0.msgType": '405'})
