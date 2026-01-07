# ہفتہ 12: ہیومنائڈ کائنی میٹکس اور کنٹرول

## تعارف

اس ہفتے، آپ ہیومنائڈز کے لیے بنیادی موشن کنٹرول نافذ کریں گے: **فارورڈ/انورس کائنی میٹکس**، **ہول باڈی کنٹرول**، اور **بیلنس**۔ یہ تکنیکیں ہیرا پھیری، چلنے، اور ماحول کے ساتھ مستحکم تعاملات کو ممکن بناتی ہیں۔

## فارورڈ کائنی میٹکس (FK)

**فارورڈ کائنی میٹکس** جوائنٹ اینگلز سے اینڈ ایفیکٹر کی پوزیشن کا حساب لگاتا ہے۔

### DH پیرامیٹرز

ڈیناویٹ-ہارٹنبرگ پیرامیٹرز لنک ٹرانسفارمز کی وضاحت کرتے ہیں:

```python
import numpy as np

class DHParameter:
    def __init__(self, a, alpha, d, theta):
        self.a = a          # لنک کی لمبائی
        self.alpha = alpha  # لنک کا موڑ
        self.d = d          # لنک کا آفسیٹ
        self.theta = theta  # جوائنٹ اینگل

def dh_transform(dh):
    """DH پیرامیٹرز سے ٹرانسفارمیشن میٹرکس کا حساب لگائیں"""
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

### 7-DOF آرم FK

```python
class HumanoidArmFK:
    def __init__(self):
        # 7-DOF آرم کے لیے DH پیرامیٹرز
        # [a, alpha, d, theta]
        self.dh_params = [
            DHParameter(0, np.pi/2, 0.05, 0),   # کندھے کی پچ
            DHParameter(0, -np.pi/2, 0, 0),     # کندھے کا رول
            DHParameter(0, np.pi/2, 0.3, 0),    # کندھے کا یاو
            DHParameter(0, -np.pi/2, 0, 0),     # کہنی
            DHParameter(0, np.pi/2, 0.25, 0),   # کلائی کی پچ
            DHParameter(0, -np.pi/2, 0, 0),     # کلائی کا رول
            DHParameter(0, 0, 0.1, 0),          # کلائی کا یاو
        ]

    def forward_kinematics(self, joint_angles):
        """جوائنٹ اینگلز سے اینڈ ایفیکٹر پوز کا حساب لگائیں"""
        T = np.eye(4)

        for i, angle in enumerate(joint_angles):
            self.dh_params[i].theta = angle
            T_i = dh_transform(self.dh_params[i])
            T = T @ T_i

        position = T[:3, 3]
        orientation = T[:3, :3]

        return position, orientation

# استعمال
arm = HumanoidArmFK()
joints = [0.5, 0.2, -0.3, 1.5, 0.0, 0.1, 0.0]  # ریڈینز
position, rotation = arm.forward_kinematics(joints)
print(f"اینڈ ایفیکٹر پوزیشن: {position}")
```

## انورس کائنی میٹکس (IK)

**انورس کائنی میٹکس** مطلوبہ اینڈ ایفیکٹر پوز کے لیے جوائنٹ اینگلز کا حساب لگاتا ہے۔

### جیکوبین کے ساتھ عددی IK

```python
class HumanoidArmIK:
    def __init__(self):
        self.fk = HumanoidArmFK()
        self.num_joints = 7

    def jacobian(self, joint_angles, delta=0.0001):
        """عددی جیکوبین کا حساب لگائیں"""
        J = np.zeros((6, self.num_joints))

        # موجودہ پوز
        pos0, rot0 = self.fk.forward_kinematics(joint_angles)

        for i in range(self.num_joints):
            # جوائنٹ i کو پریشان کریں
            joints_perturbed = joint_angles.copy()
            joints_perturbed[i] += delta

            pos1, rot1 = self.fk.forward_kinematics(joints_perturbed)

            # پوزیشن ڈیریویٹو
            J[:3, i] = (pos1 - pos0) / delta

            # اورینٹیشن ڈیریویٹو (سادہ)
            # عملی طور پر، محور-زاویہ یا کواٹرنین نمائندگی استعمال کریں
            J[3:, i] = 0  # پلیس ہولڈر

        return J

    def inverse_kinematics(self, target_pos, initial_guess=None, max_iter=100):
        """جیکوبین سیوڈو انورس کا استعمال کرتے ہوئے IK"""
        if initial_guess is None:
            joint_angles = np.zeros(self.num_joints)
        else:
            joint_angles = initial_guess.copy()

        for iteration in range(max_iter):
            # موجودہ پوزیشن
            current_pos, _ = self.fk.forward_kinematics(joint_angles)

            # غلطی
            error = target_pos - current_pos
            error_norm = np.linalg.norm(error)

            if error_norm < 0.001:  # 1 ملی میٹر کی رواداری
                return joint_angles, True

            # جیکوبین
            J = self.jacobian(joint_angles)
            J_pos = J[:3, :]  # صرف پوزیشن کا حصہ

            # سیوڈو انورس
            J_pinv = np.linalg.pinv(J_pos)

            # جوائنٹس کو اپ ڈیٹ کریں
            delta_q = J_pinv @ error
            joint_angles += 0.1 * delta_q  # قدم کا سائز

            # جوائنٹ کی حدود میں کلپ کریں
            joint_angles = np.clip(joint_angles, -np.pi, np.pi)

        return joint_angles, False  # کنورج ہونے میں ناکام

