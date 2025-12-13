# Week 12: Humanoid Kinematics and Control

## Introduction

This week, you'll implement the core motion control for humanoids: **forward/inverse kinematics**, **whole-body control**, and **balance**. These techniques enable manipulation, walking, and stable interactions with the environment.

## Forward Kinematics (FK)

**Forward kinematics** computes end-effector position from joint angles.

### DH Parameters

Denavit-Hartenberg parameters define link transforms:

```python
import numpy as np

class DHParameter:
    def __init__(self, a, alpha, d, theta):
        self.a = a          # Link length
        self.alpha = alpha  # Link twist
        self.d = d          # Link offset
        self.theta = theta  # Joint angle

def dh_transform(dh):
    """Compute transformation matrix from DH parameters"""
    ct = np.cos(dh.theta)
    st = np.sin(dh.theta)
    ca = np.cos(dh.alpha)
    sa = np.sin(dh.alpha)

    return np.array([
        [ct, -st*ca,  st*sa, dh.a*ct],
        [st,  ct*ca, -ct*sa, dh.a*st],
        [0,      sa,     ca,    dh.d],
        [0,       0,      0,       1]
    ])
```

### 7-DOF Arm FK

```python
class HumanoidArmFK:
    def __init__(self):
        # DH parameters for 7-DOF arm
        # [a, alpha, d, theta]
        self.dh_params = [
            DHParameter(0, np.pi/2, 0.05, 0),   # Shoulder pitch
            DHParameter(0, -np.pi/2, 0, 0),     # Shoulder roll
            DHParameter(0, np.pi/2, 0.3, 0),    # Shoulder yaw
            DHParameter(0, -np.pi/2, 0, 0),     # Elbow
            DHParameter(0, np.pi/2, 0.25, 0),   # Wrist pitch
            DHParameter(0, -np.pi/2, 0, 0),     # Wrist roll
            DHParameter(0, 0, 0.1, 0),          # Wrist yaw
        ]

    def forward_kinematics(self, joint_angles):
        """Compute end-effector pose from joint angles"""
        T = np.eye(4)

        for i, angle in enumerate(joint_angles):
            self.dh_params[i].theta = angle
            T_i = dh_transform(self.dh_params[i])
            T = T @ T_i

        position = T[:3, 3]
        orientation = T[:3, :3]

        return position, orientation

# Usage
arm = HumanoidArmFK()
joints = [0.5, 0.2, -0.3, 1.5, 0.0, 0.1, 0.0]  # radians
position, rotation = arm.forward_kinematics(joints)
print(f"End-effector position: {position}")
```

## Inverse Kinematics (IK)

**Inverse kinematics** computes joint angles for desired end-effector pose.

### Numerical IK with Jacobian

```python
class HumanoidArmIK:
    def __init__(self):
        self.fk = HumanoidArmFK()
        self.num_joints = 7

    def jacobian(self, joint_angles, delta=0.0001):
        """Compute numerical Jacobian"""
        J = np.zeros((6, self.num_joints))

        # Current pose
        pos0, rot0 = self.fk.forward_kinematics(joint_angles)

        for i in range(self.num_joints):
            # Perturb joint i
            joints_perturbed = joint_angles.copy()
            joints_perturbed[i] += delta

            pos1, rot1 = self.fk.forward_kinematics(joints_perturbed)

            # Position derivative
            J[:3, i] = (pos1 - pos0) / delta

            # Orientation derivative (simplified)
            # In practice, use axis-angle or quaternion representation
            J[3:, i] = 0  # Placeholder

        return J

    def inverse_kinematics(self, target_pos, initial_guess=None, max_iter=100):
        """IK using Jacobian pseudoinverse"""
        if initial_guess is None:
            joint_angles = np.zeros(self.num_joints)
        else:
            joint_angles = initial_guess.copy()

        for iteration in range(max_iter):
            # Current position
            current_pos, _ = self.fk.forward_kinematics(joint_angles)

            # Error
            error = target_pos - current_pos
            error_norm = np.linalg.norm(error)

            if error_norm < 0.001:  # 1mm tolerance
                return joint_angles, True

            # Jacobian
            J = self.jacobian(joint_angles)
            J_pos = J[:3, :]  # Position part only

            # Pseudoinverse
            J_pinv = np.linalg.pinv(J_pos)

            # Update joints
            delta_q = J_pinv @ error
            joint_angles += 0.1 * delta_q  # Step size

            # Clip to joint limits
            joint_angles = np.clip(joint_angles, -np.pi, np.pi)

        return joint_angles, False  # Failed to converge

# Usage
ik = HumanoidArmIK()
target = np.array([0.4, 0.2, 0.3])  # Desired end-effector position
joints, success = ik.inverse_kinematics(target)

if success:
    print(f"IK solution: {joints}")
else:
    print("IK failed to converge")
```

### IKFast (Analytical IK)

For faster, exact solutions, use IKFast:

```bash
# Generate IKFast solver
pip install ikfast-pybind

# In Python
from ikfast_humanoid_arm import get_ik

solutions = get_ik(target_pose)
for sol in solutions:
    print(f"Solution: {sol}")
```

## Whole-Body Control

Control all joints simultaneously while respecting constraints.

### Quadratic Programming (QP)

