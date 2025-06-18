KEYPOINT_ORDER = [
    'Pelvis', 'Left hip', 'Left knee', 'Left foot',
    'Right  hip', 'Right knee', 'Right foot',
    'Spine naval', 'Spine chest', 'Neck base', 'Center head',
    'Right shoulder', 'Right elbow', 'Right hand',
    'Left shoulder', 'Left elbow', 'Left hand'
]

ACTIONS = ['abandon', 'broken', 'theft', 'normal']
SPLITS = ['train', 'val']
NUM_KEYPOINTS = len(KEYPOINT_ORDER)