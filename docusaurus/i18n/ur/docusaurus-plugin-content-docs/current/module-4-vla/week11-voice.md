# ہفتہ 11: وسپر کے ساتھ وائس ٹو ایکشن

## تعارف

اس ہفتے، آپ **وسپر** (اسپیچ ریکگنیشن)، **ایل ایل ایم** (استدلال)، اور ایکشن پریمیٹیوز کا استعمال کرتے ہوئے اپنے ہیومنائڈ کے لیے ایک مکمل وائس کنٹرول سسٹم بنائیں گے۔ یہ پائپ لائن بولے گئے احکامات کو حقیقی وقت میں روبوٹ کے اعمال میں تبدیل کرتی ہے۔

## فن تعمیر

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│مائیکروفون│───>│  وسپر    │───>│   LLM    │───>│   اعمال   │
│  (آڈیو)  │    │   (ASR)  │    │(استدلال) │    │(روبوٹکس)│
└──────────┘    └──────────┘    └──────────┘    └──────────┘
```

**اجزاء**:
- **ASR**: وسپر (اوپن اے آئی)
- **LLM**: GPT-4, LLaMA, Mistral
- **TTS**: پائپر، کوکی-ٹی ٹی ایس (اختیاری فیڈ بیک)
- **ایکشن پریمیٹیوز**: نیویگیٹ، پک، پلیس، وغیرہ۔

## وسپر انسٹالیشن

```bash
pip install openai-whisper torch

# تیز تر انفرنس کے لیے (اختیاری)
pip install faster-whisper
```

## بنیادی وسپر استعمال

```python
import whisper

# ماڈل لوڈ کریں
model = whisper.load_model("base")  # tiny, base, small, medium, large

# آڈیو فائل کو ٹرانسکرائب کریں
result = model.transcribe("audio.mp3")

print(result["text"])
# آؤٹ پٹ: "روبوٹ، براہ کرم مجھے ایک کپ پانی لا دو"
```

## حقیقی وقت میں مائیکروفون ان پٹ

```python
import pyaudio
import numpy as np
import whisper

class VoiceListener:
    def __init__(self):
        self.model = whisper.load_model("base")

        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            frames_per_buffer=1024
        )

    def listen(self, duration=5):
        print("سن رہا ہوں...")
        frames = []

        for _ in range(0, int(16000 / 1024 * duration)):
            data = self.stream.read(1024)
            frames.append(np.frombuffer(data, dtype=np.int16))

        audio_data = np.concatenate(frames).astype(np.float32) / 32768.0

        result = self.model.transcribe(audio_data, language='en')
        return result["text"]

    def close(self):
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()

# استعمال
listener = VoiceListener()
command = listener.listen(duration=5)
print(f"آپ نے کہا: {command}")
listener.close()
```

## ROS 2 وائس کمانڈ نوڈ

```python
from std_msgs.msg import String
import whisper
import pyaudio
import numpy as np

class VoiceCommandNode(Node):
    def __init__(self):
        super().__init__('voice_command')

        # وسپر ماڈل
        self.model = whisper.load_model("base")

        # ٹرانسکرپشنز کے لیے پبلشر
        self.pub = self.create_publisher(String, '/voice_command', 10)

        # آڈیو اسٹریم
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            frames_per_buffer=1024
        )

        # مسلسل سننے کے لیے ٹائمر
        self.timer = self.create_timer(5.0, self.listen_and_transcribe)

        self.get_logger().info('وائس کمانڈ نوڈ شروع ہو گیا')

    def listen_and_transcribe(self):
        # 5 سیکنڈ کا آڈیو ریکارڈ کریں
        frames = []
        for _ in range(0, int(16000 / 1024 * 5)):
            data = self.stream.read(1024)
            frames.append(np.frombuffer(data, dtype=np.int16))

        audio_data = np.concatenate(frames).astype(np.float32) / 32768.0

        # ٹرانسکرائب کریں
        result = self.model.transcribe(audio_data, language='en', fp16=False)
        text = result["text"].strip()

        if text:
            self.get_logger().info(f'سنا: {text}')
            msg = String()
            msg.data = text
            self.pub.publish(msg)

    def destroy_node(self):
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()
        super().destroy_node()
