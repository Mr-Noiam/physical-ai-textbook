# ہفتہ 5: Gazebo طبیعیات سمولیشن

## تعارف

اس ہفتے، ہم آپ کے ہیومینائیڈ روبوٹ کو **Gazebo** میں شروع کریں گے، ROS 2 کے لیے سب سے مشہور روبوٹ سمیولیٹر۔ آپ طبیعیات کے انجنز، ورلڈ فائلوں، سینسر پلگ ان، اور Physical AI سسٹمز کی جانچ کے لیے حقیقت پسندانہ سمولیشن ماحول بنانے کے بارے میں سیکھیں گے۔

## Gazebo کیا ہے؟

**Gazebo** (اب **Gazebo Classic** کہلاتا ہے) ایک 3D روبوٹ سمیولیٹر ہے جو فراہم کرتا ہے:

- **حقیقت پسند طبیعیات**: ODE, Bullet, Simbody, DART انجن
- **سینسر سمولیشن**: کیمرہ, LiDAR, IMU, force/torque
- **GPU تیز رفتاری**: بصری سینسرز اور بڑے مناظر کے لیے
- **ROS 2 انضمام**: مقامی پیغام کی منتقلی

**Gazebo Fortress/Garden** (نئی نسل) SDF فارمیٹ اور Ignition لائبریریاں استعمال کرتا ہے۔

## SDF بمقابلہ URDF

**SDF (Simulation Description Format)** URDF سے زیادہ طاقتور ہے:

| خصوصیت | URDF | SDF |
|---------|------|-----|
| **دنیاएं** | نہیں | ہاں |
| **بند لوپس** | نہیں | ہاں |
| **متعدد روبوٹ** | محدود | ہاں |
| **سینسرز** | پلگ ان کے ذریعے | مقامی |
| **ورژن کنٹرول** | نہیں | ہاں |

URDF کو Gazebo کے ذریعے خودکار طور پر SDF میں تبدیل کیا جا سکتا ہے۔

## ورلڈ فائلیں: ماحول بنانا

ایک Gazebo ورلڈ ماحول کی وضاحت کرتی ہے:

```xml
<?xml version="1.0"?>
<sdf version="1.7">
  <world name="humanoid_world">

    <!-- طبیعیات کا انجن -->
    <physics name="default_physics" type="ode">
      <max_step_size>0.001</max_step_size>
      <real_time_factor>1.0</real_time_factor>
      <real_time_update_rate>1000</real_time_update_rate>
    </physics>

    <!-- روشنی -->
    <light name="sun" type="directional">
      <cast_shadows>true</cast_shadows>
      <pose>0 0 10 0 0 0</pose>
      <diffuse>0.8 0.8 0.8 1</diffuse>
      <specular>0.2 0.2 0.2 1</specular>
      <attenuation>
        <range>1000</range>
        <constant>0.9</constant>
        <linear>0.01</linear>
        <quadratic>0.001</quadratic>
      </attenuation>
      <direction>-0.5 0.1 -0.9</direction>
    </light>

    <!-- زمینی سطح -->
    <include>
      <uri>model://ground_plane</uri>
    </include>

    <!-- Gazebo ماڈل ڈیٹا بیس سے ماڈل شامل کریں -->
    <include>
      <uri>model://cafe</uri>
      <pose>3 0 0 0 0 0</pose>
    </include>

    <!-- حسب ضرورت رکاوٹ -->
    <model name="box_obstacle">
      <static>true</static>
      <pose>2 0 0.5 0 0 0</pose>
      <link name="link">
        <collision name="collision">
          <geometry>
            <box>
              <size>1 1 1</size>
            </box>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <box>
              <size>1 1 1</size>
            </box>
          </geometry>
          <material>
            <ambient>0.3 0.3 0.3 1</ambient>
            <diffuse>0.7 0.7 0.7 1</diffuse>
          </material>
        </visual>
      </link>
    </model>

  </world>
</sdf>
```

## طبیعیات کے انجن

### ODE (Open Dynamics Engine)

Gazebo Classic میں ڈیفالٹ۔ عمومی روبوٹکس کے لیے اچھا:

