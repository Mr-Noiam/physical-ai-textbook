# Week 3: Building ROS 2 Packages with Python

## Introduction

This week, we'll learn how to structure, build, and deploy professional ROS 2 packages using Python. You'll create a complete package with publishers, subscribers, services, and launch files that orchestrate multiple nodes.

## ROS 2 Package Structure

A Python ROS 2 package has this structure:

```
my_robot_pkg/
├── package.xml          # Package metadata
├── setup.py             # Python build configuration
├── setup.cfg            # Python install configuration
├── resource/
│   └── my_robot_pkg     # Marker file for ament
├── my_robot_pkg/
│   ├── __init__.py
│   ├── node1.py         # Node implementations
│   ├── node2.py
│   └── utils/
│       ├── __init__.py
│       └── helpers.py
├── launch/
│   └── robot.launch.py  # Launch files
├── config/
│   └── params.yaml      # Parameter files
└── test/
    └── test_node1.py    # Unit tests
```

## Creating a Package

### Using ros2 pkg create

```bash
# Navigate to your workspace src/
cd ~/ros2_ws/src

# Create package with dependencies
ros2 pkg create --build-type ament_python \
  --dependencies rclpy sensor_msgs geometry_msgs \
  --node-name minimal_node \
  humanoid_control

cd humanoid_control
```

This generates:
- `package.xml` - Dependencies and metadata
- `setup.py` - Entry points for nodes
- `setup.cfg` - Python package configuration
- `humanoid_control/` - Python module directory

## Package Metadata: package.xml

```xml
<?xml version="1.0"?>
<?xml-model href="http://download.ros.org/schema/package_format3.xsd" schematypens="http://www.w3.org/2001/XMLSchema"?>
<package format="3">
  <name>humanoid_control</name>
  <version>1.0.0</version>
  <description>Humanoid robot control package</description>
  <maintainer email="you@example.com">Your Name</maintainer>
  <license>Apache-2.0</license>

  <!-- Build dependencies -->
  <depend>rclpy</depend>
  <depend>sensor_msgs</depend>
  <depend>geometry_msgs</depend>
  <depend>std_msgs</depend>

  <!-- Testing -->
  <test_depend>ament_copyright</test_depend>
  <test_depend>ament_flake8</test_depend>
  <test_depend>ament_pep257</test_depend>
  <test_depend>python3-pytest</test_depend>

  <export>
    <build_type>ament_python</build_type>
  </export>
</package>
```

## Build Configuration: setup.py

```python
from setuptools import setup
from glob import glob
import os

package_name = 'humanoid_control'

setup(
    name=package_name,
    version='1.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # Install launch files
        (os.path.join('share', package_name, 'launch'),
            glob('launch/*.py')),
        # Install config files
        (os.path.join('share', package_name, 'config'),
            glob('config/*.yaml')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Your Name',
    maintainer_email='you@example.com',
    description='Humanoid robot control package',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'joint_controller = humanoid_control.joint_controller:main',
            'imu_processor = humanoid_control.imu_processor:main',
            'balance_controller = humanoid_control.balance_controller:main',
        ],
    },
)
```

**Key sections**:
- `data_files`: Install non-Python files (launch, config, URDF)
- `entry_points`: Executables created from Python scripts

## Example Node: Joint State Publisher

Create `humanoid_control/joint_controller.py`:

