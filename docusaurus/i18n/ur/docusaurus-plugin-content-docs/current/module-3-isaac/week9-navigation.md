#ہفتہ 9: بائی پیڈل نیویگیشن کے لیے Nav2

## تعارف

**Nav2** (نیویگیشن 2) ROS 2 کا خود مختار نیویگیشن فریم ورک ہے۔ اس ہفتے، آپ SLAM کو Nav2 کے ساتھ مربوط کریں گے تاکہ آپ کا ہیومنائڈ خود مختار طور پر نیویگیٹ کر سکے - راستوں کی منصوبہ بندی، رکاوٹوں سے بچنا، اور ناکامیوں سے بحالی۔

## Nav2 فن تعمیر

```
┌─────────┐    ┌──────────┐    ┌─────────────┐
│  SLAM   │───>│ Costmaps │───>│Path Planner │
│ (cuVSLAM)│    │(obstacles)│    │  (A*, DWB)  │
└─────────┘    └──────────┘    └─────────────┘
                                       │
                                       ▼
                               ┌───────────────┐
                               │  Controller   │
                               │ (DWB, TEB)    │
                               └───────────────┘
                                       │
                                       ▼
                               ┌───────────────┐
                               │cmd_vel (Twist)│
                               └───────────────┘
```

**اجزاء**:
- **پلانر سرور**: عالمی راستہ (A*, Theta*, SmacPlanner)
- **کنٹرولر سرور**: مقامی ٹریجکٹری (DWB, TEB, MPPI)
- **کاسٹ میپ 2D**: رکاوٹوں کی نمائندگی
- **بی ہیویئر سرور**: بحالی کے رویے
- **بی ٹی نیویگیٹر**: بی ہیویئر ٹری کوآرڈینیشن

## انسٹالیشن

```bash
# Nav2 انسٹال کریں
sudo apt install ros-humble-navigation2 ros-humble-nav2-bringup

# ٹیسٹ
ros2 pkg list | grep nav2
```

## کاسٹ میپس کنفیگریشن

`config/nav2_params.yaml` بنائیں:

```yaml
costmap_2d:
  ros__parameters:
    update_frequency: 5.0
    publish_frequency: 2.0
    global_frame: map
    robot_base_frame: base_link
    rolling_window: false
    width: 20
    height: 20
    resolution: 0.05
    robot_radius: 0.3  # ہیومنائڈ فٹ پرنٹ

    plugins: ["static_layer", "obstacle_layer", "inflation_layer"]

    static_layer:
      plugin: "nav2_costmap_2d::StaticLayer"
      map_subscribe_transient_local: true

    obstacle_layer:
      plugin: "nav2_costmap_2d::ObstacleLayer"
      enabled: true
      observation_sources: scan
      scan:
        topic: /scan
        max_obstacle_height: 2.0
        clearing: true
        marking: true
        data_type: "LaserScan"

    inflation_layer:
      plugin: "nav2_costmap_2d::InflationLayer"
      cost_scaling_factor: 3.0
      inflation_radius: 0.55
```

## پلانر کنفیگریشن

### NavFn پلانر (A*)

```yaml
planner_server:
  ros__parameters:
    expected_planner_frequency: 20.0
    planner_plugins: ["GridBased"]

    GridBased:
      plugin: "nav2_navfn_planner/NavfnPlanner"
      tolerance: 0.5
      use_astar: true
      allow_unknown: true
```

### Smac پلانر (ہائبرڈ A*)

غیر ہولونومک روبوٹس کے لیے بہتر:

```yaml
    SmacHybrid:
      plugin: "nav2_smac_planner/SmacPlannerHybrid"
      tolerance: 0.5
      downsample_costmap: false
      downsampling_factor: 1
      allow_unknown: true
      max_iterations: 1000000
      max_planning_time: 5.0
      motion_model_for_search: "REEDS_SHEPP"  # Dubin, Reeds-Shepp
      angle_quantization_bins: 72
      analytic_expansion_ratio: 3.5
      analytic_expansion_max_length: 3.0
      minimum_turning_radius: 0.4  # ہیومنائڈ ٹرننگ ریڈیس
      reverse_penalty: 2.0
      change_penalty: 0.05
      non_straight_penalty: 1.05
      cost_penalty: 2.0
```

