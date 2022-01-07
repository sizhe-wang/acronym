import json
import os
import numpy as np


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)

# # make json for non-textured objects
# src = '/home/wsz/wei_dataset_object_models/dataset/final_dataset/non_textured'
# with open('non_textured_dataset.json', 'w') as f:
#     dataset_dict = {}
#     for root, dirs, files in os.walk(src):
#         for filename in files:
#             if filename.endswith('.obj') and '_vhacd' not in filename:
#                 prefix = filename.split('/')[-1].split('.')[0]
#                 dataset_dict[prefix] = {}
#                 filepath = os.path.join(root, filename)
#                 # filepath = filepath.repalce('/home/wsz/wei_dataset_object_models/dataset/contain_old/', '')
#
#                 dataset_dict[prefix]["filepath"] = filepath
#                 dataset_dict[prefix]["object_scale"] = 1.0
#
#     json.dump(dataset_dict, f, sort_keys=True, cls=NumpyEncoder, indent=4)


# # make json for non-textured vhacd objects
# src = '/home/wsz/wei_dataset_object_models/dataset/final_dataset/non_textured'
# with open('non_textured_dataset_vhacd.json', 'w') as f:
#     dataset_dict = {}
#     for root, dirs, files in os.walk(src):
#         for filename in files:
#             if filename.endswith('_vhacd.obj'):
#                 prefix = filename.split('/')[-1].split('.')[0]
#                 dataset_dict[prefix] = {}
#                 filepath = os.path.join(root, filename)
#                 # filepath = filepath.repalce('/home/wsz/wei_dataset_object_models/dataset/contain_old/', '')
#
#                 dataset_dict[prefix]["filepath"] = filepath
#                 dataset_dict[prefix]["object_scale"] = 1.0
#
#     json.dump(dataset_dict, f, sort_keys=True, cls=NumpyEncoder, indent=4)


# # make json for textured vhacd objects
# src = '/home/wsz/wei_dataset_object_models/dataset/final_dataset/new_textured'
# with open('textured_dataset_vhacd.json', 'w') as f:
#     dataset_dict = {}
#     for root, dirs, files in os.walk(src):
#         for filename in files:
#             # if filename.endswith('.obj') and '_vhacd' not in filename and 'collision' not in filename:
#             if filename.endswith('_vhacd.obj'):# and '_vhacd' not in filename and 'collision' not in filename:
#                 prefix = filename.split('/')[-1].split('.')[0]
#                 dataset_dict[prefix] = {}
#                 filepath = os.path.join(root, filename)
#                 # filepath = filepath.repalce('/home/wsz/wei_dataset_object_models/dataset/contain_old/', '')
#
#                 dataset_dict[prefix]["filepath"] = filepath
#                 dataset_dict[prefix]["object_scale"] = 1.0
#
#     json.dump(dataset_dict, f, sort_keys=True, cls=NumpyEncoder, indent=4)



# make json for textured objects
src = '/home/wsz/wei_dataset_object_models/dataset/final_dataset/new_textured'
with open('textured_dataset.json', 'w') as f:
    dataset_dict = {}
    for root, dirs, files in os.walk(src):
        for filename in files:
            if filename.endswith('.obj') and '_vhacd' not in filename and '_collision' not in filename and '_nontextured' not in filename:
                prefix = filename.split('/')[-1].split('.')[0]
                dataset_dict[prefix] = {}
                filepath = os.path.join(root, filename)
                # filepath = filepath.repalce('/home/wsz/wei_dataset_object_models/dataset/contain_old/', '')

                dataset_dict[prefix]["filepath"] = filepath
                dataset_dict[prefix]["object_scale"] = 1.0

    json.dump(dataset_dict, f, sort_keys=True, cls=NumpyEncoder, indent=4)