```python
#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import Header
import math

class JointController(Node):
    def __init__(self):
        super().__init__('joint_controller')

        # Declare parameters
        self.declare_parameter('publish_rate', 50.0)
        self.declare_parameter('num_joints', 28)

        rate = self.get_parameter('publish_rate').value
        self.num_joints = self.get_parameter('num_joints').value

        # Publisher
        self.publisher_ = self.create_publisher(
            JointState,
            '/joint_states',
            10
        )

        # Timer for periodic publishing
        self.timer = self.create_timer(1.0/rate, self.publish_joints)

        # Joint names for 28-DOF humanoid
        self.joint_names = [
            # Torso
            'torso_pitch', 'torso_yaw', 'torso_roll',
            # Left arm
            'left_shoulder_pitch', 'left_shoulder_roll', 'left_shoulder_yaw',
            'left_elbow', 'left_wrist_pitch', 'left_wrist_roll', 'left_wrist_yaw',
            # Right arm (mirrored)
            'right_shoulder_pitch', 'right_shoulder_roll', 'right_shoulder_yaw',
            'right_elbow', 'right_wrist_pitch', 'right_wrist_roll', 'right_wrist_yaw',
            # Left leg
            'left_hip_pitch', 'left_hip_roll', 'left_hip_yaw',
            'left_knee', 'left_ankle_pitch', 'left_ankle_roll',
            # Right leg
            'right_hip_pitch', 'right_hip_roll', 'right_hip_yaw',
            'right_knee', 'right_ankle_pitch', 'right_ankle_roll',
        ]

        self.phase = 0.0
        self.get_logger().info(f'Joint controller started at {rate} Hz')

    def publish_joints(self):
        msg = JointState()
        msg.header = Header()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = self.joint_names

        # Generate sinusoidal positions (for demo)
        msg.position = [
            0.1 * math.sin(self.phase + i * 0.1)
            for i in range(len(self.joint_names))
        ]
        msg.velocity = [0.0] * len(self.joint_names)
        msg.effort = [0.0] * len(self.joint_names)

        self.publisher_.publish(msg)
        self.phase += 0.05

def main(args=None):
    rclpy.init(args=args)
    node = JointController()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Example: IMU Data Processor

Create `humanoid_control/imu_processor.py`:

```python
#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu
from geometry_msgs.msg import Vector3
import math

class ImuProcessor(Node):
    def __init__(self):
        super().__init__('imu_processor')

        # Subscribe to raw IMU
        self.subscription = self.create_subscription(
            Imu,
            '/imu/data_raw',
            self.imu_callback,
            10
        )

        # Publish filtered orientation
        self.orientation_pub = self.create_publisher(
            Vector3,
            '/imu/orientation_rpy',
            10
        )

        self.get_logger().info('IMU Processor started')

    def imu_callback(self, msg):
        # Convert quaternion to roll-pitch-yaw
        quat = msg.orientation
        rpy = self.quaternion_to_euler(quat)

        # Publish as Vector3
        rpy_msg = Vector3()
        rpy_msg.x = rpy[0]  # Roll
        rpy_msg.y = rpy[1]  # Pitch
        rpy_msg.z = rpy[2]  # Yaw

        self.orientation_pub.publish(rpy_msg)

        # Log if tilted significantly
        if abs(rpy[0]) > 0.5 or abs(rpy[1]) > 0.5:
            self.get_logger().warn(
                f'Large tilt detected: roll={rpy[0]:.2f}, pitch={rpy[1]:.2f}'
            )

    def quaternion_to_euler(self, q):
        """Convert quaternion to Euler angles (roll, pitch, yaw)"""
        # Roll (x-axis rotation)
        sinr_cosp = 2 * (q.w * q.x + q.y * q.z)
        cosr_cosp = 1 - 2 * (q.x * q.x + q.y * q.y)
        roll = math.atan2(sinr_cosp, cosr_cosp)

        # Pitch (y-axis rotation)
        sinp = 2 * (q.w * q.y - q.z * q.x)
        pitch = math.asin(max(-1.0, min(1.0, sinp)))

        # Yaw (z-axis rotation)
        siny_cosp = 2 * (q.w * q.z + q.x * q.y)
        cosy_cosp = 1 - 2 * (q.y * q.y + q.z * q.z)
        yaw = math.atan2(siny_cosp, cosy_cosp)

        return (roll, pitch, yaw)

def main(args=None):
    rclpy.init(args=args)
    node = ImuProcessor()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Building with Colcon

### Build Process

```bash
# From workspace root
cd ~/ros2_ws

# Build all packages
colcon build

# Build specific package
colcon build --packages-select humanoid_control

# Build with debug symbols
colcon build --cmake-args -DCMAKE_BUILD_TYPE=Debug

# Parallel builds (faster)
colcon build --parallel-workers 4
```

### Source the Package

```bash
# Source workspace overlay
source ~/ros2_ws/install/setup.bash

# Run node
ros2 run humanoid_control joint_controller

# With parameters
ros2 run humanoid_control joint_controller --ros-args -p publish_rate:=100.0
```

## Launch Files: Orchestrating Multiple Nodes

Create `launch/humanoid_bringup.launch.py`:

