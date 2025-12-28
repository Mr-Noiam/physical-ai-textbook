#!/usr/bin/env python3
# -*- coding: utf-8 -*-

week3_content = """# ہفتہ 3: Python میں Robot Programming

## تعارف

اس ہفتے، ہم ROS 2 کے ساتھ Python استعمال کرتے ہوئے روبوٹ کنٹرول، sensor integration، اور custom messages کو دریافت کریں گے۔

## Custom Messages بنانا

### Message فائل بنائیں

فائل: `tutorial_interfaces/msg/Num.msg`

```
int64 num
```

### CMakeLists.txt میں شامل کریں

```cmake
find_package(rosidl_default_generators REQUIRED)

rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/Num.msg"
)
```

### استعمال کریں

```python
from tutorial_interfaces.msg import Num

def timer_callback(self):
    msg = Num()
    msg.num = self.i
    self.publisher_.publish(msg)
```

## Custom Services بنانا

### Service فائل بنائیں

فائل: `tutorial_interfaces/srv/AddThreeInts.srv`

```
int64 a
int64 b
int64 c
---
int64 sum
```

### Service Server

```python
from tutorial_interfaces.srv import AddThreeInts

class AddThreeIntsServer(Node):
    def __init__(self):
        super().__init__('add_three_ints_server')
        self.srv = self.create_service(
            AddThreeInts,
            'add_three_ints',
            self.add_three_ints_callback
        )

    def add_three_ints_callback(self, request, response):
        response.sum = request.a + request.b + request.c
        return response
```

## Parameters استعمال کرنا

Parameters runtime میں node کی ترتیبات تبدیل کرنے کی اجازت دیتے ہیں۔

### Parameter declare کریں

```python
class ParameterNode(Node):
    def __init__(self):
        super().__init__('parameter_node')
        self.declare_parameter('my_parameter', 'default_value')
        my_param = self.get_parameter('my_parameter').value
```

### Parameters تبدیل کریں

```bash
ros2 run package_name node_name --ros-args -p my_parameter:=new_value
ros2 param set /node_name my_parameter new_value
ros2 param list
```

## Launch Files

Launch files کئی nodes کو ایک ساتھ شروع کرنے کی اجازت دیتی ہیں۔

```python
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(package='py_pubsub', executable='talker', name='talker'),
        Node(package='py_pubsub', executable='listener', name='listener'),
    ])
```

## TF2: Transform Library

TF2 coordinate frames کے درمیان تبدیلیوں کو ٹریک کرتا ہے۔

```python
from tf2_ros import TransformBroadcaster
from geometry_msgs.msg import TransformStamped

class FramePublisher(Node):
    def __init__(self):
        super().__init__('frame_publisher')
        self.br = TransformBroadcaster(self)
```

## خلاصہ

اس ہفتے آپ نے سیکھا:

- Custom messages اور services بنانا
- Parameters استعمال کرنا
- Launch files لکھنا
- TF2 transforms
- Colcon کے ساتھ building

## اگلا کیا ہے؟

**ہفتہ 4: URDF** - Robot descriptions سیکھیں۔

**اگلا**: [ہفتہ 4: URDF →](./week4-urdf.md)
"""

week4_content = """# ہفتہ 4: URDF اور Robot Modeling

## تعارف

اس ہفتے، ہم **URDF** (Unified Robot Description Format) استعمال کرتے ہوئے robots کو model کرنا سیکھیں گے۔

## URDF کی بنیادیں

### سادہ Robot URDF

```xml
<?xml version="1.0"?>
<robot name="simple_robot">
  <link name="base_link">
    <visual>
      <geometry>
        <box size="0.5 0.5 0.1"/>
      </geometry>
    </visual>
  </link>

  <link name="wheel_left">
    <visual>
      <geometry>
        <cylinder length="0.05" radius="0.1"/>
      </geometry>
    </visual>
  </link>

  <joint name="base_to_wheel_left" type="continuous">
    <parent link="base_link"/>
    <child link="wheel_left"/>
    <origin xyz="0 0.2 0"/>
    <axis xyz="0 0 1"/>
  </joint>
</robot>
```

## Links اور Joints

### Link کی اقسام

```xml
<link name="my_link">
  <visual>
    <geometry><box size="1 1 1"/></geometry>
  </visual>
  <collision>
    <geometry><box size="1 1 1"/></geometry>
  </collision>
  <inertial>
    <mass value="10"/>
    <inertia ixx="1.0" iyy="1.0" izz="1.0"/>
  </inertial>
</link>
```

### Joint کی اقسام

1. **Fixed**: کوئی حرکت نہیں
2. **Revolute**: گھومنے والا (limited)
3. **Continuous**: گھومنے والا (unlimited)
4. **Prismatic**: سلائیڈنگ

```xml
<joint name="shoulder_joint" type="revolute">
  <parent link="torso"/>
  <child link="upper_arm"/>
  <axis xyz="0 1 0"/>
  <limit lower="-1.57" upper="1.57" effort="100"/>
</joint>
```

## Xacro: URDF Macros

Xacro URDF کو زیادہ modular بناتا ہے۔

```xml
<?xml version="1.0"?>
<robot xmlns:xacro="http://www.ros.org/wiki/xacro" name="my_robot">
  <xacro:property name="wheel_radius" value="0.1"/>

  <xacro:macro name="wheel" params="prefix reflect">
    <link name="${prefix}_wheel">
      <visual>
        <geometry>
          <cylinder radius="${wheel_radius}" length="0.05"/>
        </geometry>
      </visual>
    </link>
  </xacro:macro>

  <xacro:wheel prefix="left" reflect="1"/>
  <xacro:wheel prefix="right" reflect="-1"/>
</robot>
```

## RViz میں دیکھیں

```bash
ros2 launch my_robot_description view_robot.launch.py
```

## Gazebo Integration

```xml
<gazebo reference="base_link">
  <material>Gazebo/Blue</material>
</gazebo>

<gazebo>
  <plugin name="drive_controller" filename="libgazebo_ros_diff_drive.so">
    <left_joint>base_to_left_wheel</left_joint>
    <right_joint>base_to_right_wheel</right_joint>
  </plugin>
</gazebo>
```

## خلاصہ

اس ہفتے آپ نے سیکھا:

- URDF کی بنیادیں
- Links اور joints کی تعریف
- Xacro macros
- RViz visualization
- Gazebo integration

## اگلا کیا ہے؟

**ہفتہ 5: Gazebo Simulation** - Robot simulation سیکھیں۔

**اگلا**: [ہفتہ 5: Gazebo →](../module-2-gazebo/week5-simulation.md)
"""

# Write files
import os

base_path = "../docusaurus/i18n/ur/docusaurus-plugin-content-docs/current/module-1-ros2"

week3_path = os.path.join(base_path, "week3-python.md")
week4_path = os.path.join(base_path, "week4-urdf.md")

with open(week3_path, 'w', encoding='utf-8') as f:
    f.write(week3_content)
print(f"✓ Written: {week3_path}")

with open(week4_path, 'w', encoding='utf-8') as f:
    f.write(week4_content)
print(f"✓ Written: {week4_path}")

print("✓ All files written successfully!")
