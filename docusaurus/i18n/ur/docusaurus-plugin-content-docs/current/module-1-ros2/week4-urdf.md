# Week 4: URDF for Humanoid Robot Descriptions

## Introduction

This week, we'll learn to describe humanoid robots using **URDF** (Unified Robot Description Format). URDF is an XML-based format that defines robot kinematics, geometry, and visual appearance. You'll build a complete 28-DOF humanoid model ready for simulation and control.

## What is URDF?

**URDF** describes robots as a tree of links and joints:

- **Links**: Rigid bodies (torso, limbs, sensors)
- **Joints**: Connections between links (revolute, prismatic, fixed)

```xml
<robot name="my_robot">
  <link name="base_link">
    <visual>...</visual>
    <collision>...</collision>
    <inertial>...</inertial>
  </link>

  <joint name="joint1" type="revolute">
    <parent link="base_link"/>
    <child link="link1"/>
    <axis xyz="0 0 1"/>
    <limit effort="100" velocity="1.0" lower="-3.14" upper="3.14"/>
  </joint>

  <link name="link1">...</link>
</robot>
```

## URDF Link Structure

A link has three components:

### 1. Visual (Appearance)

```xml
<visual>
  <origin xyz="0 0 0" rpy="0 0 0"/>
  <geometry>
    <box size="0.1 0.1 0.2"/>
    <!-- OR -->
    <cylinder radius="0.05" length="0.2"/>
    <!-- OR -->
    <sphere radius="0.05"/>
    <!-- OR -->
    <mesh filename="package://my_robot/meshes/torso.stl" scale="1.0 1.0 1.0"/>
  </geometry>
  <material name="blue">
    <color rgba="0 0 1 1"/>
  </material>
</visual>
```

### 2. Collision (Physics)

```xml
<collision>
  <origin xyz="0 0 0" rpy="0 0 0"/>
  <geometry>
    <!-- Simpler geometry than visual for performance -->
    <box size="0.1 0.1 0.2"/>
  </geometry>
</collision>
```

### 3. Inertial (Dynamics)

```xml
<inertial>
  <origin xyz="0 0 0.1" rpy="0 0 0"/>
  <mass value="5.0"/>
  <inertia ixx="0.015" ixy="0.0" ixz="0.0"
           iyy="0.015" iyz="0.0" izz="0.005"/>
</inertial>
```

Calculate inertia for common shapes:

**Box** (m, w, h, d):
```
ixx = (m/12) * (h² + d²)
iyy = (m/12) * (w² + d²)
izz = (m/12) * (w² + h²)
```

**Cylinder** (m, r, h):
```
ixx = (m/12) * (3r² + h²)
iyy = (m/12) * (3r² + h²)
izz = (m/2) * r²
```

## URDF Joint Types

### 1. Revolute (Rotational)

```xml
<joint name="shoulder_pitch" type="revolute">
  <parent link="torso"/>
  <child link="upper_arm"/>
  <origin xyz="0 0.15 0.4" rpy="0 0 0"/>
  <axis xyz="0 1 0"/>  <!-- Y-axis rotation -->
  <limit effort="100" velocity="2.0" lower="-3.14" upper="3.14"/>
  <dynamics damping="0.7" friction="0.1"/>
</joint>
```

### 2. Continuous (Unlimited Rotation)

```xml
<joint name="wheel_joint" type="continuous">
  <parent link="base"/>
  <child link="wheel"/>
  <axis xyz="0 1 0"/>
  <limit effort="50" velocity="10.0"/>
</joint>
```

### 3. Prismatic (Linear)

```xml
<joint name="telescoping_leg" type="prismatic">
  <parent link="upper_leg"/>
  <child link="lower_leg"/>
  <axis xyz="0 0 1"/>
  <limit effort="500" velocity="1.0" lower="0.0" upper="0.3"/>
</joint>
```

### 4. Fixed (Rigid Connection)

```xml
<joint name="camera_mount" type="fixed">
  <parent link="head"/>
  <child link="camera_link"/>
  <origin xyz="0.05 0 0.1" rpy="0 0 0"/>
</joint>
```

