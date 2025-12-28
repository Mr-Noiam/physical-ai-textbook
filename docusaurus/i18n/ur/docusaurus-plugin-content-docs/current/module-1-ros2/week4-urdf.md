# ہفتہ 4: ہیومینائیڈ روبوٹ کی تفصیلات کے لیے URDF

## تعارف

اس ہفتے، ہم سیکھیں گے کہ کس طرح **URDF** (Unified Robot Description Format) کا استعمال کرتے ہوئے انسانی شکل کے روبوٹوں کی وضاحت کی جائے۔ URDF ایک XML پر مبنی فارمیٹ ہے جو روبوٹ کی حرکیات، جیومیٹری، اور بصری ظاہری شکل کی وضاحت کرتا ہے۔ آپ ایک مکمل 28-DOF انسانی شکل کا ماڈل بنائیں گے جو سمولیشن اور کنٹرول کے لیے تیار ہوگا۔

## URDF کیا ہے؟

**URDF** روبوٹس کو لنکس اور جوائنٹس کے درخت کے طور پر بیان کرتا ہے:

- **لنکس**: سخت جسم (دھڑ، اعضاء، سینسرز)
- **جوائنٹس**: لنکس کے درمیان کنکشن (گھومنے والے، پرزماٹک، مقررہ)

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

## URDF لنک کی ساخت

ایک لنک میں تین اجزاء ہوتے ہیں:

### 1. بصری (ظاہری شکل)

```xml
<visual>
  <origin xyz="0 0 0" rpy="0 0 0"/>
  <geometry>
    <box size="0.1 0.1 0.2"/>
    <!-- یا -->
    <cylinder radius="0.05" length="0.2"/>
    <!-- یا -->
    <sphere radius="0.05"/>
    <!-- یا -->
    <mesh filename="package://my_robot/meshes/torso.stl" scale="1.0 1.0 1.0"/>
  </geometry>
  <material name="blue">
    <color rgba="0 0 1 1"/>
  </material>
</visual>
```

### 2. ٹکراؤ (طبیعیات)

```xml
<collision>
  <origin xyz="0 0 0" rpy="0 0 0"/>
  <geometry>
    <!-- کارکردگی کے لیے بصری سے آسان جیومیٹری -->
    <box size="0.1 0.1 0.2"/>
  </geometry>
</collision>
```

### 3. جمودی (حرکیات)

```xml
<inertial>
  <origin xyz="0 0 0.1" rpy="0 0 0"/>
  <mass value="5.0"/>
  <inertia ixx="0.015" ixy="0.0" ixz="0.0"
           iyy="0.015" iyz="0.0" izz="0.005"/>
</inertial>
```

عام شکلوں کے لیے جمود کا حساب لگائیں:

**باکس** (m, w, h, d):
```
ixx = (m/12) * (h² + d²)
iyy = (m/12) * (w² + d²)
izz = (m/12) * (w² + h²)
```

**سلنڈر** (m, r, h):
```
ixx = (m/12) * (3r² + h²)
iyy = (m/12) * (3r² + h²)
izz = (m/2) * r²
```

## URDF جوائنٹ کی اقسام

### 1. گھومنے والا (Revolute)

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

### 2. مسلسل (لامحدود گردش)

```xml
<joint name="wheel_joint" type="continuous">
  <parent link="base"/>
  <child link="wheel"/>
  <axis xyz="0 1 0"/>
  <limit effort="50" velocity="10.0"/>
</joint>
```

### 3. پرزماٹک (لکیری)

```xml
<joint name="telescoping_leg" type="prismatic">
  <parent link="upper_leg"/>
  <child link="lower_leg"/>
  <axis xyz="0 0 1"/>
  <limit effort="500" velocity="1.0" lower="0.0" upper="0.3"/>
</joint>
```

### 4. مقررہ (سخت کنکشن)

```xml
<joint name="camera_mount" type="fixed">
  <parent link="head"/>
  <child link="camera_link"/>
  <origin xyz="0.05 0 0.1" rpy="0 0 0"/>
</joint>
```

## ہیومینائیڈ URDF مثال: اوپری جسم

آئیے دھڑ اور بازوؤں کو بنائیں:

```xml
<?xml version="1.0"?>
<robot name="humanoid">

  <!-- بنیادی لنک (حوالہ جاتی فریم) -->
  <link name="base_link"/>

  <!-- دھڑ -->
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

  <!-- بائیں کندھے کی اسمبلی -->
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

  <!-- بائیں اوپری بازو -->
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

  <!-- بائیں کہنی -->
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

## مکمل 28-DOF ہیومینائیڈ URDF

یہاں ایک آسان مکمل جسم ہے (کلیدی حصے):

```xml
<?xml version="1.0"?>
<robot name="humanoid_28dof">

  <material name="gray"><color rgba="0.5 0.5 0.5 1"/></material>
  <material name="red"><color rgba="1 0 0 1"/></material>
  <material name="blue"><color rgba="0 0 1 1"/></material>

  <!-- دھڑ -->
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

  <!-- سر -->
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

  <!-- بائیں ٹانگ کی زنجیر: کولہا (3 DOF) + گھٹنا (1 DOF) + ٹخنا (2 DOF) -->
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

  <!-- دائیں ٹانگ: بائیں کا عکس (مختصر کے لیے چھوڑ دیا گیا) -->
  <!-- دائیں بازو: بائیں کا عکس (مختصر کے لیے چھوڑ دیا گیا) -->

  <!-- سینسرز: کیمرہ، IMU، LiDAR -->
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

