# ہفتہ 2: ROS 2 کی تعمیرات - نوڈز، موضوعات، خدمات
## کا تعارف
اس ہفتے، ہم ROS 2 کے بنیادی مواصلاتی پیٹرنز کا جائزہ لیں گے اور اپنے پہلے روبوٹ نوڈز بنائیں گے۔ آپ یہ سیکھیں گے کہ تقسیم شدہ روبوٹ سسٹمز کس طرح publish-subscribe اور request-response پیراڈائمز کا استعمال کرتے ہوئے بات چیت کرتے ہیں۔
## ROS 2 حسابی گراف
ROS 2 کی ایپلیکیشنز کو **حسابی گراف** کے طور پر نوڈز میں منظم کیا جاتا ہے:
```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│Camera Node  │  topic  │ Vision Node  │  topic  │ Planner Node│
│  (Publisher)│────────>│(Sub + Pub)   │────────>│(Subscriber) │
└─────────────┘         └──────────────┘         └─────────────┘
       │                                                  │
       │                                                  │
       └──────────service: /get_camera_info─────────────┘
```

### اہم تصورات
**نوڈ**: ایک عمل جو حساب کتاب انجام دیتا ہے (کیمرہ ڈرائیور، منصوبہ ساز، کنٹرولر)
**موضوع**: غیر ہم وقتی سٹریمنگ ڈیٹا کے لیے نامزد چینل (سینسر ڈیٹا، احکامات)
**سروس**: ہم وقتی درخواست-جواب تعامل (پیرا میٹر حاصل کریں، عمل شروع کریں)
**عمل**: فیڈبیک کے ساتھ طویل مدتی کام (ہدف کی طرف جانا، چیز اٹھانا)
## نوڈز: بنیادی بلاکس
### نوڈ کیا ہے؟
ایک **نوڈ** ایک مخصوص مقصد کے لیے چلنے والا پروگرام ہے جو دوسرے نوڈز کے ساتھ بات چیت کرتا ہے:
```python
import rclpy
from rclpy.node import Node

class MinimalNode(Node):
    def __init__(self):
        super().__init__('minimal_node')
        self.get_logger().info('Node started!')

def main(args=None):
    rclpy.init(args=args)
    node = MinimalNode()
    rclpy.spin(node)  # Keep node alive
    rclpy.shutdown()
```

**نوڈ کی زندگی کا چکر**:
1. `rclpy.init()` - ROS 2 سیاق و سباق کو شروع کریں
2. نوڈ کا نمونہ بنائیں
3. `rclpy.spin()` - کال بیکس (سبسکرپشنز، ٹائمرز، خدمات) کو پروسیس کریں
4. `rclpy.shutdown()` - صاف بندش
### نوڈ کی دریافت
ROS 2 **DDS (ڈیٹا تقسیم سروس)** کا استعمال خودکار نوڈ دریافت کے لیے کرتا ہے:
- نوڈز اپنے موضوعات/سروسز کو شروع ہونے پر اشتہار دیتے ہیں
- دوسرے نوڈز انہیں خود بخود دریافت کرتے ہیں (کوئی ماسٹر پروسیس کی ضرورت نہیں!)
- ملٹی مشین کی حمایت بغیر کسی اضافی کام کے
## موضوعات: پب-سب مواصلات
### ناشر کی مثال
100 Hz پر IMU ڈیٹا شائع کرنا:
```python
from rclpy.node import Node
from sensor_msgs.msg import Imu

class ImuPublisher(Node):
    def __init__(self):
        super().__init__('imu_publisher')
        self.publisher_ = self.create_publisher(Imu, '/imu/data', 10)
        self.timer = self.create_timer(0.01, self.publish_imu)  # 100 Hz

    def publish_imu(self):
        msg = Imu()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'imu_link'
        # Fill in IMU data...
        self.publisher_.publish(msg)
```

### سبسکرائبر کی مثال
IMU ڈیٹا کی پروسیسنگ:
```python
from rclpy.node import Node
from sensor_msgs.msg import Imu

class ImuSubscriber(Node):
    def __init__(self):
        super().__init__('imu_subscriber')
        self.subscription = self.create_subscription(
            Imu,
            '/imu/data',
            self.imu_callback,
            10  # QoS queue size
        )

    def imu_callback(self, msg):
        # Process IMU data
        accel = msg.linear_acceleration
        self.get_logger().info(f'Accel: x={accel.x:.2f} m/s²')
```