# استعمال
ik = HumanoidArmIK()
target = np.array([0.4, 0.2, 0.3])  # مطلوبہ اینڈ ایفیکٹر پوزیشن
joints, success = ik.inverse_kinematics(target)

if success:
    print(f"IK حل: {joints}")
else:
    print("IK کنورج ہونے میں ناکام")
```

### IKFast (تجزیاتی IK)

تیز، درست حل کے لیے، IKFast استعمال کریں:

```bash
# IKFast سالور تیار کریں
pip install ikfast-pybind

# پائیتھن میں
from ikfast_humanoid_arm import get_ik

solutions = get_ik(target_pose)
for sol in solutions:
    print(f"حل: {sol}")
```

## ہول باڈی کنٹرول

رکاوٹوں کا احترام کرتے ہوئے تمام جوڑوں کو بیک وقت کنٹرول کریں۔

### کواڈریٹک پروگرامنگ (QP)

```python
import cvxpy as cp

class WholeBodyController:
    def __init__(self, num_joints=28):
        self.num_joints = num_joints

    def solve(self, desired_accelerations, joint_limits, contact_forces):
        """جوائنٹ ٹارک کے لیے QP حل کریں"""
        # فیصلے کے متغیرات
        tau = cp.Variable(self.num_joints)  # جوائنٹ ٹارک
        f_contact = cp.Variable(4)  # رابطہ قوتیں (2 پاؤں)

        # ڈائنامکس: M * ddq = tau + J^T * f
        # سادہ: ٹریکنگ کی غلطی کو کم سے کم کریں + ریگولرائزیشن

        # لاگت کا فنکشن
        cost = cp.sum_squares(tau - desired_accelerations * 10)
        cost += 0.01 * cp.sum_squares(tau)  # ریگولرائزیشن

        # رکاوٹیں
        constraints = [
            tau >= joint_limits[:, 0],  # نچلی حدود
            tau <= joint_limits[:, 1],  # اوپری حدود
            f_contact >= 0,  # یکطرفہ رابطے
        ]

        # حل کریں
        problem = cp.Problem(cp.Minimize(cost), constraints)
        problem.solve()

        return tau.value

# استعمال
wbc = WholeBodyController(num_joints=28)
joint_limits = np.array([[-100, 100]] * 28)  # Nm
desired_acc = np.zeros(28)
contact_forces = np.zeros(4)

torques = wbc.solve(desired_acc, joint_limits, contact_forces)
```

## بیلنس کنٹرول

**زیرو مومنٹ پوائنٹ (ZMP)** کا استعمال کرتے ہوئے استحکام برقرار رکھیں۔

### ZMP کا حساب کتاب

```python
class BalanceController:
    def __init__(self, mass=60.0, height=1.0):
        self.mass = mass
        self.g = 9.81
        self.height = height

    def compute_zmp(self, com_pos, com_acc):
        """CoM حالت سے ZMP کا حساب لگائیں"""
        # ZMP_x = CoM_x - (CoM_z / g) * CoM_ddx
        zmp_x = com_pos[0] - (com_pos[2] / self.g) * com_acc[0]
        zmp_y = com_pos[1] - (com_pos[2] / self.g) * com_acc[1]

        return np.array([zmp_x, zmp_y])

    def is_stable(self, zmp, support_polygon):
        """چیک کریں کہ آیا ZMP سپورٹ پولی گون کے اندر ہے"""
        # سادہ مستطیل چیک
        x_min, x_max = support_polygon[0]
        y_min, y_max = support_polygon[1]

        return (x_min <= zmp[0] <= x_max) and (y_min <= zmp[1] <= y_max)

    def stabilize(self, current_com, desired_com, support_polygon):
        """مستحکم کرنے کے لیے CoM ایکسلریشن کا حساب لگائیں"""
        # CoM کے لیے PD کنٹرولر
        kp = 100.0
        kd = 20.0

        com_error = desired_com - current_com[:3]
        com_vel = current_com[3:]

        com_acc = kp * com_error - kd * com_vel

        # ZMP چیک کریں
        zmp = self.compute_zmp(current_com[:3], com_acc)

        if not self.is_stable(zmp, support_polygon):
            # ایکسلریشن کو کم کریں
            com_acc *= 0.5

        return com_acc

