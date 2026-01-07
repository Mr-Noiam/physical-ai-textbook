# ہفتہ 7: NVIDIA Isaac Sim

## تعارف

**NVIDIA Isaac Sim** سب سے جدید روبوٹ سمیلیٹر ہے، جو Omniverse پر بنایا گیا ہے۔ یہ RTX رے ٹریسڈ رینڈرنگ، PhysX فزکس، اور NVIDIA AI ٹولز کے ساتھ مقامی انضمام فراہم کرتا ہے۔ اس ہفتے، آپ ہیومنائڈز لوڈ کریں گے، سینسرز کو کنفیگر کریں گے، اور بڑے پیمانے پر مصنوعی تربیتی ڈیٹا تیار کریں گے۔

## آئزک سم کیوں؟

**فوائد**:

- **RTX رینڈرنگ**: سم-ٹو-ریئل کے لیے فوٹو ریئلسٹک، رے ٹریسڈ گرافکس
- **PhysX 5**: تیز سیمولیشن کے لیے GPU-ایکسلریٹڈ فزکس
- **USD فارمیٹ**: تعاون کے لیے یونیورسل سین ڈسکرپشن
- **مصنوعی ڈیٹا**: ڈیٹا سیٹ جنریشن کے لیے بلٹ ان ریپلیکیٹر
- **Isaac ROS**: ROS 2 GEMs (GPU- فعال ماڈیولز) کے ساتھ براہ راست انضمام
- **AI ورک فلوز**: TensorRT, cuDNN, cuVSLAM, DeepStream

**استعمال کے معاملات**:
- پرسیپشن ماڈلز کی تربیت
- ملٹی روبوٹ کوآرڈینیشن
- ڈیجیٹل ٹوئنز
- ری انفورسمنٹ لرننگ

## انسٹالیشن

### ضروریات

```bash
# NVIDIA GPU درکار ہے (RTX سیریز تجویز کردہ)
# Ubuntu 22.04 یا Windows 11
# ڈرائیور 525+

# NVIDIA ڈرائیور چیک کریں
nvidia-smi
```

### آئزک سم

یہاں سے ڈاؤن لوڈ کریں: https://developer.nvidia.com/isaac-sim

```bash
# اومنیورس لانچر انسٹال کریں
# Launch > Library > Isaac Sim
# انسٹال پر کلک کریں (Isaac Sim 2023.1.0+)

# یا ڈاکر:
docker pull nvcr.io/nvidia/isaac-sim:2023.1.0
```

### ROS 2 برج

```bash
# آئزک سم میں ROS 2 برج کو فعال کریں:
# Window > Extensions > ROS/ROS 2 Bridge
# "omni.isaac.ros2_bridge" کو فعال کریں

# ROS 2 Humble انسٹال کریں (اگر پہلے سے نہیں ہے)
sudo apt install ros-humble-desktop
```

## USD فارمیٹ

**یونیورسل سین ڈسکرپشن** پکسر کا انٹرچینج فارمیٹ ہے:

```python
# Python USD API
from pxr import Usd, UsdGeom, Gf

# اسٹیج بنائیں
stage = Usd.Stage.CreateNew('/tmp/scene.usda')

# دائرہ شامل کریں
sphere = UsdGeom.Sphere.Define(stage, '/World/Sphere')
sphere.GetRadiusAttr().Set(1.0)
sphere.AddTranslateOp().Set(Gf.Vec3d(0, 0, 1))

# محفوظ کریں
stage.Save()
```

## آئزک سم میں ہیومنائڈ لوڈ کرنا

### طریقہ 1: URDF درآمد

```python
import omni
from omni.isaac.core.utils.extensions import enable_extension

# URDF امپورٹر کو فعال کریں
enable_extension("omni.importer.urdf")

import omni.kit.commands
from omni.importer.urdf import _urdf

# URDF درآمد کریں
_urdf.acquire_urdf_interface()
urdf_interface = _urdf.get_urdf_interface()

# درآمدی ترتیب
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

# USD اثاثہ لوڈ کریں
add_reference_to_stage(
    usd_path="/Isaac/Robots/Humanoid/humanoid.usd",
    prim_path="/World/Humanoid"
)
```

## فزکس کنفیگریشن

