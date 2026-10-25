"""Read eye tracks from the installed OpenGOAL exporter's labelled word dump.

The dump stays private. Layout references: art-h.gc art-joint-anim and merc-h.gc
merc-eye-anim-block/merc-eye-anim-frame; shader equations in eye.gc render-eyes.
"""
import re
import struct
from pathlib import Path


class Words:
    def __init__(self, path: Path):
        self.words, self.labels = [], {}
        for line in path.read_text(encoding='utf-8').splitlines():
            if line.startswith('L'):
                match = re.fullmatch(r'(L\d+):(?: \(offset (\d)\))?', line)
                if not match:
                    raise ValueError(f'Unknown dump label: {line}')
                self.labels[match[1]] = len(self.words) * 4 + int(match[2] or 0)
            elif line.lstrip().startswith(('.word ', '.type ', '.symbol ')):
                self.words.append(tuple(line.strip().split(' ', 1)))

    def pointer(self, word):
        directive, label = self.words[word]
        if directive != '.word' or label not in self.labels:
            raise ValueError(f'Expected linked data pointer at word {word}')
        return self.labels[label]

    def bytes(self, offset, size):
        first, last = offset // 4, (offset + size + 3) // 4
        words = self.words[first:last]
        if any(kind != '.word' or not value.startswith('0x') for kind, value in words):
            raise ValueError('Eye data overlaps relocated pointer or type information')
        return b''.join(struct.pack('<I', int(value, 16)) for _, value in words)[offset % 4:][:size]

    def string(self, word):
        offset = self.pointer(word)
        size = struct.unpack('<I', self.bytes(offset, 4))[0]
        if not 0 < size < 256:
            raise ValueError('Invalid animation name length')
        return self.bytes(offset + 4, size).decode('utf-8')


def tracks(path: Path):
    data = Words(path)
    result = {}
    for i, word in enumerate(data.words):
        if word != ('.type', 'art-joint-anim'):
            continue
        name = data.string(i + 2)
        if data.words[i + 1] == ('.symbol', '#f'):
            continue
        offset = data.pointer(i + 1)
        count = struct.unpack('<h', data.bytes(offset, 2))[0] + 1
        if not 1 <= count <= 10000:
            raise ValueError(f'{name}: invalid eye frame count')
        raw = data.bytes(offset + 8, count * 16)
        frames = []
        for frame in range(count):
            pair = {}
            for side, extra in (('left', 0), ('right', 8)):
                values = struct.unpack_from('<3bB4B', raw, frame * 16 + extra)
                pair[side] = dict(zip(('x', 'y', 'lid', 'reserved', 'iris_scale',
                                      'pupil_scale', 'lid_scale', 'reserved2'), values))
            frames.append(pair)
        result[name] = frames
    return result