```

## کمانڈ پارسنگ کے لیے LLM

نیت اور پیرامیٹرز نکالنے کے لیے LLM استعمال کریں:

```python
from openai import OpenAI

class CommandParser:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def parse_command(self, text):
        prompt = f"""اس روبوٹ کمانڈ کو JSON ایکشن میں پارس کریں:
کمانڈ: "{text}"

دستیاب اعمال:
- navigate(location: str)
- pick(object: str)
- place(object: str, location: str)
- search(object: str)

صرف JSON واپس کریں، کوئی وضاحت نہیں۔
مثال: {{"action": "navigate", "params": {{"location": "kitchen"}}}}"""

        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0
        )

        import json
        return json.loads(response.choices[0].message.content)

# استعمال
parser = CommandParser()
result = parser.parse_command("روبوٹ، مجھے کچن سے ایک کپ لا دو")
print(result)
# {"action": "pick", "params": {"object": "cup", "location": "kitchen"}}
```

## مکمل وائس ٹو ایکشن پائپ لائن

```python
from std_msgs.msg import String
from geometry_msgs.msg import PoseStamped
from nav2_simple_commander.robot_navigator import BasicNavigator
import whisper
import json

class VoiceToActionNode(Node):
    def __init__(self):
        super().__init__('voice_to_action')

        # وسپر
        self.whisper_model = whisper.load_model("base")

        # LLM پارسر
        self.llm = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        # نیویگیٹر
        self.navigator = BasicNavigator()

        # وائس کمانڈ سبسکرائبر
        self.sub = self.create_subscription(
            String,
            '/voice_command',
            self.command_callback,
            10
        )

        # پہلے سے طے شدہ مقامات
        self.locations = {
            "kitchen": (3.0, 2.0),
            "living room": (1.0, 1.0),
            "bedroom": (5.0, 4.0),
        }

        self.get_logger().info('وائس ٹو ایکشن تیار ہے')

    def command_callback(self, msg):
        command_text = msg.data

        # LLM کے ساتھ پارس کریں
        action = self.parse_command(command_text)

        self.get_logger().info(f'عمل درآمد: {action}')

        # عمل درآمد کریں
        if action["action"] == "navigate":
            self.navigate_to(action["params"]["location"])
        elif action["action"] == "pick":
            self.pick_object(action["params"]["object"])
        elif action["action"] == "search":
            self.search_object(action["params"]["object"])

    def parse_command(self, text):
        prompt = f"""پارس کریں: "{text}"
اعمال: navigate(location), pick(object), search(object)
صرف JSON:"""

        response = self.llm.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0
        )

        return json.loads(response.choices[0].message.content)

    def navigate_to(self, location):
        if location in self.locations:
            x, y = self.locations[location]

            goal_pose = PoseStamped()
            goal_pose.header.frame_id = 'map'
            goal_pose.pose.position.x = x
            goal_pose.pose.position.y = y
            goal_pose.pose.orientation.w = 1.0

            self.navigator.goToPose(goal_pose)
            self.get_logger().info(f'{location} پر نیویگیٹ کر رہا ہے')
        else:
            self.get_logger().warn(f'نامعلوم مقام: {location}')

    def pick_object(self, object_name):
        self.get_logger().info(f'{object_name} اٹھا رہا ہے')
        # اٹھانے کی منطق نافذ کریں (ہفتہ 12)

    def search_object(self, object_name):
        self.get_logger().info(f'{object_name} کی تلاش ہے')
        # آبجیکٹ تلاش کرنے کے لیے CLIP استعمال کریں (ہفتہ 10)