```python
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    # Get package directory
    pkg_dir = get_package_share_directory('humanoid_control')

    # Declare launch arguments
    use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time',
        default_value='false',
        description='Use simulation time'
    )

    publish_rate_arg = DeclareLaunchArgument(
        'publish_rate',
        default_value='50.0',
        description='Joint state publish rate (Hz)'
    )

    # Load parameters from YAML
    config_file = os.path.join(pkg_dir, 'config', 'humanoid_params.yaml')

    # Joint controller node
    joint_controller = Node(
        package='humanoid_control',
        executable='joint_controller',
        name='joint_controller',
        parameters=[
            config_file,
            {'publish_rate': LaunchConfiguration('publish_rate')}
        ],
        output='screen'
    )

    # IMU processor node
    imu_processor = Node(
        package='humanoid_control',
        executable='imu_processor',
        name='imu_processor',
        parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}],
        output='screen'
    )

    # Balance controller
    balance_controller = Node(
        package='humanoid_control',
        executable='balance_controller',
        name='balance_controller',
        parameters=[config_file],
        output='screen',
        respawn=True  # Restart if crashes
    )

    # RViz for visualization
    rviz_config = os.path.join(pkg_dir, 'config', 'humanoid.rviz')
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config],
        output='screen'
    )

    return LaunchDescription([
        use_sim_time_arg,
        publish_rate_arg,
        joint_controller,
        imu_processor,
        balance_controller,
        rviz
    ])
```

### Launch the System

```bash
# Launch with defaults
ros2 launch humanoid_control humanoid_bringup.launch.py

# Override parameters
ros2 launch humanoid_control humanoid_bringup.launch.py \
  use_sim_time:=true \
  publish_rate:=100.0
```

## Configuration Files

Create `config/humanoid_params.yaml`:

```yaml
joint_controller:
  ros__parameters:
    publish_rate: 50.0
    num_joints: 28
    joint_limits:
      torso_pitch: [-0.5, 0.5]
      torso_yaw: [-1.0, 1.0]
      left_shoulder_pitch: [-3.14, 3.14]

balance_controller:
  ros__parameters:
    kp_balance: 10.0
    kd_balance: 2.0
    zmp_threshold: 0.05
    update_rate: 100.0

imu_processor:
  ros__parameters:
    filter_alpha: 0.95
    gravity_compensation: true
```

## Testing Your Package

Create `test/test_joint_controller.py`:

```python
import pytest
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState

@pytest.fixture
def node():
    rclpy.init()
    test_node = Node('test_node')
    yield test_node
    test_node.destroy_node()
    rclpy.shutdown()

def test_joint_controller_publishes(node):
    """Test that joint controller publishes messages"""
    received_msgs = []

    def callback(msg):
        received_msgs.append(msg)

    subscription = node.create_subscription(
        JointState,
        '/joint_states',
        callback,
        10
    )

    # Spin for 1 second
    import time
    start = time.time()
    while time.time() - start < 1.0:
        rclpy.spin_once(node, timeout_sec=0.1)

    # Should have received messages
    assert len(received_msgs) > 0
    assert len(received_msgs[0].name) == 28
```

Run tests:

```bash
colcon test --packages-select humanoid_control
colcon test-result --verbose
```

## Debugging Tips

### Check Node Status

```bash
ros2 node list
ros2 node info /joint_controller
```

### Monitor Topics

```bash
ros2 topic list
ros2 topic echo /joint_states
ros2 topic hz /joint_states
```

### Logging Levels

```python
self.get_logger().debug('Debug info')
self.get_logger().info('Normal operation')
self.get_logger().warn('Warning')
self.get_logger().error('Error occurred')
```

Set log level:

```bash
ros2 run humanoid_control joint_controller --ros-args --log-level DEBUG
```

## Best Practices

### Package Organization
- One package per robot or functional unit
- Separate interface packages (messages/services)
- Use metapackages to group related packages

### Version Control
```bash
# .gitignore
build/
install/
log/
*.pyc
__pycache__/
```

### Documentation
```python
"""
Joint Controller Node

Publishes joint states for 28-DOF humanoid.

Published Topics:
    /joint_states (sensor_msgs/JointState)

Parameters:
    publish_rate (float): Hz (default: 50.0)
"""
```

## Summary

This week you learned:

- ROS 2 Python package structure
- `package.xml` and `setup.py` configuration
- Creating nodes with publishers/subscribers
- Building with `colcon`
- Launch files for multi-node systems
- YAML parameter configuration
- Testing with pytest
- Debugging techniques

## What's Next?

**Week 4: URDF for Humanoid Robot Descriptions** - Learn to describe robot geometry and kinematics using URDF and Xacro.

**Next**: [Week 4: URDF Modeling →](./week4-urdf.md)
