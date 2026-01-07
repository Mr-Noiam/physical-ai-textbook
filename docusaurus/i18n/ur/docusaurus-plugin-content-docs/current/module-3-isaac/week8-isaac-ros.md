# ہفتہ 8: VSLAM کے لیے آئزک ROS

## تعارف

**آئزک ROS** GPU-ایکسلریٹڈ پرسیپشن اور نیویگیشن پیکجز (GEMs - GPU-فعال ماڈیولز) فراہم کرتا ہے۔ اس ہفتے، آپ **cuVSLAM** کا استعمال کرتے ہوئے بصری SLAM (بیک وقت لوکلائزیشن اور میپنگ) نافذ کریں گے، جس سے آپ کا ہیومنائڈ نقشے بنا سکے گا اور حقیقی وقت میں لوکلائز کر سکے گا۔

## آئزک ROS فن تعمیر

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

**آئزک ROS GEMs**:
- cuVSLAM: بصری SLAM
- DNN انفرنس: آبجیکٹ ڈیٹیکشن کے لیے TensorRT
- امیج پروسیسنگ: سٹیریو ڈسپیرٹی، ریکٹیفیکیشن
- اپریل ٹیگ: فیڈوشل مارکرز

## انسٹالیشن

### آئزک ROS کی ضروریات

```bash
# NVIDIA کنٹینر ٹول کٹ انسٹال کریں
distribution=$(. /etc/os-release;echo $ID$VERSION_ID) \
   && curl -s -L https://nvidia.github.io/libnvidia-container/gpgkey | sudo apt-key add - \
   && curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list | sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

sudo apt update && sudo apt install nvidia-docker2
sudo systemctl restart docker

# ٹیسٹ
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi
```

### آئزک ROS ورک اسپیس

```bash
# ورک اسپیس بنائیں
mkdir -p ~/isaac_ros_ws/src
cd ~/isaac_ros_ws/src

# آئزک ROS کلون کریں
git clone --recurse-submodules https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_common.git
git clone --recurse-submodules https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_visual_slam.git
git clone --recurse-submodules https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_image_pipeline.git

# بلڈ کریں (آئزک ROS ڈاکر کا استعمال کرتے ہوئے)
cd ~/isaac_ros_ws
./src/isaac_ros_common/scripts/run_dev.sh

# کنٹینر کے اندر
cd /workspaces/isaac_ros_ws
colcon build --symlink-install
source install/setup.bash
```

## cuVSLAM سیٹ اپ

### cuVSLAM لانچ کریں

```bash
# ٹرمینل 1: آئزک ROS کنٹینر
cd ~/isaac_ros_ws
./src/isaac_ros_common/scripts/run_dev.sh
source install/setup.bash

# cuVSLAM لانچ کریں
ros2 launch isaac_ros_visual_slam isaac_ros_visual_slam.launch.py
```

### ان پٹ ٹاپکس

cuVSLAM کو سٹیریو یا RGB-D کی ضرورت ہے:

- **/stereo_camera/left/image_raw**: بائیں ریکٹیفائیڈ تصویر
- **/stereo_camera/left/camera_info**: کیمرہ کیلیبریشن
- **/stereo_camera/right/image_raw**: دائیں ریکٹیفائیڈ تصویر
- **/stereo_camera/right/camera_info**

## آئزک سم کیمرہ کو جوڑنا

### آئزک سم: سٹیریو کیمرہ

```python
from omni.isaac.kit import SimulationApp
simulation_app = SimulationApp({"headless": False})

from omni.isaac.core import World
from omni.isaac.sensor import Camera
import omni.graph.core as og
import numpy as np

# ورلڈ بنائیں
world = World()

# بائیں کیمرہ
left_camera = Camera(
    prim_path="/World/Humanoid/head/stereo_left",
    position=np.array([0.1, -0.03, 0.15]),
    frequency=30,
    resolution=(640, 480),
)

# دائیں کیمرہ
right_camera = Camera(
    prim_path="/World/Humanoid/head/stereo_right",
    position=np.array([0.1, 0.03, 0.15]),
    frequency=30,
    resolution=(640, 480),
)

# بائیں کیمرے کے لیے ROS 2 برج
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

# دائیں کیمرے کے لیے اسی طرح
# ... (stereo_right کے لیے دہرائیں)

world.reset()
for i in range(1000):
    world.step(render=True)

simulation_app.close()
```

### کیمرہ کیلیبریشن

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

کیمرہ معلومات شائع کریں:

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
        # ... (باقی بھریں)

    def publish_info(self):
        self.info.header.stamp = self.get_clock().now().to_msg()
        self.info.header.frame_id = "stereo_left"
        self.publisher.publish(self.info)
```

## cuVSLAM چلانا

### لانچ فائل

```python
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        # cuVSLAM نوڈ
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

        # RViz ویژولائزیشن
        Node(
            package='rviz2',
            executable='rviz2',
            arguments=['-d', '/path/to/vslam.rviz']
        ),
    ])
