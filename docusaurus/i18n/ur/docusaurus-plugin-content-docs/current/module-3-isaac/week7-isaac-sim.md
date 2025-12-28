# ہفتہ 7: NVIDIA Isaac Sim

## تعارف

**NVIDIA Isaac Sim** سب سے جدید روبوٹ سمیولیٹر ہے، Omniverse پر بنایا گیا۔ یہ RTX رے ٹریسڈ رینڈرنگ، PhysX طبیعیات، اور NVIDIA AI ٹولز کے ساتھ مقامی انضمام فراہم کرتا ہے۔ اس ہفتے، آپ ہیومینائیڈز لوڈ کریں گے، سینسرز کو ترتیب دیں گے، اور بڑے پیمانے پر مصنوعی تربیتی ڈیٹا تیار کریں گے۔

## Isaac Sim کیوں؟

**فوائد**:

- **RTX رینڈرنگ**: سم سے حقیقت کے لیے فوٹو ریئلسٹک، رے ٹریسڈ گرافکس
- **PhysX 5**: تیز سمولیشن کے لیے GPU سے تیز شدہ طبیعیات
- **USD فارمیٹ**: تعاون کے لیے یونیورسل سین Description
- **مصنوعی ڈیٹا**: ڈیٹا سیٹ کی تخلیق کے لیے بلٹ ان Replicator
- **Isaac ROS**: ROS 2 GEMs کے ساتھ براہ راست انضمام (GPU-Enabled Modules)
- **AI Workflows**: TensorRT, cuDNN, cuVSLAM, DeepStream

**استعمال کے معاملات**:
- perception ماڈلز کی تربیت
- Multi-robot coordination
- ڈیجیٹل ٹوئنز
- Reinforcement learning

## تنصیب

### ضروریات

```bash
# NVIDIA GPU ضروری (RTX سیریز تجویز کردہ)
# Ubuntu 22.04 یا Windows 11
# Driver 525+

# NVIDIA driver چیک کریں
nvidia-smi
```

### Isaac Sim

ڈاؤن لوڈ کریں: https://developer.nvidia.com/isaac-sim

```bash
# Omniverse Launcher انسٹال کریں
# Launch > Library > Isaac Sim
# Install پر کلک کریں (Isaac Sim 2023.1.0+)

# یا Docker:
docker pull nvcr.io/nvidia/isaac-sim:2023.1.0
```

### ROS 2 Bridge

```bash
# Isaac Sim میں ROS 2 Bridge فعال کریں:
# Window > Extensions > ROS/ROS 2 Bridge
# "omni.isaac.ros2_bridge" کو فعال کریں

# ROS 2 Humble انسٹال کریں (اگر پہلے سے نہیں ہے)
sudo apt install ros-humble-desktop
```

## USD فارمیٹ

**Universal Scene Description** Pixar کا تبادلہ فارمیٹ ہے:

```python
# Python USD API
from pxr import Usd, UsdGeom, Gf

# stage بنائیں
stage = Usd.Stage.CreateNew('/tmp/scene.usda')

# sphere شامل کریں
sphere = UsdGeom.Sphere.Define(stage, '/World/Sphere')
sphere.GetRadiusAttr().Set(1.0)
sphere.AddTranslateOp().Set(Gf.Vec3d(0, 0, 1))

# محفوظ کریں
stage.Save()
```

## Isaac Sim میں ہیومینائیڈ لوڈ کرنا

### طریقہ 1: URDF درآمد

```python
import omni
from omni.isaac.core.utils.extensions import enable_extension

# URDF importer فعال کریں
enable_extension("omni.importer.urdf")

import omni.kit.commands
from omni.importer.urdf import _urdf

# URDF درآمد کریں
_urdf.acquire_urdf_interface()
urdf_interface = _urdf.get_urdf_interface()

# درآمد کی ترتیب
import_config = _urdf.ImportConfig()
import_config.merge_fixed_joints = False
import_config.convex_decomp = True
import_config.import_inertia_tensor = True
import_config.fix_base = False

# درآمد کریں
success, prim_path = omni.kit.commands.execute(
    "URDFParseAndImportFile",
    urdf_path="/path/to/humanoid.urdf",
    import_config=import_config,
)

print(f"Imported humanoid at: {prim_path}")
```

