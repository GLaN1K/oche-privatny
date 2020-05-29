#!/usr/bin/env python3

import signal
import os
import time
import sys

class SignalTransport(object):
    def __init__(self):
        self._high = 31
        self._low = 30
        self._control = 28

        self._handshaked = False

class SignalSender(SignalTransport):

    def __init__(self, receiver_pid):

        super().__init__()

        self._receiver_pid = receiver_pid
        self._ready = False


    def _receive_confirmation(self, *_):
        self._ready = True

    def _receive_handshake(self, *_):
        self._handshaked = True
        signal.signal(self._control, self._receive_confirmation)

    def _do_handshake(self):

        signal.signal(self._control, self._receive_handshake)

        pid = os.getpid()

        encoded_message = self._encode_message(pid)
        self._do_transaction(encoded_message)


    @staticmethod
    def _encode_message(message):
        message = str(message)
        message_bytes = bin(int.from_bytes(message.encode(sys.getdefaultencoding()), sys.byteorder))[2:]
        message_bytes = message_bytes.zfill(8 * ((len(message_bytes) + 7) // 8))

        return message_bytes

    def _do_transaction(self, encoded_message):

#       print("Encoded message: {}".format(encoded_message))
#        print("Timestamp in MS: {}".format(int(round(time.time() * 1000))))

        print("Timestamp in MS: {}".format(int(round(time.time() * 1000))))

        for bit in encoded_message:

            self._wait_for_ready()

            if self._handshaked:
                self._ready = False

            if bit == "1":
                os.kill(self._receiver_pid, self._high)
            elif bit == "0":
                os.kill(self._receiver_pid, self._low)

        self._wait_for_ready()

        os.kill(self._receiver_pid, self._control)


    def _wait_for_ready(self):
        if self._handshaked:
            while not self._ready:
                pass
        else:
            time.sleep(0.1)

    def send_message(self, message):

        k = self._encode_message(message)

        if not self._handshaked:
            self._do_handshake()

        self._do_transaction(k)

if __name__ == '__main__':

    PID = int(input("Enter reciever PID: "))

    ss = SignalSender(PID)

    while True:
        message = input("Enter your message: ")
        ss.send_message(message)
