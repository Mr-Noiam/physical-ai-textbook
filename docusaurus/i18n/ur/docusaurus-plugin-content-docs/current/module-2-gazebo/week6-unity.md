# ہفتہ 6: روبوٹ کی تصویر سازی کے لیے Unity

## تعارف

اس ہفتے، ہم **Unity Robotics Hub** کو دریافت کریں گے، جو روبوٹکس میں فوٹو ریئلسٹک رینڈرنگ، طبیعیات کی سمولیشن، اور مصنوعی ڈیٹا کی تخلیق فراہم کرتا ہے۔ Unity کمپیوٹر وژن اور VLA ماڈلز کے لیے بصری طور پر درست تربیتی ڈیٹا بنانے میں بہترین ہے۔

## روبوٹکس کے لیے Unity کیوں؟

**Gazebo پر فوائد**:

- **فوٹو ریئلزم**: سم سے حقیقت کی منتقلی کے لیے اعلیٰ معیار کا گرافکس
- **مصنوعی ڈیٹا**: لیبل شدہ ڈیٹا سیٹ تیار کریں (باؤنڈنگ باکسز، تقسیم کے ماسک)
- **کارکردگی**: GPU سے تیز شدہ طبیعیات اور رینڈرنگ
- **ڈومین رینڈمائزیشن**: روشنی، ٹیکسچر، آبجیکٹ کی پوزیشن میں تبدیلی آسان
- **ایسٹ اسٹور**: ہزاروں 3D ماڈلز اور ماحول

**استعمال کے معاملات**:
- وژن ماڈلز کی تربیت
- انسان-روبوٹ تعامل کی تصویر سازی
- VR/AR ٹیلی آپریشن
- مارکیٹنگ اور ڈیمو

## Unity Robotics Hub فن تعمیر

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

## تنصیب

### Unity Hub اور Editor

```bash
# Unity Hub ڈاؤن لوڈ کریں
wget https://public-cdn.cloud.unity3d.com/hub/prod/UnityHubSetup.AppImage

# Unity 2022.3 LTS انسٹال کریں
# Unity Hub > Installs > Add > 2022.3 LTS
```

### Unity Robotics پیکجز

Unity میں، Package Manager کھولیں:

1. Window > Package Manager
2. git URL سے پیکیج شامل کریں:
   - `https://github.com/Unity-Technologies/ROS-TCP-Connector.git?path=/com.unity.robotics.ros-tcp-connector`
   - `https://github.com/Unity-Technologies/URDF-Importer.git?path=/com.unity.robotics.urdf-importer`

### ROS 2 TCP Endpoint

```bash
# ROS-TCP-Endpoint کلون کریں
cd ~/ros2_ws/src
git clone https://github.com/Unity-Technologies/ROS-TCP-Endpoint

# بنائیں
cd ~/ros2_ws
colcon build --packages-select ros_tcp_endpoint

# سورس کریں
source install/setup.bash
```

## ہیومینائیڈ URDF درآمد کرنا

### 1. URDF تیار کریں

Unity URDF Importer کی ضروریات ہیں:

```xml
<?xml version="1.0"?>
<robot name="humanoid">
  <!-- یقینی بنائیں کہ تمام meshes مطلق راستے یا package:// URIs استعمال کریں -->
  <link name="torso">
    <visual>
      <geometry>
        <!-- تعاون یافتہ: .obj, .stl, .dae -->
        <mesh filename="package://humanoid_description/meshes/torso.obj"/>
      </geometry>
    </visual>
  </link>
</robot>
```

### 2. Unity میں درآمد کریں

1. Assets > Import Robot from URDF
2. اپنی URDF فائل منتخب کریں
3. درآمد کی ترتیبات کو ترتیب دیں:
   - Axis Type: Y-Axis
   - Mesh Decomposer: VHACD (ٹکراؤ کے لیے)
4. درآمد کریں

Unity تخلیق کرتا ہے:
- GameObject کی ہائیرارکی جو URDF سے میل کھاتی ہے
- جوائنٹس کے لیے ArticulationBody اجزاء
- Colliders اور بصری meshes