### طریقہ 2: USD درآمد

```python
from omni.isaac.core.utils.stage import add_reference_to_stage

# USD asset لوڈ کریں
add_reference_to_stage(
    usd_path="/Isaac/Robots/Humanoid/humanoid.usd",
    prim_path="/World/Humanoid"
)
```

## طبیعیات کی ترتیب

```python
from omni.isaac.core import World
from omni.isaac.core.prims import RigidPrimView
from pxr import PhysxSchema

# طبیعیات کے ساتھ دنیا بنائیں
world = World(stage_units_in_meters=1.0)
world.scene.add_default_ground_plane()

# طبیعیات scene کو ترتیب دیں
physx_scene = PhysxSchema.PhysxSceneAPI.Apply(world.stage.GetPrimAtPath("/physicsScene"))
physx_scene.GetEnableGPUDynamicsAttr().Set(True)
physx_scene.GetBroadphaseTypeAttr().Set("GPU")
physx_scene.GetSolverTypeAttr().Set("TGS")

# دنیا reset کریں
world.reset()

# سمولیشن چلائیں
for i in range(1000):
    world.step(render=True)
```

## سینسرز شامل کرنا

### RGB-D کیمرہ

```python
from omni.isaac.sensor import Camera
import omni.replicator.core as rep

# کیمرہ بنائیں
camera = Camera(
    prim_path="/World/Humanoid/head/camera",
    frequency=30,
    resolution=(640, 480),
)

# RGB رینڈر کریں
camera.initialize()
rgb = camera.get_rgba()

# گہرائی حاصل کریں
depth = camera.get_depth()

# Replicator کے لیے render product بنائیں
render_product = rep.create.render_product(
    camera.prim_path,
    resolution=(640, 480)
)

# Annotators (ground truth)
rgb_annot = rep.AnnotatorRegistry.get_annotator("rgb")
depth_annot = rep.AnnotatorRegistry.get_annotator("distance_to_camera")
bbox_annot = rep.AnnotatorRegistry.get_annotator("bounding_box_2d_tight")

# render product سے منسلک کریں
rgb_annot.attach([render_product])
depth_annot.attach([render_product])
bbox_annot.attach([render_product])
```

### LiDAR

```python
from omni.isaac.range_sensor import _range_sensor

# LiDAR بنائیں
result, lidar = omni.kit.commands.execute(
    "RangeSensorCreateLidar",
    path="/World/Humanoid/lidar",
    parent="/World/Humanoid",
    min_range=0.4,
    max_range=100.0,
    draw_points=True,
    draw_lines=False,
    horizontal_fov=360.0,
    vertical_fov=30.0,
    horizontal_resolution=0.4,
    vertical_resolution=4.0,
    rotation_rate=20.0,  # Hz
    high_lod=True,
    yaw_offset=0.0,
    enable_semantics=True
)

# point cloud ڈیٹا حاصل کریں
lidar_interface = _range_sensor.acquire_lidar_sensor_interface()
depth_data = lidar_interface.get_linear_depth_data("/World/Humanoid/lidar")
```

### IMU

```python
from omni.isaac.sensor import IMUSensor

# IMU بنائیں
imu = IMUSensor(
    prim_path="/World/Humanoid/torso/imu",
    name="imu_sensor",
    frequency=100,
    translation=np.array([0, 0, 0]),
)

# ریڈنگز حاصل کریں
imu.initialize()
current_frame = imu.get_current_frame()

linear_acc = current_frame["lin_acc"]
angular_vel = current_frame["ang_vel"]
orientation = current_frame["orientation"]
```

## ROS 2 Bridge

### کیمرہ شائع کریں