## کنٹرولر کنفیگریشن

### DWB کنٹرولر

```yaml
controller_server:
  ros__parameters:
    controller_frequency: 20.0
    min_x_velocity_threshold: 0.001
    min_y_velocity_threshold: 0.001
    min_theta_velocity_threshold: 0.001
    failure_tolerance: 0.3
    progress_checker_plugin: "progress_checker"
    goal_checker_plugins: ["general_goal_checker"]
    controller_plugins: ["FollowPath"]

    progress_checker:
      plugin: "nav2_controller::SimpleProgressChecker"
      required_movement_radius: 0.5
      movement_time_allowance: 10.0

    general_goal_checker:
      plugin: "nav2_controller::SimpleGoalChecker"
      xy_goal_tolerance: 0.25
      yaw_goal_tolerance: 0.25
      stateful: true

    FollowPath:
      plugin: "dwb_core::DWBLocalPlanner"
      debug_trajectory_details: true
      min_vel_x: 0.0
      min_vel_y: 0.0
      max_vel_x: 0.5  # ہیومنائڈ کی زیادہ سے زیادہ چلنے کی رفتار
      max_vel_y: 0.0
      max_vel_theta: 1.0
      min_speed_xy: 0.0
      max_speed_xy: 0.5
      min_speed_theta: 0.0
      acc_lim_x: 0.3
      acc_lim_y: 0.0
      acc_lim_theta: 1.0
      decel_lim_x: -0.3
      decel_lim_y: 0.0
      decel_lim_theta: -1.0
      vx_samples: 20
      vy_samples: 0
      vtheta_samples: 40
      sim_time: 1.7
      linear_granularity: 0.05
      angular_granularity: 0.025
      transform_tolerance: 0.2
      xy_goal_tolerance: 0.25
      trans_stopped_velocity: 0.25
      short_circuit_trajectory_evaluation: true
      stateful: true
      critics: ["RotateToGoal", "Oscillation", "BaseObstacle", "GoalAlign", "PathAlign", "PathDist", "GoalDist"]

      BaseObstacle.scale: 0.02
      PathAlign.scale: 32.0
      PathAlign.forward_point_distance: 0.1
      GoalAlign.scale: 24.0
      GoalAlign.forward_point_distance: 0.1
      PathDist.scale: 32.0
      GoalDist.scale: 24.0
      RotateToGoal.scale: 32.0
      RotateToGoal.slowing_factor: 5.0
      RotateToGoal.lookahead_time: -1.0
```

## بی ہیویئر سرور

ناکامیوں کے لیے بحالی کے رویے:

```yaml
behavior_server:
  ros__parameters:
    costmap_topic: local_costmap/costmap_raw
    footprint_topic: local_costmap/published_footprint
    cycle_frequency: 10.0
    behavior_plugins: ["spin", "backup", "wait"]

    spin:
      plugin: "nav2_behaviors::Spin"
    backup:
      plugin: "nav2_behaviors::BackUp"
    wait:
      plugin: "nav2_behaviors::Wait"

    global_frame: map
    robot_base_frame: base_link
    transform_tolerance: 0.1
    simulate_ahead_time: 2.0
    max_rotational_vel: 1.0
    min_rotational_vel: 0.4
    rotational_acc_lim: 3.2
```

## Nav2 لانچ کریں

```python
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    pkg_dir = get_package_share_directory('humanoid_navigation')
    nav2_params = os.path.join(pkg_dir, 'config', 'nav2_params.yaml')

    return LaunchDescription([
        # میپ سرور (اگر پہلے سے بنایا ہوا نقشہ استعمال کر رہے ہیں)
        Node(
            package='nav2_map_server',
            executable='map_server',
            parameters=[{'yaml_filename': '/path/to/map.yaml'}]
        ),

        # میپ سرور کے لیے لائف سائیکل مینیجر
        Node(
            package='nav2_lifecycle_manager',
            executable='lifecycle_manager',
            parameters=[{
                'autostart': True,
                'node_names': ['map_server']
            }]
        ),

        # AMCL لوکلائزیشن (اگر cuVSLAM استعمال نہیں کر رہے ہیں)
        # Node(...),

        # Nav2 برنگ اپ
        IncludeLaunchDescription(
            os.path.join(
                get_package_share_directory('nav2_bringup'),
                'launch', 'navigation_launch.py'
            ),
            launch_arguments={
                'params_file': nav2_params,
                'use_sim_time': 'true'
            }.items()
        ),
    ])
```

