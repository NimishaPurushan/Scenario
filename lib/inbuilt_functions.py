from os import path
from os.path import *
from os import remove, rename, chdir
from subprocess import check_output
import subprocess
import json


class PcapAnalyser:

    def __init__(self, pcap_file, tshark_path):
        self.tshark_path = tshark_path

    def check_timing(self):
        pass

    def tshark_validate(self, pcap_filename: str = None, read_filter: str = None,
                        dual_pass=True, protocol: str = None):
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

    @staticmethod
    def _check_message(pkt_msg, msg2):
        # print("pkt_msg",pkt_msg)
        # print("msg",msg2)
        for msg in pkt_msg.values():
            for val in msg.values():
                # print(val,msg2)
                if msg2.items() <= val.items():
                    return True
        return False
