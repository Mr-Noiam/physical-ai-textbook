# ہفتہ 13: کیپ اسٹون پروجیکٹ - خود مختار ہیومنائڈ اسسٹنٹ

## تعارف

اس ہفتے، آپ **جو کچھ بھی سیکھا ہے** اسے ایک مکمل خود مختار ہیومنائڈ اسسٹنٹ میں ضم کریں گے۔ آپ کا روبوٹ اندرونی ماحول میں نیویگیٹ کرے گا، صوتی احکامات کو سمجھے گا، وژن-لینگویج ماڈلز کے ساتھ اشیاء کو پہچانے گا، اور کثیر مرحلہ والے کاموں کو انجام دے گا۔

## پروجیکٹ کا جائزہ

**مقصد**: ایک صوتی کنٹرول والا ہیومنائڈ بنانا جو کر سکتا ہے:
1. **سننا**: وسپر کے ذریعے قدرتی زبان کے احکامات قبول کرنا
2. **دیکھنا**: CLIP کے ساتھ اشیاء کا پتہ لگانا اور LLaVA کے ساتھ سوالات کے جواب دینا
3. **استدلال**: GPT-4 کے ساتھ اعمال کی منصوبہ بندی کرنا
4. **نیویگیٹ**: Nav2 کا استعمال کرتے ہوئے مقامات پر جانا
5. **ہیرا پھیری**: IK کا استعمال کرتے ہوئے اشیاء کو اٹھانا اور رکھنا

**مثال کے طور پر کام**: "کچن میں جاؤ، نیلا مگ تلاش کرو، اور اسے میرے پاس لاؤ۔"

## سسٹم فن تعمیر

```
┌─────────────────────────────────────────────────────┐
│                 یوزر انٹرفیس                       │
│              (آواز + بصری فیڈ بیک)               │
└──────────────────┬──────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────┐
│              ٹاسک آرکیسٹریٹر                       │
│         (GPT-4 پلاننگ + اسٹیٹ مشین)             │
└─┬────────────┬────────────┬──────────────┬─────────┘
  │            │            │              │
  ▼            ▼            ▼              ▼
┌────────┐ ┌────────┐ ┌──────────┐ ┌──────────────┐
│ وسپر   │ │  CLIP  │ │   Nav2   │ │ IK کنٹرولر  │
│  ASR   │ │ LLaVA  │ │نیویگیشن │ │ ہیرا پھیری   │
└────────┘ └────────┘ └──────────┘ └──────────────┘
     │         │           │              │
     └─────────┴───────────┴──────────────┘
                      │
              ┌───────▼────────┐
              │   ROS 2 گراف  │
              │ (ٹاپکس/سروسز)│
              └───────┬────────┘
                      │
              ┌───────▼────────┐
              │ آئزک سم / HW │
              │   (28-DOF)     │
              └────────────────┘
```

## ضروریات

یقینی بنائیں کہ پچھلے تمام ہفتوں کے پیکجز انسٹال ہیں:

```bash
# ROS 2 پیکجز
sudo apt install ros-humble-nav2-* ros-humble-robot-state-publisher

# پائیتھن پیکجز
pip install openai-whisper openai clip torch transformers sounddevice

# NVIDIA آئزک (سم کے لیے اختیاری)
# ہفتہ 7 کی انسٹالیشن دیکھیں
```

## مرحلہ 1: ٹاسک آرکیسٹریٹر

### اسٹیٹ مشین ڈیزائن

`humanoid_assistant/task_orchestrator.py` بنائیں:

```python
#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from enum import Enum
import openai
import os

class TaskState(Enum):
    IDLE = 0
    LISTENING = 1
    PLANNING = 2
    NAVIGATING = 3
    DETECTING = 4
    MANIPULATING = 5
    RETURNING = 6
    COMPLETE = 7
    ERROR = 8

class TaskOrchestrator(Node):
    def __init__(self):
        super().__init__('task_orchestrator')

        # OpenAI API
        openai.api_key = os.getenv("OPENAI_API_KEY")

        # اسٹیٹ مشین
        self.state = TaskState.IDLE
        self.current_task = None
        self.task_plan = []

        # سروس کلائنٹس (پرسیپشن، نیویگیشن، ہیرا پھیری سے جڑیں گے)
        self.setup_clients()

        # اسٹیٹ مشین کے لیے ٹائمر
        self.timer = self.create_timer(0.1, self.state_machine_loop)

        self.get_logger().info('ٹاسک آرکیسٹریٹر شروع ہو گیا')

    def setup_clients(self):
        """ایکشن/سروس کلائنٹس کو شروع کریں"""
        from nav2_msgs.action import NavigateToPose
        from humanoid_msgs.srv import DetectObject, PickObject

        self.nav_client = ActionClient(self, NavigateToPose, 'navigate_to_pose')
        self.detect_client = self.create_client(DetectObject, 'detect_object')
        self.pick_client = self.create_client(PickObject, 'pick_object')

    def state_machine_loop(self):
        """مرکزی اسٹیٹ مشین"""
        if self.state == TaskState.IDLE:
            # صوتی کمانڈ کا انتظار کریں
            pass

        elif self.state == TaskState.PLANNING:
            self.plan_task()

        elif self.state == TaskState.NAVIGATING:
            self.execute_navigation()

        elif self.state == TaskState.DETECTING:
            self.execute_detection()

        elif self.state == TaskState.MANIPULATING:
            self.execute_manipulation()

        elif self.state == TaskState.COMPLETE:
            self.get_logger().info('✅ کام مکمل!')
            self.state = TaskState.IDLE

    def plan_task(self):
        """GPT-4 کا استعمال کرتے ہوئے کام کو مراحل میں تقسیم کریں"""
        prompt = f"""
آپ ایک ہیومنائڈ روبوٹ ٹاسک پلانر ہیں۔ اس کمانڈ کو جوہری مراحل میں تقسیم کریں:
کمانڈ: "{self.current_task}"

دستیاب اعمال:
- navigate(location): ایک نامی مقام پر جائیں
- detect(object): وژن کا استعمال کرتے ہوئے ایک آبجیکٹ تلاش کریں
- pick(object): پتہ لگائے گئے آبجیکٹ کو پکڑیں
- place(location): آبجیکٹ کو مقام پر رکھیں

مراحل کی JSON فہرست آؤٹ پٹ کریں:
[{{"action": "navigate", "params": {{"location": "kitchen"}}}}, ...]
"""

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )

        # منصوبہ پارس کریں
        import json
        self.task_plan = json.loads(response.choices[0].message.content)

        self.get_logger().info(f'ٹاسک منصوبہ: {self.task_plan}')
        self.state = TaskState.NAVIGATING  # عمل درآمد شروع کریں

    def execute_navigation(self):
        """نیویگیشن مرحلہ انجام دیں"""
        # موجودہ مرحلہ حاصل کریں
        step = self.task_plan[0]

        if step['action'] == 'navigate':
            location = step['params']['location']
            self.get_logger().info(f'{location} پر نیویگیٹ کر رہا ہے')

            # Nav2 ہدف بھیجیں (سادہ)
            goal = self.create_navigation_goal(location)
            self.nav_client.send_goal_async(goal)

            # اگلی حالت پر جائیں
            self.task_plan.pop(0)
            self.state = TaskState.DETECTING if self.task_plan else TaskState.COMPLETE

    def execute_detection(self):
        """آبجیکٹ ڈیٹیکشن مرحلہ انجام دیں"""
        step = self.task_plan[0]

        if step['action'] == 'detect':
            object_name = step['params']['object']
            self.get_logger().info(f'{object_name} کا پتہ لگا رہا ہے')

            # ڈیٹیکشن سروس کو کال کریں
            request = DetectObject.Request()
            request.object_name = object_name
            future = self.detect_client.call_async(request)

            # نتیجہ کا انتظار کریں (سادہ)
            rclpy.spin_until_future_complete(self, future, timeout_sec=5.0)

            if future.result().found:
                self.task_plan.pop(0)
                self.state = TaskState.MANIPULATING
            else:
                self.get_logger().warn(f'آبجیکٹ {object_name} نہیں ملا')
                self.state = TaskState.ERROR

    def execute_manipulation(self):
        """پک/پلیس مرحلہ انجام دیں"""
        step = self.task_plan[0]

        if step['action'] == 'pick':
            object_name = step['params']['object']
            self.get_logger().info(f'{object_name} اٹھا رہا ہے')

            # ہیرا پھیری سروس کو کال کریں
            request = PickObject.Request()
            request.object_name = object_name
            self.pick_client.call_async(request)

            self.task_plan.pop(0)
            self.state = TaskState.NAVIGATING if self.task_plan else TaskState.COMPLETE

def main(args=None):
    rclpy.init(args=args)
    node = TaskOrchestrator()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## مرحلہ 2: وائس کمانڈ انٹرفیس

### وسپر انضمام

`humanoid_assistant/voice_interface.py` بنائیں:

```python
#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import whisper
import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write