## Xacro: URDF کے لیے میکرو زبان

**Xacro** URDF کو بڑھاتا ہے:
- متغیرات اور مستقل
- ریاضیاتی اظہار
- دوبارہ استعمال کی ساختوں کے لیے میکروز

### بنیادی Xacro خصوصیات

```xml
<?xml version="1.0"?>
<robot xmlns:xacro="http://www.ros.org/wiki/xacro" name="humanoid">

  <!-- مستقل -->
  <xacro:property name="torso_mass" value="30.0"/>
  <xacro:property name="pi" value="3.14159"/>

  <!-- حسابی اقدار -->
  <xacro:property name="leg_length" value="${0.4 + 0.35}"/>

  <!-- مواد -->
  <material name="gray">
    <color rgba="0.5 0.5 0.5 1"/>
  </material>

  <!-- ہم آہنگ اعضاء کے لیے میکرو -->
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

  <!-- دونوں بازوؤں کے لیے فوری طور پر بنائیں -->
  <xacro:arm side="left" reflect="1"/>
  <xacro:arm side="right" reflect="-1"/>

</robot>
```

### جمود میکرو

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

<!-- استعمال -->
<link name="leg">
  <xacro:cylinder_inertia mass="5.0" radius="0.05" length="0.4"/>
</link>
```

## ROS 2 میں URDF لوڈ کرنا

### robot_state_publisher

`/tf` میں روبوٹ کی تبدیلیوں کو شائع کرتا ہے:

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

    # xacro کو URDF میں پروسیس کریں
    robot_description = Command(['xacro ', urdf_file])

    # روبوٹ کی حالت شائع کریں
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': robot_description}]
    )

    # جوائنٹ کی حالتیں شائع کریں
    joint_state_publisher = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui'
    )

    return LaunchDescription([
        robot_state_publisher,
        joint_state_publisher
    ])
```

### RViz میں دیکھیں

```bash
# روبوٹ کی تفصیل شروع کریں
ros2 launch my_robot display.launch.py

# RViz روبوٹ ماڈل دکھائے گا
# ڈسپلے شامل کریں: RobotModel, TF
```

## Gazebo انضمام

Gazebo کے مخصوص ٹیگز شامل کریں:

```xml
<gazebo reference="torso">
  <material>Gazebo/Grey</material>
  <mu1>0.9</mu1>  <!-- رگڑ -->
  <mu2>0.9</mu2>
</gazebo>

<gazebo reference="left_knee">
  <implicitSpringDamper>true</implicitSpringDamper>
</gazebo>

<!-- Gazebo پلگ ان -->
<gazebo>
  <plugin name="gazebo_ros_control" filename="libgazebo_ros_control.so">
    <robotNamespace>/</robotNamespace>
  </plugin>
</gazebo>
```

## بہترین طریقے

### 1. کوآرڈینیٹ فریمز
- Z-محور اوپر (ROS کنونشن)
- X-محور آگے
- گردش کے لیے دائیں ہاتھ کا قاعدہ

### 2. بڑے پیمانے پر تقسیم
- کل ماس ہدف روبوٹ سے میل کھانا چاہیے
- مرکز ثقل توازن پر اثر انداز ہوتا ہے
- حقیقی جمود کی اقدار استعمال کریں

### 3. جوائنٹ کی حدود
- حقیقت پسندانہ پوزیشن کی حدود مقرر کریں
- ایکچوایٹرز پر مبنی رفتار کی حدود
- کوشش کی حدود سمولیشن میں نقصان سے بچاتی ہیں

### 4. ٹکراؤ جیومیٹری
- بصری سے آسان شکلیں استعمال کریں
- پیچیدہ میش کے لیے محدب ہلز
- خود ٹکراؤ سے بچیں

### 5. تنظیم
```
my_robot/
├── urdf/
│   ├── humanoid.urdf.xacro       # مرکزی فائل
│   ├── torso.xacro               # ماڈیولر اجزاء
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

## اپنے URDF کی جانچ کرنا

### URDF کی صحت چیک کریں

```bash
check_urdf humanoid.urdf
```

آؤٹ پٹ لنک ٹری اور جوائنٹ کی معلومات دکھاتا ہے۔

### جوائنٹ کی حدود کو دیکھیں

```bash
urdf_to_graphiz humanoid.urdf
```

حرکیاتی درخت دکھانے والی PDF تیار کرتا ہے۔

## خلاصہ

اس ہفتے آپ نے سیکھا:

- لنکس اور جوائنٹس کے لیے URDF نحو
- بصری، ٹکراؤ، اور جمودی خصوصیات
- جوائنٹ کی اقسام: گھومنے والا، مسلسل، پرزماٹک، مقررہ
- 28-DOF ہیومینائیڈ URDF بنانا
- کوڈ کے دوبارہ استعمال کے لیے Xacro میکروز
- robot_state_publisher کے ساتھ URDF لوڈ کرنا
- RViz میں دیکھنا
- Gazebo انضمام ٹیگز
- URDF کی تنظیم کے لیے بہترین طریقے

## اگلا کیا ہے؟

**ہفتہ 5: Gazebo طبیعیات سمولیشن** - اپنے ہیومینائیڈ کو Gazebo میں شروع کریں، طبیعیات شامل کریں، اور سینسرز کو مربوط کریں۔

**اگلا**: [ہفتہ 5: Gazebo سمولیشن →](../module-2-gazebo/week5-simulation.md)
