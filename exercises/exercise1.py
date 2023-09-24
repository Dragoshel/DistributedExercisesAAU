from emulators.Device import Device
from emulators.Medium import Medium
from emulators.MessageStub import MessageStub

from random import randrange

import time

class GossipMessage(MessageStub):

    def __init__(self, sender: int, destination: int, secrets):
        super().__init__(sender, destination)
        # we use a set to keep the "secrets" here
        self.secrets = secrets

    def __str__(self):
        return f'{self.source} -> {self.destination} : {self.secrets}'

class GossipScenario2(Device):
    def __init__(self, index, num_devices, medium):
        super().__init__(index, num_devices, medium)
        self._secrets = set([index])

    def run(self):
        while len(self._secrets) < self.number_of_devices():
            right = (self.index() + 1) % self.number_of_devices()
            self.medium().send(GossipMessage(self.index(), right, self._secrets))

            message = self.medium().receive()
            if message is None:
                self.medium().wait_for_next_round()
                continue

            self._secrets.update(message.secrets)

            self.medium().wait_for_next_round()

    def print_result(self):
        print(f'\tDevice {self.index()} got secrets: {self._secrets}')

class GossipScenario1(Device):
    def __init__(self, index: int, number_of_devices: int, medium: Medium):
        super().__init__(index, number_of_devices, medium)
        self._secrets = set([index])

    def run(self):
        for i in range(self.number_of_devices()):
            self.medium().send(GossipMessage(self.index(), i, self.index()))

        while len(self._secrets) < self.number_of_devices():
            message = self.medium().receive()
            if message is None:
                self.medium().wait_for_next_round()
                continue

            self._secrets.add(message.secrets)

            self.medium().wait_for_next_round()


    def print_result(self):
        print(f'\tDevice {self.index()} got secrets: {self._secrets}')


class Gossip(Device):

    def __init__(self, index: int, number_of_devices: int, medium: Medium):
        super().__init__(index, number_of_devices, medium)
        # for this exercise we use the index as the "secret", but it could have been a new routing-table (for instance)
        # or sharing of all the public keys in a cryptographic system
        self._secrets = set([index])

    def run(self):
        # we send a message to the last device in the network unless we are the last device
        if self.index() < self.number_of_devices() - 1:
            self.medium().send(GossipMessage(
                self.index(), self.number_of_devices() - 1, self._secrets))

        # we wait for a message
        while True:
            message = self.medium().receive()
            if message is None:
                self.medium().wait_for_next_round()
                continue

            # we add the secrets from the message to our own set
            self._secrets.update(message.secrets)

            # if we are the last device, we wait until we have all the secrets then we send it to everyone else
            if self.index() == self.number_of_devices() - 1:
                if len(self._secrets) == self.number_of_devices():
                    for i in range(self.number_of_devices()):
                        if i != self.index():
                            self.medium().send(GossipMessage(self.index(), i, self._secrets))
                    break

            # if we are not then we wait for the secrets
            if len(self._secrets) == self.number_of_devices():
                break
            self.medium().wait_for_next_round()

        return

    def print_result(self):
        print(f'\tDevice {self.index()} got secrets: {self._secrets}')
