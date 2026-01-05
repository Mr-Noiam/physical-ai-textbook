[TRANSLATION_FAILED] # Week 8: Isaac ROS for VSLAM

[TRANSLATION_FAILED] ## Introduction

[TRANSLATION_FAILED] **Isaac ROS** provides GPU-accelerated perception and navigation packages (GEMs - GPU-Enabled Modules). This week, you'll implement visual SLAM (Simultaneous Localization and Mapping) using **cuVSLAM**, enabling your humanoid to build maps and localize in real-time.

[TRANSLATION_FAILED] ## Isaac ROS Architecture

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│Camera/Sensors│───>│ Isaac ROS    │───>│   cuVSLAM    │
│ (ROS topics) │    │ Pre-process  │    │ (GPU-accel.) │
└──────────────┘    └──────────────┘    └──────────────┘
                                              │
                                              ▼
                                        ┌──────────────┐
                                        │  Map + Pose  │
                                        │  (/tf, /map) │
                                        └──────────────┘
```

[TRANSLATION_FAILED] **Isaac ROS GEMs**:
[TRANSLATION_FAILED] - cuVSLAM: Visual SLAM
[TRANSLATION_FAILED] - DNN Inference: TensorRT for object detection
[TRANSLATION_FAILED] - Image Processing: Stereo disparity, rectification
[TRANSLATION_FAILED] - AprilTag: Fiducial markers

[TRANSLATION_FAILED] ## Installation

[TRANSLATION_FAILED] ### Isaac ROS Prerequisites

```bash
# Install NVIDIA Container Toolkit
distribution=$(. /etc/os-release;echo $ID$VERSION_ID) \
   && curl -s -L https://nvidia.github.io/libnvidia-container/gpgkey | sudo apt-key add - \
   && curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list | sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

sudo apt update && sudo apt install nvidia-docker2
sudo systemctl restart docker

# Test
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi
```

[TRANSLATION_FAILED] ### Isaac ROS Workspace

```bash
# Create workspace
mkdir -p ~/isaac_ros_ws/src
cd ~/isaac_ros_ws/src

# Clone Isaac ROS
git clone --recurse-submodules https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_common.git
git clone --recurse-submodules https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_visual_slam.git
git clone --recurse-submodules https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_image_pipeline.git

# Build (using Isaac ROS Docker)
cd ~/isaac_ros_ws
./src/isaac_ros_common/scripts/run_dev.sh

# Inside container
cd /workspaces/isaac_ros_ws
colcon build --symlink-install
source install/setup.bash
```

[TRANSLATION_FAILED] ## cuVSLAM Setup

[TRANSLATION_FAILED] ### Launch cuVSLAM

```bash
# Terminal 1: Isaac ROS container
cd ~/isaac_ros_ws
./src/isaac_ros_common/scripts/run_dev.sh
source install/setup.bash

# Launch cuVSLAM
ros2 launch isaac_ros_visual_slam isaac_ros_visual_slam.launch.py
```

[TRANSLATION_FAILED] ### Input Topics

[TRANSLATION_FAILED] cuVSLAM requires stereo or RGB-D:

[TRANSLATION_FAILED] - **/stereo_camera/left/image_raw**: Left rectified image
[TRANSLATION_FAILED] - **/stereo_camera/left/camera_info**: Camera calibration
[TRANSLATION_FAILED] - **/stereo_camera/right/image_raw**: Right rectified image
[TRANSLATION_FAILED] - **/stereo_camera/right/camera_info**

[TRANSLATION_FAILED] ## Connecting Isaac Sim Camera

[TRANSLATION_FAILED] ### Isaac Sim: Stereo Camera

```python
from omni.isaac.kit import SimulationApp
simulation_app = SimulationApp({"headless": False})

from omni.isaac.core import World
from omni.isaac.sensor import Camera
import omni.graph.core as og
import numpy as np

# Create world
world = World()