```python
import omni.graph.core as og

# ROS 2 کیمرہ publisher گراف بنائیں
keys = og.Controller.Keys
(graph, nodes, _, _) = og.Controller.edit(
    {"graph_path": "/ActionGraph", "evaluator_name": "execution"},
    {
        keys.CREATE_NODES: [
            ("OnPlaybackTick", "omni.graph.action.OnPlaybackTick"),
            ("CreateRenderProduct", "omni.isaac.core_nodes.IsaacCreateRenderProduct"),
            ("ROS2CameraHelper", "omni.isaac.ros2_bridge.ROS2CameraHelper"),
        ],
        keys.SET_VALUES: [
            ("CreateRenderProduct.inputs:cameraPrim", "/World/Humanoid/head/camera"),
            ("ROS2CameraHelper.inputs:topicName", "camera/image_raw"),
            ("ROS2CameraHelper.inputs:frameId", "camera_link"),
        ],
        keys.CONNECT: [
            ("OnPlaybackTick.outputs:tick", "CreateRenderProduct.inputs:execIn"),
            ("CreateRenderProduct.outputs:execOut", "ROS2CameraHelper.inputs:execIn"),
            ("CreateRenderProduct.outputs:renderProductPath", "ROS2CameraHelper.inputs:renderProductPath"),
        ],
    },
)
```

### جوائنٹ States شائع کریں

```python
# جوائنٹ state publisher بنائیں
(graph, nodes, _, _) = og.Controller.edit(
    {"graph_path": "/JointStateGraph", "evaluator_name": "execution"},
    {
        keys.CREATE_NODES: [
            ("OnPlaybackTick", "omni.graph.action.OnPlaybackTick"),
            ("ReadJointState", "omni.isaac.core_nodes.IsaacReadJointState"),
            ("PublishJointState", "omni.isaac.ros2_bridge.ROS2PublishJointState"),
        ],
        keys.SET_VALUES: [
            ("ReadJointState.inputs:prim", "/World/Humanoid"),
            ("PublishJointState.inputs:topicName", "joint_states"),
        ],
        keys.CONNECT: [
            ("OnPlaybackTick.outputs:tick", "ReadJointState.inputs:execIn"),
            ("ReadJointState.outputs:execOut", "PublishJointState.inputs:execIn"),
            ("ReadJointState.outputs:jointNames", "PublishJointState.inputs:jointNames"),
            ("ReadJointState.outputs:positions", "PublishJointState.inputs:positions"),
            ("ReadJointState.outputs:velocities", "PublishJointState.inputs:velocities"),
            ("ReadJointState.outputs:efforts", "PublishJointState.inputs:efforts"),
        ],
    },
)
```

### کمانڈز کو سبسکرائب کریں

```python
# جوائنٹ trajectory کمانڈز کو سبسکرائب کریں
(graph, nodes, _, _) = og.Controller.edit(
    {"graph_path": "/JointCommandGraph", "evaluator_name": "execution"},
    {
        keys.CREATE_NODES: [
            ("SubscribeJointState", "omni.isaac.ros2_bridge.ROS2SubscribeJointState"),
            ("ArticulationController", "omni.isaac.core_nodes.IsaacArticulationController"),
        ],
        keys.SET_VALUES: [
            ("SubscribeJointState.inputs:topicName", "joint_commands"),
            ("ArticulationController.inputs:robotPath", "/World/Humanoid"),
        ],
        keys.CONNECT: [
            ("SubscribeJointState.outputs:execOut", "ArticulationController.inputs:execIn"),
            ("SubscribeJointState.outputs:jointNames", "ArticulationController.inputs:jointNames"),
            ("SubscribeJointState.outputs:positions", "ArticulationController.inputs:positionCommand"),
        ],
    },
)
```

## مصنوعی ڈیٹا کی تخلیق

### ڈیٹا سیٹ کے لیے Replicator

```python
import omni.replicator.core as rep

# کیمرہ pose کو بے ترتیب بنائیں
with rep.trigger.on_frame(num_frames=1000):
    # روشنی کو بے ترتیب بنائیں
    with rep.get.light():
        rep.modify.attribute("intensity", rep.distribution.uniform(500, 3000))
        rep.modify.attribute("color", rep.distribution.uniform((0.8, 0.8, 0.8), (1.0, 1.0, 1.0)))

    # آبجیکٹ materials کو بے ترتیب بنائیں
    with rep.get.prims(semantics=[("class", "object")]):
        rep.randomizer.materials(
            materials=rep.get.material(semantics=[("class", "random_mat")])
        )

    # کیمرہ pose کو بے ترتیب بنائیں
    with rep.get.prims(path_pattern="/World/Humanoid/head/camera"):
        rep.modify.pose(
            position=rep.distribution.uniform((-2, -2, 0.5), (2, 2, 2.0)),
            look_at="/World/Target"
        )

# RGB-D ڈیٹا لکھیں
writer = rep.WriterRegistry.get("BasicWriter")
writer.initialize(
    output_dir="/tmp/synthetic_data",
    rgb=True,
    bounding_box_2d_tight=True,
    semantic_segmentation=True,
    distance_to_camera=True,
)

# چلائیں
rep.orchestrator.run()
```