### سروس کا معیار (QoS)
ROS 2 پیغام کی ترسیل پر باریک بینی سے کنٹرول کی اجازت دیتا ہے:
```python
from rclpy.qos import QoSProfile, QoSReliabilityPolicy, QoSHistoryPolicy

qos_profile = QoSProfile(
    reliability=QoSReliabilityPolicy.BEST_EFFORT,  # vs RELIABLE
    history=QoSHistoryPolicy.KEEP_LAST,
    depth=10
)

self.publisher_ = self.create_publisher(Imu, '/imu/data', qos_profile)
```

**قابل اعتماد**:
- `BEST_EFFORT`: تیز، پیغامات گرا سکتا ہے (سینسر کا ڈیٹا)
- `RELIABLE`: ترسیل کی ضمانت دیتا ہے (احکامات)
## خدمات: درخواست-جواب
### سروس سرور
کیمرے کی کیلیبریشن کی معلومات فراہم کریں:
```python
from rclpy.node import Node
from sensor_msgs.srv import SetCameraInfo

class CameraServer(Node):
    def __init__(self):
        super().__init__('camera_server')
        self.srv = self.create_service(
            SetCameraInfo,
            '/camera/set_camera_info',
            self.set_info_callback
        )

    def set_info_callback(self, request, response):
        # Validate and store calibration
        response.success = True
        response.status_message = 'Calibration saved'
        return response
```

### سروس کلائنٹ
کیلیبریشن کی درخواست:
```python
from sensor_msgs.srv import SetCameraInfo

class CameraClient(Node):
    def __init__(self):
        super().__init__('camera_client')
        self.client = self.create_client(SetCameraInfo, '/camera/set_camera_info')

    def send_request(self, camera_info):
        request = SetCameraInfo.Request()
        request.camera_info = camera_info

        future = self.client.call_async(request)
        rclpy.spin_until_future_complete(self, future)

        return future.result()
```

## اقدامات: طویل مدتی کام
عملات پب-سب (فیڈبیک) + درخواست-جواب (نتیجہ) کو ملا دیتی ہیں:
```python
from rclpy.action import ActionServer
from example_interfaces.action import Fibonacci

class FibonacciServer(Node):
    def __init__(self):
        super().__init__('fibonacci_server')
        self._action_server = ActionServer(
            self,
            Fibonacci,
            'fibonacci',
            self.execute_callback
        )

    def execute_callback(self, goal_handle):
        # Long-running task
        feedback_msg = Fibonacci.Feedback()
        sequence = [0, 1]

        for i in range(1, goal_handle.request.order):
            sequence.append(sequence[i] + sequence[i-1])
            feedback_msg.partial_sequence = sequence
            goal_handle.publish_feedback(feedback_msg)
            time.sleep(1)

        goal_handle.succeed()
        result = Fibonacci.Result()
        result.sequence = sequence
        return result
```

## ROS 2 کمانڈ لائن کے ٹولز
### خود نگریستی
```bash
# List all nodes
ros2 node list

# Node info (topics, services, actions)
ros2 node info /camera_node

# List topics
ros2 topic list

# Echo topic messages
ros2 topic echo /imu/data

# Topic info (type, publishers, subscribers)
ros2 topic info /imu/data

# Publish to topic
ros2 topic pub /cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 1.0}, angular: {z: 0.5}}"
```

### خدمات اور اقدامات
```bash
# List services
ros2 service list

# Call service
ros2 service call /camera/set_camera_info sensor_msgs/srv/SetCameraInfo "{}"

# List actions
ros2 action list

# Send goal
ros2 action send_goal /fibonacci example_interfaces/action/Fibonacci "{order: 5}"
```

## پیرامیٹرز: رن ٹائم کنفیگریشن
نوڈز قابل ترتیب پیرامیٹرز کو ظاہر کر سکتے ہیں:
```python
class ConfigurableNode(Node):
    def __init__(self):
        super().__init__('configurable_node')

        # Declare parameters with defaults
        self.declare_parameter('update_rate', 10.0)
        self.declare_parameter('robot_name', 'my_robot')

        # Get parameter values
        rate = self.get_parameter('update_rate').value
        name = self.get_parameter('robot_name').value

        self.get_logger().info(f'Robot: {name}, Rate: {rate} Hz')
```

