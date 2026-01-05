[TRANSLATION_FAILED] # Week 9: Nav2 for Bipedal Navigation

[TRANSLATION_FAILED] ## Introduction

[TRANSLATION_FAILED] **Nav2** (Navigation2) is ROS 2's autonomous navigation framework. This week, you'll integrate SLAM with Nav2 to enable your humanoid to navigate autonomously - planning paths, avoiding obstacles, and recovering from failures.

[TRANSLATION_FAILED] ## Nav2 Architecture

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

[TRANSLATION_FAILED] **Components**:
[TRANSLATION_FAILED] - **Planner Server**: Global path (A*, Theta*, SmacPlanner)
[TRANSLATION_FAILED] - **Controller Server**: Local trajectory (DWB, TEB, MPPI)
[TRANSLATION_FAILED] - **Costmap 2D**: Obstacle representation
[TRANSLATION_FAILED] - **Behavior Server**: Recovery behaviors
[TRANSLATION_FAILED] - **BT Navigator**: Behavior tree coordination

[TRANSLATION_FAILED] ## Installation

```bash
# Install Nav2
sudo apt install ros-humble-navigation2 ros-humble-nav2-bringup

# Test
ros2 pkg list | grep nav2
```

[TRANSLATION_FAILED] ## Costmaps Configuration

[TRANSLATION_FAILED] Create `config/nav2_params.yaml`:

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
    robot_radius: 0.3  # Humanoid footprint

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

[TRANSLATION_FAILED] ## Planner Configuration

[TRANSLATION_FAILED] ### NavFn Planner (A*)

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

[TRANSLATION_FAILED] ### Smac Planner (Hybrid A*)

[TRANSLATION_FAILED] Better for non-holonomic robots:

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
      minimum_turning_radius: 0.4  # Humanoid turning radius
      reverse_penalty: 2.0
      change_penalty: 0.05
      non_straight_penalty: 1.05
      cost_penalty: 2.0
```

[TRANSLATION_FAILED] ## Controller Configuration

[TRANSLATION_FAILED] ### DWB Controller

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
      max_vel_x: 0.5  # Humanoid max walk speed
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

[TRANSLATION_FAILED] ## Behavior Server

[TRANSLATION_FAILED] Recovery behaviors for failures:

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

[TRANSLATION_FAILED] ## Launch Nav2

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
        # Map server (if using pre-built map)
        Node(
            package='nav2_map_server',
            executable='map_server',
            parameters=[{'yaml_filename': '/path/to/map.yaml'}]
        ),

        # Lifecycle manager for map server
        Node(
            package='nav2_lifecycle_manager',
            executable='lifecycle_manager',
            parameters=[{
                'autostart': True,
                'node_names': ['map_server']
            }]
        ),

        # AMCL localization (if not using cuVSLAM)
        # Node(...),

        # Nav2 bringup
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

[TRANSLATION_FAILED] Run:

```bash
ros2 launch humanoid_navigation nav2.launch.py
```

[TRANSLATION_FAILED] ## Sending Navigation Goals

[TRANSLATION_FAILED] ### Command Line

```bash
# Send goal via RViz: 2D Goal Pose button

# Or via command line:
ros2 topic pub --once /goal_pose geometry_msgs/PoseStamped \
  "{header: {frame_id: 'map'}, \
    pose: {position: {x: 2.0, y: 1.0, z: 0.0}, \
           orientation: {x: 0.0, y: 0.0, z: 0.0, w: 1.0}}}"
```

[TRANSLATION_FAILED] ### Python API

```python
from geometry_msgs.msg import PoseStamped
from nav2_simple_commander.robot_navigator import BasicNavigator
import rclpy

def main():
    rclpy.init()
    navigator = BasicNavigator()

    # Wait for Nav2 to activate
    navigator.waitUntilNav2Active()

    # Create goal pose
    goal_pose = PoseStamped()
    goal_pose.header.frame_id = 'map'
    goal_pose.header.stamp = navigator.get_clock().now().to_msg()
    goal_pose.pose.position.x = 2.0
    goal_pose.pose.position.y = 1.0
    goal_pose.pose.orientation.w = 1.0

    # Navigate to goal
    navigator.goToPose(goal_pose)

    # Wait for completion
    while not navigator.isTaskComplete():
        feedback = navigator.getFeedback()
        print(f"Distance remaining: {feedback.distance_remaining:.2f} m")
        rclpy.spin_once(navigator, timeout_sec=0.1)

    result = navigator.getResult()
    if result == TaskResult.SUCCEEDED:
        print('Goal reached!')
    elif result == TaskResult.CANCELED:
        print('Goal canceled')
    elif result == TaskResult.FAILED:
        print('Goal failed')

    navigator.lifecycleShutdown()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