class VoiceInterface(Node):
    def __init__(self):
        super().__init__('voice_interface')

        # وسپر ماڈل لوڈ کریں
        self.get_logger().info('وسپر ماڈل لوڈ ہو رہا ہے...')
        self.model = whisper.load_model("base")

        # ٹرانسکرائب شدہ کمانڈز کے لیے پبلشر
        self.command_pub = self.create_publisher(String, '/voice_command', 10)

        # ریکارڈنگ پیرامیٹرز
        self.sample_rate = 16000
        self.duration = 5  # سیکنڈز

        self.get_logger().info('وائس انٹرفیس تیار ہے۔ فعال کرنے کے لیے "روبوٹ" کہیں۔')

        # سننے کا لوپ شروع کریں
        self.timer = self.create_timer(0.5, self.listen_for_wake_word)

    def listen_for_wake_word(self):
        """مسلسل ویک ورڈ کے لیے سنیں"""
        self.get_logger().info('سن رہا ہوں...')

        # آڈیو ریکارڈ کریں
        audio = sd.rec(
            int(self.duration * self.sample_rate),
            samplerate=self.sample_rate,
            channels=1,
            dtype='float32'
        )
        sd.wait()

        # عارضی فائل محفوظ کریں
        write('/tmp/command.wav', self.sample_rate, audio)

        # ٹرانسکرائب کریں
        result = self.model.transcribe('/tmp/command.wav')
        text = result['text'].lower()

        self.get_logger().info(f'سنا: {text}')

        # ویک ورڈ کے لیے چیک کریں
        if 'robot' in text:
            # ویک ورڈ کے بعد کمانڈ نکالیں
            command = text.split('robot', 1)[1].strip()

            if command:
                self.get_logger().info(f'کمانڈ: {command}')

                # کمانڈ شائع کریں
                msg = String()
                msg.data = command
                self.command_pub.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = VoiceInterface()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## مرحلہ 3: وژن-لینگویج پرسیپشن

### CLIP + LLaVA انضمام

`humanoid_assistant/vision_perception.py` بنائیں:

