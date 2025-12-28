# ہفتہ 6: روبوٹ کی تصویر سازی کے لیے Unity

## تعارف

اس ہفتے، ہم **Unity Robotics Hub** کو دریافت کریں گے، جو روبوٹکس میں فوٹو ریئلسٹک رینڈرنگ، طبیعیات کی سمولیشن، اور مصنوعی ڈیٹا کی تخلیق فراہم کرتا ہے۔ Unity کمپیوٹر وژن اور VLA ماڈلز کے لیے بصری طور پر درست تربیتی ڈیٹا بنانے میں بہترین ہے۔

## Why Unity for Robotics?

**Advantages over Gazebo**:

- **Photorealism**: High-quality graphics for sim-to-real transfer
- **Synthetic data**: Generate labeled datasets (bounding boxes, segmentation masks)
- **Performance**: GPU-accelerated physics and rendering
- **Domain randomization**: Easy to vary lighting, textures, object poses
- **Asset store**: Thousands of 3D models and environments

**Use cases**:
- Training vision models
- Human-robot interaction visualization
- VR/AR teleoperation
- Marketing and demos

## Unity Robotics Hub Architecture

```
┌─────────────────┐         ┌──────────────────┐
│  Unity Editor   │◄───────►│   ROS 2 Bridge   │
│  (Simulation)   │  TCP-IP │   (Python/C++)   │
└─────────────────┘         └──────────────────┘
        │                            │
        │                            │
    USD/URDF                    ROS 2 Topics
        │                            │
        ▼                            ▼
  Robot Model                   ROS 2 Network
```

## Installation

### Unity Hub and Editor

```bash
# Download Unity Hub
wget https://public-cdn.cloud.unity3d.com/hub/prod/UnityHubSetup.AppImage

# Install Unity 2022.3 LTS
# Unity Hub > Installs > Add > 2022.3 LTS
```

### Unity Robotics Packages

In Unity, open Package Manager:

1. Window > Package Manager
2. Add package from git URL:
   - `https://github.com/Unity-Technologies/ROS-TCP-Connector.git?path=/com.unity.robotics.ros-tcp-connector`
   - `https://github.com/Unity-Technologies/URDF-Importer.git?path=/com.unity.robotics.urdf-importer`

### ROS 2 TCP Endpoint

```bash
# Clone ROS-TCP-Endpoint
cd ~/ros2_ws/src
git clone https://github.com/Unity-Technologies/ROS-TCP-Endpoint

# Build
cd ~/ros2_ws
colcon build --packages-select ros_tcp_endpoint

# Source
source install/setup.bash
```

## Importing Humanoid URDF

### 1. Prepare URDF

Unity URDF Importer has requirements:

```xml
<?xml version="1.0"?>
<robot name="humanoid">
  <!-- Ensure all meshes use absolute paths or package:// URIs -->
  <link name="torso">
    <visual>
      <geometry>
        <!-- Supported: .obj, .stl, .dae -->
        <mesh filename="package://humanoid_description/meshes/torso.obj"/>
      </geometry>
    </visual>
  </link>
</robot>
```

### 2. Import to Unity

1. Assets > Import Robot from URDF
2. Select your URDF file
3. Configure import settings:
   - Axis Type: Y-Axis
   - Mesh Decomposer: VHACD (for collisions)
4. Import

Unity creates:
- GameObject hierarchy matching URDF
- ArticulationBody components for joints
- Colliders and visual meshes

### 3. Configure ArticulationBodies

Unity uses **ArticulationBody** (successor to Rigidbody):

```csharp
using UnityEngine;

public class JointController : MonoBehaviour
{
    private ArticulationBody[] joints;

    void Start()
    {
        // Get all articulation bodies (joints)
        joints = GetComponentsInChildren<ArticulationBody>();

        foreach (var joint in joints)
        {
            if (joint.jointType == ArticulationJointType.RevoluteJoint)
            {
                // Set drive properties
                var drive = joint.xDrive;
                drive.stiffness = 10000;
                drive.damping = 500;
                drive.forceLimit = 100;
                joint.xDrive = drive;
            }
        }
    }

    public void SetJointPosition(string jointName, float angle)
    {
        var joint = System.Array.Find(joints, j => j.name == jointName);
        if (joint != null)
        {
            var drive = joint.xDrive;
            drive.target = angle * Mathf.Rad2Deg;
            joint.xDrive = drive;
        }
    }
}
```