چلانے کے وقت پیرامیٹرز سیٹ کریں:
```bash
# Set parameter
ros2 param set /configurable_node update_rate 20.0

# Get parameter
ros2 param get /configurable_node robot_name

# List all parameters
ros2 param list
```

## عملی کام: ایک ہیومینائڈ جوائنٹ کنٹرولر بنائیں
آئیں ایک سادہ جوائنٹ پوزیشن کنٹرولر بنائیں:
```python
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import Float64MultiArray

class JointController(Node):
    def __init__(self):
        super().__init__('joint_controller')

        # Subscribe to joint states (position feedback)
        self.joint_sub = self.create_subscription(
            JointState,
            '/joint_states',
            self.joint_callback,
            10
        )

        # Publish joint commands
        self.cmd_pub = self.create_publisher(
            Float64MultiArray,
            '/joint_commands',
            10
        )

        # Control loop at 100 Hz
        self.timer = self.create_timer(0.01, self.control_loop)

        self.current_positions = []
        self.target_positions = [0.0] * 28  # 28 DOF humanoid

    def joint_callback(self, msg):
        self.current_positions = msg.position

    def control_loop(self):
        if not self.current_positions:
            return

        # Simple P controller
        cmd = Float64MultiArray()
        kp = 10.0  # Proportional gain

        cmd.data = [
            kp * (target - current)
            for target, current in zip(self.target_positions, self.current_positions)
        ]

        self.cmd_pub.publish(cmd)
```

## بہترین طریقے
### 1. نوڈ ڈیزائن
- **اکیلی ذمہ داری**: ایک نوڈ = ایک فنکشن
- **دوبارہ استعمال کے قابل**: عمومی پیرامیٹرز، ہارڈ کوڈڈ قیمتیں نہیں
- **مضبوط**: غائب پیغامات کا خیال رکھیں، پیغام کی عمر چیک کریں
### 2. موضوع کا نام
- `/namespace/topic_name` کے اصول کا استعمال کریں
- چھوٹے حروف اور انڈر سکور کے ساتھ: `/camera/image_raw`
- غیر واضح ناموں سے پرہیز کریں: `/data` (برا) بمقابلہ `/imu/linear_accel` (اچھا)
### 3. پیغام کی اقسام
- جب ممکن ہو، معیاری پیغامات کا استعمال کریں (`sensor_msgs`, `geometry_msgs`)
- حسب ضرورت ہی حسب ضرورت پیغامات کا استعمال کریں
- حسب ضرورت پیغام کے میدانوں کو واضح طور پر دستاویز کریں
### 4. غلطی کا انتظام
```python
def callback(self, msg):
    try:
        # Process message
        self.process(msg)
    except Exception as e:
        self.get_logger().error(f'Processing failed: {e}')
```

## خلاصہ
اس ہفتے آپ نے سیکھا:
✅ **نوڈز** واحد مقصد کے عمل ہیں جو ROS 2 کے ذریعے بات چیت کرتے ہیں
✅ **موضوعات** غیر ہم وقتی شائع-سبسکرائب مواصلت کو فعال کرتے ہیں
✅ **سروسز** ہم وقتی درخواست-جواب تعامل فراہم کرتی ہیں
✅ **عمل** طویل مدتی کاموں کی حمایت کرتے ہیں جن میں فیڈبیک شامل ہوتا ہے
✅ **پیرامیٹرز** رن ٹائم کی تشکیل کی اجازت دیتے ہیں
✅ **QoS** پیغام کی ترسیل کی ضمانتوں کو کنٹرول کرتا ہے
✅ **CLI ٹولز** ڈیبگنگ اور جانچ کے لیے
## آگے کیا ہے؟
**ہفتہ 3: Python کے ساتھ ROS 2 پیکیجز بنانا** - colcon کے ساتھ مکمل ROS 2 ایپلیکیشنز کی ساخت، تعمیر، اور آغاز کرنا سیکھیں۔
**اگلا**: [ہفتہ 3: Python کے ساتھ تعمیر کرنا →](./week3-python.md)