```python
import cvxpy as cp

class WholeBodyController:
    def __init__(self, num_joints=28):
        self.num_joints = num_joints

    def solve(self, desired_accelerations, joint_limits, contact_forces):
        """Solve QP for joint torques"""
        # Decision variables
        tau = cp.Variable(self.num_joints)  # Joint torques
        f_contact = cp.Variable(4)  # Contact forces (2 feet)

        # Dynamics: M * ddq = tau + J^T * f
        # Simplified: minimize tracking error + regularization

        # Cost function
        cost = cp.sum_squares(tau - desired_accelerations * 10)
        cost += 0.01 * cp.sum_squares(tau)  # Regularization

        # Constraints
        constraints = [
            tau >= joint_limits[:, 0],  # Lower limits
            tau <= joint_limits[:, 1],  # Upper limits
            f_contact >= 0,  # Unilateral contacts
        ]

        # Solve
        problem = cp.Problem(cp.Minimize(cost), constraints)
        problem.solve()

        return tau.value

# Usage
wbc = WholeBodyController(num_joints=28)
joint_limits = np.array([[-100, 100]] * 28)  # Nm
desired_acc = np.zeros(28)
contact_forces = np.zeros(4)

torques = wbc.solve(desired_acc, joint_limits, contact_forces)
```

## Balance Control

Maintain stability using **Zero Moment Point (ZMP)**.

### ZMP Calculation

```python
class BalanceController:
    def __init__(self, mass=60.0, height=1.0):
        self.mass = mass
        self.g = 9.81
        self.height = height

    def compute_zmp(self, com_pos, com_acc):
        """Compute ZMP from CoM state"""
        # ZMP_x = CoM_x - (CoM_z / g) * CoM_ddx
        zmp_x = com_pos[0] - (com_pos[2] / self.g) * com_acc[0]
        zmp_y = com_pos[1] - (com_pos[2] / self.g) * com_acc[1]

        return np.array([zmp_x, zmp_y])

    def is_stable(self, zmp, support_polygon):
        """Check if ZMP is inside support polygon"""
        # Simple rectangular check
        x_min, x_max = support_polygon[0]
        y_min, y_max = support_polygon[1]

        return (x_min <= zmp[0] <= x_max) and (y_min <= zmp[1] <= y_max)

    def stabilize(self, current_com, desired_com, support_polygon):
        """Compute CoM acceleration to stabilize"""
        # PD controller for CoM
        kp = 100.0
        kd = 20.0

        com_error = desired_com - current_com[:3]
        com_vel = current_com[3:]

        com_acc = kp * com_error - kd * com_vel

        # Check ZMP
        zmp = self.compute_zmp(current_com[:3], com_acc)

        if not self.is_stable(zmp, support_polygon):
            # Reduce acceleration
            com_acc *= 0.5

        return com_acc

# Usage
balance = BalanceController(mass=60.0)
current_com = np.array([0.0, 0.0, 1.0, 0.0, 0.0, 0.0])  # [x, y, z, vx, vy, vz]
desired_com = np.array([0.1, 0.0, 1.0])
support = [(-0.1, 0.1), (-0.05, 0.05)]  # Foot polygon

com_acc = balance.stabilize(current_com, desired_com, support)
```

## Walking Gait Generation

### Simple Periodic Gait

```python
class GaitGenerator:
    def __init__(self, step_length=0.2, step_height=0.05, period=1.0):
        self.step_length = step_length
        self.step_height = step_height
        self.period = period

    def foot_trajectory(self, t, phase='swing'):
        """Generate foot trajectory"""
        if phase == 'swing':
            # Sinusoidal swing
            progress = (t % self.period) / self.period

            x = self.step_length * progress
            z = self.step_height * np.sin(np.pi * progress)
            y = 0.0

            return np.array([x, y, z])
        else:
            # Stance (stationary)
            return np.array([0.0, 0.0, 0.0])

    def generate_gait(self, t):
        """Generate full walking pattern"""
        # Alternate legs
        left_phase = 'swing' if (t // self.period) % 2 == 0 else 'stance'
        right_phase = 'stance' if left_phase == 'swing' else 'swing'

        left_foot = self.foot_trajectory(t, left_phase)
        right_foot = self.foot_trajectory(t, right_phase)

        return left_foot, right_foot

# Usage
gait = GaitGenerator(step_length=0.2, step_height=0.05, period=1.0)

for t in np.linspace(0, 4, 100):
    left, right = gait.generate_gait(t)
    print(f"t={t:.2f}: Left={left}, Right={right}")
```

## ROS 2 Integration

```python
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint

class HumanoidController(Node):
    def __init__(self):
        super().__init__('humanoid_controller')

        # Publishers
        self.traj_pub = self.create_publisher(
            JointTrajectory,
            '/joint_trajectory',
            10
        )

        # IK solver
        self.ik_solver = HumanoidArmIK()

        # Service for cartesian goals
        self.srv = self.create_service(
            MoveToCartesian,
            'move_to_cartesian',
            self.move_callback
        )

    def move_callback(self, request, response):
        # request.target_pose = [x, y, z]
        target = np.array([request.x, request.y, request.z])

        # Solve IK
        joints, success = self.ik_solver.inverse_kinematics(target)

        if success:
            # Send trajectory
            self.send_trajectory(joints)
            response.success = True
        else:
            response.success = False
            response.message = "IK failed"

        return response

    def send_trajectory(self, joint_positions):
        msg = JointTrajectory()
        msg.joint_names = [f'joint_{i}' for i in range(7)]

        point = JointTrajectoryPoint()
        point.positions = joint_positions.tolist()
        point.time_from_start.sec = 2

        msg.points = [point]
        self.traj_pub.publish(msg)
```

## Summary

This week you learned:

- Forward kinematics with DH parameters
- Inverse kinematics (numerical and analytical)
- Jacobian-based methods
- Whole-body control with QP
- Balance control and ZMP
- Walking gait generation
- ROS 2 motion control integration

## What's Next?

**Week 13: Capstone Project** - Build a complete autonomous humanoid assistant integrating all modules.

**Next**: [Week 13: Capstone →](./week13-capstone.md)