[TRANSLATION_FAILED] ### Action Client

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

        # Convert theta to quaternion
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
            f'Distance: {feedback.distance_remaining:.2f} m, '
            f'ETA: {feedback.estimated_time_remaining.sec} s'
        )

    def goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().warn('Goal rejected')
            return

        get_result_future = goal_handle.get_result_async()
        get_result_future.add_done_callback(self.result_callback)

    def result_callback(self, future):
        result = future.result().result
        self.get_logger().info(f'Result: {result}')
```

[TRANSLATION_FAILED] ## Waypoint Following

[TRANSLATION_FAILED] Navigate through multiple points:

```python
from nav2_simple_commander.robot_navigator import BasicNavigator

navigator = BasicNavigator()
navigator.waitUntilNav2Active()

# Define waypoints
waypoints = [
    create_pose(1.0, 1.0),
    create_pose(2.0, 0.5),
    create_pose(3.0, 1.5),
    create_pose(2.0, 2.0),
]

navigator.followWaypoints(waypoints)

while not navigator.isTaskComplete():
    feedback = navigator.getFeedback()
    print(f'Waypoint {feedback.current_waypoint + 1}/{len(waypoints)}')

navigator.lifecycleShutdown()

def create_pose(x, y, theta=0.0):
    pose = PoseStamped()
    pose.header.frame_id = 'map'
    pose.pose.position.x = x
    pose.pose.position.y = y
    pose.pose.orientation.w = 1.0
    return pose
```

[TRANSLATION_FAILED] ## Obstacle Avoidance

[TRANSLATION_FAILED] ### Dynamic Obstacles

[TRANSLATION_FAILED] Nav2 automatically avoids obstacles detected by sensors.

[TRANSLATION_FAILED] ### Keepout Zones

[TRANSLATION_FAILED] Define no-go areas:

```yaml
# keepout_filter.yaml
filters:
  - name: "keepout_filter"
    type: "nav2_costmap_2d::KeepoutFilter"
    params:
      enabled: true
      filter_info_topic: "/costmap_filter_info"

# Define keepout zones in map
```

[TRANSLATION_FAILED] ## Complete Humanoid Navigation Example

```python
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription

def generate_launch_description():
    return LaunchDescription([
        # Isaac Sim with cuVSLAM
        # (run separately)

        # Nav2
        IncludeLaunchDescription(
            '/opt/ros/humble/share/nav2_bringup/launch/navigation_launch.py',
            launch_arguments={
                'params_file': '/path/to/nav2_params.yaml',
                'use_sim_time': 'true'
            }.items()
        ),

        # RViz with Nav2 plugins
        Node(
            package='rviz2',
            executable='rviz2',
            arguments=['-d', '/path/to/nav2.rviz']
        ),
    ])
```

[TRANSLATION_FAILED] ## Tuning Tips

[TRANSLATION_FAILED] ### Speed up planning:
[TRANSLATION_FAILED] - Reduce `expected_planner_frequency`
[TRANSLATION_FAILED] - Lower costmap `update_frequency`

[TRANSLATION_FAILED] ### Better accuracy:
[TRANSLATION_FAILED] - Increase `sim_time` in DWB
[TRANSLATION_FAILED] - More `vx_samples` and `vtheta_samples`

[TRANSLATION_FAILED] ### Humanoid-specific:
[TRANSLATION_FAILED] - Small `robot_radius` for narrow passages
[TRANSLATION_FAILED] - Low `max_vel_x` (0.3-0.5 m/s)
[TRANSLATION_FAILED] - High `decel_lim_x` for quick stops
[TRANSLATION_FAILED] - Enable `RotateToGoal` critic

[TRANSLATION_FAILED] ## Summary

[TRANSLATION_FAILED] This week you learned:

[TRANSLATION_FAILED] - Nav2 architecture and components
[TRANSLATION_FAILED] - Costmap configuration for humanoids
[TRANSLATION_FAILED] - Path planning with A* and Smac
[TRANSLATION_FAILED] - DWB controller for trajectory tracking
[TRANSLATION_FAILED] - Recovery behaviors
[TRANSLATION_FAILED] - Sending navigation goals via API
[TRANSLATION_FAILED] - Waypoint following
[TRANSLATION_FAILED] - Complete SLAM + Nav2 integration

[TRANSLATION_FAILED] ## What's Next?

[TRANSLATION_FAILED] **Week 10: Vision-Language-Action Models** - Integrate VLMs like CLIP for object-aware navigation and manipulation.

[TRANSLATION_FAILED] **Next**: [Week 10: VLA Introduction →](../module-4-vla/week10-vla-intro.md)
