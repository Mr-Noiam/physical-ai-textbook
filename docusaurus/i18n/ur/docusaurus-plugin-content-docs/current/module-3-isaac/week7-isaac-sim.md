[TRANSLATION_FAILED] # Week 7: NVIDIA Isaac Sim

[TRANSLATION_FAILED] ## Introduction

[TRANSLATION_FAILED] **NVIDIA Isaac Sim** is the most advanced robot simulator, built on Omniverse. It provides RTX ray-traced rendering, PhysX physics, and native integration with NVIDIA AI tools. This week, you'll load humanoids, configure sensors, and generate synthetic training data at scale.

[TRANSLATION_FAILED] ## Why Isaac Sim?

[TRANSLATION_FAILED] **Advantages**:

[TRANSLATION_FAILED] - **RTX Rendering**: Photorealistic, ray-traced graphics for sim-to-real
[TRANSLATION_FAILED] - **PhysX 5**: GPU-accelerated physics for fast simulation
[TRANSLATION_FAILED] - **USD Format**: Universal Scene Description for collaboration
[TRANSLATION_FAILED] - **Synthetic Data**: Built-in Replicator for dataset generation
[TRANSLATION_FAILED] - **Isaac ROS**: Direct integration with ROS 2 GEMs (GPU-Enabled Modules)
[TRANSLATION_FAILED] - **AI Workflows**: TensorRT, cuDNN, cuVSLAM, DeepStream

[TRANSLATION_FAILED] **Use cases**:
[TRANSLATION_FAILED] - Training perception models
[TRANSLATION_FAILED] - Multi-robot coordination
[TRANSLATION_FAILED] - Digital twins
[TRANSLATION_FAILED] - Reinforcement learning

[TRANSLATION_FAILED] ## Installation

[TRANSLATION_FAILED] ### Prerequisites

```bash
# NVIDIA GPU required (RTX series recommended)
# Ubuntu 22.04 or Windows 11
# Driver 525+

# Check NVIDIA driver
nvidia-smi
```

[TRANSLATION_FAILED] ### Isaac Sim

[TRANSLATION_FAILED] Download from: https://developer.nvidia.com/isaac-sim

```bash
# Install Omniverse Launcher
# Launch > Library > Isaac Sim
# Click Install (Isaac Sim 2023.1.0+)

# Or Docker:
docker pull nvcr.io/nvidia/isaac-sim:2023.1.0
```

[TRANSLATION_FAILED] ### ROS 2 Bridge

```bash
# Enable ROS 2 Bridge in Isaac Sim:
# Window > Extensions > ROS/ROS 2 Bridge
# Enable "omni.isaac.ros2_bridge"

# Install ROS 2 Humble (if not already)
sudo apt install ros-humble-desktop
```

[TRANSLATION_FAILED] ## USD Format

[TRANSLATION_FAILED] **Universal Scene Description** is Pixar's interchange format:

```python
# Python USD API
from pxr import Usd, UsdGeom, Gf

# Create stage
stage = Usd.Stage.CreateNew('/tmp/scene.usda')

# Add sphere
sphere = UsdGeom.Sphere.Define(stage, '/World/Sphere')
sphere.GetRadiusAttr().Set(1.0)
sphere.AddTranslateOp().Set(Gf.Vec3d(0, 0, 1))

# Save
stage.Save()
```

[TRANSLATION_FAILED] ## Loading Humanoid in Isaac Sim

[TRANSLATION_FAILED] ### Method 1: URDF Import

```python
import omni
from omni.isaac.core.utils.extensions import enable_extension

# Enable URDF importer
enable_extension("omni.importer.urdf")

import omni.kit.commands
from omni.importer.urdf import _urdf

# Import URDF
_urdf.acquire_urdf_interface()
urdf_interface = _urdf.get_urdf_interface()

# Import configuration
import_config = _urdf.ImportConfig()
import_config.merge_fixed_joints = False
import_config.convex_decomp = True
import_config.import_inertia_tensor = True
import_config.fix_base = False

# Import
success, prim_path = omni.kit.commands.execute(
    "URDFParseAndImportFile",
    urdf_path="/path/to/humanoid.urdf",
    import_config=import_config,
)

print(f"Imported humanoid at: {prim_path}")
```

