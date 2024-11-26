import re
import bpy
import math

# path to your replay file
# probably ends with something like "replays/<DATE> <MAP_NAME>.rpl"
replay = r""

# how long the replay is
# this length is shown when you open the replay in game
# this should be able to be extracted from the replay file, but I haven't found how to do that
duration = 0

# the directory for beamNG
# is probably something like "C:\Users\<NAME>\AppData\Local\BeamNG.drive\<VERSION>\\"
folder = r""



# Interpolate between two angles, taking into account wrapping.
def interpolate_angles(angle1, angle2, steps):
    # Calculate the difference
    delta = angle2 - angle1
    
    # Wrap delta to be within -π to π
    if delta > math.pi:
        delta -= 2 * math.pi
    elif delta < -math.pi:
        delta += 2 * math.pi
    
    # Generate interpolated values
    interpolated_angles = [angle1 + (delta * t / (steps - 1)) for t in range(steps)]
    normalized_interpolated_angles = [math.atan2(math.sin(angle), math.cos(angle)) for angle in interpolated_angles]
    return normalized_interpolated_angles



cube = "Cube"
cubeObj = bpy.data.objects.get(cube)
posLast = [0, 0, 0]
rotLast = [0, 0, 0]
frameLast = 0

path = folder + replay
print(f"Importing from {path}")

#duration = 10.234
fps = bpy.context.scene.render.fps
f = open(path, "rb")


frame = 0

#count number of frames
for line in f:
    line = str(line)
    if "position" in line:
        frame += 1
print(f"{frame} frames")

rate = fps/(frame/duration)

frame = 0
f.seek(0)

i = 0
for line in f:
    line = str(line)
    
    position = re.search(r"\"position\":{\"y\":([-.e0-9]+),\"z\":([-.e0-9]+),\"x\":([-.e0-9]+)},", line)
    rotation = re.search(r"\"roll\":([-.e0-9]+).*\"pitch\":([-.e0-9]+).*\"yaw\":([-.e0-9]+)", line)
    
    if position and rotation:
        thisFrame = round(frame)
        
        y = float(position.group(1))
        z = float(position.group(2))
        x = float(position.group(3))
        
        cubeObj.location = [x, y, z]
        if x != posLast[0]:
            cubeObj.keyframe_insert(data_path="location", index=0, frame = thisFrame)
        if x != posLast[0]:
            cubeObj.keyframe_insert(data_path="location", index=1, frame = thisFrame)
        if x != posLast[0]:
            cubeObj.keyframe_insert(data_path="location", index=2, frame = thisFrame)
        
        posLast = [x, y, z]


        roll  = float(rotation.group(1))
        pitch = float(rotation.group(2))
        yaw   = float(rotation.group(3))
        cubeObj.rotation_euler = [roll, pitch, yaw]
        
        if roll != rotLast[0]:
            cubeObj.keyframe_insert(data_path="rotation_euler", index=0, frame=thisFrame)
        if pitch != rotLast[1]:
            cubeObj.keyframe_insert(data_path="rotation_euler", index=1, frame=thisFrame)
        if yaw != rotLast[2]:
            cubeObj.keyframe_insert(data_path="rotation_euler", index=2, frame=thisFrame)
#            correct if rotation jumps from ~ -pi to +pi
            if thisFrame-frameLast > 1 and abs(yaw-rotLast[2]) > math.radians(180):
                interpolation = interpolate_angles(rotLast[2], yaw, thisFrame-frameLast+1)
                cubeObj.rotation_euler = [roll, pitch, interpolation[len(interpolation)-2]]
                cubeObj.keyframe_insert(data_path="rotation_euler", index=2, frame=thisFrame-1)
                print(f"{thisFrame}: {interpolation}")

            frameLast = thisFrame
        
        rotLast = [roll, pitch, yaw]
        frame +=rate
    i+=1

bpy.context.scene.frame_end = round(frame)
print(f"Frame Rate: {frame/duration} fps")
print(f"Num Frames: {frame}")
# print("\n")
