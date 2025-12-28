# ہفتہ 3: Python میں Robot Programming

## تعارف

اس ہفتے، ہم ROS 2 کے ساتھ Python استعمال کرتے ہوئے روبوٹ کنٹرول، sensor integration، اور custom messages کو دریافت کریں گے۔

## Custom Messages بنانا

### Message فائل بنائیں

فائل: `tutorial_interfaces/msg/Num.msg`

```
int64 num
```

### CMakeLists.txt میں شامل کریں

```cmake
find_package(rosidl_default_generators REQUIRED)

rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/Num.msg"
)
```

### استعمال کریں

```python
from tutorial_interfaces.msg import Num

def timer_callback(self):
    msg = Num()
    msg.num = self.i
    self.publisher_.publish(msg)
```

## Custom Services بنانا

### Service فائل بنائیں

فائل: `tutorial_interfaces/srv/AddThreeInts.srv`

```
int64 a
int64 b
int64 c
---
int64 sum
```

### Service Server

```python
from tutorial_interfaces.srv import AddThreeInts

class AddThreeIntsServer(Node):
    def __init__(self):
        super().__init__('add_three_ints_server')
        self.srv = self.create_service(
            AddThreeInts,
            'add_three_ints',
            self.add_three_ints_callback
        )

    def add_three_ints_callback(self, request, response):
        response.sum = request.a + request.b + request.c
        return response
```

## Parameters استعمال کرنا

Parameters runtime میں node کی ترتیبات تبدیل کرنے کی اجازت دیتے ہیں۔

### Parameter declare کریں

```python
class ParameterNode(Node):
    def __init__(self):
        super().__init__('parameter_node')
        self.declare_parameter('my_parameter', 'default_value')
        my_param = self.get_parameter('my_parameter').value
```

### Parameters تبدیل کریں

```bash
ros2 run package_name node_name --ros-args -p my_parameter:=new_value
ros2 param set /node_name my_parameter new_value
ros2 param list
```

## Launch Files

Launch files کئی nodes کو ایک ساتھ شروع کرنے کی اجازت دیتی ہیں۔

```python
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(package='py_pubsub', executable='talker', name='talker'),
        Node(package='py_pubsub', executable='listener', name='listener'),
    ])
```

## TF2: Transform Library

TF2 coordinate frames کے درمیان تبدیلیوں کو ٹریک کرتا ہے۔

```python
from tf2_ros import TransformBroadcaster
from geometry_msgs.msg import TransformStamped

class FramePublisher(Node):
    def __init__(self):
        super().__init__('frame_publisher')
        self.br = TransformBroadcaster(self)
```

## خلاصہ

اس ہفتے آپ نے سیکھا:

- Custom messages اور services بنانا
- Parameters استعمال کرنا
- Launch files لکھنا
- TF2 transforms
- Colcon کے ساتھ building

## اگلا کیا ہے؟

**ہفتہ 4: URDF** - Robot descriptions سیکھیں۔

**اگلا**: [ہفتہ 4: URDF →](./week4-urdf.md)