[TRANSLATION_FAILED] ### Method 2: USD Import

```python
from omni.isaac.core.utils.stage import add_reference_to_stage

# Load USD asset
add_reference_to_stage(
    usd_path="/Isaac/Robots/Humanoid/humanoid.usd",
    prim_path="/World/Humanoid"
)
```

[TRANSLATION_FAILED] ## Physics Configuration

```python
from omni.isaac.core import World
from omni.isaac.core.prims import RigidPrimView
from pxr import PhysxSchema

# Create world with physics
world = World(stage_units_in_meters=1.0)
world.scene.add_default_ground_plane()

# Configure physics scene
physx_scene = PhysxSchema.PhysxSceneAPI.Apply(world.stage.GetPrimAtPath("/physicsScene"))
physx_scene.GetEnableGPUDynamicsAttr().Set(True)
physx_scene.GetBroadphaseTypeAttr().Set("GPU")
physx_scene.GetSolverTypeAttr().Set("TGS")

# Reset world
world.reset()

# Run simulation
for i in range(1000):
    world.step(render=True)
```

[TRANSLATION_FAILED] ## Adding Sensors

[TRANSLATION_FAILED] ### RGB-D Camera

```python
from omni.isaac.sensor import Camera
import omni.replicator.core as rep

# Create camera
camera = Camera(
    prim_path="/World/Humanoid/head/camera",
    frequency=30,
    resolution=(640, 480),
)

# Render RGB
camera.initialize()
rgb = camera.get_rgba()

# Get depth
depth = camera.get_depth()

# Create render product for Replicator
render_product = rep.create.render_product(
    camera.prim_path,
    resolution=(640, 480)
)

# Annotators (ground truth)
rgb_annot = rep.AnnotatorRegistry.get_annotator("rgb")
depth_annot = rep.AnnotatorRegistry.get_annotator("distance_to_camera")
bbox_annot = rep.AnnotatorRegistry.get_annotator("bounding_box_2d_tight")

# Attach to render product
rgb_annot.attach([render_product])
depth_annot.attach([render_product])
bbox_annot.attach([render_product])
```

[TRANSLATION_FAILED] ### LiDAR

```python
from omni.isaac.range_sensor import _range_sensor

# Create LiDAR
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

# Get point cloud data
lidar_interface = _range_sensor.acquire_lidar_sensor_interface()
depth_data = lidar_interface.get_linear_depth_data("/World/Humanoid/lidar")
```

[TRANSLATION_FAILED] ### IMU

```python
from omni.isaac.sensor import IMUSensor

# Create IMU
imu = IMUSensor(
    prim_path="/World/Humanoid/torso/imu",
    name="imu_sensor",
    frequency=100,
    translation=np.array([0, 0, 0]),
)

# Get readings
imu.initialize()
current_frame = imu.get_current_frame()

linear_acc = current_frame["lin_acc"]
angular_vel = current_frame["ang_vel"]
orientation = current_frame["orientation"]
```

[TRANSLATION_FAILED] ## ROS 2 Bridge

[TRANSLATION_FAILED] ### Publish Camera

```python
import omni.graph.core as og

# Create ROS 2 camera publisher graph
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

[TRANSLATION_FAILED] ### Publish Joint States

```python
# Create joint state publisher
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

[TRANSLATION_FAILED] ### Subscribe to Commands

```python
# Subscribe to joint trajectory commands
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

[TRANSLATION_FAILED] ## Synthetic Data Generation

[TRANSLATION_FAILED] ### Replicator for Datasets

```python
import omni.replicator.core as rep

# Randomize camera pose
with rep.trigger.on_frame(num_frames=1000):
    # Randomize lighting
    with rep.get.light():
        rep.modify.attribute("intensity", rep.distribution.uniform(500, 3000))
        rep.modify.attribute("color", rep.distribution.uniform((0.8, 0.8, 0.8), (1.0, 1.0, 1.0)))

    # Randomize object materials
    with rep.get.prims(semantics=[("class", "object")]):
        rep.randomizer.materials(
            materials=rep.get.material(semantics=[("class", "random_mat")])
        )

    # Randomize camera pose
    with rep.get.prims(path_pattern="/World/Humanoid/head/camera"):
        rep.modify.pose(
            position=rep.distribution.uniform((-2, -2, 0.5), (2, 2, 2.0)),
            look_at="/World/Target"
        )

