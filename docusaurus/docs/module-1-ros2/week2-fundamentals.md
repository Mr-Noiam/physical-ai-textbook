# Week 2: ROS 2 Architecture - Nodes, Topics, Services

## Introduction

This week, we'll explore ROS 2's core communication patterns and build our first robot nodes. You'll learn how distributed robot systems communicate using the publish-subscribe and request-response paradigms.

## ROS 2 Computation Graph

ROS 2 applications are organized as a **computation graph** of nodes:

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│Camera Node  │  topic  │ Vision Node  │  topic  │ Planner Node│
│  (Publisher)│────────>│(Sub + Pub)   │────────>│(Subscriber) │
└─────────────┘         └──────────────┘         └─────────────┘
       │                                                  │
       │                                                  │
       └──────────service: /get_camera_info─────────────┘
```

### Key Concepts

**Node**: A process that performs computation (camera driver, planner, controller)
**Topic**: Named channel for asynchronous streaming data (sensor data, commands)
**Service**: Synchronous request-response interaction (get parameter, trigger action)
**Action**: Long-running task with feedback (navigate to goal, pick object)

## Nodes: The Building Blocks

### What is a Node?

A **node** is a single-purpose executable that communicates with other nodes:

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

**Node Lifecycle**:
1. `rclpy.init()` - Initialize ROS 2 context
2. Create node instance
3. `rclpy.spin()` - Process callbacks (subscriptions, timers, services)
4. `rclpy.shutdown()` - Clean shutdown

### Node Discovery

ROS 2 uses **DDS (Data Distribution Service)** for automatic node discovery:
- Nodes advertise their topics/services on startup
- Other nodes discover them automatically (no master process needed!)
- Multi-machine support out-of-the-box

## Topics: Pub-Sub Communication

### Publisher Example

Publishing IMU data at 100 Hz:

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

### Subscriber Example

Processing IMU data:

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

### Quality of Service (QoS)

ROS 2 allows fine-grained control over message delivery:

```python
from rclpy.qos import QoSProfile, QoSReliabilityPolicy, QoSHistoryPolicy

qos_profile = QoSProfile(
    reliability=QoSReliabilityPolicy.BEST_EFFORT,  # vs RELIABLE
    history=QoSHistoryPolicy.KEEP_LAST,
    depth=10
)

self.publisher_ = self.create_publisher(Imu, '/imu/data', qos_profile)
```

**Reliability**:
- `BEST_EFFORT`: Fast, may drop messages (sensor data)
- `RELIABLE`: Guarantees delivery (commands)

## Services: Request-Response

### Service Server

Provide camera calibration info:

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

### Service Client

Request calibration:

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

## Actions: Long-Running Tasks

Actions combine pub-sub (feedback) + request-response (result):

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

## ROS 2 Command-Line Tools

### Introspection

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

### Services & Actions

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

## Parameters: Runtime Configuration

Nodes can expose configurable parameters:

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

Set parameters at runtime:

```bash
# Set parameter
ros2 param set /configurable_node update_rate 20.0

# Get parameter
ros2 param get /configurable_node robot_name

# List all parameters
ros2 param list
```

## Hands-On: Build a Humanoid Joint Controller

Let's build a simple joint position controller:

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

## Best Practices

### 1. Node Design
- **Single responsibility**: One node = one function
- **Reusable**: Generic parameters, not hardcoded values
- **Robust**: Handle missing messages, check message age

### 2. Topic Naming
- Use `/namespace/topic_name` convention
- Lowercase with underscores: `/camera/image_raw`
- Avoid ambiguous names: `/data` (bad) vs `/imu/linear_accel` (good)

### 3. Message Types
- Use standard messages when possible (`sensor_msgs`, `geometry_msgs`)
- Custom messages only when necessary
- Document custom message fields clearly

### 4. Error Handling
```python
def callback(self, msg):
    try:
        # Process message
        self.process(msg)
    except Exception as e:
        self.get_logger().error(f'Processing failed: {e}')
```

## Summary

This week you learned:

✅ **Nodes** are single-purpose processes that communicate via ROS 2
✅ **Topics** enable asynchronous publish-subscribe communication
✅ **Services** provide synchronous request-response interaction
✅ **Actions** support long-running tasks with feedback
✅ **Parameters** allow runtime configuration
✅ **QoS** controls message delivery guarantees
✅ **CLI tools** for debugging and introspection

## What's Next?

**Week 3: Building ROS 2 Packages with Python** - Learn to structure, build, and launch complete ROS 2 applications with colcon.

**Next**: [Week 3: Building with Python →](./week3-python.md)