# استعمال
balance = BalanceController(mass=60.0)
current_com = np.array([0.0, 0.0, 1.0, 0.0, 0.0, 0.0])  # [x, y, z, vx, vy, vz]
desired_com = np.array([0.1, 0.0, 1.0])
support = [(-0.1, 0.1), (-0.05, 0.05)]  # پاؤں کا پولی گون

com_acc = balance.stabilize(current_com, desired_com, support)
```

## چلنے کی چال کی جنریشن

### سادہ متواتر چال

```python
class GaitGenerator:
    def __init__(self, step_length=0.2, step_height=0.05, period=1.0):
        self.step_length = step_length
        self.step_height = step_height
        self.period = period

    def foot_trajectory(self, t, phase='swing'):
        """پاؤں کی ٹریجکٹری تیار کریں"""
        if phase == 'swing':
            # سائنوسائیڈل سوئنگ
            progress = (t % self.period) / self.period

            x = self.step_length * progress
            z = self.step_height * np.sin(np.pi * progress)
            y = 0.0

            return np.array([x, y, z])
        else:
            # اسٹینس (اسٹیشنری)
            return np.array([0.0, 0.0, 0.0])

    def generate_gait(self, t):
        """مکمل چلنے کا پیٹرن تیار کریں"""
        # ٹانگوں کو باری باری
        left_phase = 'swing' if (t // self.period) % 2 == 0 else 'stance'
        right_phase = 'stance' if left_phase == 'swing' else 'swing'

        left_foot = self.foot_trajectory(t, left_phase)
        right_foot = self.foot_trajectory(t, right_phase)

        return left_foot, right_foot

# استعمال
gait = GaitGenerator(step_length=0.2, step_height=0.05, period=1.0)

for t in np.linspace(0, 4, 100):
    left, right = gait.generate_gait(t)
    print(f"t={t:.2f}: Left={left}, Right={right}")
```

## ROS 2 انضمام

```python
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint

class HumanoidController(Node):
    def __init__(self):
        super().__init__('humanoid_controller')

        # پبلشرز
        self.traj_pub = self.create_publisher(
            JointTrajectory,
            '/joint_trajectory',
            10
        )

        # IK سالور
        self.ik_solver = HumanoidArmIK()

        # کارٹیشین اہداف کے لیے سروس
        self.srv = self.create_service(
            MoveToCartesian,
            'move_to_cartesian',
            self.move_callback
        )

    def move_callback(self, request, response):
        # request.target_pose = [x, y, z]
        target = np.array([request.x, request.y, request.z])

        # IK حل کریں
        joints, success = self.ik_solver.inverse_kinematics(target)

        if success:
            # ٹریجکٹری بھیجیں
            self.send_trajectory(joints)
            response.success = True
        else:
            response.success = False
            response.message = "IK ناکام"

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

## خلاصہ

اس ہفتے آپ نے سیکھا:

- DH پیرامیٹرز کے ساتھ فارورڈ کائنی میٹکس
- انورس کائنی میٹکس (عددی اور تجزیاتی)
- جیکوبین پر مبنی طریقے
- QP کے ساتھ ہول باڈی کنٹرول
- بیلنس کنٹرول اور ZMP
- چلنے کی چال کی جنریشن
- ROS 2 موشن کنٹرول انضمام

## آگے کیا ہے؟

**ہفتہ 13: کیپ اسٹون پروجیکٹ** - تمام ماڈیولز کو مربوط کرتے ہوئے ایک مکمل خود مختار ہیومنائڈ اسسٹنٹ بنائیں۔

**آگے**: [ہفتہ 13: کیپ اسٹون →](./week13-capstone.md)