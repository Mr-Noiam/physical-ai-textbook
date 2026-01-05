[TRANSLATION_FAILED] # Week 5: Gazebo Physics Simulation

[TRANSLATION_FAILED] ## Introduction

[TRANSLATION_FAILED] This week, we'll launch your humanoid robot in **Gazebo**, the most popular robot simulator for ROS 2. You'll learn about physics engines, world files, sensor plugins, and how to create realistic simulation environments for testing Physical AI systems.

[TRANSLATION_FAILED] ## What is Gazebo?

[TRANSLATION_FAILED] **Gazebo** (now called **Gazebo Classic**) is a 3D robot simulator that provides:

[TRANSLATION_FAILED] - **Realistic physics**: ODE, Bullet, Simbody, DART engines
[TRANSLATION_FAILED] - **Sensor simulation**: Camera, LiDAR, IMU, force/torque
[TRANSLATION_FAILED] - **GPU acceleration**: For vision sensors and large scenes
[TRANSLATION_FAILED] - **ROS 2 integration**: Native message passing

[TRANSLATION_FAILED] **Gazebo Fortress/Garden** (new generation) uses SDF format and Ignition libraries.

[TRANSLATION_FAILED] ## SDF vs URDF

[TRANSLATION_FAILED] **SDF (Simulation Description Format)** is more powerful than URDF:

[TRANSLATION_FAILED] | Feature | URDF | SDF |
[TRANSLATION_FAILED] |---------|------|-----|
[TRANSLATION_FAILED] | **Worlds** | No | Yes |
[TRANSLATION_FAILED] | **Closed loops** | No | Yes |
[TRANSLATION_FAILED] | **Multiple robots** | Limited | Yes |
[TRANSLATION_FAILED] | **Sensors** | Via plugins | Native |
[TRANSLATION_FAILED] | **Version control** | No | Yes |

[TRANSLATION_FAILED] URDF can be automatically converted to SDF by Gazebo.

[TRANSLATION_FAILED] ## World Files: Creating Environments

[TRANSLATION_FAILED] A Gazebo world defines the environment:

```xml
<?xml version="1.0"?>
<sdf version="1.7">
  <world name="humanoid_world">

    <!-- Physics engine -->
    <physics name="default_physics" type="ode">
      <max_step_size>0.001</max_step_size>
      <real_time_factor>1.0</real_time_factor>
      <real_time_update_rate>1000</real_time_update_rate>
    </physics>

    <!-- Lighting -->
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

    <!-- Ground plane -->
    <include>
      <uri>model://ground_plane</uri>
    </include>

    <!-- Include models from Gazebo model database -->
    <include>
      <uri>model://cafe</uri>
      <pose>3 0 0 0 0 0</pose>
    </include>

    <!-- Custom obstacle -->
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

[TRANSLATION_FAILED] ## Physics Engines

[TRANSLATION_FAILED] ### ODE (Open Dynamics Engine)

[TRANSLATION_FAILED] Default in Gazebo Classic. Good for general robotics:

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

[TRANSLATION_FAILED] ### Bullet

[TRANSLATION_FAILED] Better for complex contacts:

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

[TRANSLATION_FAILED] ### DART

[TRANSLATION_FAILED] Best for humanoid dynamics:

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

[TRANSLATION_FAILED] ## Launching Humanoid in Gazebo

[TRANSLATION_FAILED] Create `launch/gazebo_humanoid.launch.py`:

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

    # URDF file
    urdf_file = os.path.join(pkg_dir, 'urdf', 'humanoid.urdf.xacro')
    robot_description = Command(['xacro ', urdf_file])

    # World file
    world_file = os.path.join(pkg_dir, 'worlds', 'humanoid_world.world')

    # Gazebo launch
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(get_package_share_directory('gazebo_ros'),
                        'launch', 'gazebo.launch.py')
        ]),
        launch_arguments={'world': world_file, 'verbose': 'true'}.items()
    )

    # Spawn robot
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

    # Robot state publisher
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

[TRANSLATION_FAILED] Launch:

```bash
ros2 launch humanoid_gazebo gazebo_humanoid.launch.py
```

[TRANSLATION_FAILED] ## Sensor Plugins

[TRANSLATION_FAILED] ### Camera Plugin

[TRANSLATION_FAILED] Add to URDF:

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

[TRANSLATION_FAILED] Subscribe to camera:

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

[TRANSLATION_FAILED] ### Depth Camera (RGB-D)

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

[TRANSLATION_FAILED] ### IMU Plugin

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

[TRANSLATION_FAILED] ### LiDAR Plugin

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

[TRANSLATION_FAILED] ## Joint Control Plugins

[TRANSLATION_FAILED] ### Joint State Publisher

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

[TRANSLATION_FAILED] ### Position Control

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

[TRANSLATION_FAILED] Send commands:

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

[TRANSLATION_FAILED] ## Contact Sensors

[TRANSLATION_FAILED] Detect foot contacts for balance:

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

[TRANSLATION_FAILED] ## Complete Simulation Example

[TRANSLATION_FAILED] Here's a full launch setup:

```python
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, Command
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    pkg_dir = get_package_share_directory('humanoid_gazebo')

    # Arguments
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    gui = LaunchConfiguration('gui', default='true')
    headless = LaunchConfiguration('headless', default='false')

    # Files
    urdf_file = os.path.join(pkg_dir, 'urdf', 'humanoid.urdf.xacro')
    world_file = os.path.join(pkg_dir, 'worlds', 'indoor.world')
    rviz_config = os.path.join(pkg_dir, 'rviz', 'simulation.rviz')

    # Robot description
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

    # Spawn robot
    spawn = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-entity', 'humanoid',
            '-topic', 'robot_description',
            '-x', '0', '-y', '0', '-z', '1.1'
        ]
    )

    # Robot state publisher
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

[TRANSLATION_FAILED] ## Performance Optimization

[TRANSLATION_FAILED] ### 1. Reduce Physics Step Size

```xml
<physics>
  <max_step_size>0.002</max_step_size>  <!-- Increase from 0.001 -->
  <real_time_factor>1.0</real_time_factor>
</physics>
```

[TRANSLATION_FAILED] ### 2. Simplify Collision Meshes

[TRANSLATION_FAILED] Use primitive shapes instead of complex meshes.

[TRANSLATION_FAILED] ### 3. GPU Acceleration

[TRANSLATION_FAILED] For camera sensors:

```xml
<camera>
  <image>
    <width>320</width>  <!-- Lower resolution -->
    <height>240</height>
  </image>
</camera>
```

[TRANSLATION_FAILED] ### 4. Disable Unused Sensors

[TRANSLATION_FAILED] Comment out sensors you don't need.

[TRANSLATION_FAILED] ## Summary

[TRANSLATION_FAILED] This week you learned:

[TRANSLATION_FAILED] - Gazebo architecture and physics engines
[TRANSLATION_FAILED] - SDF world file format
[TRANSLATION_FAILED] - Launching robots in Gazebo with ROS 2
[TRANSLATION_FAILED] - Camera, depth, IMU, and LiDAR sensor plugins
[TRANSLATION_FAILED] - Joint control and contact sensors
[TRANSLATION_FAILED] - Performance optimization techniques
[TRANSLATION_FAILED] - Complete simulation launch files

[TRANSLATION_FAILED] ## What's Next?

[TRANSLATION_FAILED] **Week 6: Unity for Robot Visualization** - Explore Unity Robotics Hub for photorealistic rendering and synthetic data generation.

[TRANSLATION_FAILED] **Next**: [Week 6: Unity Integration →](./week6-unity.md)
