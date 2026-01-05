[TRANSLATION_FAILED] # Week 6: Unity for Robot Visualization

[TRANSLATION_FAILED] ## Introduction

[TRANSLATION_FAILED] This week, we'll explore **Unity Robotics Hub**, which brings photorealistic rendering, physics simulation, and synthetic data generation to robotics. Unity excels at creating visually accurate training data for computer vision and VLA models.

[TRANSLATION_FAILED] ## Why Unity for Robotics?

[TRANSLATION_FAILED] **Advantages over Gazebo**:

[TRANSLATION_FAILED] - **Photorealism**: High-quality graphics for sim-to-real transfer
[TRANSLATION_FAILED] - **Synthetic data**: Generate labeled datasets (bounding boxes, segmentation masks)
[TRANSLATION_FAILED] - **Performance**: GPU-accelerated physics and rendering
[TRANSLATION_FAILED] - **Domain randomization**: Easy to vary lighting, textures, object poses
[TRANSLATION_FAILED] - **Asset store**: Thousands of 3D models and environments

[TRANSLATION_FAILED] **Use cases**:
[TRANSLATION_FAILED] - Training vision models
[TRANSLATION_FAILED] - Human-robot interaction visualization
[TRANSLATION_FAILED] - VR/AR teleoperation
[TRANSLATION_FAILED] - Marketing and demos

[TRANSLATION_FAILED] ## Unity Robotics Hub Architecture

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

[TRANSLATION_FAILED] ## Installation

[TRANSLATION_FAILED] ### Unity Hub and Editor

```bash
# Download Unity Hub
wget https://public-cdn.cloud.unity3d.com/hub/prod/UnityHubSetup.AppImage

# Install Unity 2022.3 LTS
# Unity Hub > Installs > Add > 2022.3 LTS
```

[TRANSLATION_FAILED] ### Unity Robotics Packages

[TRANSLATION_FAILED] In Unity, open Package Manager:

[TRANSLATION_FAILED] 1. Window > Package Manager
[TRANSLATION_FAILED] 2. Add package from git URL:
   [TRANSLATION_FAILED] - `https://github.com/Unity-Technologies/ROS-TCP-Connector.git?path=/com.unity.robotics.ros-tcp-connector`
   [TRANSLATION_FAILED] - `https://github.com/Unity-Technologies/URDF-Importer.git?path=/com.unity.robotics.urdf-importer`

[TRANSLATION_FAILED] ### ROS 2 TCP Endpoint

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

[TRANSLATION_FAILED] ## Importing Humanoid URDF

[TRANSLATION_FAILED] ### 1. Prepare URDF

[TRANSLATION_FAILED] Unity URDF Importer has requirements:

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

[TRANSLATION_FAILED] ### 2. Import to Unity

[TRANSLATION_FAILED] 1. Assets > Import Robot from URDF
[TRANSLATION_FAILED] 2. Select your URDF file
[TRANSLATION_FAILED] 3. Configure import settings:
   [TRANSLATION_FAILED] - Axis Type: Y-Axis
   [TRANSLATION_FAILED] - Mesh Decomposer: VHACD (for collisions)
[TRANSLATION_FAILED] 4. Import

[TRANSLATION_FAILED] Unity creates:
[TRANSLATION_FAILED] - GameObject hierarchy matching URDF
[TRANSLATION_FAILED] - ArticulationBody components for joints
[TRANSLATION_FAILED] - Colliders and visual meshes

[TRANSLATION_FAILED] ### 3. Configure ArticulationBodies

[TRANSLATION_FAILED] Unity uses **ArticulationBody** (successor to Rigidbody):

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

[TRANSLATION_FAILED] ## ROS 2 - Unity Communication

[TRANSLATION_FAILED] ### Unity Side: Subscribe to Joint Commands

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

[TRANSLATION_FAILED] ### ROS Side: Publish Joint Commands

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

[TRANSLATION_FAILED] ### Start ROS-TCP Endpoint

```bash
ros2 run ros_tcp_endpoint default_server_endpoint --ros-args -p ROS_IP:=0.0.0.0
```

[TRANSLATION_FAILED] In Unity:
[TRANSLATION_FAILED] - Robotics > ROS Settings
[TRANSLATION_FAILED] - ROS IP Address: localhost
[TRANSLATION_FAILED] - ROS Port: 10000

[TRANSLATION_FAILED] ## Camera and Sensors

[TRANSLATION_FAILED] ### RGB Camera

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

[TRANSLATION_FAILED] ### Depth Camera

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

[TRANSLATION_FAILED] ## Synthetic Data Generation

[TRANSLATION_FAILED] ### Perception Camera (for labeled data)

[TRANSLATION_FAILED] Unity Perception package provides:

[TRANSLATION_FAILED] - Bounding boxes (2D/3D)
[TRANSLATION_FAILED] - Instance segmentation
[TRANSLATION_FAILED] - Semantic segmentation
[TRANSLATION_FAILED] - Keypoint annotation

[TRANSLATION_FAILED] Install:
```
Window > Package Manager > Unity Registry > Perception
```

[TRANSLATION_FAILED] Example labeler:

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

[TRANSLATION_FAILED] ### Domain Randomization

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

[TRANSLATION_FAILED] ## Complete Unity-ROS 2 Example

[TRANSLATION_FAILED] ### Scene Setup

[TRANSLATION_FAILED] 1. Create empty scene
[TRANSLATION_FAILED] 2. Add Plane (ground)
[TRANSLATION_FAILED] 3. Import humanoid URDF
[TRANSLATION_FAILED] 4. Add camera to robot head
[TRANSLATION_FAILED] 5. Add directional light

[TRANSLATION_FAILED] ### Unity Scripts

[TRANSLATION_FAILED] Attach to robot root:

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

[TRANSLATION_FAILED] ### ROS Launch File

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

[TRANSLATION_FAILED] ## Performance Tips

[TRANSLATION_FAILED] ### 1. Reduce Quality for Simulation

```csharp
void Start()
{
    QualitySettings.SetQualityLevel(2);  // Medium quality
    Application.targetFrameRate = 60;
}
```

[TRANSLATION_FAILED] ### 2. Use Object Pooling

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

[TRANSLATION_FAILED] ### 3. Batch Rendering

[TRANSLATION_FAILED] Use Unity's GPU instancing for multiple identical objects.

[TRANSLATION_FAILED] ## Summary

[TRANSLATION_FAILED] This week you learned:

[TRANSLATION_FAILED] - Unity Robotics Hub architecture
[TRANSLATION_FAILED] - Importing URDF to Unity
[TRANSLATION_FAILED] - ArticulationBody physics
[TRANSLATION_FAILED] - ROS 2 - Unity TCP communication
[TRANSLATION_FAILED] - Publishing camera and sensor data
[TRANSLATION_FAILED] - Synthetic data generation with Perception
[TRANSLATION_FAILED] - Domain randomization for sim-to-real
[TRANSLATION_FAILED] - Performance optimization

[TRANSLATION_FAILED] ## What's Next?

[TRANSLATION_FAILED] **Week 7: NVIDIA Isaac Sim** - Explore the most advanced robot simulator with RTX rendering, PhysX, and integrated AI tools.

[TRANSLATION_FAILED] **Next**: [Week 7: Isaac Sim →](../module-3-isaac/week7-isaac-sim.md)