## Humanoid URDF Example: Upper Body

Let's build the torso and arms:

```xml
<?xml version="1.0"?>
<robot name="humanoid">

  <!-- Base link (reference frame) -->
  <link name="base_link"/>

  <!-- Torso -->
  <link name="torso">
    <visual>
      <geometry>
        <box size="0.3 0.4 0.6"/>
      </geometry>
      <material name="gray">
        <color rgba="0.5 0.5 0.5 1"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <box size="0.3 0.4 0.6"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="30.0"/>
      <inertia ixx="1.95" ixy="0" ixz="0"
               iyy="1.65" iyz="0" izz="1.05"/>
    </inertial>
  </link>

  <joint name="base_to_torso" type="fixed">
    <parent link="base_link"/>
    <child link="torso"/>
    <origin xyz="0 0 1.0" rpy="0 0 0"/>
  </joint>

  <!-- Left Shoulder Assembly -->
  <link name="left_shoulder_pitch_link">
    <visual>
      <geometry>
        <cylinder radius="0.04" length="0.08"/>
      </geometry>
      <material name="red">
        <color rgba="1 0 0 1"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <cylinder radius="0.04" length="0.08"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="0.5"/>
      <inertia ixx="0.0001" ixy="0" ixz="0"
               iyy="0.0001" iyz="0" izz="0.0001"/>
    </inertial>
  </link>

  <joint name="left_shoulder_pitch" type="revolute">
    <parent link="torso"/>
    <child link="left_shoulder_pitch_link"/>
    <origin xyz="0 0.22 0.25" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>
    <limit effort="100" velocity="2.0" lower="-3.14" upper="3.14"/>
    <dynamics damping="0.7"/>
  </joint>

  <!-- Left Upper Arm -->
  <link name="left_upper_arm">
    <visual>
      <origin xyz="0 0 -0.15" rpy="0 0 0"/>
      <geometry>
        <cylinder radius="0.04" length="0.3"/>
      </geometry>
      <material name="gray"/>
    </visual>
    <collision>
      <origin xyz="0 0 -0.15" rpy="0 0 0"/>
      <geometry>
        <cylinder radius="0.04" length="0.3"/>
      </geometry>
    </collision>
    <inertial>
      <origin xyz="0 0 -0.15" rpy="0 0 0"/>
      <mass value="2.0"/>
      <inertia ixx="0.015" ixy="0" ixz="0"
               iyy="0.015" iyz="0" izz="0.001"/>
    </inertial>
  </link>

  <joint name="left_shoulder_roll" type="revolute">
    <parent link="left_shoulder_pitch_link"/>
    <child link="left_upper_arm"/>
    <origin xyz="0 0.04 0" rpy="0 0 0"/>
    <axis xyz="1 0 0"/>
    <limit effort="100" velocity="2.0" lower="-1.57" upper="3.14"/>
    <dynamics damping="0.7"/>
  </joint>

  <!-- Left Elbow -->
  <link name="left_forearm">
    <visual>
      <origin xyz="0 0 -0.125" rpy="0 0 0"/>
      <geometry>
        <cylinder radius="0.03" length="0.25"/>
      </geometry>
      <material name="gray"/>
    </visual>
    <collision>
      <origin xyz="0 0 -0.125" rpy="0 0 0"/>
      <geometry>
        <cylinder radius="0.03" length="0.25"/>
      </geometry>
    </collision>
    <inertial>
      <origin xyz="0 0 -0.125" rpy="0 0 0"/>
      <mass value="1.5"/>
      <inertia ixx="0.008" ixy="0" ixz="0"
               iyy="0.008" iyz="0" izz="0.001"/>
    </inertial>
  </link>

  <joint name="left_elbow" type="revolute">
    <parent link="left_upper_arm"/>
    <child link="left_forearm"/>
    <origin xyz="0 0 -0.3" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>
    <limit effort="80" velocity="2.5" lower="0" upper="2.6"/>
    <dynamics damping="0.5"/>
  </joint>

</robot>
```

## Complete 28-DOF Humanoid URDF