چلائیں:

```bash
ros2 launch humanoid_navigation nav2.launch.py
```

## نیویگیشن اہداف بھیجنا

### کمانڈ لائن

```bash
# RViz کے ذریعے ہدف بھیجیں: 2D گول پوز بٹن

# یا کمانڈ لائن کے ذریعے:
ros2 topic pub --once /goal_pose geometry_msgs/PoseStamped \
  "{header: {frame_id: 'map'}, \
    pose: {position: {x: 2.0, y: 1.0, z: 0.0}, \
           orientation: {x: 0.0, y: 0.0, z: 0.0, w: 1.0}}"}
```

### پائیتھن API

```python
from geometry_msgs.msg import PoseStamped
from nav2_simple_commander.robot_navigator import BasicNavigator
import rclpy

def main():
    rclpy.init()
    navigator = BasicNavigator()

    # Nav2 کے فعال ہونے کا انتظار کریں
    navigator.waitUntilNav2Active()

    # ہدف پوز بنائیں
    goal_pose = PoseStamped()
    goal_pose.header.frame_id = 'map'
    goal_pose.header.stamp = navigator.get_clock().now().to_msg()
    goal_pose.pose.position.x = 2.0
    goal_pose.pose.position.y = 1.0
    goal_pose.pose.orientation.w = 1.0

    # ہدف پر نیویگیٹ کریں
    navigator.goToPose(goal_pose)

    # تکمیل کا انتظار کریں
    while not navigator.isTaskComplete():
        feedback = navigator.getFeedback()
        print(f"باقی فاصلہ: {feedback.distance_remaining:.2f} m")
        rclpy.spin_once(navigator, timeout_sec=0.1)

    result = navigator.getResult()
    if result == TaskResult.SUCCEEDED:
        print('ہدف تک پہنچ گئے!')
    elif result == TaskResult.CANCELED:
        print('ہدف منسوخ کر دیا گیا')
    elif result == TaskResult.FAILED:
        print('ہدف ناکام ہو گیا')

    navigator.lifecycleShutdown()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

### ایکشن کلائنٹ

```python
from rclpy.action import ActionClient
from nav2_msgs.action import NavigateToPose
from geometry_msgs.msg import PoseStamped

class NavigationClient(Node):
    def __init__(self):
        super().__init__('navigation_client')
        self.action_client = ActionClient(self, NavigateToPose, 'navigate_to_pose')

    def send_goal(self, x, y, theta):
        goal_msg = NavigateToPose.Goal()
        goal_msg.pose.header.frame_id = 'map'
        goal_msg.pose.pose.position.x = x
        goal_msg.pose.pose.position.y = y

        # تھیٹا کو کواٹرنین میں تبدیل کریں
        import math
        goal_msg.pose.pose.orientation.z = math.sin(theta / 2)
        goal_msg.pose.pose.orientation.w = math.cos(theta / 2)

        self.action_client.wait_for_server()
        send_goal_future = self.action_client.send_goal_async(
            goal_msg,
            feedback_callback=self.feedback_callback
        )
        send_goal_future.add_done_callback(self.goal_response_callback)

    def feedback_callback(self, feedback_msg):
        feedback = feedback_msg.feedback
        self.get_logger().info(
            f'فاصلہ: {feedback.distance_remaining:.2f} m, ' 
            f'ETA: {feedback.estimated_time_remaining.sec} s'
        )

    def goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().warn('ہدف مسترد کر دیا گیا')
            return

        get_result_future = goal_handle.get_result_async()
        get_result_future.add_done_callback(self.result_callback)

    def result_callback(self, future):
        result = future.result().result
        self.get_logger().info(f'نتیجہ: {result}')