```python
from omni.isaac.core import World
from omni.isaac.core.prims import RigidPrimView
from pxr import PhysxSchema

# فزکس کے ساتھ ورلڈ بنائیں
world = World(stage_units_in_meters=1.0)
world.scene.add_default_ground_plane()

# فزکس سین کو کنفیگر کریں
physx_scene = PhysxSchema.PhysxSceneAPI.Apply(world.stage.GetPrimAtPath("/physicsScene"))
physx_scene.GetEnableGPUDynamicsAttr().Set(True)
physx_scene.GetBroadphaseTypeAttr().Set("GPU")
physx_scene.GetSolverTypeAttr().Set("TGS")

# ورلڈ ری سیٹ کریں
world.reset()

# سیمولیشن چلائیں
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

# ڈیپتھ حاصل کریں
depth = camera.get_depth()

# ریپلیکیٹر کے لیے رینڈر پروڈکٹ بنائیں
render_product = rep.create.render_product(
    camera.prim_path,
    resolution=(640, 480)
)

# تشریح کار (زمینی سچائی)
rgb_annot = rep.AnnotatorRegistry.get_annotator("rgb")
depth_annot = rep.AnnotatorRegistry.get_annotator("distance_to_camera")
bbox_annot = rep.AnnotatorRegistry.get_annotator("bounding_box_2d_tight")

# رینڈر پروڈکٹ سے منسلک کریں
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

# پوائنٹ کلاؤڈ ڈیٹا حاصل کریں
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

## ROS 2 برج

### کیمرہ شائع کریں

```python
import omni.graph.core as og

# ROS 2 کیمرہ پبلشر گراف بنائیں
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

### جوائنٹ اسٹیٹس شائع کریں

```python
# جوائنٹ اسٹیٹ پبلشر بنائیں
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
# جوائنٹ ٹریجکٹری کمانڈز کو سبسکرائب کریں
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

## مصنوعی ڈیٹا جنریشن

### ڈیٹا سیٹس کے لیے ریپلیکیٹر

```python
import omni.replicator.core as rep

# کیمرہ پوز کو رینڈمائز کریں
with rep.trigger.on_frame(num_frames=1000):
    # روشنی کو رینڈمائز کریں
    with rep.get.light():
        rep.modify.attribute("intensity", rep.distribution.uniform(500, 3000))
        rep.modify.attribute("color", rep.distribution.uniform((0.8, 0.8, 0.8), (1.0, 1.0, 1.0)))

    # آبجیکٹ میٹریلز کو رینڈمائز کریں
    with rep.get.prims(semantics=[("class", "object")]):
        rep.randomizer.materials(
            materials=rep.get.material(semantics=[("class", "random_mat")])
        )

    # کیمرہ پوز کو رینڈمائز کریں
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

# فزکس پیرامیٹرز کو رینڈمائز کریں
with rep.trigger.on_frame():
    # جوائنٹ فریکشن کو رینڈمائز کریں
    with rep.get.prims(path_pattern="/World/Humanoid/.*", prim_type="Joint"):
        rep.modify.attribute("physxJoint:jointFriction", rep.distribution.uniform(0.0, 0.5))

    # ماس کو رینڈمائز کریں
    with rep.get.prims(path_pattern="/World/Humanoid/.*", prim_type="RigidBody"):
        rep.modify.attribute("physics:mass", rep.distribution.uniform(0.5, 2.0))
```

## مکمل مثال: سینسرز کے ساتھ ہیومنائڈ

```python
from omni.isaac.kit import SimulationApp

# سمیلیٹر شروع کریں
simulation_app = SimulationApp({"headless": False})

from omni.isaac.core import World
from omni.isaac.core.utils.stage import add_reference_to_stage
from omni.isaac.sensor import Camera, IMUSensor
import numpy as np

# ورلڈ بنائیں
world = World(stage_units_in_meters=1.0)
world.scene.add_default_ground_plane()

# ہیومنائڈ لوڈ کریں
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

# ری سیٹ کریں
world.reset()
camera.initialize()
imu.initialize()

# سیمولیشن لوپ
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

### GPU ایکسلریشن

```python
# GPU فزکس کو فعال کریں
from pxr import PhysxSchema

physx_scene = PhysxSchema.PhysxSceneAPI.Apply(stage.GetPrimAtPath("/physicsScene"))
physx_scene.GetEnableGPUDynamicsAttr().Set(True)
physx_scene.GetBroadphaseTypeAttr().Set("GPU")
```

### ہیڈ لیس موڈ

```bash
# تیز ڈیٹا جنریشن کے لیے GUI کے بغیر چلائیں
simulation_app = SimulationApp({"headless": True})
```

### تفصیل کی سطح (LOD)

دور دراز اشیاء کے لیے میش کی پیچیدگی کو کم کریں۔

## خلاصہ

اس ہفتے آپ نے سیکھا:

- آئزک سم فن تعمیر اور USD فارمیٹ
- ہیومنائڈ URDF/USD ماڈلز لوڈ کرنا
- PhysX GPU فزکس کنفیگریشن
- RGB-D کیمرے، LiDAR، اور IMU سینسرز
- پب/سب کے لیے ROS 2 برج
- ریپلیکیٹر کے ساتھ مصنوعی ڈیٹا جنریشن
- مضبوط تربیت کے لیے ڈومین رینڈمائزیشن
- کارکردگی کی اصلاح کی تکنیکیں

## آگے کیا ہے؟

**ہفتہ 8: VSLAM کے لیے آئزک ROS** - بصری SLAM اور نیویگیشن کے لیے NVIDIA کا GPU-ایکسلریٹڈ پرسیپشن اسٹیک استعمال کریں۔

**آگے**: [ہفتہ 8: آئزک ROS →](./week8-isaac-ros.md)