```xml
<physics type="ode">
  <max_step_size>0.001</max_step_size>
  <real_time_factor>1.0</real_time_factor>
  <real_time_update_rate>1000</real_time_update_rate>
  <ode>
    <solver>
      <type>quick</type>
      <iters>50</iters>
      <sor>1.3</sor>
    </solver>
    <constraints>
      <cfm>0.0</cfm>
      <erp>0.2</erp>
      <contact_max_correcting_vel>100.0</contact_max_correcting_vel>
      <contact_surface_layer>0.001</contact_surface_layer>
    </constraints>
  </ode>
</physics>
```

### Bullet

پیچیدہ رابطوں کے لیے بہتر:

```xml
<physics type="bullet">
  <max_step_size>0.001</max_step_size>
  <bullet>
    <solver>
      <type>sequential_impulse</type>
      <iters>50</iters>
      <sor>1.3</sor>
    </solver>
  </bullet>
</physics>
```

### DART

ہیومینائیڈ حرکیات کے لیے بہترین:

```xml
<physics type="dart">
  <max_step_size>0.001</max_step_size>
  <dart>
    <solver>
      <solver_type>dantzig</solver_type>
    </solver>
    <collision_detector>bullet</collision_detector>
  </dart>
</physics>
```

## Gazebo میں ہیومینائیڈ شروع کرنا

`launch/gazebo_humanoid.launch.py` بنائیں:

```python
import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, ExecuteProcess
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch.substitutions import Command
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    pkg_dir = get_package_share_directory('humanoid_gazebo')

    # URDF فائل
    urdf_file = os.path.join(pkg_dir, 'urdf', 'humanoid.urdf.xacro')
    robot_description = Command(['xacro ', urdf_file])

    # ورلڈ فائل
    world_file = os.path.join(pkg_dir, 'worlds', 'humanoid_world.world')

    # Gazebo لانچ
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(get_package_share_directory('gazebo_ros'),
                        'launch', 'gazebo.launch.py')
        ]),
        launch_arguments={'world': world_file, 'verbose': 'true'}.items()
    )

    # روبوٹ Spawn کریں
    spawn_entity = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-entity', 'humanoid',
            '-topic', 'robot_description',
            '-x', '0', '-y', '0', '-z', '1.0'
        ],
        output='screen'
    )

    # روبوٹ کی حالت شائع کرنے والا
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': robot_description}],
        output='screen'
    )

    return LaunchDescription([
        gazebo,
        robot_state_publisher,
        spawn_entity
    ])
```

شروع کریں:

```bash
ros2 launch humanoid_gazebo gazebo_humanoid.launch.py
```

## سینسر پلگ ان

### کیمرہ پلگ ان

URDF میں شامل کریں:

```xml
<gazebo reference="camera_link">
  <sensor name="camera" type="camera">
    <update_rate>30</update_rate>
    <camera>
      <horizontal_fov>1.047</horizontal_fov>
      <image>
        <width>640</width>
        <height>480</height>
        <format>R8G8B8</format>
      </image>
      <clip>
        <near>0.1</near>
        <far>100</far>
      </clip>
    </camera>
    <plugin name="camera_controller" filename="libgazebo_ros_camera.so">
      <ros>
        <namespace>/humanoid</namespace>
        <remapping>image_raw:=camera/image_raw</remapping>
        <remapping>camera_info:=camera/camera_info</remapping>
      </ros>
      <camera_name>head_camera</camera_name>
      <frame_name>camera_link</frame_name>
    </plugin>
  </sensor>
</gazebo>
```

کیمرہ سبسکرائب کریں:

```python
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2

class CameraSubscriber(Node):
    def __init__(self):
        super().__init__('camera_subscriber')
        self.bridge = CvBridge()

        self.subscription = self.create_subscription(
            Image,
            '/humanoid/camera/image_raw',
            self.image_callback,
            10
        )

    def image_callback(self, msg):
        cv_image = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
        cv2.imshow('Humanoid Camera', cv_image)
        cv2.waitKey(1)
```

### گہرائی کا کیمرہ (RGB-D)

```xml
<gazebo reference="camera_link">
  <sensor name="depth_camera" type="depth">
    <update_rate>20</update_rate>
    <camera>
      <horizontal_fov>1.047</horizontal_fov>
      <image>
        <width>640</width>
        <height>480</height>
      </image>
      <clip>
        <near>0.3</near>
        <far>10.0</far>
      </clip>
    </camera>
    <plugin name="depth_camera_controller" filename="libgazebo_ros_camera.so">
      <ros>
        <namespace>/humanoid</namespace>
        <remapping>depth/image_raw:=depth/image_raw</remapping>
        <remapping>depth/points:=depth/points</remapping>
      </ros>
      <camera_name>depth_camera</camera_name>
      <frame_name>camera_link</frame_name>
      <min_depth>0.3</min_depth>
      <max_depth>10.0</max_depth>
    </plugin>
  </sensor>
</gazebo>
```