# Left camera
left_camera = Camera(
    prim_path="/World/Humanoid/head/stereo_left",
    position=np.array([0.1, -0.03, 0.15]),
    frequency=30,
    resolution=(640, 480),
)

# Right camera
right_camera = Camera(
    prim_path="/World/Humanoid/head/stereo_right",
    position=np.array([0.1, 0.03, 0.15]),
    frequency=30,
    resolution=(640, 480),
)

# ROS 2 bridge for left camera
keys = og.Controller.Keys
og.Controller.edit(
    {"graph_path": "/StereoGraphLeft", "evaluator_name": "execution"},
    {
        keys.CREATE_NODES: [
            ("OnTick", "omni.graph.action.OnPlaybackTick"),
            ("CreateRP", "omni.isaac.core_nodes.IsaacCreateRenderProduct"),
            ("ROS2Cam", "omni.isaac.ros2_bridge.ROS2CameraHelper"),
        ],
        keys.SET_VALUES: [
            ("CreateRP.inputs:cameraPrim", "/World/Humanoid/head/stereo_left"),
            ("ROS2Cam.inputs:topicName", "stereo_camera/left/image_raw"),
            ("ROS2Cam.inputs:frameId", "stereo_left"),
        ],
        keys.CONNECT: [
            ("OnTick.outputs:tick", "CreateRP.inputs:execIn"),
            ("CreateRP.outputs:execOut", "ROS2Cam.inputs:execIn"),
            ("CreateRP.outputs:renderProductPath", "ROS2Cam.inputs:renderProductPath"),
        ],
    },
)

# Similar for right camera
# ... (repeat for stereo_right)

world.reset()
for i in range(1000):
    world.step(render=True)

simulation_app.close()
```

[TRANSLATION_FAILED] ### Camera Calibration

```yaml
# stereo_left_camera_info.yaml
image_width: 640
image_height: 480
camera_name: stereo_left
camera_matrix:
  rows: 3
  cols: 3
  data: [387.229, 0.0, 320.0,
         0.0, 387.229, 240.0,
         0.0, 0.0, 1.0]
distortion_model: plumb_bob
distortion_coefficients:
  rows: 1
  cols: 5
  data: [0.0, 0.0, 0.0, 0.0, 0.0]
rectification_matrix:
  rows: 3
  cols: 3
  data: [1.0, 0.0, 0.0,
         0.0, 1.0, 0.0,
         0.0, 0.0, 1.0]
projection_matrix:
  rows: 3
  cols: 4
  data: [387.229, 0.0, 320.0, 0.0,
         0.0, 387.229, 240.0, 0.0,
         0.0, 0.0, 1.0, 0.0]
```

[TRANSLATION_FAILED] Publish camera info:

```python
from sensor_msgs.msg import CameraInfo

class CameraInfoPublisher(Node):
    def __init__(self):
        super().__init__('camera_info_publisher')
        self.publisher = self.create_publisher(CameraInfo, 'stereo_camera/left/camera_info', 10)
        self.timer = self.create_timer(1/30, self.publish_info)

        self.info = CameraInfo()
        self.info.width = 640
        self.info.height = 480
        self.info.k = [387.229, 0.0, 320.0, 0.0, 387.229, 240.0, 0.0, 0.0, 1.0]
        # ... (fill in rest)

    def publish_info(self):
        self.info.header.stamp = self.get_clock().now().to_msg()
        self.info.header.frame_id = "stereo_left"
        self.publisher.publish(self.info)