```python
#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from humanoid_msgs.srv import DetectObject, AnswerQuestion
from cv_bridge import CvBridge
import torch
import clip
from PIL import Image as PILImage

class VisionPerception(Node):
    def __init__(self):
        super().__init__('vision_perception')
        self.bridge = CvBridge()

        # CLIP لوڈ کریں
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.clip_model, self.preprocess = clip.load("ViT-L/14", device=self.device)

        # کیمرہ کو سبسکرائب کریں
        self.subscription = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.image_callback,
            10
        )
        self.latest_image = None

        # سروسز
        self.detect_srv = self.create_service(
            DetectObject,
            'detect_object',
            self.detect_callback
        )

        self.get_logger().info('وژن پرسیپشن تیار ہے')

    def image_callback(self, msg):
        """تازہ ترین تصویر محفوظ کریں"""
        cv_image = self.bridge.imgmsg_to_cv2(msg, "rgb8")
        self.latest_image = PILImage.fromarray(cv_image)

    def detect_callback(self, request, response):
        """CLIP کا استعمال کرتے ہوئے آبجیکٹ کا پتہ لگائیں"""
        if self.latest_image is None:
            response.found = False
            return response

        # تصویر کو پری پروسیس کریں
        image = self.preprocess(self.latest_image).unsqueeze(0).to(self.device)

        # ٹیکسٹ سوالات
        text = clip.tokenize([
            f"a photo of a {request.object_name}",
            "a photo of background"
        ]).to(self.device)

        # مماثلت کا حساب لگائیں
        with torch.no_grad():
            image_features = self.clip_model.encode_image(image)
            text_features = self.clip_model.encode_text(text)

            similarity = (image_features @ text_features.T).softmax(dim=-1)
            confidence = similarity[0][0].item()

        self.get_logger().info(f'{request.object_name} کے لیے پتہ لگانے کا اعتماد: {confidence:.2%}')

        # حد
        response.found = confidence > 0.3
        response.confidence = confidence

        # 3D پوزیشن کا تخمینہ لگائیں (سادہ - حقیقی نظام میں ڈیپتھ کیمرہ استعمال کریں)
        if response.found:
            response.position.x = 1.0  # 1 میٹر آگے
            response.position.y = 0.0
            response.position.z = 0.5

        return response

def main(args=None):
    rclpy.init(args=args)
    node = VisionPerception()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## مرحلہ 4: نیویگیشن انضمام

### سیمنٹک لوکیشن میپنگ

`config/semantic_map.yaml` بنائیں:

```yaml
# Nav2 کے لیے سیمنٹک لوکیشن کوآرڈینیٹس
locations:
  kitchen:
    x: 5.0
    y: 3.0
    theta: 0.0

  living_room:
    x: 0.0
    y: 0.0
    theta: 1.57

  bedroom:
    x: -3.0
    y: 4.0
    theta: -1.57

  charging_station:
    x: 0.0
    y: 0.0
    theta: 0.0
```

`humanoid_assistant/semantic_navigator.py` بنائیں:

```python
#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from nav2_msgs.action import NavigateToPose
from geometry_msgs.msg import PoseStamped
import yaml

class SemanticNavigator(Node):
    def __init__(self):
        super().__init__('semantic_navigator')

        # سیمنٹک نقشہ لوڈ کریں
        with open('config/semantic_map.yaml') as f:
            config = yaml.safe_load(f)
            self.locations = config['locations']

        # Nav2 ایکشن کلائنٹ
        self.nav_client = ActionClient(self, NavigateToPose, 'navigate_to_pose')

        self.get_logger().info(f'{len(self.locations)} مقامات لوڈ کیے گئے')

    def navigate_to_location(self, location_name):
        """نامی مقام پر نیویگیٹ کریں"""
        if location_name not in self.locations:
            self.get_logger().error(f'نامعلوم مقام: {location_name}')
            return False

        loc = self.locations[location_name]

        # ہدف بنائیں
        goal = NavigateToPose.Goal()
        goal.pose = PoseStamped()
        goal.pose.header.frame_id = 'map'
        goal.pose.pose.position.x = loc['x']
        goal.pose.pose.position.y = loc['y']

        # یاو سے کواٹرنین
        import math
        theta = loc['theta']
        goal.pose.pose.orientation.z = math.sin(theta / 2)
        goal.pose.pose.orientation.w = math.cos(theta / 2)

        self.get_logger().info(f'{location_name} پر ({loc["x"]}, {loc["y"]}) پر نیویگیٹ کر رہا ہے')

        # ہدف بھیجیں
        self.nav_client.wait_for_server()
        future = self.nav_client.send_goal_async(goal)

        return True

def main(args=None):
    rclpy.init(args=args)
    node = SemanticNavigator()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## مرحلہ 5: ہیرا پھیری کنٹرولر

### IK پر مبنی پک اور پلیس

`humanoid_assistant/manipulation_controller.py` بنائیں:

```python
#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from humanoid_msgs.srv import PickObject, PlaceObject
import numpy as np

class ManipulationController(Node):
    def __init__(self):
        super().__init__('manipulation_controller')

        # IK سالور (ہفتہ 12 کا نفاذ استعمال کریں)
        from humanoid_kinematics import InverseKinematics
        self.ik_solver = InverseKinematics()

        # سروسز
        self.pick_srv = self.create_service(PickObject, 'pick_object', self.pick_callback)
        self.place_srv = self.create_service(PlaceObject, 'place_object', self.place_callback)

        # جوائنٹ کمانڈ پبلشر
        from sensor_msgs.msg import JointState
        self.joint_pub = self.create_publisher(JointState, '/joint_commands', 10)

        self.get_logger().info('ہیرا پھیری کنٹرولر تیار ہے')

    def pick_callback(self, request, response):
        """پک کی ترتیب انجام دیں"""
        # وژن سروس سے آبجیکٹ کی پوزیشن فرض کریں
        target_pos = np.array([
            request.object_position.x,
            request.object_position.y,
            request.object_position.z
        ])

        self.get_logger().info(f'{target_pos} پر اٹھا رہا ہے')

        # 1. پری گراسپ: بازو کو آبجیکٹ کے اوپر لے جائیں
        pre_grasp_pos = target_pos + np.array([0, 0, 0.1])
        joint_angles = self.ik_solver.solve(pre_grasp_pos, arm='right')
        self.move_arm(joint_angles)

        # 2. گرپر کھولیں
        self.control_gripper(open=True)

        # 3. اپروچ: آبجیکٹ کی طرف نیچے جائیں
        joint_angles = self.ik_solver.solve(target_pos, arm='right')
        self.move_arm(joint_angles)

        # 4. گرپر بند کریں
        self.control_gripper(open=False)

        # 5. اٹھائیں
        lift_pos = target_pos + np.array([0, 0, 0.2])
        joint_angles = self.ik_solver.solve(lift_pos, arm='right')
        self.move_arm(joint_angles)

        response.success = True
        return response

    def move_arm(self, joint_angles):
        """جوائنٹ کمانڈز شائع کریں"""
        msg = JointState()
        msg.name = ['right_shoulder_pitch', 'right_shoulder_roll',
                    'right_elbow', 'right_wrist_pitch']
        msg.position = joint_angles.tolist()

        self.joint_pub.publish(msg)

        # حرکت مکمل ہونے کا انتظار کریں (سادہ)
        import time
        time.sleep(2.0)

    def control_gripper(self, open=True):
        """گرپر کھولیں یا بند کریں"""
        self.get_logger().info(f'گرپر: {"کھلا" if open else "بند"}')
        # گرپر کمانڈ شائع کریں

def main(args=None):
    rclpy.init(args=args)
    node = ManipulationController()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## مکمل لانچ فائل

`launch/humanoid_assistant.launch.py` بنائیں:

```python
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    # Nav2 (ہفتہ 9 سے)
    nav2_dir = get_package_share_directory('nav2_bringup')
    nav2_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(nav2_dir, 'launch', 'navigation_launch.py')
        ),
        launch_arguments={'use_sim_time': 'true'}.items()
    )

    return LaunchDescription([
        # نیویگیشن اسٹیک
        nav2_launch,

        # وائس انٹرفیس
        Node(
            package='humanoid_assistant',
            executable='voice_interface',
            name='voice_interface',
            output='screen'
        ),

        # وژن پرسیپشن
        Node(
            package='humanoid_assistant',
            executable='vision_perception',
            name='vision_perception',
            output='screen'
        ),

        # سیمنٹک نیویگیٹر
        Node(
            package='humanoid_assistant',
            executable='semantic_navigator',
            name='semantic_navigator',
            output='screen'
        ),

        # ہیرا پھیری کنٹرولر
        Node(
            package='humanoid_assistant',
            executable='manipulation_controller',
            name='manipulation_controller',
            output='screen'
        ),

        # ٹاسک آرکیسٹریٹر (مرکزی دماغ)
        Node(
            package='humanoid_assistant',
            executable='task_orchestrator',
            name='task_orchestrator',
            output='screen',
            parameters=[{'openai_api_key': os.getenv('OPENAI_API_KEY')}]
        ),
    ])