# Write RGB-D data
writer = rep.WriterRegistry.get("BasicWriter")
writer.initialize(
    output_dir="/tmp/synthetic_data",
    rgb=True,
    bounding_box_2d_tight=True,
    semantic_segmentation=True,
    distance_to_camera=True,
)

# Run
rep.orchestrator.run()
```

[TRANSLATION_FAILED] ### Domain Randomization

```python
import omni.replicator.core as rep

# Randomize physics parameters
with rep.trigger.on_frame():
    # Randomize joint friction
    with rep.get.prims(path_pattern="/World/Humanoid/.*", prim_type="Joint"):
        rep.modify.attribute("physxJoint:jointFriction", rep.distribution.uniform(0.0, 0.5))

    # Randomize mass
    with rep.get.prims(path_pattern="/World/Humanoid/.*", prim_type="RigidBody"):
        rep.modify.attribute("physics:mass", rep.distribution.uniform(0.5, 2.0))
```

[TRANSLATION_FAILED] ## Complete Example: Humanoid with Sensors

```python
from omni.isaac.kit import SimulationApp

# Start simulator
simulation_app = SimulationApp({"headless": False})

from omni.isaac.core import World
from omni.isaac.core.utils.stage import add_reference_to_stage
from omni.isaac.sensor import Camera, IMUSensor
import numpy as np

# Create world
world = World(stage_units_in_meters=1.0)
world.scene.add_default_ground_plane()

# Load humanoid
add_reference_to_stage(
    usd_path="/Isaac/Robots/Humanoid/humanoid.usd",
    prim_path="/World/Humanoid"
)

# Add camera
camera = Camera(
    prim_path="/World/Humanoid/head/camera",
    position=np.array([0.1, 0, 0.15]),
    frequency=30,
    resolution=(640, 480),
)

# Add IMU
imu = IMUSensor(
    prim_path="/World/Humanoid/torso/imu",
    frequency=100,
)

# Reset
world.reset()
camera.initialize()
imu.initialize()

# Simulation loop
for i in range(1000):
    world.step(render=True)

    if i % 30 == 0:  # Every 30 frames
        # Get sensor data
        rgb = camera.get_rgba()
        depth = camera.get_depth()
        imu_data = imu.get_current_frame()

        print(f"Frame {i}: IMU orientation = {imu_data['orientation']}")

simulation_app.close()
```

[TRANSLATION_FAILED] ## Performance Optimization

[TRANSLATION_FAILED] ### GPU Acceleration

```python
# Enable GPU physics
from pxr import PhysxSchema

physx_scene = PhysxSchema.PhysxSceneAPI.Apply(stage.GetPrimAtPath("/physicsScene"))
physx_scene.GetEnableGPUDynamicsAttr().Set(True)
physx_scene.GetBroadphaseTypeAttr().Set("GPU")
```

[TRANSLATION_FAILED] ### Headless Mode

```bash
# Run without GUI for faster data generation
simulation_app = SimulationApp({"headless": True})
```

[TRANSLATION_FAILED] ### Level of Detail (LOD)

[TRANSLATION_FAILED] Reduce mesh complexity for distant objects.

[TRANSLATION_FAILED] ## Summary

[TRANSLATION_FAILED] This week you learned:

[TRANSLATION_FAILED] - Isaac Sim architecture and USD format
[TRANSLATION_FAILED] - Loading humanoid URDF/USD models
[TRANSLATION_FAILED] - PhysX GPU physics configuration
[TRANSLATION_FAILED] - RGB-D cameras, LiDAR, and IMU sensors
[TRANSLATION_FAILED] - ROS 2 bridge for pub/sub
[TRANSLATION_FAILED] - Synthetic data generation with Replicator
[TRANSLATION_FAILED] - Domain randomization for robust training
[TRANSLATION_FAILED] - Performance optimization techniques

[TRANSLATION_FAILED] ## What's Next?

[TRANSLATION_FAILED] **Week 8: Isaac ROS for VSLAM** - Use NVIDIA's GPU-accelerated perception stack for visual SLAM and navigation.

[TRANSLATION_FAILED] **Next**: [Week 8: Isaac ROS →](./week8-isaac-ros.md)
