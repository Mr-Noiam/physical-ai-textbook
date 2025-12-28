# ہفتہ 9: دو پیروں کے نیویگیشن کے لیے Nav2

## تعارف

**Nav2** (Navigation2) ROS 2 کا خودکار نیویگیشن فریم ورک ہے۔ اس ہفتے، آپ SLAM کو Nav2 کے ساتھ مربوط کریں گے تاکہ آپ کا ہیومینائیڈ خودکار طور پر نیویگیٹ کر سکے - راستے کی منصوبہ بندی کرنا، رکاوٹوں سے بچنا، اور ناکامیوں سے بحال ہونا۔

## Nav2 فن تعمیر

```
┌─────────────┐
│   SLAM      │ (نقشہ + Localization)
└──────┬──────┘
       │
┌──────▼──────┐
│  Nav2 Stack │
├─────────────┤
│ - Planner   │ (عالمی راستہ)
│ - Controller│ (مقامی راستہ)
│ - Recoveries│ (ناکامی کی بحالی)
│ - BT        │ (رویہ کا درخت)
└──────┬──────┘
       │
┌──────▼──────┐
│   Robot     │ (حرکت کے احکامات)
└─────────────┘
```

## تنصیب

```bash
# Nav2 انسٹال کریں
sudo apt install ros-humble-navigation2 ros-humble-nav2-bringup

# TurtleBot3 ماڈل سیٹ کریں (بطور مثال)
echo "export TURTLEBOT3_MODEL=waffle_pi" >> ~/.bashrc
source ~/.bashrc
```

## Nav2 شروع کرنا

### بنیادی لانچ

```bash
# SLAM کے ساتھ Nav2
ros2 launch nav2_bringup navigation_launch.py \
  use_sim_time:=False

# Map سرور (پہلے سے بنے ہوئے نقشے کے ساتھ)
ros2 run nav2_map_server map_server \
  --ros-args -p yaml_filename:=my_map.yaml
```

### پروگرامی نیویگیشن

```python
from geometry_msgs.msg import PoseStamped
from nav2_simple_commander.robot_navigator import BasicNavigator
import rclpy

rclpy.init()

navigator = BasicNavigator()

# ابتدائی pose سیٹ کریں
initial_pose = PoseStamped()
initial_pose.header.frame_id = 'map'
initial_pose.header.stamp = navigator.get_clock().now().to_msg()
initial_pose.pose.position.x = 0.0
initial_pose.pose.position.y = 0.0
initial_pose.pose.orientation.w = 1.0

navigator.setInitialPose(initial_pose)
navigator.waitUntilNav2Active()

# ہدف pose
goal_pose = PoseStamped()
goal_pose.header.frame_id = 'map'
goal_pose.header.stamp = navigator.get_clock().now().to_msg()
goal_pose.pose.position.x = 2.0
goal_pose.pose.position.y = 1.0
goal_pose.pose.orientation.w = 1.0

# Navigate!
navigator.goToPose(goal_pose)

while not navigator.isTaskComplete():
    feedback = navigator.getFeedback()
    print(f"باقی فاصلہ: {feedback.distance_remaining:.2f}m")

print('مکمل!')
navigator.lifecycleShutdown()
```

## راستہ کی منصوبہ بندی

### عالمی منصوبہ ساز (Dijkstra/A*)

```yaml
planner_server:
  ros__parameters:
    expected_planner_frequency: 20.0
    planner_plugins: ["GridBased"]
    GridBased:
      plugin: "nav2_navfn_planner/NavfnPlanner"
      tolerance: 0.5
      use_astar: True
      allow_unknown: True
```

### مقامی منصوبہ ساز (DWB)

```yaml
controller_server:
  ros__parameters:
    controller_frequency: 20.0
    FollowPath:
      plugin: "dwb_core::DWBLocalPlanner"
      min_vel_x: 0.0
      max_vel_x: 0.5
      max_vel_theta: 1.0
      min_speed_xy: 0.0
      max_speed_xy: 0.5
      acc_lim_x: 2.5
      acc_lim_theta: 3.2
      decel_lim_x: -2.5
      decel_lim_theta: -3.2
```

## رکاوٹوں سے بچاؤ

### Costmap ترتیب

```yaml
local_costmap:
  local_costmap:
    ros__parameters:
      global_frame: odom
      robot_base_frame: base_link
      update_frequency: 5.0
      publish_frequency: 2.0
      width: 3
      height: 3
      resolution: 0.05
      robot_radius: 0.22

      plugins: ["obstacle_layer", "inflation_layer"]

      obstacle_layer:
        plugin: "nav2_costmap_2d::ObstacleLayer"
        enabled: True
        observation_sources: scan
        scan:
          topic: /scan
          max_obstacle_height: 2.0
          clearing: True
          marking: True

      inflation_layer:
        plugin: "nav2_costmap_2d::InflationLayer"
        inflation_radius: 0.55
        cost_scaling_factor: 3.0
```

## بحالی کے طریقے

```yaml
recoveries_server:
  ros__parameters:
    recovery_plugins: ["spin", "backup", "wait"]

    spin:
      plugin: "nav2_recoveries/Spin"
      simulate_ahead_time: 2.0

    backup:
      plugin: "nav2_recoveries/BackUp"
      simulate_ahead_time: 2.0

    wait:
      plugin: "nav2_recoveries/Wait"
      simulate_ahead_time: 2.0
```

## Behavior Trees

```xml
<root main_tree_to_execute="MainTree">
  <BehaviorTree ID="MainTree">
    <RecoveryNode number_of_retries="6">
      <Sequence>
        <RateController hz="1.0">
          <ComputePathToPose goal="{goal}" path="{path}"/>
        </RateController>
        <FollowPath path="{path}"/>
      </Sequence>
      <ReactiveFallback>
        <Spin spin_dist="1.57"/>
        <Wait wait_duration="5"/>
        <BackUp backup_dist="0.3" backup_speed="0.05"/>
      </ReactiveFallback>
    </RecoveryNode>
  </BehaviorTree>
</root>
```

## کارکردگی کی اصلاح

### 1. Costmap ریزولوشن

```yaml
resolution: 0.05  # 5cm per cell (توازن)
```

### 2. اپ ڈیٹ کی تعدد

```yaml
update_frequency: 5.0  # پروسیسنگ کو کم کرنے کے لیے کم کریں
```

### 3. منصوبہ ساز کی تعدد

```yaml
expected_planner_frequency: 1.0  # مستحکم راستوں کے لیے کم کریں
```

## خلاصہ

اس ہفتے آپ نے سیکھا:

- Nav2 فن تعمیر اور اجزاء
- SLAM کے ساتھ نیویگیشن انضمام
- عالمی اور مقامی راستہ کی منصوبہ بندی
- رکاوٹوں سے بچاؤ (Costmaps)
- بحالی کے طریقے
- Behavior Trees
- کارکردگی کی اصلاح

## اگلا کیا ہے؟

**ماڈیول 4: VLA اور Humanoid AI** - Vision-Language-Action ماڈلز کے ساتھ اگلی نسل کے ہیومینائیڈز بنائیں!

**اگلا**: [ماڈیول 4 شروع کریں →](../module-4-vla/week10-vla-intro.md)
