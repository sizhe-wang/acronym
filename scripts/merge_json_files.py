import json
import os
import argparse
import sys
import numpy as np


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)


def make_parser():
    parser = argparse.ArgumentParser(
        description="Merge json files into one json file.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "--json_file_root",
        required=True,
        help="The path of root dir."
    )

    parser.add_argument(
        "--json_file_dst",
        required=True,
        help="The path of dir to store new json file."
    )

    parser.add_argument(
        "--json_file_name",
        required=True,
        help="The name of the new json file."
    )
    return parser


def main(argv=sys.argv[1:]):
    parser = make_parser()
    args = parser.parse_args(argv)

    # create new json file to write
    with open(os.path.join(args.json_file_dst, args.json_file_name), 'w') as f:
        data_dict = {}
        for root, dirs, files in os.walk(args.json_file_root):
            for file in files:
                if file.endswith('.json'):
                    filename = file.split('.')[0]
                    with open(os.path.join(root, file), 'r') as ff:
                        data = json.load(fp=ff)
                        data_dict[filename] = data
        json.dump(data_dict, f, sort_keys=True, cls=NumpyEncoder, indent=4)


if __name__ == '__main__':
    main()