Here's a simplified full body (key sections):

```xml
<?xml version="1.0"?>
<robot name="humanoid_28dof">

  <material name="gray"><color rgba="0.5 0.5 0.5 1"/></material>
  <material name="red"><color rgba="1 0 0 1"/></material>
  <material name="blue"><color rgba="0 0 1 1"/></material>

  <!-- Torso -->
  <link name="base_link"/>
  <link name="torso">
    <visual>
      <geometry><box size="0.3 0.4 0.6"/></geometry>
      <material name="gray"/>
    </visual>
    <collision>
      <geometry><box size="0.3 0.4 0.6"/></geometry>
    </collision>
    <inertial>
      <mass value="30"/>
      <inertia ixx="1.95" iyy="1.65" izz="1.05" ixy="0" ixz="0" iyz="0"/>
    </inertial>
  </link>
  <joint name="base_to_torso" type="fixed">
    <parent link="base_link"/>
    <child link="torso"/>
    <origin xyz="0 0 1.0"/>
  </joint>

  <!-- Head -->
  <link name="head">
    <visual>
      <geometry><sphere radius="0.12"/></geometry>
      <material name="gray"/>
    </visual>
    <collision>
      <geometry><sphere radius="0.12"/></geometry>
    </collision>
    <inertial>
      <mass value="4.0"/>
      <inertia ixx="0.02" iyy="0.02" izz="0.02" ixy="0" ixz="0" iyz="0"/>
    </inertial>
  </link>
  <joint name="neck_pitch" type="revolute">
    <parent link="torso"/>
    <child link="head"/>
    <origin xyz="0 0 0.35" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>
    <limit effort="30" velocity="1.5" lower="-0.5" upper="0.5"/>
  </joint>

  <!-- Left Leg Chain: hip (3 DOF) + knee (1 DOF) + ankle (2 DOF) -->
  <link name="left_hip_yaw_link">
    <visual>
      <geometry><cylinder radius="0.04" length="0.06"/></geometry>
      <material name="red"/>
    </visual>
    <inertial>
      <mass value="0.5"/>
      <inertia ixx="0.0001" iyy="0.0001" izz="0.0001" ixy="0" ixz="0" iyz="0"/>
    </inertial>
  </link>
  <joint name="left_hip_yaw" type="revolute">
    <parent link="torso"/>
    <child link="left_hip_yaw_link"/>
    <origin xyz="0 0.1 -0.3" rpy="0 0 0"/>
    <axis xyz="0 0 1"/>
    <limit effort="200" velocity="1.5" lower="-0.5" upper="0.5"/>
  </joint>

  <link name="left_upper_leg">
    <visual>
      <origin xyz="0 0 -0.2"/>
      <geometry><cylinder radius="0.05" length="0.4"/></geometry>
      <material name="gray"/>
    </visual>
    <collision>
      <origin xyz="0 0 -0.2"/>
      <geometry><cylinder radius="0.05" length="0.4"/></geometry>
    </collision>
    <inertial>
      <origin xyz="0 0 -0.2"/>
      <mass value="8.0"/>
      <inertia ixx="0.11" iyy="0.11" izz="0.01" ixy="0" ixz="0" iyz="0"/>
    </inertial>
  </link>
  <joint name="left_hip_pitch" type="revolute">
    <parent link="left_hip_yaw_link"/>
    <child link="left_upper_leg"/>
    <origin xyz="0 0 0" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>
    <limit effort="250" velocity="2.0" lower="-2.5" upper="2.5"/>
  </joint>

  <link name="left_lower_leg">
    <visual>
      <origin xyz="0 0 -0.175"/>
      <geometry><cylinder radius="0.04" length="0.35"/></geometry>
      <material name="gray"/>
    </visual>
    <collision>
      <origin xyz="0 0 -0.175"/>
      <geometry><cylinder radius="0.04" length="0.35"/></geometry>
    </collision>
    <inertial>
      <origin xyz="0 0 -0.175"/>
      <mass value="5.0"/>
      <inertia ixx="0.05" iyy="0.05" izz="0.005" ixy="0" ixz="0" iyz="0"/>
    </inertial>
  </link>
  <joint name="left_knee" type="revolute">
    <parent link="left_upper_leg"/>
    <child link="left_lower_leg"/>
    <origin xyz="0 0 -0.4" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>
    <limit effort="200" velocity="2.5" lower="0" upper="2.6"/>
  </joint>

  <link name="left_foot">
    <visual>
      <origin xyz="0.05 0 -0.025"/>
      <geometry><box size="0.2 0.1 0.05"/></geometry>
      <material name="blue"/>
    </visual>
    <collision>
      <origin xyz="0.05 0 -0.025"/>
      <geometry><box size="0.2 0.1 0.05"/></geometry>
    </collision>
    <inertial>
      <origin xyz="0.05 0 -0.025"/>
      <mass value="1.0"/>
      <inertia ixx="0.001" iyy="0.004" izz="0.004" ixy="0" ixz="0" iyz="0"/>
    </inertial>
  </link>
  <joint name="left_ankle_pitch" type="revolute">
    <parent link="left_lower_leg"/>
    <child link="left_foot"/>
    <origin xyz="0 0 -0.35" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>
    <limit effort="150" velocity="2.0" lower="-0.8" upper="0.8"/>
  </joint>

  <!-- Right leg: mirror of left (omitted for brevity) -->
  <!-- Right arm: mirror of left (omitted for brevity) -->

  <!-- Sensors: Camera, IMU, LiDAR -->
  <link name="camera_link">
    <visual>
      <geometry><box size="0.02 0.05 0.02"/></geometry>
      <material name="red"/>
    </visual>
    <inertial>
      <mass value="0.1"/>
      <inertia ixx="0.0001" iyy="0.0001" izz="0.0001" ixy="0" ixz="0" iyz="0"/>
    </inertial>
  </link>
  <joint name="camera_joint" type="fixed">
    <parent link="head"/>
    <child link="camera_link"/>
    <origin xyz="0.12 0 0" rpy="0 0 0"/>
  </joint>

  <link name="imu_link">
    <inertial>
      <mass value="0.05"/>
      <inertia ixx="0.00001" iyy="0.00001" izz="0.00001" ixy="0" ixz="0" iyz="0"/>
    </inertial>
  </link>
  <joint name="imu_joint" type="fixed">
    <parent link="torso"/>
    <child link="imu_link"/>
    <origin xyz="0 0 0" rpy="0 0 0"/>
  </joint>

</robot>
```