## ROS 2 - Unity Communication

### Unity Side: Subscribe to Joint Commands

```csharp
using UnityEngine;
using Unity.Robotics.ROSTCPConnector;
using RosMessageTypes.Sensor;

public class JointStateSubscriber : MonoBehaviour
{
    private ROSConnection ros;
    private ArticulationBody[] joints;

    void Start()
    {
        // Connect to ROS
        ros = ROSConnection.GetOrCreateInstance();
        ros.RegisterSubscriber<JointStateMsg>("joint_commands", UpdateJoints);

        joints = GetComponentsInChildren<ArticulationBody>();
    }

    void UpdateJoints(JointStateMsg msg)
    {
        for (int i = 0; i < msg.name.Length; i++)
        {
            var joint = System.Array.Find(joints, j => j.name == msg.name[i]);
            if (joint != null && i < msg.position.Length)
            {
                var drive = joint.xDrive;
                drive.target = (float)msg.position[i] * Mathf.Rad2Deg;
                joint.xDrive = drive;
            }
        }
    }
}
```

### ROS Side: Publish Joint Commands

```python
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState

class UnityJointPublisher(Node):
    def __init__(self):
        super().__init__('unity_joint_publisher')
        self.publisher_ = self.create_publisher(JointState, 'joint_commands', 10)
        self.timer = self.create_timer(0.02, self.publish_joints)  # 50 Hz

        self.joint_names = ['left_shoulder_pitch', 'left_elbow']
        self.phase = 0.0

    def publish_joints(self):
        msg = JointState()
        msg.name = self.joint_names
        msg.position = [0.5 * math.sin(self.phase), 1.0 * math.cos(self.phase)]

        self.publisher_.publish(msg)
        self.phase += 0.1
```

### Start ROS-TCP Endpoint

```bash
ros2 run ros_tcp_endpoint default_server_endpoint --ros-args -p ROS_IP:=0.0.0.0
```

In Unity:
- Robotics > ROS Settings
- ROS IP Address: localhost
- ROS Port: 10000

## Camera and Sensors

### RGB Camera

```csharp
using UnityEngine;
using Unity.Robotics.ROSTCPConnector;
using RosMessageTypes.Sensor;

public class CameraPublisher : MonoBehaviour
{
    private ROSConnection ros;
    private Camera cam;
    private Texture2D tex;

    void Start()
    {
        ros = ROSConnection.GetOrCreateInstance();
        cam = GetComponent<Camera>();
        tex = new Texture2D(cam.pixelWidth, cam.pixelHeight, TextureFormat.RGB24, false);

        ros.RegisterPublisher<ImageMsg>("camera/image_raw");
    }

    void Update()
    {
        if (Time.frameCount % 3 == 0)  // 30 Hz @ 90 FPS
        {
            RenderTexture rt = RenderTexture.GetTemporary(cam.pixelWidth, cam.pixelHeight);
            cam.targetTexture = rt;
            cam.Render();

            RenderTexture.active = rt;
            tex.ReadPixels(new Rect(0, 0, cam.pixelWidth, cam.pixelHeight), 0, 0);
            tex.Apply();

            ImageMsg msg = new ImageMsg
            {
                header = new RosMessageTypes.Std.HeaderMsg { frame_id = "camera_link" },
                height = (uint)cam.pixelHeight,
                width = (uint)cam.pixelWidth,
                encoding = "rgb8",
                step = (uint)cam.pixelWidth * 3,
                data = tex.GetRawTextureData()
            };

            ros.Publish("camera/image_raw", msg);

            RenderTexture.ReleaseTemporary(rt);
        }
    }
}
```

### Depth Camera

```csharp
public class DepthCameraPublisher : MonoBehaviour
{
    private Camera depthCam;

    void Start()
    {
        depthCam = GetComponent<Camera>();
        depthCam.depthTextureMode = DepthTextureMode.Depth;

        // Shader for depth visualization
        depthCam.SetReplacementShader(Shader.Find("Custom/DepthShader"), "");
    }

    // Publish depth as Float32 array
    void PublishDepth()
    {
        // Convert depth buffer to ROS PointCloud2
        // Implementation depends on use case
    }
}
```

## Synthetic Data Generation

### Perception Camera (for labeled data)

Unity Perception package provides:

