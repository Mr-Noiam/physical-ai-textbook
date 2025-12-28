# ہفتہ 1: Physical AI کی بنیادیں

## Embodied Intelligence کا تعارف

ہفتہ 1 میں خوش آمدید! اس ہفتے، ہم **Physical AI** کے بنیادی تصورات کو دریافت کریں گے - مصنوعی ذہانت کے نظام جو روبوٹس جیسے embodied پلیٹ فارمز کے ذریعے جسمانی دنیا کے ساتھ تعامل کرتے ہیں اور اس سے سیکھتے ہیں۔

### Physical AI کیا ہے؟

**Physical AI** سے مراد وہ AI نظام ہیں جو:
1. **محسوس کرتے ہیں** sensors (cameras, LiDAR, IMUs) کے ذریعے جسمانی دنیا کو
2. **استدلال کرتے ہیں** مقامی تعلقات، طبیعیات، اور causality کے بارے میں  
3. **عمل کرتے ہیں** actuators (motors, grippers) کے ذریعے حقیقی دنیا میں
4. **سیکھتے ہیں** جسمانی تعاملات اور feedback سے

خالص ڈیجیٹل AI (جیسے ChatGPT) کے برعکس، Physical AI کو سنبھالنا ہوتا ہے:
- **حقیقی وقت کی پابندیاں**: فیصلے milliseconds میں کرنے ہوتے ہیں
- **غیر یقینی**: Sensors شور مچاتے ہیں، دنیا غیر متوقع ہے
- **حفاظت**: غلطیاں جسمانی نقصان کا سبب بن سکتی ہیں
- **Embodiment**: AI کا "جسم" (robot morphology) اس بات پر اثر انداز ہوتا ہے کہ یہ کیا کر سکتا ہے

## ہیومینائیڈ روبوٹس کیوں؟

ہیومینائیڈ روبوٹس انسانوں کی طرح کی شکل رکھتے ہیں - دو بازو، دو ٹانگیں، ایک torso، اور ایک سر۔ یہ ڈیزائن کئی فوائد پیش کرتا ہے:

- **انسانی ماحول کے لیے**: زیادہ تر عمارتیں، اوزار، اور فرنیچر انسانی جسم کے لیے ڈیزائن کیے گئے ہیں
- **قدرتی تعامل**: لوگ ہیومینائیڈز کے ساتھ زیادہ آرام سے بات چیت کرتے ہیں
- **عام مقصد**: ایک morphology مختلف کاموں کو سنبھال سکتی ہے
- **Embodied learning**: انسانی ڈیٹا (demonstrations، videos) کا فائدہ اٹھا سکتے ہیں

## Physical AI Stack

Physical AI نظام کئی تہوں پر مشتمل ہے:

```
┌─────────────────────────────────────┐
│   High-Level Intelligence (VLAs)    │ ← GPT-4، CLIP، Whisper
├─────────────────────────────────────┤
│   Motion Planning & Control          │ ← MuJoCo، Isaac Gym
├─────────────────────────────────────┤
│   Perception & State Estimation      │ ← SLAM، Object Detection
├─────────────────────────────────────┤
│   Robot Middleware (ROS 2)           │ ← Communication، Tools
├─────────────────────────────────────┤
│   Hardware (Actuators، Sensors)      │ ← Motors، Cameras، IMUs
└─────────────────────────────────────┘
```

## ROS 2 کا کردار

**ROS 2** (Robot Operating System 2) robotics میں de facto standard middleware ہے۔ یہ فراہم کرتا ہے:

- **Communication**: Nodes کے درمیان ڈیٹا بھیجنے کے لیے topics/services
- **Tools**: Visualization (RViz)، recording (rosbag)، simulation (Gazebo)
- **Ecosystem**: ہزاروں open-source packages
- **Real-time support**: DDS کے ذریعے deterministic communication

### ROS 2 کیوں؟

ROS 1 کے مقابلے میں:
- ✅ **Real-time**: DDS middleware deterministic latency کے لیے
- ✅ **Security**: Encrypted communication
- ✅ **Multi-robot**: Built-in support
- ✅ **Cross-platform**: Linux، Windows، macOS
- ✅ **Python 3**: Modern language support

## یہ ہفتے کے سیکھنے کے مقاصد

اس ہفتے کے اختتام تک، آپ قابل ہوں گے:

1. Physical AI اور embodied intelligence کی وضاحت کرنا
2. ROS 2 architecture کو سمجھنا  
3. Ubuntu 22.04 پر ROS 2 Humble انسٹال کرنا
4. Basic ROS 2 concepts (nodes، topics، services) کو سمجھنا
5. ایک simple talker/listener node چلانا

## اگلا کیا ہے؟

**ہفتہ 2: ROS 2 Architecture** - Nodes، topics، services، اور actions کو گہرائی میں جانیں۔

**اگلا**: [ہفتہ 2: ROS 2 Fundamentals →](./week2-fundamentals.md)