```

[TRANSLATION_FAILED] ## Running cuVSLAM

[TRANSLATION_FAILED] ### Launch File

```python
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        # cuVSLAM node
        Node(
            package='isaac_ros_visual_slam',
            executable='visual_slam_node',
            name='visual_slam',
            parameters=[{
                'enable_rectified_pose': True,
                'denoise_input_images': False,
                'rectified_images': True,
                'enable_debug_mode': False,
                'debug_dump_path': '/tmp/cuvslam',
                'enable_slam_visualization': True,
                'enable_landmarks_view': True,
                'enable_observations_view': True,
                'map_frame': 'map',
                'odom_frame': 'odom',
                'base_frame': 'base_link',
                'input_base_frame': 'camera_frame',
                'img_jitter_threshold_ms': 35.0,
            }],
            remappings=[
                ('stereo_camera/left/image', '/stereo_camera/left/image_raw'),
                ('stereo_camera/left/camera_info', '/stereo_camera/left/camera_info'),
                ('stereo_camera/right/image', '/stereo_camera/right/image_raw'),
                ('stereo_camera/right/camera_info', '/stereo_camera/right/camera_info'),
            ]
        ),

        # RViz visualization
        Node(
            package='rviz2',
            executable='rviz2',
            arguments=['-d', '/path/to/vslam.rviz']
        ),
    ])
```

[TRANSLATION_FAILED] ### Run

```bash
ros2 launch humanoid_navigation cuvslam.launch.py
```

[TRANSLATION_FAILED] ## Output Topics

[TRANSLATION_FAILED] cuVSLAM publishes:

[TRANSLATION_FAILED] - **/visual_slam/tracking/odometry**: Visual odometry (nav_msgs/Odometry)
[TRANSLATION_FAILED] - **/visual_slam/tracking/vo_pose**: Pose estimate (geometry_msgs/PoseStamped)
[TRANSLATION_FAILED] - **/visual_slam/tracking/slam_path**: Robot trajectory (nav_msgs/Path)
[TRANSLATION_FAILED] - **/visual_slam/vis/landmarks_cloud**: 3D map points (sensor_msgs/PointCloud2)
[TRANSLATION_FAILED] - **/tf**: Transform tree (map → odom → base_link)

[TRANSLATION_FAILED] Subscribe to pose:

```python
from nav_msgs.msg import Odometry

class SLAMSubscriber(Node):
    def __init__(self):
        super().__init__('slam_subscriber')
        self.subscription = self.create_subscription(
            Odometry,
            '/visual_slam/tracking/odometry',
            self.odom_callback,
            10
        )

    def odom_callback(self, msg):
        pos = msg.pose.pose.position
        self.get_logger().info(f'Position: x={pos.x:.2f}, y={pos.y:.2f}, z={pos.z:.2f}')
```

[TRANSLATION_FAILED] ## AprilTag Detection

[TRANSLATION_FAILED] AprilTags provide fiducial markers for localization:

[TRANSLATION_FAILED] ### Install Isaac ROS AprilTag

```bash
cd ~/isaac_ros_ws/src
git clone --recurse-submodules https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_apriltag.git

# Build
cd ~/isaac_ros_ws
colcon build --packages-select isaac_ros_apriltag
```

[TRANSLATION_FAILED] ### Launch AprilTag Detector

```python
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='isaac_ros_apriltag',
            executable='apriltag_node',
            name='apriltag_detector',
            parameters=[{
                'size': 0.16,  # Tag size in meters
                'max_tags': 64,
                'family': '36h11',
            }],
            remappings=[
                ('image', '/camera/image_raw'),
                ('camera_info', '/camera/camera_info'),
            ]
        ),
    ])
```

[TRANSLATION_FAILED] ### Output

```bash
# Detected tags published on:
ros2 topic echo /tag_detections
```

[TRANSLATION_FAILED] Process detections:

```python
from isaac_ros_apriltag_interfaces.msg import AprilTagDetectionArray

class AprilTagProcessor(Node):
    def __init__(self):
        super().__init__('apriltag_processor')
        self.subscription = self.create_subscription(
            AprilTagDetectionArray,
            '/tag_detections',
            self.tag_callback,
            10
        )

    def tag_callback(self, msg):
        for detection in msg.detections:
            tag_id = detection.id
            pose = detection.pose.pose.pose

            self.get_logger().info(
                f'Tag {tag_id}: x={pose.position.x:.2f}, y={pose.position.y:.2f}'
            )