- Bounding boxes (2D/3D)
- Instance segmentation
- Semantic segmentation
- Keypoint annotation

Install:
```
Window > Package Manager > Unity Registry > Perception
```

Example labeler:

```csharp
using UnityEngine;
using UnityEngine.Perception.GroundTruth;

public class DatasetGenerator : MonoBehaviour
{
    void Start()
    {
        var perceptionCamera = GetComponent<PerceptionCamera>();

        // Add labelers
        var boundingBox2DLabeler = new BoundingBox2DLabeler();
        perceptionCamera.AddLabeler(boundingBox2DLabeler);

        var semanticSegmentationLabeler = new SemanticSegmentationLabeler();
        perceptionCamera.AddLabeler(semanticSegmentationLabeler);
    }
}
```

### Domain Randomization

```csharp
using UnityEngine;
using UnityEngine.Perception.Randomization.Scenarios;
using UnityEngine.Perception.Randomization.Randomizers;

[AddComponentMenu("Perception/Domain Randomization")]
public class DomainRandomizer : MonoBehaviour
{
    public Light sunLight;
    public Material[] materials;

    void OnEnable()
    {
        RandomizeLighting();
        RandomizeMaterials();
    }

    void RandomizeLighting()
    {
        sunLight.intensity = Random.Range(0.5f, 2.0f);
        sunLight.color = new Color(
            Random.Range(0.8f, 1.0f),
            Random.Range(0.8f, 1.0f),
            Random.Range(0.8f, 1.0f)
        );
    }

    void RandomizeMaterials()
    {
        var renderers = FindObjectsOfType<Renderer>();
        foreach (var renderer in renderers)
        {
            if (Random.value > 0.5f)
            {
                renderer.material = materials[Random.Range(0, materials.Length)];
            }
        }
    }
}
```

## Complete Unity-ROS 2 Example

### Scene Setup

1. Create empty scene
2. Add Plane (ground)
3. Import humanoid URDF
4. Add camera to robot head
5. Add directional light

### Unity Scripts

Attach to robot root:

```csharp
using UnityEngine;
using Unity.Robotics.ROSTCPConnector;

public class HumanoidController : MonoBehaviour
{
    void Start()
    {
        // Initialize ROS connection
        var ros = ROSConnection.GetOrCreateInstance();
        ros.ConnectOnStart = true;

        // Add components
        gameObject.AddComponent<JointStateSubscriber>();
        gameObject.AddComponent<CameraPublisher>();
        gameObject.AddComponent<IMUPublisher>();
    }
}
```

### ROS Launch File

```python
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        # ROS-TCP Endpoint
        Node(
            package='ros_tcp_endpoint',
            executable='default_server_endpoint',
            parameters=[{'ROS_IP': '0.0.0.0'}]
        ),

        # Joint state publisher
        Node(
            package='humanoid_unity',
            executable='joint_publisher'
        ),

        # Image viewer
        Node(
            package='rqt_image_view',
            executable='rqt_image_view',
            arguments=['image:=/camera/image_raw']
        )
    ])
```

## Performance Tips

### 1. Reduce Quality for Simulation

```csharp
void Start()
{
    QualitySettings.SetQualityLevel(2);  // Medium quality
    Application.targetFrameRate = 60;
}
```

### 2. Use Object Pooling

```csharp
public class ObjectPool : MonoBehaviour
{
    public GameObject prefab;
    private Queue<GameObject> pool = new Queue<GameObject>();

    public GameObject Get()
    {
        if (pool.Count > 0)
        {
            var obj = pool.Dequeue();
            obj.SetActive(true);
            return obj;
        }
        return Instantiate(prefab);
    }

    public void Return(GameObject obj)
    {
        obj.SetActive(false);
        pool.Enqueue(obj);
    }
}
```

### 3. Batch Rendering

Use Unity's GPU instancing for multiple identical objects.

## Summary

This week you learned:

- Unity Robotics Hub architecture
- Importing URDF to Unity
- ArticulationBody physics
- ROS 2 - Unity TCP communication
- Publishing camera and sensor data
- Synthetic data generation with Perception
- Domain randomization for sim-to-real
- Performance optimization

## What's Next?

**Week 7: NVIDIA Isaac Sim** - Explore the most advanced robot simulator with RTX rendering, PhysX, and integrated AI tools.

**Next**: [Week 7: Isaac Sim →](../module-3-isaac/week7-isaac-sim.md)
