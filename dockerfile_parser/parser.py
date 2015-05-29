import json
import hashlib
import random

import filters

from collections import OrderedDict

_INSTRUCTIONS = ['FROM',
                 'MAINTAINER',
                 'RUN',
                 'CMD',
                 'LABEL',
                 'EXPOSE',
                 'ENV',
                 'ADD',
                 'COPY',
                 'ENTRYPOINT',
                 'VOLUME',
                 'USER',
                 'WORKDIR',
                 'ONBUILD']


def _hash_image_name(name):
    """
    Create fake `CONTAINER ID`
    """

    return hashlib.md5(name + str(random.randint(100, 200))).hexdigest()[12:]


def _get_dist_name(commands):
    """
    Get the first name of the operating system
    """

    for command in commands:
        line = [command.strip() for command in command.split(' ')]
        if len(line):
            if line[0] == 'FROM':
                return _hash_image_name(line[-1])

    return False


def _parse_raw_dockerfile(lines):
    """
    Author: Michal Papierski <michal@papierski.net>
    https://github.com/mpapierski/dockerfile-parser
    """

    result, current_line = [], []
    for line in lines:
        if line.startswith('#') or not line.strip():
            continue
        current_line.append(line)
        if line.rstrip()[-1] != '\\':
            result.append(''.join(current_line))
            current_line = []

    return result


def _to_commands(path):
    """
    Split dockerfile-file on the instructions
    """

    with open(path) as f:
        commands = _parse_raw_dockerfile(f.read().splitlines())

    return commands


def parse(file_or_cmds, onbuid=False, with_container_id=False):
    """
    Getting the structure Dockerfile
    """

    commands = file_or_cmds if onbuid else _to_commands(file_or_cmds)
    image = _get_dist_name(commands)

    workdir, first, user, data, onbuild_lines = '/', True, 'root', \
                                                OrderedDict(), []
    for command in commands:
        if with_container_id:
            if image not in data:
                data[image] = OrderedDict()

            if not onbuid:
                if 'workdir' not in data[image]:
                    data[image]['workdir'] = OrderedDict()

                if workdir not in data[image]['workdir']:
                    data[image]['workdir'][workdir] = OrderedDict()

                if user not in data[image]['workdir'][workdir]:
                    data[image]['workdir'][workdir][user] = OrderedDict()

            struct = data[image]
        else:
            if not onbuid:
                if 'workdir' not in data:
                    data['workdir'] = OrderedDict()

                if workdir not in data['workdir']:
                    data['workdir'][workdir] = OrderedDict()

                if user not in data['workdir'][workdir]:
                    data['workdir'][workdir][user] = OrderedDict()

            struct = data

        if onbuid:
            udata = struct
        else:
            udata = struct['workdir'][workdir][user]
        split = [v for v in command.split() if len(v)]

        instr, value = split[0].upper(), ' '.join(split[1:]).strip()
        if instr not in _INSTRUCTIONS:
            break

        if instr == 'FROM':
            if with_container_id and not first:
                image = _hash_image_name(value)
                data[image] = OrderedDict()
                data[image]['from'] = filters.from_filter(value)
            else:
                first = False
                struct['from'] = filters.from_filter(value)
        elif instr == 'MAINTAINER':
            struct['maintainer'] = filters.maintainer_filter(value)
        elif instr == 'RUN':
            if 'run' not in udata:
                udata['run'] = []
            udata['run'] = filters.run_filter(udata['run'], value)
        elif instr == 'CMD':
            if 'cmd' not in udata:
                udata['cmd'] = []
            udata['cmd'] = filters.cmd_filter(udata['cmd'], value)
        elif instr == 'LABEL':
            if 'label' not in struct:
                struct['label'] = OrderedDict()
            struct['label'] = filters.label_filter(struct['label'], value)
        elif instr == 'EXPOSE':
            if 'expose' not in struct:
                struct['expose'] = []
            struct['expose'] = filters.expose_filter(struct['expose'], value)
        elif instr == 'ENV':
            if 'env' not in struct:
                struct['env'] = OrderedDict()
            struct['env'] = filters.env_filter(struct['env'], value)
        elif instr == 'ADD':
            if 'add' not in udata:
                udata['add'] = []
            udata['add'] = filters.add_filter(udata['add'], value)
        elif instr == 'COPY':
            if 'copy' not in udata:
                udata['copy'] = []
            udata['copy'] = filters.copy_filter(udata['copy'], value)
        elif instr == 'ENTRYPOINT':
            udata['entrypoint'] = filters.entrypoint_filter(value)
        elif instr == 'VOLUME':
            if 'volume' not in struct:
                struct['volume'] = []
            struct['volume'] = filters.volume_filter(struct['volume'], value)
        elif instr == 'USER':
            user = value
        elif instr == 'WORKDIR':
            workdir = value
        elif instr == 'ONBUILD':
            onbuild_lines.append(value)

        if len(onbuild_lines):
            struct['onbuild'] = parse(
                onbuild_lines, onbuid=True, with_container_id=False)

    return data


if __name__ == '__main__':
    parsed = parse('../Dockerfile')
    print(json.dumps(parsed, indent=2, separators=(',', ': ')))