```

## اپنے سسٹم کی جانچ

### یونٹ ٹیسٹ

`test/test_integration.py` بنائیں:

```python
import pytest
import rclpy
from humanoid_msgs.srv import DetectObject

def test_object_detection():
    """وژن پرسیپشن سروس کی جانچ کریں"""
    rclpy.init()
    node = rclpy.create_node('test_node')

    client = node.create_client(DetectObject, 'detect_object')
    client.wait_for_service(timeout_sec=5.0)

    request = DetectObject.Request()
    request.object_name = "cup"

    future = client.call_async(request)
    rclpy.spin_until_future_complete(node, future)

    assert future.result().found in [True, False]

    node.destroy_node()
    rclpy.shutdown()
```

### انضمام ٹیسٹ کے منظرنامے

```bash
# منظر نامہ 1: سادہ فیچ
ros2 topic pub /voice_command std_msgs/String "data: 'کچن میں جاؤ اور کپ تلاش کرو'"

# منظر نامہ 2: کثیر مرحلہ والا کام
ros2 topic pub /voice_command std_msgs/String "data: 'مجھے بیڈ روم سے لیپ ٹاپ لا دو'"

# منظر نامہ 3: بصری سوال
ros2 service call /ask_question humanoid_msgs/AskQuestion "{question: 'تمہیں کون سی اشیاء نظر آ رہی ہیں؟'}"
```

## تعیناتی کے اختیارات

### آپشن 1: آئزک سم (ترقی کے لیے تجویز کردہ)

```bash
# ہیومنائڈ کے ساتھ آئزک سم لانچ کریں
./isaac-sim.sh

# الگ ٹرمینل میں:
ros2 launch humanoid_assistant humanoid_assistant.launch.py use_sim_time:=true
```

### آپشن 2: حقیقی ہارڈ ویئر

ضروریات:
- 28-DOF ہیومنائڈ پلیٹ فارم
- NVIDIA Jetson AGX Orin (64GB)
- RealSense D435i کیمرہ
- USB مائیکروفون

```bash
# روبوٹ کمپیوٹر پر:
ros2 launch humanoid_assistant humanoid_assistant.launch.py use_sim_time:=false
```

## کارکردگی کی اصلاح

### لیٹنسی کے اہداف

| جزو | ہدف لیٹنسی | اصلاح |
|-----------|---------------|--------------|
| آواز کی شناخت | &lt;2s | وسپر بیس ماڈل استعمال کریں |
| آبجیکٹ ڈیٹیکشن | &lt;500ms | CLIP ViT-B/32, GPU |
| نیویگیشن پلاننگ | &lt;1s | Nav2 GPU کاسٹ میپس |
| IK حل کرنا | &lt;100ms | کیشڈ حل |
| کل ٹاسک سائیکل | &lt;10s | متوازی عمل درآمد |

### GPU کا استعمال

```python
# GPU استعمال کی نگرانی کریں
import torch
print(f"GPU میموری: {torch.cuda.memory_allocated() / 1e9:.2f} GB")
```

## تشخیصی روبرک

### कार्यात्मक आवश्यकताएं (60 پوائنٹس)

- [20] **صوتی کنٹرول**: احکامات کو درست طریقے سے ٹرانسکرائب اور انجام دیتا ہے
- [20] **وژن**: مخصوص اشیاء کا >70% درستگی کے ساتھ پتہ لگاتا ہے
- [10] **نیویگیشن**: نامی مقامات تک 10 سینٹی میٹر کے اندر پہنچتا ہے
- [10] **ہیرا پھیری**: 80% وقت اشیاء کو کامیابی سے پکڑتا ہے

### انضمام (30 پوائنٹس)

- [10] **کثیر مرحلہ والے کام**: 3 مرحلہ والے کاموں کو خود مختار طور پر مکمل کرتا ہے
- [10] **غلطی سے بحالی**: گمشدہ اشیاء کو احسن طریقے سے ہینڈل کرتا ہے
- [10] **حقیقی وقت کی کارکردگی**: لیٹنسی کے اہداف کو پورا کرتا ہے

### کوڈ کا معیار (10 پوائنٹس)

- [5] **دستاویزی**: واضح ڈاک اسٹرنگز اور تبصرے
- [5] **جانچ**: تمام اجزاء کے لیے یونٹ ٹیسٹ

## توسیع (اختیاری)

### 1. ملٹی روبوٹ کوآرڈینیشن

```python
# متعدد ہیومنائڈز کے ساتھ کوآرڈینیٹ کریں
from humanoid_msgs.msg import TaskAssignment