### IMU پلگ ان

```xml
<gazebo reference="imu_link">
  <sensor name="imu" type="imu">
    <always_on>true</always_on>
    <update_rate>100</update_rate>
    <imu>
      <angular_velocity>
        <x>
          <noise type="gaussian">
            <mean>0.0</mean>
            <stddev>0.0002</stddev>
          </noise>
        </x>
        <y>
          <noise type="gaussian">
            <mean>0.0</mean>
            <stddev>0.0002</stddev>
          </noise>
        </y>
        <z>
          <noise type="gaussian">
            <mean>0.0</mean>
            <stddev>0.0002</stddev>
          </noise>
        </z>
      </angular_velocity>
      <linear_acceleration>
        <x>
          <noise type="gaussian">
            <mean>0.0</mean>
            <stddev>0.017</stddev>
          </noise>
        </x>
        <y>
          <noise type="gaussian">
            <mean>0.0</mean>
            <stddev>0.017</stddev>
          </noise>
        </y>
        <z>
          <noise type="gaussian">
            <mean>0.0</mean>
            <stddev>0.017</stddev>
          </noise>
        </z>
      </linear_acceleration>
    </imu>
    <plugin name="imu_plugin" filename="libgazebo_ros_imu_sensor.so">
      <ros>
        <namespace>/humanoid</namespace>
        <remapping>~/out:=imu/data</remapping>
      </ros>
      <frame_name>imu_link</frame_name>
    </plugin>
  </sensor>
</gazebo>
```

### LiDAR پلگ ان

```xml
<gazebo reference="lidar_link">
  <sensor name="lidar" type="ray">
    <always_on>true</always_on>
    <update_rate>10</update_rate>
    <ray>
      <scan>
        <horizontal>
          <samples>360</samples>
          <resolution>1</resolution>
          <min_angle>-3.14159</min_angle>
          <max_angle>3.14159</max_angle>
        </horizontal>
        <vertical>
          <samples>16</samples>
          <resolution>1</resolution>
          <min_angle>-0.261799</min_angle>
          <max_angle>0.261799</max_angle>
        </vertical>
      </scan>
      <range>
        <min>0.3</min>
        <max>30.0</max>
        <resolution>0.01</resolution>
      </range>
    </ray>
    <plugin name="lidar_controller" filename="libgazebo_ros_ray_sensor.so">
      <ros>
        <namespace>/humanoid</namespace>
        <remapping>~/out:=scan</remapping>
      </ros>
      <output_type>sensor_msgs/LaserScan</output_type>
      <frame_name>lidar_link</frame_name>
    </plugin>
  </sensor>
</gazebo>
```

## جوائنٹ کنٹرول پلگ ان

### جوائنٹ حالت شائع کرنے والا

```xml
<gazebo>
  <plugin name="gazebo_ros_joint_state_publisher"
          filename="libgazebo_ros_joint_state_publisher.so">
    <ros>
      <namespace>/humanoid</namespace>
      <remapping>~/out:=joint_states</remapping>
    </ros>
    <update_rate>50</update_rate>
  </plugin>
</gazebo>
```

### پوزیشن کنٹرول

```xml
<gazebo>
  <plugin name="gazebo_ros_joint_pose_trajectory"
          filename="libgazebo_ros_joint_pose_trajectory.so">
    <ros>
      <namespace>/humanoid</namespace>
      <remapping>~/set_joint_trajectory:=set_joint_trajectory</remapping>
    </ros>
    <update_rate>100</update_rate>
  </plugin>
</gazebo>
```

کمانڈز بھیجیں:

```python
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint

class JointCommander(Node):
    def __init__(self):
        super().__init__('joint_commander')
        self.publisher = self.create_publisher(
            JointTrajectory,
            '/humanoid/set_joint_trajectory',
            10
        )

    def send_trajectory(self):
        msg = JointTrajectory()
        msg.joint_names = ['left_shoulder_pitch', 'left_elbow']

        point = JointTrajectoryPoint()
        point.positions = [1.57, 1.0]
        point.time_from_start.sec = 2

        msg.points = [point]
        self.publisher.publish(msg)
```