### ڈومین رینڈمائزیشن

```python
import omni.replicator.core as rep

# طبیعیات کے پیرامیٹرز کو بے ترتیب بنائیں
with rep.trigger.on_frame():
    # جوائنٹ رگڑ کو بے ترتیب بنائیں
    with rep.get.prims(path_pattern="/World/Humanoid/.*", prim_type="Joint"):
        rep.modify.attribute("physxJoint:jointFriction", rep.distribution.uniform(0.0, 0.5))

    # ماس کو بے ترتیب بنائیں
    with rep.get.prims(path_pattern="/World/Humanoid/.*", prim_type="RigidBody"):
        rep.modify.attribute("physics:mass", rep.distribution.uniform(0.5, 2.0))
```

## مکمل مثال: سینسرز کے ساتھ ہیومینائیڈ

```python
from omni.isaac.kit import SimulationApp

# سمیولیٹر شروع کریں
simulation_app = SimulationApp({"headless": False})

from omni.isaac.core import World
from omni.isaac.core.utils.stage import add_reference_to_stage
from omni.isaac.sensor import Camera, IMUSensor
import numpy as np

# دنیا بنائیں
world = World(stage_units_in_meters=1.0)
world.scene.add_default_ground_plane()

# ہیومینائیڈ لوڈ کریں
add_reference_to_stage(
    usd_path="/Isaac/Robots/Humanoid/humanoid.usd",
    prim_path="/World/Humanoid"
)

# کیمرہ شامل کریں
camera = Camera(
    prim_path="/World/Humanoid/head/camera",
    position=np.array([0.1, 0, 0.15]),
    frequency=30,
    resolution=(640, 480),
)

# IMU شامل کریں
imu = IMUSensor(
    prim_path="/World/Humanoid/torso/imu",
    frequency=100,
)

# Reset
world.reset()
camera.initialize()
imu.initialize()

# سمولیشن لوپ
for i in range(1000):
    world.step(render=True)

    if i % 30 == 0:  # ہر 30 فریمز
        # سینسر ڈیٹا حاصل کریں
        rgb = camera.get_rgba()
        depth = camera.get_depth()
        imu_data = imu.get_current_frame()

        print(f"Frame {i}: IMU orientation = {imu_data['orientation']}")

simulation_app.close()
```

## کارکردگی کی اصلاح

### GPU تیز رفتاری

```python
# GPU طبیعیات فعال کریں
from pxr import PhysxSchema

physx_scene = PhysxSchema.PhysxSceneAPI.Apply(stage.GetPrimAtPath("/physicsScene"))
physx_scene.GetEnableGPUDynamicsAttr().Set(True)
physx_scene.GetBroadphaseTypeAttr().Set("GPU")
```

### Headless موڈ

```bash
# تیز ڈیٹا کی تخلیق کے لیے GUI کے بغیر چلائیں
simulation_app = SimulationApp({"headless": True})
```

### Level of Detail (LOD)

دور کے اشیاء کے لیے mesh کی پیچیدگی کم کریں۔

## خلاصہ

اس ہفتے آپ نے سیکھا:

- Isaac Sim فن تعمیر اور USD فارمیٹ
- ہیومینائیڈ URDF/USD ماڈلز لوڈ کرنا
- PhysX GPU طبیعیات کی ترتیب
- RGB-D کیمرے، LiDAR، اور IMU سینسرز
- pub/sub کے لیے ROS 2 bridge
- Replicator کے ساتھ مصنوعی ڈیٹا کی تخلیق
- مضبوط تربیت کے لیے ڈومین رینڈمائزیشن
- کارکردگی کی اصلاح کی تکنیکیں

## اگلا کیا ہے؟

**ہفتہ 8: VSLAM کے لیے Isaac ROS** - بصری SLAM اور نیویگیشن کے لیے NVIDIA کے GPU سے تیز شدہ perception stack استعمال کریں۔

**اگلا**: [ہفتہ 8: Isaac ROS →](./week8-isaac-ros.md)
