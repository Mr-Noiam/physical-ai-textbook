# ہفتہ 8: VSLAM کے لیے Isaac ROS

## تعارف

**Isaac ROS** GPU سے تیز شدہ perception اور نیویگیشن پیکجز (GEMs - GPU-Enabled Modules) فراہم کرتا ہے۔ اس ہفتے، آپ **cuVSLAM** استعمال کرتے ہوئے بصری SLAM (Simultaneous Localization and Mapping) نافذ کریں گے، جو آپ کے ہیومینائیڈ کو حقیقی وقت میں نقشے بنانے اور localize کرنے کے قابل بناتا ہے۔

## Isaac ROS کیوں؟

**روایتی ROS سے فوائد**:

- **GPU تیز رفتاری**: CPU کے مقابلے میں 10-100x تیز
- **کم تاخیر**: حقیقی وقت کی کارکردگی کے لیے <10ms
- **بہتر شدہ**: NVIDIA ہارڈویئر کے لیے خاص طور پر ٹیون کیا گیا
- **پیداوار کے لیے تیار**: مضبوط، ٹیسٹ شدہ، اور برقرار رکھا ہوا

**کلیدی GEMs**:
- **cuVSLAM**: بصری SLAM
- **cuVOX**: Voxel میپنگ
- **cuMotion**: حرکت کی منصوبہ بندی
- **DNN Inference**: TensorRT سے چلنے والا

## تنصیب

### ضروریات

```bash
# NVIDIA GPU (Jetson یا RTX)
# JetPack 5.1+ (Jetson) یا Ubuntu 22.04 (x86)
# ROS 2 Humble
# Docker (تجویز کردہ)

# NVIDIA Container Toolkit
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
  sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker
```

### Isaac ROS

```bash
# Isaac ROS repository کلون کریں
mkdir -p ~/workspaces/isaac_ros-dev/src
cd ~/workspaces/isaac_ros-dev/src
git clone https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_common.git

# Docker container چلائیں
cd ~/workspaces/isaac_ros-dev/src/isaac_ros_common
./scripts/run_dev.sh

# Container کے اندر، Isaac ROS packages بنائیں
cd /workspaces/isaac_ros-dev
colcon build --symlink-install
source install/setup.bash
```

## cuVSLAM: بصری SLAM

### خصوصیات

- **Stereo یا RGB-D**: کیمرہ کی دونوں اقسام کی حمایت
- **لوپ بندش**: طویل trajectories کے لیے drift کو کم کرتا ہے
- **حقیقی وقت**: GPU acceleration کے ساتھ 30+ FPS
- **ROS 2 مقامی**: معیاری `nav_msgs/Odometry` شائع کرتا ہے

### بنیادی استعمال

```bash
# ZED کیمرہ کے ساتھ cuVSLAM شروع کریں
ros2 launch isaac_ros_visual_slam isaac_ros_visual_slam_zed.launch.py

# یا RealSense:
ros2 launch isaac_ros_visual_slam isaac_ros_visual_slam_realsense.launch.py

# odometry دیکھیں
ros2 topic echo /visual_slam/tracking/odometry
```

### Python کے ساتھ انضمام

```python
import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from geometry_msgs.msg import PoseStamped

class VisualSLAMMonitor(Node):
    def __init__(self):
        super().__init__('vslam_monitor')

        # cuVSLAM سے odometry سبسکرائب کریں
        self.odom_sub = self.create_subscription(
            Odometry,
            '/visual_slam/tracking/odometry',
            self.odom_callback,
            10
        )

        # نیویگیشن کے لیے pose شائع کریں
        self.pose_pub = self.create_publisher(
            PoseStamped,
            '/current_pose',
            10
        )

    def odom_callback(self, msg):
        # odometry کو pose میں تبدیل کریں
        pose = PoseStamped()
        pose.header = msg.header
        pose.pose = msg.pose.pose

        self.pose_pub.publish(pose)

        # موجودہ پوزیشن لاگ کریں
        x = msg.pose.pose.position.x
        y = msg.pose.pose.position.y
        self.get_logger().info(f'Position: x={x:.2f}, y={y:.2f}')

def main():
    rclpy.init()
    node = VisualSLAMMonitor()
    rclpy.spin(node)
    rclpy.shutdown()
```

## Nav2 کے ساتھ انضمام

```yaml
# Nav2 پیرامیٹرز
bt_navigator:
  ros__parameters:
    global_frame: map
    robot_base_frame: base_link
    odom_topic: /visual_slam/tracking/odometry  # cuVSLAM سے

controller_server:
  ros__parameters:
    controller_frequency: 20.0
    FollowPath:
      plugin: "dwb_core::DWBLocalPlanner"
      max_vel_x: 0.5
      max_vel_theta: 1.0
```

## کارکردگی کی اصلاح

### کیمرہ ریزولوشن

```bash
# کم ریزولوشن = تیز پروسیسنگ
ros2 param set /visual_slam image_height 480
ros2 param set /visual_slam image_width 640
```

### GPU میموری

```bash
# GPU استعمال کی نگرانی کریں
nvidia-smi

# map سائز محدود کریں
ros2 param set /visual_slam max_map_size 1000
```

## خلاصہ

اس ہفتے آپ نے سیکھا:

- Isaac ROS فن تعمیر اور GEMs
- GPU سے تیز شدہ cuVSLAM
- حقیقی وقت میں بصری SLAM
- Stereo/RGB-D کیمرہ انضمام
- Nav2 کے ساتھ نیویگیشن
- کارکردگی کی اصلاح

## اگلا کیا ہے؟

**ہفتہ 9: دو پیروں کے نیویگیشن کے لیے Nav2** - خودکار نیویگیشن، راستہ کی منصوبہ بندی، اور رکاوٹوں سے بچنا۔

**اگلا**: [ہفتہ 9: نیویگیشن →](./week9-navigation.md)