class MultiRobotCoordinator(Node):
    def assign_tasks(self, tasks):
        # دستیاب روبوٹس میں کام تقسیم کریں
        for robot_id, task in enumerate(tasks):
            self.publish_assignment(robot_id, task)
```

### 2. مظاہرے سے سیکھنا

```python
# انسانی مظاہروں کو ریکارڈ کریں
from humanoid_msgs.msg import TrajectoryRecording

class DemonstrationRecorder(Node):
    def record_trajectory(self):
        # جوائنٹ اسٹیٹس + آبجیکٹ تعاملات ریکارڈ کریں
        # رویے کی کلوننگ پالیسی کو تربیت دیں
        pass
```

### 3. اردو زبان کی معاونت

```python
# اردو صوتی احکامات شامل کریں (وسپر ملٹی لینگول کا استعمال کرتے ہوئے)
from transformers import WhisperProcessor, WhisperForConditionalGeneration

processor = WhisperProcessor.from_pretrained("openai/whisper-large-v2")
model = WhisperForConditionalGeneration.from_pretrained("openai/whisper-large-v2")

# اردو آڈیو کو ٹرانسکرائب کریں
result = model.transcribe(audio, language="ur")
```

## خلاصہ

یہ کیپ اسٹون پروجیکٹ ضم کرتا ہے:

- **ماڈیول 1 (ROS 2)**: پیکیج کی ساخت، نوڈز، ٹاپکس، سروسز، لانچ فائلیں
- **ماڈیول 2 (سیمولیشن)**: گیزبو/یونٹی/آئزک سم میں جانچ
- **ماڈیول 3 (NVIDIA)**: آئزک ROS پرسیپشن، Nav2 نیویگیشن
- **ماڈیول 4 (VLA)**: CLIP ڈیٹیکشن، وسپر ASR، GPT-4 پلاننگ

اب آپ کے پاس ایک **مکمل خود مختار ہیومنائڈ سسٹم** ہے جو فزیکل AI تحقیق سے قابل تعیناتی روبوٹکس تک کے فرق کو پر کرتا ہے۔

## اگلے اقدامات

1. **حقیقی ہارڈ ویئر پر تعینات کریں**: اپنے سسٹم کو فزیکل ہیومنائڈ پر پورٹ کریں
2. **اوپن سورس میں حصہ ڈالیں**: ROS 2 پیکجز میں بہتری شیئر کریں
3. **تحقیق**: ڈیفیوژن پالیسیاں، درجہ بندی RL، سم-ٹو-ریئل کو دریافت کریں
4. **صنعت**: ان مہارتوں کو روبوٹکس کمپنیوں، تحقیقی لیبز میں لاگو کریں

**فزیکل AI اور ہیومنائڈ روبوٹکس کورس مکمل کرنے پر مبارک ہو!** 🎓🤖

---

**وسائل**:
- [ROS 2 ڈاکومنٹیشن](https://docs.ros.org/en/humble/)
- [NVIDIA آئزک](https://developer.nvidia.com/isaac-sim)
- [اوپن اے آئی API](https://platform.openai.com/docs)
- [ہیومنائڈ روبوٹکس پیپرز](https://github.com/Improbable-AI/awesome-humanoid-robotics)