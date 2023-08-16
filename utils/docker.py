import logging
import re
import json

import aiodocker
from utils.decoders import read_stream_as_string
from utils.exceptions import UnexpectedOutput


class BaseCommandOutputParser:
    def __init__(self, command_output):
        self.command_output = command_output


class MinecraftCommandOutputParser(BaseCommandOutputParser):
    def get_online_stats(self):
        message = self.command_output
        
        pattern1 = r"There are (\d+) of a max of (\d+) players online:(.*)"
        pattern2 = r"There are (\d+)/(\d+) players online:(.*)"

        match1 = re.match(pattern1, message)
        if match1:
            num_online = int(match1.group(1))
            server_max_size = int(match1.group(2))
            player_names = match1.group(3).split(", ")
            return num_online, server_max_size, [p for p in player_names if p]

        match2 = re.match(pattern2, message)
        if match2:
            num_online = int(match2.group(1))
            server_max_size = int(match2.group(2))
            player_names = match2.group(3).split(", ")
            return num_online, server_max_size, [p for p in player_names if p]

        raise UnexpectedOutput(message)

    def check_say(self):
        message = self.command_output.replace("\n", "")
        if message != "":
            raise UnexpectedOutput(self.command_output)


class BaseContainerManager:
    def __init__(self, container_name, client=None):
        self.container_name = container_name
        self.client = client

        if self.client is None:
            self.client = aiodocker.Docker()

        self.container = None

    async def get_container(self):
        if self.container:
            return self.container
        containers = await self.client.containers.list()
        containers = [c for c in containers if str(c["Names"][0].lstrip('/')).startswith(self.container_name)]
        if len(containers) < 1:
            raise ValueError(f"No container that match container name {self.container_name}")
        return containers[0]

    async def exec(self, command):
        container = await self.get_container()
        exec_object = await container.exec(command.replace("'", "\\'").replace('"', '\\"'))
        stream = exec_object.start()
        command_output = await read_stream_as_string(stream)
        return command_output


class MinecraftContainerManager(BaseContainerManager):
    async def exec_rcon(self, command):
        return await self.exec("rcon-cli " + command)

    async def get_online_stats(self):
        command = "list"
        command_output = await self.exec_rcon(command)
        parser = MinecraftCommandOutputParser(command_output)
        parsed_info = parser.get_online_stats()
        return parsed_info

    async def tell(self, message):
        command = "say " + message
        command_output = await self.exec_rcon(command)
        parser = MinecraftCommandOutputParser(command_output)
        parser.check_say()
