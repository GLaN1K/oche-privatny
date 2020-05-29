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


class SignalReciever(SignalTransport):

    def __init__(self):

        super().__init__()

        self._messages = []

        self._buffer = ""

        self.sender_pid = 0

        signal.signal(self._high, self._receive_message)
        signal.signal(self._low, self._receive_message)
        signal.signal(self._control, self._receive_message)

        print("Reciever PID: {}".format(os.getpid()))

    def _receive_message(self, signal, _):

        if signal == self._high:
            self._buffer = self._buffer + "1"
        elif signal == self._low:
            self._buffer = self._buffer + "0"
        
        elif signal == self._control:
            if not self._handshaked:
                self._sender_pid = int(self._decode_message(self._buffer))
                self._handshaked = True
            else:
                self._messages.append(self._buffer)

            self._buffer = ""

        if self._handshaked:
            os.kill(self._sender_pid, self._control)

    @staticmethod
    def _decode_message(encoded_message):
            print("Encoded message: {}".format(encoded_message))
            n = int(encoded_message, 2)
            return n.to_bytes((n.bit_length() + 7) // 8, sys.byteorder).decode(sys.getdefaultencoding()) or '\0'


    def get_last_message(self):
        if self._messages:
            encoded_message = self._messages.pop()
            return self._decode_message(encoded_message)

if __name__ == '__main__':

    sr = SignalReciever()

    while True:
        message = sr.get_last_message()
        if message:
            print("Timestamp in MS: {}".format(int(round(time.time() * 1000))))
            print("Decoded message: {}".format(message))
    input()