## Xacro: Macro Language for URDF

**Xacro** extends URDF with:
- Variables and constants
- Mathematical expressions
- Macros for repetitive structures

### Basic Xacro Features

```xml
<?xml version="1.0"?>
<robot xmlns:xacro="http://www.ros.org/wiki/xacro" name="humanoid">

  <!-- Constants -->
  <xacro:property name="torso_mass" value="30.0"/>
  <xacro:property name="pi" value="3.14159"/>

  <!-- Calculated values -->
  <xacro:property name="leg_length" value="${0.4 + 0.35}"/>

  <!-- Materials -->
  <material name="gray">
    <color rgba="0.5 0.5 0.5 1"/>
  </material>

  <!-- Macro for symmetric limbs -->
  <xacro:macro name="arm" params="side reflect">
    <link name="${side}_upper_arm">
      <visual>
        <origin xyz="0 0 -0.15"/>
        <geometry>
          <cylinder radius="0.04" length="0.3"/>
        </geometry>
        <material name="gray"/>
      </visual>
      <inertial>
        <origin xyz="0 0 -0.15"/>
        <mass value="2.0"/>
        <inertia ixx="0.015" iyy="0.015" izz="0.001" ixy="0" ixz="0" iyz="0"/>
      </inertial>
    </link>

    <joint name="${side}_shoulder_roll" type="revolute">
      <parent link="torso"/>
      <child link="${side}_upper_arm"/>
      <origin xyz="0 ${reflect * 0.22} 0.25" rpy="0 0 0"/>
      <axis xyz="1 0 0"/>
      <limit effort="100" velocity="2.0" lower="-1.57" upper="3.14"/>
    </joint>
  </xacro:macro>

  <!-- Instantiate for both arms -->
  <xacro:arm side="left" reflect="1"/>
  <xacro:arm side="right" reflect="-1"/>

</robot>
```

