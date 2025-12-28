# ہفتہ 2: ROS 2 Architecture - Nodes، Topics، Services

## تعارف

اس ہفتے، ہم ROS 2 کے بنیادی communication patterns کو دریافت کریں گے اور اپنے پہلے robot nodes بنائیں گے۔

## ROS 2 Computation Graph

ROS 2 applications **computation graph** کے طور پر منظم ہیں:

- **Nodes**: عمل کی اکائیاں (processes)
- **Topics**: Publish-subscribe communication
- **Services**: Request-response communication
- **Actions**: طویل مدتی کام

### Nodes کیا ہیں؟

**Node** ایک عمل ہے جو ایک مخصوص کام انجام دیتا ہے۔ مثال کے طور پر:
- Camera node تصاویر publish کرتا ہے
- Motion planner node راستے کا حساب لگاتا ہے
- Motor controller node پہیوں کو کنٹرول کرتا ہے

## Topics: Publish-Subscribe Pattern

**Topics** ایک طرفہ data streams ہیں جہاں:
- **Publishers** data بھیجتے ہیں
- **Subscribers** data وصول کرتے ہیں
- کئی publishers اور subscribers ایک topic سے منسلک ہو سکتے ہیں

### اپنا پہلا Publisher لکھیں

```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class MinimalPublisher(Node):
    def __init__(self):
        super().__init__('minimal_publisher')
        self.publisher_ = self.create_publisher(String, 'topic', 10)
        self.timer = self.create_timer(0.5, self.timer_callback)
        self.i = 0

    def timer_callback(self):
        msg = String()
        msg.data = f'Hello World: {self.i}'
        self.publisher_.publish(msg)
        self.get_logger().info(f'Publishing: "{msg.data}"')
        self.i += 1

def main(args=None):
    rclpy.init(args=args)
    minimal_publisher = MinimalPublisher()
    rclpy.spin(minimal_publisher)
    minimal_publisher.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

### اپنا پہلا Subscriber لکھیں

```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class MinimalSubscriber(Node):
    def __init__(self):
        super().__init__('minimal_subscriber')
        self.subscription = self.create_subscription(
            String,
            'topic',
            self.listener_callback,
            10)

    def listener_callback(self, msg):
        self.get_logger().info(f'I heard: "{msg.data}"')

def main(args=None):
    rclpy.init(args=args)
    minimal_subscriber = MinimalSubscriber()
    rclpy.spin(minimal_subscriber)
    minimal_subscriber.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Services: Request-Response Pattern

**Services** دو طرفہ communication فراہم کرتے ہیں:
- **Client** request بھیجتا ہے
- **Server** جواب دیتا ہے
- مثال: "روبوٹ کو یہاں لے جاؤ" (request) → "ٹھیک ہے، میں وہاں پہنچ گیا" (response)

### Service Server بنائیں

```python
from example_interfaces.srv import AddTwoInts
import rclpy
from rclpy.node import Node

class MinimalService(Node):
    def __init__(self):
        super().__init__('minimal_service')
        self.srv = self.create_service(
            AddTwoInts,
            'add_two_ints',
            self.add_two_ints_callback
        )

    def add_two_ints_callback(self, request, response):
        response.sum = request.a + request.b
        self.get_logger().info(
            f'Incoming request: a={request.a} b={request.b}'
        )
        return response

def main(args=None):
    rclpy.init(args=args)
    minimal_service = MinimalService()
    rclpy.spin(minimal_service)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

### Service Client بنائیں

```python
import sys
from example_interfaces.srv import AddTwoInts
import rclpy
from rclpy.node import Node

class MinimalClientAsync(Node):
    def __init__(self):
        super().__init__('minimal_client_async')
        self.cli = self.create_client(AddTwoInts, 'add_two_ints')
        while not self.cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('service not available, waiting...')
        self.req = AddTwoInts.Request()

    def send_request(self, a, b):
        self.req.a = a
        self.req.b = b
        self.future = self.cli.call_async(self.req)
        rclpy.spin_until_future_complete(self, self.future)
        return self.future.result()

def main(args=None):
    rclpy.init(args=args)
    minimal_client = MinimalClientAsync()
    response = minimal_client.send_request(int(sys.argv[1]), int(sys.argv[2]))
    minimal_client.get_logger().info(
        f'Result: {int(sys.argv[1])} + {int(sys.argv[2])} = {response.sum}'
    )
    minimal_client.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## ROS 2 Commands

### Nodes دیکھیں

```bash
# تمام چل رہے nodes کی فہرست
ros2 node list

# Node کی معلومات
ros2 node info /node_name
```

### Topics دیکھیں

```bash
# تمام topics کی فہرست
ros2 topic list

# Topic پر data دیکھیں
ros2 topic echo /topic_name

# Topic کی معلومات
ros2 topic info /topic_name

# Topic کی شرح دیکھیں
ros2 topic hz /topic_name
```

### Services دیکھیں

```bash
# تمام services کی فہرست
ros2 service list

# Service کو کال کریں
ros2 service call /service_name example_interfaces/srv/AddTwoInts "{a: 1, b: 2}"
```

## عملی مشق: Talker/Listener

### پیکیج بنائیں

```bash
cd ~/ros2_ws/src
ros2 pkg create --build-type ament_python py_pubsub
```

### Publisher کوڈ شامل کریں

فائل: `py_pubsub/py_pubsub/publisher_member_function.py`

(اوپر دیا گیا MinimalPublisher کوڈ استعمال کریں)

### Subscriber کوڈ شامل کریں

فائل: `py_pubsub/py_pubsub/subscriber_member_function.py`

(اوپر دیا گیا MinimalSubscriber کوڈ استعمال کریں)

### setup.py میں entry points شامل کریں

```python
entry_points={
    'console_scripts': [
        'talker = py_pubsub.publisher_member_function:main',
        'listener = py_pubsub.subscriber_member_function:main',
    ],
},
```

### Build اور Run کریں

```bash
cd ~/ros2_ws
colcon build --packages-select py_pubsub

# پہلے terminal میں
source ~/ros2_ws/install/setup.bash
ros2 run py_pubsub talker

# دوسرے terminal میں
source ~/ros2_ws/install/setup.bash
ros2 run py_pubsub listener
```

## خلاصہ

اس ہفتے آپ نے سیکھا:

- ROS 2 computation graph
- Nodes، topics، services
- Publisher/subscriber pattern
- Service client/server pattern
- ROS 2 command line tools
- اپنا پہلا ROS 2 پیکیج بنانا

## اگلا کیا ہے؟

**ہفتہ 3: Python میں Robot Control** - Motor control، sensor integration، اور custom messages سیکھیں۔

**اگلا**: [ہفتہ 3: Python →](./week3-python.md)