```

## وے پوائنٹ فالوونگ

متعدد پوائنٹس کے ذریعے نیویگیٹ کریں:

```python
from nav2_simple_commander.robot_navigator import BasicNavigator

navigator = BasicNavigator()
avigator.waitUntilNav2Active()

# وے پوائنٹس کی وضاحت کریں
waypoints = [
    create_pose(1.0, 1.0),
    create_pose(2.0, 0.5),
    create_pose(3.0, 1.5),
    create_pose(2.0, 2.0),
]

avigator.followWaypoints(waypoints)

while not navigator.isTaskComplete():
    feedback = navigator.getFeedback()
    print(f'وے پوائنٹ {feedback.current_waypoint + 1}/{len(waypoints)}')

avigator.lifecycleShutdown()

def create_pose(x, y, theta=0.0):
    pose = PoseStamped()
    pose.header.frame_id = 'map'
    pose.pose.position.x = x
    pose.pose.position.y = y
    pose.pose.orientation.w = 1.0
    return pose
```

## رکاوٹوں سے بچنا

### متحرک رکاوٹیں

Nav2 خود بخود سینسرز کے ذریعے پتہ لگائی گئی رکاوٹوں سے بچتا ہے۔

### کیپ آؤٹ زونز

نو-گو ایریاز کی وضاحت کریں:

```yaml
# keepout_filter.yaml
filters:
  - name: "keepout_filter"
    type: "nav2_costmap_2d::KeepoutFilter"
    params:
      enabled: true
      filter_info_topic: "/costmap_filter_info"

# نقشے میں کیپ آؤٹ زونز کی وضاحت کریں
```

## مکمل ہیومنائڈ نیویگیشن مثال

```python
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription

def generate_launch_description():
    return LaunchDescription([
        # cuVSLAM کے ساتھ آئزک سم
        # (الگ سے چلائیں)

        # Nav2
        IncludeLaunchDescription(
            '/opt/ros/humble/share/nav2_bringup/launch/navigation_launch.py',
            launch_arguments={
                'params_file': '/path/to/nav2_params.yaml',
                'use_sim_time': 'true'
            }.items()
        ),

        # Nav2 پلگ انز کے ساتھ RViz
        Node(
            package='rviz2',
            executable='rviz2',
            arguments=['-d', '/path/to/nav2.rviz']
        ),
    ])
```

## ٹیوننگ کی تجاویز

### منصوبہ بندی کو تیز کریں:
- `expected_planner_frequency` کو کم کریں
- کاسٹ میپ `update_frequency` کو کم کریں

### بہتر درستگی:
- DWB میں `sim_time` بڑھائیں
- زیادہ `vx_samples` اور `vtheta_samples`

### ہیومنائڈ کے لیے مخصوص:
- تنگ راستوں کے لیے چھوٹا `robot_radius`
- کم `max_vel_x` (0.3-0.5 m/s)
- فوری رکنے کے لیے زیادہ `decel_lim_x`
- `RotateToGoal` نقاد کو فعال کریں

## خلاصہ

اس ہفتے آپ نے سیکھا:

- Nav2 فن تعمیر اور اجزاء
- ہیومنائڈز کے لیے کاسٹ میپ کنفیگریشن
- A* اور Smac کے ساتھ پاتھ پلاننگ
- ٹریجکٹری ٹریکنگ کے لیے DWB کنٹرولر
- بحالی کے رویے
- API کے ذریعے نیویگیشن اہداف بھیجنا
- وے پوائنٹ فالوونگ
- مکمل SLAM + Nav2 انضمام

## آگے کیا ہے؟

**ہفتہ 10: وژن-لینگویج-ایکشن ماڈلز** - آبجیکٹ سے آگاہ نیویگیشن اور ہیرا پھیری کے لیے CLIP جیسے VLMs کو مربوط کریں۔

**آگے**: [ہفتہ 10: VLA تعارف →](../module-4-vla/week10-vla-intro.md)