```

### چلائیں

```bash
ros2 launch humanoid_navigation cuvslam.launch.py
```

## آؤٹ پٹ ٹاپکس

cuVSLAM شائع کرتا ہے:

- **/visual_slam/tracking/odometry**: بصری اوڈومیٹری (nav_msgs/Odometry)
- **/visual_slam/tracking/vo_pose**: پوز کا تخمینہ (geometry_msgs/PoseStamped)
- **/visual_slam/tracking/slam_path**: روبوٹ کا راستہ (nav_msgs/Path)
- **/visual_slam/vis/landmarks_cloud**: 3D نقشہ پوائنٹس (sensor_msgs/PointCloud2)
- **/tf**: ٹرانسفارم ٹری (map → odom → base_link)

پوز کو سبسکرائب کریں:

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

## اپریل ٹیگ ڈیٹیکشن

اپریل ٹیگز لوکلائزیشن کے لیے فیڈوشل مارکر فراہم کرتے ہیں:

### آئزک ROS اپریل ٹیگ انسٹال کریں

```bash
cd ~/isaac_ros_ws/src
git clone --recurse-submodules https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_apriltag.git

# بلڈ کریں
cd ~/isaac_ros_ws
colcon build --packages-select isaac_ros_apriltag
```

### اپریل ٹیگ ڈیٹیکٹر لانچ کریں

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
                'size': 0.16,  #میٹر میں ٹیگ کا سائز
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

### آؤٹ پٹ

```bash
# پتہ لگائے گئے ٹیگز یہاں شائع ہوتے ہیں:
ros2 topic echo /tag_detections
```

پتہ لگائے گئے ٹیگز پر کارروائی کریں:

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

## نقشہ محفوظ کرنا اور لوڈ کرنا

### نقشہ محفوظ کریں

```bash
# cuVSLAM نقشے کو خود بخود ڈسک پر محفوظ کرتا ہے
# /tmp/cuvslam یا کنفیگر شدہ پاتھ چیک کریں

# متبادل طور پر، ROS 2 سروس استعمال کریں
ros2 service call /visual_slam/save_map isaac_ros_visual_slam_interfaces/srv/FilePath \
  "{file_path: '/tmp/my_map.osa'}"
```

### نقشہ لوڈ کریں

```bash
ros2 service call /visual_slam/load_map isaac_ros_visual_slam_interfaces/srv/FilePath \
  "{file_path: '/tmp/my_map.osa'}"
```

### SLAM ری سیٹ کریں

```bash
ros2 service call /visual_slam/reset std_srvs/srv/Empty
```

## کارکردگی کی ٹیوننگ

### امیج ریزولوشن

کم ریزولوشن = تیز پراسیسنگ:

```python
camera = Camera(
    resolution=(320, 240),  # (640, 480) سے کم کیا گیا
)
```

### فریم ریٹ

```python
parameters=[{
    'img_jitter_threshold_ms': 50.0,  # زیادہ جٹر برداشت کریں
}]
```

### ڈیبگنگ کو غیر فعال کریں

```python
parameters=[{
    'enable_debug_mode': False,
    'enable_slam_visualization': False,
}]
```

## مکمل ہیومنائڈ VSLAM مثال

```python
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription

def generate_launch_description():
    return LaunchDescription([
        # آئزک سم (الگ سے چلائیں)
        # ros2 launch humanoid_sim isaac_sim.launch.py

        # کیمرہ معلومات پبلشرز
        Node(
            package='humanoid_navigation',
            executable='camera_info_publisher',
            parameters=[{'config': '/path/to/stereo_calibration.yaml'}]
        ),

        # cuVSLAM
        Node(
            package='isaac_ros_visual_slam',
            executable='visual_slam_node',
            parameters=[
                {
                    'map_frame': 'map',
                    'odom_frame': 'odom',
                    'base_frame': 'base_link',
                    'enable_slam_visualization': True,
                }
            ],
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

## خلاصہ

اس ہفتے آپ نے سیکھا:

- آئزک ROS فن تعمیر اور GEMs
- ڈاکر میں cuVSLAM انسٹال کرنا
- آئزک سم میں سٹیریو کیمرہ سیٹ اپ
- بصری SLAM کے لیے cuVSLAM چلانا
- فیڈوشلز کے لیے اپریل ٹیگ ڈیٹیکشن
- نقشہ محفوظ کرنا/لوڈ کرنا
- کارکردگی کی اصلاح
- مکمل ہیومنائڈ VSLAM پائپ لائن

## آگے کیا ہے؟

**ہفتہ 9: بائی پیڈل نیویگیشن کے لیے Nav2** - خود مختار نیویگیشن اور پاتھ پلاننگ کے لیے SLAM کو Nav2 کے ساتھ مربوط کریں۔

**آگے**: [ہفتہ 9: نیویگیشن →](./week9-navigation.md)