## رابطہ سینسرز

توازن کے لیے پاؤں کے رابطوں کا پتہ لگائیں:

```xml
<gazebo reference="left_foot">
  <sensor name="left_foot_contact" type="contact">
    <always_on>true</always_on>
    <update_rate>100</update_rate>
    <contact>
      <collision>left_foot_collision</collision>
    </contact>
    <plugin name="left_foot_contact_plugin"
            filename="libgazebo_ros_bumper_sensor.so">
      <ros>
        <namespace>/humanoid</namespace>
        <remapping>~/out:=left_foot_contact</remapping>
      </ros>
      <frame_name>left_foot</frame_name>
    </plugin>
  </sensor>
</gazebo>
```

## مکمل سمولیشن مثال

یہاں ایک مکمل لانچ سیٹ اپ ہے:

```python
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, Command
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    pkg_dir = get_package_share_directory('humanoid_gazebo')

    # آرگومنٹس
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    gui = LaunchConfiguration('gui', default='true')
    headless = LaunchConfiguration('headless', default='false')

    # فائلیں
    urdf_file = os.path.join(pkg_dir, 'urdf', 'humanoid.urdf.xacro')
    world_file = os.path.join(pkg_dir, 'worlds', 'indoor.world')
    rviz_config = os.path.join(pkg_dir, 'rviz', 'simulation.rviz')

    # روبوٹ کی تفصیل
    robot_description = Command([
        'xacro ', urdf_file,
        ' use_sim_time:=', use_sim_time
    ])

    # Gazebo
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(get_package_share_directory('gazebo_ros'),
                        'launch', 'gazebo.launch.py')
        ]),
        launch_arguments={
            'world': world_file,
            'gui': gui,
            'headless': headless
        }.items()
    )

    # روبوٹ Spawn کریں
    spawn = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-entity', 'humanoid',
            '-topic', 'robot_description',
            '-x', '0', '-y', '0', '-z', '1.1'
        ]
    )

    # روبوٹ کی حالت شائع کرنے والا
    robot_state_pub = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{
            'robot_description': robot_description,
            'use_sim_time': use_sim_time
        }]
    )

    # RViz
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', rviz_config],
        parameters=[{'use_sim_time': use_sim_time}]
    )

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        DeclareLaunchArgument('gui', default_value='true'),
        DeclareLaunchArgument('headless', default_value='false'),
        gazebo,
        robot_state_pub,
        spawn,
        rviz
    ])
```

## کارکردگی کی اصلاح

### 1. طبیعیات کے قدم کا سائز کم کریں

```xml
<physics>
  <max_step_size>0.002</max_step_size>  <!-- 0.001 سے بڑھائیں -->
  <real_time_factor>1.0</real_time_factor>
</physics>
```

### 2. ٹکراؤ کی Meshes کو آسان بنائیں

پیچیدہ meshes کے بجائے primitive shapes استعمال کریں۔

### 3. GPU تیز رفتاری

کیمرہ سینسرز کے لیے:

```xml
<camera>
  <image>
    <width>320</width>  <!-- کم ریزولوشن -->
    <height>240</height>
  </image>
</camera>
```

### 4. غیر استعمال شدہ سینسرز کو غیر فعال کریں

جن سینسرز کی آپ کو ضرورت نہیں انہیں کمنٹ آؤٹ کریں۔

## خلاصہ

اس ہفتے آپ نے سیکھا:

- Gazebo فن تعمیر اور طبیعیات کے انجن
- SDF ورلڈ فائل فارمیٹ
- ROS 2 کے ساتھ Gazebo میں روبوٹس شروع کرنا
- کیمرہ، گہرائی، IMU، اور LiDAR سینسر پلگ ان
- جوائنٹ کنٹرول اور رابطہ سینسرز
- کارکردگی کی اصلاح کی تکنیکیں
- مکمل سمولیشن لانچ فائلیں

## اگلا کیا ہے؟

**ہفتہ 6: روبوٹ کی تصویر سازی کے لیے Unity** - فوٹو ریئلسٹک رینڈرنگ اور مصنوعی ڈیٹا کی تخلیق کے لیے Unity Robotics Hub دریافت کریں۔

**اگلا**: [ہفتہ 6: Unity انضمام →](./week6-unity.md)