```

## ٹیکسٹ ٹو اسپیچ فیڈ بیک

صوتی فیڈ بیک فراہم کریں:

```python
from piper import PiperVoice

class VoiceFeedback:
    def __init__(self):
        self.voice = PiperVoice.load("en_US-lessac-medium")

    def speak(self, text):
        audio = self.voice.synthesize(text)
        # آڈیو چلائیں
        import sounddevice as sd
        sd.play(audio, samplerate=22050)
        sd.wait()

# نوڈ میں
class VoiceToActionNode(Node):
    def __init__(self):
        # ...
        self.feedback = VoiceFeedback()

    def navigate_to(self, location):
        self.feedback.speak(f"{location} پر نیویگیٹ کر رہا ہوں")
        # ...
```

## ویک ورڈ ڈیٹیکشن

وائس ایکٹیویٹی ڈیٹیکشن استعمال کریں:

```python
import webrtcvad

class WakeWordDetector:
    def __init__(self, wake_word="robot"):
        self.wake_word = wake_word
        self.vad = webrtcvad.Vad(3)  # جارحیت 0-3

    def is_wake_word(self, audio_chunk):
        # سادہ نفاذ: وسپر استعمال کریں
        model = whisper.load_model("tiny")
        result = model.transcribe(audio_chunk)

        return self.wake_word.lower() in result["text"].lower()

# استعمال
detector = WakeWordDetector(wake_word="hey robot")

while True:
    audio = record_audio(duration=2)
    if detector.is_wake_word(audio):
        print("ویک ورڈ کا پتہ چلا!")
        command = record_audio(duration=5)
        # کمانڈ پر کارروائی کریں
```

## مکمل مثال لانچ

```python
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        # وائس کمانڈ لسنسر
        Node(
            package='humanoid_voice',
            executable='voice_listener',
            name='voice_listener',
            output='screen'
        ),

        # وائس ٹو ایکشن ایگزیکیوٹر
        Node(
            package='humanoid_voice',
            executable='voice_to_action',
            name='voice_to_action',
            parameters=[{
                'llm_model': 'gpt-4',
                'whisper_model': 'base'
            }],
            output='screen'
        ),

        # نیویگیشن (ہفتہ 9 سے)
        # CLIP ڈیٹیکشن (ہفتہ 10 سے)
    ])
```

## غلطی سے نمٹنا

```python
def command_callback(self, msg):
    try:
        action = self.parse_command(msg.data)
        self.execute_action(action)
    except json.JSONDecodeError:
        self.get_logger().error('کمانڈ پارس کرنے میں ناکام')
        self.feedback.speak("مجھے یہ سمجھ نہیں آیا")
    except KeyError as e:
        self.get_logger().error(f'پیرامیٹر غائب ہے: {e}')
        self.feedback.speak("مجھے کچھ معلومات غائب ہیں")
    except Exception as e:
        self.get_logger().error(f'خرابی: {e}')
        self.feedback.speak("کچھ غلط ہو گیا")
```

## خلاصہ

اس ہفتے آپ نے سیکھا:

- اسپیچ ٹو ٹیکسٹ کے لیے وسپر
- حقیقی وقت میں مائیکروفون ان پٹ
- ایل ایل ایم کمانڈ پارسنگ
- وائس ٹو ایکشن پائپ لائن
- ٹیکسٹ ٹو اسپیچ فیڈ بیک
- ویک ورڈ ڈیٹیکشن
- مکمل ROS 2 انضمام

## آگے کیا ہے؟

**ہفتہ 12: ہیومنائڈ کائنی میٹکس اور کنٹرول** - ہیرا پھیری کے لیے فارورڈ/انورس کائنی میٹکس اور ہول باڈی کنٹرول نافذ کریں۔

**آگے**: [ہفتہ 12: ہیومنائڈ کنٹرول →](./week12-humanoid.md)