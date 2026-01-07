# ہفتہ 6: روبوٹ ویژولائزیشن کے لیے یونٹی

## تعارف

اس ہفتے، ہم **یونٹی روبوٹکس ہب** کو دریافت کریں گے، جو روبوٹکس میں فوٹو ریئلسٹک رینڈرنگ، فزکس سیمولیشن، اور مصنوعی ڈیٹا جنریشن لاتا ہے۔ یونٹی کمپیوٹر وژن اور VLA ماڈلز کے لیے بصری طور پر درست تربیتی ڈیٹا بنانے میں مہارت رکھتا ہے۔

## روبوٹکس کے لیے یونٹی کیوں؟

**گیزبو پر فوائد**:

- **فوٹو ریئلزم**: سم-ٹو-ریئل منتقلی کے لیے اعلیٰ معیار کے گرافکس
- **مصنوعی ڈیٹا**: لیبل شدہ ڈیٹا سیٹ بنائیں (باؤنڈنگ باکسز، سیگمنٹیشن ماسک)
- **کارکردگی**: GPU-ایکسلریٹڈ فزکس اور رینڈرنگ
- **ڈومین رینڈمائزیشن**: روشنی، بناوٹ، آبجیکٹ پوز کو تبدیل کرنا آسان ہے
- **ایسٹ سٹور**: ہزاروں 3D ماڈلز اور ماحول

**استعمال کے معاملات**:
- وژن ماڈلز کی تربیت
- انسانی روبوٹ کے تعامل کا تصور
- VR/AR ٹیلی آپریشن
- مارکیٹنگ اور ڈیمو

## یونٹی روبوٹکس ہب فن تعمیر

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

## انسٹالیشن

### یونٹی ہب اور ایڈیٹر

```bash
# یونٹی ہب ڈاؤن لوڈ کریں
wget https://public-cdn.cloud.unity3d.com/hub/prod/UnityHubSetup.AppImage

# یونٹی 2022.3 LTS انسٹال کریں
# Unity Hub > Installs > Add > 2022.3 LTS
```

### یونٹی روبوٹکس پیکجز

یونٹی میں، پیکیج مینیجر کھولیں:

1. Window > Package Manager
2. گٹ یو آر ایل سے پیکیج شامل کریں:
   - `https://github.com/Unity-Technologies/ROS-TCP-Connector.git?path=/com.unity.robotics.ros-tcp-connector`
   - `https://github.com/Unity-Technologies/URDF-Importer.git?path=/com.unity.robotics.urdf-importer`

### ROS 2 TCP اینڈ پوائنٹ

```bash
# ROS-TCP-Endpoint کلون کریں
cd ~/ros2_ws/src
git clone https://github.com/Unity-Technologies/ROS-TCP-Endpoint

# بلڈ کریں
cd ~/ros2_ws
colcon build --packages-select ros_tcp_endpoint

# سورس
source install/setup.bash
```

## ہیومنائڈ URDF درآمد کرنا

### 1. URDF تیار کریں

یونٹی URDF امپورٹر کی ضروریات ہیں:

```xml
<?xml version="1.0"?>
<robot name="humanoid">
  <!-- یقینی بنائیں کہ تمام میشز مطلق راستے یا package:// URIs استعمال کرتے ہیں -->
  <link name="torso">
    <visual>
      <geometry>
        <!-- معاونت شدہ: .obj, .stl, .dae -->
        <mesh filename="package://humanoid_description/meshes/torso.obj"/>
      </geometry>
    </visual>
  </link>
</robot>
```

### 2. یونٹی میں درآمد کریں

1. Assets > Import Robot from URDF
2. اپنی URDF فائل منتخب کریں
3. درآمدی ترتیبات تشکیل دیں:
   - Axis Type: Y-Axis
   - Mesh Decomposer: VHACD (تصادم کے لیے)
4. درآمد کریں

یونٹی بناتا ہے:
- گیم آبجیکٹ درجہ بندی جو URDF سے ملتی ہے
- جوڑوں کے لیے آرٹیکولیشن باڈی اجزاء
- کولائیڈرز اور بصری میشز

### 3. آرٹیکولیشن باڈیز کو تشکیل دیں

یونٹی **آرٹیکولیشن باڈی** (رجڈ باڈی کا جانشین) استعمال کرتا ہے:

```csharp
using UnityEngine;

public class JointController : MonoBehaviour
{
    private ArticulationBody[] joints;

    void Start()
    {
        // تمام آرٹیکولیشن باڈیز (جوائنٹس) حاصل کریں
        joints = GetComponentsInChildren<ArticulationBody>();

        foreach (var joint in joints)
        {
            if (joint.jointType == ArticulationJointType.RevoluteJoint)
            {
                // ڈرائیو پراپرٹیز سیٹ کریں
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

## ROS 2 - یونٹی مواصلات

### یونٹی سائیڈ: جوائنٹ کمانڈز کو سبسکرائب کریں

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
        // ROS سے جڑیں
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

### ROS-TCP اینڈ پوائنٹ شروع کریں

```bash
ros2 run ros_tcp_endpoint default_server_endpoint --ros-args -p ROS_IP:=0.0.0.0
```

یونٹی میں:
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

### ڈیپتھ کیمرہ

```csharp
public class DepthCameraPublisher : MonoBehaviour
{
    private Camera depthCam;

    void Start()
    {
        depthCam = GetComponent<Camera>();
        depthCam.depthTextureMode = DepthTextureMode.Depth;

        // ڈیپتھ ویژولائزیشن کے لیے شیڈر
        depthCam.SetReplacementShader(Shader.Find("Custom/DepthShader"), "");
    }

    // ڈیپتھ کو Float32 ارے کے طور پر شائع کریں
    void PublishDepth()
    {
        // ڈیپتھ بفر کو ROS PointCloud2 میں تبدیل کریں
        // نفاذ استعمال کے کیس پر منحصر ہے
    }
}
```

## مصنوعی ڈیٹا جنریشن

### پرسیپشن کیمرہ (لیبل شدہ ڈیٹا کے لیے)

یونٹی پرسیپشن پیکیج فراہم کرتا ہے:

- باؤنڈنگ باکسز (2D/3D)
- انسٹنس سیگمنٹیشن
- سیمنٹک سیگمنٹیشن
- کی پوائنٹ تشریح

انسٹال کریں:
```
Window > Package Manager > Unity Registry > Perception
```

مثال کے طور پر لیبلر:

```csharp
using UnityEngine;
using UnityEngine.Perception.GroundTruth;

public class DatasetGenerator : MonoBehaviour
{
    void Start()
    {
        var perceptionCamera = GetComponent<PerceptionCamera>();

        // لیبلرز شامل کریں
        var boundingBox2DLabeler = new BoundingBox2DLabeler();
        perceptionCamera.AddLabeler(boundingBox2DLabeler);

        var semanticSegmentationLabeler = new SemanticSegmentationLabeler();
        perceptionCamera.AddLabeler(semanticSegmentationLabeler);
    }
}
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

## مکمل یونٹی-ROS 2 مثال

### سین سیٹ اپ

1. خالی سین بنائیں
2. پلین (زمین) شامل کریں
3. ہیومنائڈ URDF درآمد کریں
4. روبوٹ کے سر پر کیمرہ شامل کریں
5. ڈائریکشنل لائٹ شامل کریں

### یونٹی اسکرپٹس

روبوٹ روٹ سے منسلک کریں:

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
        gameObject.AddComponent<IMUPublisher>();
    }
}
```

### ROS لانچ فائل

```python
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        # ROS-TCP اینڈ پوائنٹ
        Node(
            package='ros_tcp_endpoint',
            executable='default_server_endpoint',
            parameters=[{'ROS_IP': '0.0.0.0'}]
        ),

        # جوائنٹ اسٹیٹ پبلشر
        Node(
            package='humanoid_unity',
            executable='joint_publisher'
        ),

        # امیج ویور
        Node(
            package='rqt_image_view',
            executable='rqt_image_view',
            arguments=['image:=/camera/image_raw']
        )
    ])
```

## کارکردگی کی تجاویز

### 1. سیمولیشن کے لیے معیار کو کم کریں

```csharp
void Start()
{
    QualitySettings.SetQualityLevel(2);  // درمیانہ معیار
    Application.targetFrameRate = 60;
}
```

### 2. آبجیکٹ پولنگ استعمال کریں

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

### 3. بیچ رینڈرنگ

متعدد یکساں اشیاء کے لیے یونٹی کا GPU انسٹرنسنگ استعمال کریں۔

## خلاصہ

اس ہفتے آپ نے سیکھا:

- یونٹی روبوٹکس ہب فن تعمیر
- URDF کو یونٹی میں درآمد کرنا
- آرٹیکولیشن باڈی فزکس
- ROS 2 - یونٹی TCP مواصلات
- کیمرہ اور سینسر ڈیٹا شائع کرنا
- پرسیپشن کے ساتھ مصنوعی ڈیٹا جنریشن
- سم-ٹو-ریئل کے لیے ڈومین رینڈمائزیشن
- کارکردگی کی اصلاح

## آگے کیا ہے؟

**ہفتہ 7: NVIDIA Isaac Sim** - RTX رینڈرنگ، PhysX، اور مربوط AI ٹولز کے ساتھ سب سے جدید روبوٹ سمیلیٹر کو دریافت کریں۔

**آگے**: [ہفتہ 7: Isaac Sim →](../module-3-isaac/week7-isaac-sim.md)