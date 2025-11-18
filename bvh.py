# BVH string constants
HIERARCHY = "HIERARCHY"
ROOT = "ROOT"
OFFSET = "OFFSET"
CHANNELS = "CHANNELS"
JOINT = "JOINT"
ENDSITE = "End Site"
MOTION = "MOTION"
FRAMES = "Frames:"
FRAME_TIME = "Frame Time:"
XPOSITION = "Xposition"
YPOSITION = "Yposition"
ZPOSITION = "Zposition"
XROTATION = "Xrotation"
YROTATION = "Yrotation"
ZROTATION = "Zrotation"


class BVHNode:
    def __init__(self, name):
        self.name = name
        self.offset = []
        self.num_channels = 0
        self.channel_keys = []
        self.channel_values = []
        self.childs = []

    def parse(self, lines, line_idx):
        while line_idx < len(lines):
            line = lines[line_idx]
            line_idx += 1
            if line.startswith("{"):
                continue
            elif line.startswith(OFFSET):
                self.offset = list(map(float, line.split()[1:4]))
            elif line.startswith(CHANNELS):
                self.channel_keys = line.split()[2:]
                self.num_channels = len(self.channel_keys)
                self.channel_values = [[] for _ in range(self.num_channels)]
            elif line.startswith(JOINT) or line.startswith(ENDSITE):
                joint_name = line.split()[1] if line.startswith(JOINT) else ENDSITE
                child = BVHNode(joint_name)
                line_idx = child.parse(lines, line_idx)
                self.childs.append(child)
            elif line.startswith("}"):
                # End of this node's definition
                return line_idx

        # ERROR: Should be returned before reaching here
        assert False, "BVH parsing error: no closing brace found for node"

    def append_channel_values(self, channel_values, idx):
        for channel_idx in range(self.num_channels):
            self.channel_values[channel_idx].append(channel_values[idx + channel_idx])
        idx = idx + self.num_channels
        for child in self.childs:
            idx = child.append_channel_values(channel_values, idx)
        return idx

    def print(self, indent=0):
        name = " " * indent + self.name
        offset = " ".join(f"{x:8.3f}" for x in self.offset)
        channels = " ".join(self.channel_keys)
        print(f"{name:20s}    {offset}    {channels}")
        for child in self.childs:
            child.print(indent + 1)


class BVH:
    def __init__(self, filepath):
        self.root: BVHNode
        self.frames: int
        self.frame_time: float

        with open(filepath, "r") as files:
            lines = [line.strip() for line in files.readlines()]

        line_idx = 0
        while line_idx < len(lines):
            line = lines[line_idx]
            line_idx += 1
            if line.startswith(HIERARCHY):
                line_idx = self.parse_hierarchy(lines, line_idx)
            elif line.startswith(MOTION):
                line_idx = self.parse_motion(lines, line_idx)

    def parse_hierarchy(self, lines, line_idx):
        while line_idx < len(lines):
            line = lines[line_idx]
            line_idx += 1
            if line.startswith(ROOT):
                root_name = line.split()[1]
                self.root = BVHNode(root_name)
                line_idx = self.root.parse(lines, line_idx)
                return line_idx

        # ERROR: Should be returned before reaching here
        assert False, "BVH parsing error: no ROOT found in HIERARCHY"

    def parse_motion(self, lines, line_idx):
        while line_idx < len(lines):
            line = lines[line_idx]
            line_idx += 1
            if line.startswith(FRAMES):
                self.frames = int(line.split()[1])
            elif line.startswith(FRAME_TIME):
                self.frame_time = float(line.split()[2])
            else:
                # Motion data lines
                values = list(map(float, line.split()))
                self.root.append_channel_values(values, idx=0)

        return line_idx

    def print(self):
        print(f"Frames: {self.frames}, Frame Time: {self.frame_time}, Hierarchy:")
        self.root.print()