```

[TRANSLATION_FAILED] ## Map Saving and Loading

[TRANSLATION_FAILED] ### Save Map

```bash
# cuVSLAM saves map to disk automatically
# Check /tmp/cuvslam or configured path

# Alternatively, use ROS 2 service
ros2 service call /visual_slam/save_map isaac_ros_visual_slam_interfaces/srv/FilePath \
  "{file_path: '/tmp/my_map.osa'}"
```

[TRANSLATION_FAILED] ### Load Map

```bash
ros2 service call /visual_slam/load_map isaac_ros_visual_slam_interfaces/srv/FilePath \
  "{file_path: '/tmp/my_map.osa'}"
```

[TRANSLATION_FAILED] ### Reset SLAM

```bash
ros2 service call /visual_slam/reset std_srvs/srv/Empty
```

[TRANSLATION_FAILED] ## Performance Tuning

[TRANSLATION_FAILED] ### Image Resolution

[TRANSLATION_FAILED] Lower resolution = faster processing:

```python
camera = Camera(
    resolution=(320, 240),  # Reduced from (640, 480)
)
```

[TRANSLATION_FAILED] ### Frame Rate

```python
parameters=[{
    'img_jitter_threshold_ms': 50.0,  # Tolerate more jitter
}]
```

[TRANSLATION_FAILED] ### Disable Debugging

```python
parameters=[{
    'enable_debug_mode': False,
    'enable_slam_visualization': False,
}]
```

[TRANSLATION_FAILED] ## Complete Humanoid VSLAM Example

```python
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription

def generate_launch_description():
    return LaunchDescription([
        # Isaac Sim (run separately)
        # ros2 launch humanoid_sim isaac_sim.launch.py

        # Camera info publishers
        Node(
            package='humanoid_navigation',
            executable='camera_info_publisher',
            parameters=[{'config': '/path/to/stereo_calibration.yaml'}]
        ),

        # cuVSLAM
        Node(
            package='isaac_ros_visual_slam',
            executable='visual_slam_node',
            parameters=[{
                'map_frame': 'map',
                'odom_frame': 'odom',
                'base_frame': 'base_link',
                'enable_slam_visualization': True,
            }],
            remappings=[
                ('stereo_camera/left/image', '/stereo_camera/left/image_raw'),
                ('stereo_camera/left/camera_info', '/stereo_camera/left/camera_info'),
                ('stereo_camera/right/image', '/stereo_camera/right/image_raw'),
                ('stereo_camera/right/camera_info', '/stereo_camera/right/camera_info'),
            ]
        ),

        # RViz
        Node(
            package='rviz2',
            executable='rviz2',
            arguments=['-d', '/path/to/vslam.rviz']
        ),
    ])
```

[TRANSLATION_FAILED] ## Summary

[TRANSLATION_FAILED] This week you learned:

[TRANSLATION_FAILED] - Isaac ROS architecture and GEMs
[TRANSLATION_FAILED] - Installing cuVSLAM in Docker
[TRANSLATION_FAILED] - Stereo camera setup in Isaac Sim
[TRANSLATION_FAILED] - Running cuVSLAM for visual SLAM
[TRANSLATION_FAILED] - AprilTag detection for fiducials
[TRANSLATION_FAILED] - Map saving/loading
[TRANSLATION_FAILED] - Performance optimization
[TRANSLATION_FAILED] - Complete humanoid VSLAM pipeline

[TRANSLATION_FAILED] ## What's Next?

[TRANSLATION_FAILED] **Week 9: Nav2 for Bipedal Navigation** - Integrate SLAM with Nav2 for autonomous navigation and path planning.

[TRANSLATION_FAILED] **Next**: [Week 9: Navigation →](./week9-navigation.md)