### 3. ArticulationBodies کو ترتیب دیں

Unity **ArticulationBody** استعمال کرتا ہے (Rigidbody کا جانشین):

```csharp
using UnityEngine;

public class JointController : MonoBehaviour
{
    private ArticulationBody[] joints;

    void Start()
    {
        // تمام articulation bodies (joints) حاصل کریں
        joints = GetComponentsInChildren<ArticulationBody>();

        foreach (var joint in joints)
        {
            if (joint.jointType == ArticulationJointType.RevoluteJoint)
            {
                // ڈرائیو کی خصوصیات مقرر کریں
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

## ROS 2 - Unity مواصلات

### Unity سائیڈ: جوائنٹ کمانڈز کو سبسکرائب کریں

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
        // ROS سے منسلک ہوں
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

### ROS سائیڈ: جوائنٹ کمانڈز شائع کریں

```python
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
import math

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

### ROS-TCP Endpoint شروع کریں

```bash
ros2 run ros_tcp_endpoint default_server_endpoint --ros-args -p ROS_IP:=0.0.0.0
```

Unity میں:
- Robotics > ROS Settings
- ROS IP Address: localhost
- ROS Port: 10000

## کیمرہ اور سینسرز

### RGB کیمرہ

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

## مصنوعی ڈیٹا کی تخلیق

### Perception کیمرہ (لیبل شدہ ڈیٹا کے لیے)

Unity Perception پیکیج فراہم کرتا ہے:

- باؤنڈنگ باکسز (2D/3D)
- Instance segmentation
- Semantic segmentation
- Keypoint annotation

انسٹال کریں:
```
Window > Package Manager > Unity Registry > Perception
```

### ڈومین رینڈمائزیشن

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

## مکمل Unity-ROS 2 مثال

### Scene سیٹ اپ

1. خالی scene بنائیں
2. Plane (زمین) شامل کریں
3. ہیومینائیڈ URDF درآمد کریں
4. روبوٹ کے سر میں کیمرہ شامل کریں
5. Directional light شامل کریں

### Unity Scripts

روبوٹ root سے منسلک کریں:

```csharp
using UnityEngine;
using Unity.Robotics.ROSTCPConnector;

public class HumanoidController : MonoBehaviour
{
    void Start()
    {
        // ROS کنکشن شروع کریں
        var ros = ROSConnection.GetOrCreateInstance();
        ros.ConnectOnStart = true;

        // اجزاء شامل کریں
        gameObject.AddComponent<JointStateSubscriber>();
        gameObject.AddComponent<CameraPublisher>();
    }
}
```

### ROS Launch فائل

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

## کارکردگی کے نکات

### 1. سمولیشن کے لیے معیار کم کریں

```csharp
void Start()
{
    QualitySettings.SetQualityLevel(2);  // درمیانی معیار
    Application.targetFrameRate = 60;
}
```

### 2. Object Pooling استعمال کریں

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

ایک جیسے متعدد اشیاء کے لیے Unity کی GPU instancing استعمال کریں۔

## خلاصہ

اس ہفتے آپ نے سیکھا:

- Unity Robotics Hub فن تعمیر
- URDF کو Unity میں درآمد کرنا
- ArticulationBody طبیعیات
- ROS 2 - Unity TCP مواصلات
- کیمرہ اور سینسر ڈیٹا شائع کرنا
- Perception کے ساتھ مصنوعی ڈیٹا کی تخلیق
- سم سے حقیقت کے لیے ڈومین رینڈمائزیشن
- کارکردگی کی اصلاح

## اگلا کیا ہے؟

**ہفتہ 7: NVIDIA Isaac Sim** - RTX رینڈرنگ، PhysX، اور مربوط AI ٹولز کے ساتھ سب سے جدید روبوٹ سمیولیٹر دریافت کریں۔

**اگلا**: [ہفتہ 7: Isaac Sim →](../module-3-isaac/week7-isaac-sim.md)