### Inertia Macro

```xml
<xacro:macro name="cylinder_inertia" params="mass radius length">
  <inertial>
    <mass value="${mass}"/>
    <inertia ixx="${(mass/12) * (3*radius*radius + length*length)}"
             iyy="${(mass/12) * (3*radius*radius + length*length)}"
             izz="${(mass/2) * radius*radius}"
             ixy="0" ixz="0" iyz="0"/>
  </inertial>
</xacro:macro>

<!-- Usage -->
<link name="leg">
  <xacro:cylinder_inertia mass="5.0" radius="0.05" length="0.4"/>
</link>
```

## Loading URDF in ROS 2

### robot_state_publisher

Publishes robot transforms to `/tf`:

```python
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import Command
import os

def generate_launch_description():
    urdf_file = os.path.join(
        get_package_share_directory('my_robot'),
        'urdf', 'humanoid.urdf.xacro'
    )

    # Process xacro to URDF
    robot_description = Command(['xacro ', urdf_file])

    # Publish robot state
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': robot_description}]
    )

    # Publish joint states
    joint_state_publisher = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui'
    )

    return LaunchDescription([
        robot_state_publisher,
        joint_state_publisher
    ])
```

### Visualize in RViz

```bash
# Launch robot description
ros2 launch my_robot display.launch.py

# RViz will show the robot model
# Add displays: RobotModel, TF
```

## Gazebo Integration

Add Gazebo-specific tags:

```xml
<gazebo reference="torso">
  <material>Gazebo/Grey</material>
  <mu1>0.9</mu1>  <!-- Friction -->
  <mu2>0.9</mu2>
</gazebo>

<gazebo reference="left_knee">
  <implicitSpringDamper>true</implicitSpringDamper>
</gazebo>

<!-- Gazebo plugins -->
<gazebo>
  <plugin name="gazebo_ros_control" filename="libgazebo_ros_control.so">
    <robotNamespace>/</robotNamespace>
  </plugin>
</gazebo>
```

## Best Practices

### 1. Coordinate Frames
- Z-axis up (ROS convention)
- X-axis forward
- Right-hand rule for rotations

### 2. Mass Distribution
- Total mass should match target robot
- Center of mass affects balance
- Use realistic inertia values

### 3. Joint Limits
- Set realistic position limits
- Velocity limits based on actuators
- Effort limits prevent damage in simulation

### 4. Collision Geometry
- Use simpler shapes than visual
- Convex hulls for complex meshes
- Avoid self-collisions

### 5. Organization
```
my_robot/
├── urdf/
│   ├── humanoid.urdf.xacro       # Main file
│   ├── torso.xacro               # Modular components
│   ├── arm.xacro
│   ├── leg.xacro
│   └── sensors.xacro
├── meshes/
│   ├── visual/
│   │   └── torso.stl
│   └── collision/
│       └── torso_collision.stl
└── launch/
    └── display.launch.py
```

## Testing Your URDF

### Check URDF Validity

```bash
check_urdf humanoid.urdf
```

Output shows link tree and joint info.

### Visualize Joint Limits

```bash
urdf_to_graphiz humanoid.urdf
```

Generates PDF showing kinematic tree.

## Summary

This week you learned:

- URDF syntax for links and joints
- Visual, collision, and inertial properties
- Joint types: revolute, continuous, prismatic, fixed
- Building a 28-DOF humanoid URDF
- Xacro macros for code reuse
- Loading URDF with robot_state_publisher
- Visualizing in RViz
- Gazebo integration tags
- Best practices for URDF organization

## What's Next?

**Week 5: Gazebo Physics Simulation** - Launch your humanoid in Gazebo, add physics, and integrate sensors.

**Next**: [Week 5: Gazebo Simulation →](../module-2-gazebo/week5-simulation.md)
