#!/usr/bin/env python3
"""
The MIT License (MIT)

Copyright (c) 2020 NVIDIA Corporation

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
import sys
import json
import h5py
import trimesh
from pathlib import Path
import argparse
import numpy as np
import trimesh.path
from shapely.geometry import Point
import multiprocessing as mp
import math
import os
import time
import random
from tqdm import tqdm

from acronym_tools import Scene, load_mesh, load_grasps, create_gripper_marker

json_file_root = '../data/json_output/textured'


def make_parser():
    parser = argparse.ArgumentParser(
        description="Generate a random scene arrangement and filtering grasps that are in collision.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--objects_json", required=True,  help="HDF5 or JSON Object file(s).")
    parser.add_argument(
        "--support",
        required=True,
        type=str,
        help="HDF5 or JSON File for support object.",
    )
    # parser.add_argument("--num_object_per_scene", required=True, type=int, help="Number of objects per scene")
    parser.add_argument(
        "--support_scale", default=1.0, help="Scale factor of support mesh."
    )
    parser.add_argument(
        "--multiprocessing",
        action="store_true",
        help="Processing with multi thread.",
    )
    parser.add_argument(
        "--num_scenes",
        default=10,
        help="Number of scenes to create."
    )

    parser.add_argument(
        "--show_grasps",
        action="store_true",
        help="Show all grasps that are not in collision.",
    )
    # parser.add_argument(
    #     "--mesh_root", default=".", help="Directory used for loading meshes."
    # )
    parser.add_argument(
        "--num_grasps_per_object",
        default=20,
        help="Maximum number of grasps to show per object.",
    )
    return parser


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)


def save_object_poses_of_one_scene(pose_dict, path_dict, scene_id):
    json_file = os.path.join(json_file_root, 'scene_{:05d}.json'.format(scene_id))
    data_dict = {}
    for key in pose_dict:
        data_dict[key] = {}
        data_dict[key]['pose'] = pose_dict[key]
        data_dict[key]['path'] = path_dict[key]
    with open(json_file, 'w') as f:
        json.dump(data_dict, f, sort_keys=True, cls=NumpyEncoder, indent=4)

    # with open(json_file_name, 'w') as f:
    #     poses_dict['scene_{}'.format(secne_id)] = pose_dict
    #     json.dump(poses_dict, f, sort_keys=True, cls=NumpyEncoder, indent=4)
    #     f.close()


create_sence_call_num = 0
num_placed = 0
'''create a scene, the objects were chosen in order of objects meshes list
'''
def create_scene(object_meshes, support_mesh, object_names):
    # sample random number of objects to place
    # normal distribution, sigma=2.5, mu=5
    min_objects = 2
    max_objects = 9
    num_objects = min(max(math.ceil(2.5 * np.random.randn() + 5), min_objects), max_objects)
    global create_sence_call_num
    global num_placed
    object_name_group = object_names[num_placed:min(num_placed + num_objects, len(object_meshes))]
    object_group = object_meshes[num_placed:min(num_placed + num_objects, len(object_meshes))]
    scene = Scene.random_arrangement(object_group, support_mesh, object_name_group)
    print("Place {} objects in scene {}".format(min(num_objects, len(object_meshes) - num_placed), create_sence_call_num))
    # print("objects poses: {}".format(scene._poses))
    save_object_poses_of_one_scene(scene._poses, create_sence_call_num)
    # scene.colorize().as_trimesh_scene().show()
    # scene.as_trimesh_scene().show()
    create_sence_call_num += 1
    num_placed += num_objects
    return scene


'''create a scene, the objects were chosen in objects meshes list randomly
'''
def create_scene_random(object_meshes, support_mesh, object_names, object_paths, support_path, scene_idx):
    np.random.seed(scene_idx)
    min_objects = 2
    max_objects = 9
    # sample random number of objects to place
    # normal distribution, sigma=2.5, mu=5
    num_objects = min(max(math.ceil(2.5 * np.random.randn() + 5), min_objects), max_objects)
    index = np.arange(len(object_meshes), dtype=np.int32)
    chosen_index = np.random.choice(index, size=num_objects, replace=False)
    object_name_group = [(object_names[i]) for i in chosen_index]
    object_mesh_group = [(object_meshes[i]) for i in chosen_index]
    scene = Scene.random_arrangement(object_mesh_group, support_mesh, object_name_group)
    # print("Place {} objects in scene {}".format(min(num_objects, len(object_meshes) - num_placed), create_sence_call_num))
    # print("objects poses: {}".format(scene._poses))
    chosen_object_path_dict = {}
    for i in chosen_index:
        chosen_object_path_dict[object_names[i]] = object_paths[i]
    chosen_object_path_dict['support_object'] = support_path
    save_object_poses_of_one_scene(scene._poses, chosen_object_path_dict, scene_idx)
    scene.as_trimesh_scene().show()
    return scene


def main(argv=sys.argv[1:]):
    parser = make_parser()
    args = parser.parse_args(argv)

    # load object meshes
    object_meshes, object_names = load_mesh(args.objects_json)
    support_mesh, support_name = load_mesh(
        args.support, scale=args.support_scale
    )
    support_mesh = support_mesh[0]
    support_name = support_name[0]
    # print('names: {}'.format(object_names))
    # print('support {} name {}'.format(support_mesh, support_name))

    # num_scene = math.ceil(len(object_meshes) // args.num_object_per_scene)
    # print("Creating {} scenes...".format(num_scene))
    # if os.path.exists(json_file_name):
    #     os.remove(json_file_name)
    global num_placed
    pool = None
    if args.multiprocessing:
        pool = mp.Pool(mp.cpu_count())
    # print("num_scenes", int(args.num_scenes))
    # condition = (int(args.num_scenes) - create_sence_call_num * mp.cpu_count() > 0) if args.multiprocessing else (len(object_meshes) - num_placed > 0)
    # count = 0
    # while (int(args.num_scenes) - create_sence_call_num * mp.cpu_count() > 0) if args.multiprocessing else (len(object_meshes) - num_placed > 0):
    num_scene = 5000
    for i in range(num_scene):


        if args.multiprocessing:
            pool.apply_async(create_scene_random, args=(object_meshes, support_mesh, object_names, i))
        else:
            # scene = create_scene(object_meshes, support_mesh, num_objects, object_names)
            scene = create_scene_random(object_meshes, support_mesh, object_names, i)
        # # show the random scene in 3D viewer
        # scene.colorize().as_trimesh_scene().show()
        # condition = (int(args.num_scenes) - create_sence_call_num * mp.cpu_count() > 0) if args.multiprocessing else (
        #             len(object_meshes) - num_placed > 0)


    if args.multiprocessing:
        pool.close()
        pool.join()

    if args.show_grasps:
        # load gripper mesh for collision check
        gripper_mesh = trimesh.load(
            Path(__file__).parent.parent / "data/franka_gripper_collision_mesh.stl"
        )
        gripper_markers = []
        for i, fname in enumerate(args.objects_json):
            T, success = load_grasps(fname)
            obj_pose = scene._poses["obj{}".format(i)]

            # check collisions
            collision_free = np.array(
                [
                    i
                    for i, t in enumerate(T[success == 1][: args.num_grasps_per_object])
                    if not scene.in_collision_with(
                        gripper_mesh, transform=np.dot(obj_pose, t)
                    )
                ]
            )

            if len(collision_free) == 0:
                continue

            # add a gripper marker for every collision free grasp
            gripper_markers.extend(
                [
                    create_gripper_marker(color=[0, 255, 0]).apply_transform(
                        np.dot(obj_pose, t)
                    )
                    for t in T[success == 1][collision_free]
                ]
            )

        # show scene together with successful and collision-free grasps of all objects
        trimesh.scene.scene.append_scenes(
            [scene.colorize().as_trimesh_scene(), trimesh.Scene(gripper_markers)]
        ).show()


if __name__ == "__main__":
    main()
