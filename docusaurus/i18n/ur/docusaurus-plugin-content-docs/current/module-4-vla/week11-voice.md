[TRANSLATION_FAILED] # Week 11: Voice-to-Action with Whisper

[TRANSLATION_FAILED] ## Introduction

[TRANSLATION_FAILED] This week, you'll build a complete voice control system for your humanoid using **Whisper** (speech recognition), **LLMs** (reasoning), and action primitives. The pipeline converts spoken commands to robot actions in real-time.

[TRANSLATION_FAILED] ## Architecture

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│Microphone│───>│ Whisper  │───>│   LLM    │───>│ Actions  │
│  (Audio) │    │   (ASR)  │    │(Reasoning)│    │(Robotics)│
└──────────┘    └──────────┘    └──────────┘    └──────────┘
```

[TRANSLATION_FAILED] **Components**:
[TRANSLATION_FAILED] - **ASR**: Whisper (OpenAI)
[TRANSLATION_FAILED] - **LLM**: GPT-4, LLaMA, Mistral
[TRANSLATION_FAILED] - **TTS**: piper, coqui-tts (optional feedback)
[TRANSLATION_FAILED] - **Action primitives**: Navigate, pick, place, etc.

[TRANSLATION_FAILED] ## Whisper Installation

```bash
pip install openai-whisper torch

# For faster inference (optional)
pip install faster-whisper
```

[TRANSLATION_FAILED] ## Basic Whisper Usage

```python
import whisper

# Load model
model = whisper.load_model("base")  # tiny, base, small, medium, large

# Transcribe audio file
result = model.transcribe("audio.mp3")

print(result["text"])
# Output: "Robot, please bring me a cup of water"
```

[TRANSLATION_FAILED] ## Real-Time Microphone Input

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
        print("Listening...")
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

# Usage
listener = VoiceListener()
command = listener.listen(duration=5)
print(f"You said: {command}")
listener.close()
```

[TRANSLATION_FAILED] ## ROS 2 Voice Command Node

```python
from std_msgs.msg import String
import whisper
import pyaudio
import numpy as np

class VoiceCommandNode(Node):
    def __init__(self):
        super().__init__('voice_command')

        # Whisper model
        self.model = whisper.load_model("base")

        # Publisher for transcriptions
        self.pub = self.create_publisher(String, '/voice_command', 10)

        # Audio stream
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            frames_per_buffer=1024
        )

        # Timer for continuous listening
        self.timer = self.create_timer(5.0, self.listen_and_transcribe)

        self.get_logger().info('Voice command node started')

    def listen_and_transcribe(self):
        # Record 5 seconds of audio
        frames = []
        for _ in range(0, int(16000 / 1024 * 5)):
            data = self.stream.read(1024)
            frames.append(np.frombuffer(data, dtype=np.int16))

        audio_data = np.concatenate(frames).astype(np.float32) / 32768.0

        # Transcribe
        result = self.model.transcribe(audio_data, language='en', fp16=False)
        text = result["text"].strip()

        if text:
            self.get_logger().info(f'Heard: {text}')
            msg = String()
            msg.data = text
            self.pub.publish(msg)

    def destroy_node(self):
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()
        super().destroy_node()
```

[TRANSLATION_FAILED] ## LLM for Command Parsing

[TRANSLATION_FAILED] Use LLM to extract intent and parameters:

```python
from openai import OpenAI

class CommandParser:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def parse_command(self, text):
        prompt = f"""Parse this robot command into a JSON action:
Command: "{text}"

Available actions:
- navigate(location: str)
- pick(object: str)
- place(object: str, location: str)
- search(object: str)

Return only JSON, no explanation.
Example: {{"action": "navigate", "params": {{"location": "kitchen"}}}}"""

        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0
        )

        import json
        return json.loads(response.choices[0].message.content)

# Usage
parser = CommandParser()
result = parser.parse_command("Robot, bring me a cup from the kitchen")
print(result)
# {"action": "pick", "params": {"object": "cup", "location": "kitchen"}}
```

[TRANSLATION_FAILED] ## Complete Voice-to-Action Pipeline

```python
from std_msgs.msg import String
from geometry_msgs.msg import PoseStamped
from nav2_simple_commander.robot_navigator import BasicNavigator
import whisper
import json

class VoiceToActionNode(Node):
    def __init__(self):
        super().__init__('voice_to_action')

        # Whisper
        self.whisper_model = whisper.load_model("base")

        # LLM parser
        self.llm = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        # Navigator
        self.navigator = BasicNavigator()

        # Voice command subscriber
        self.sub = self.create_subscription(
            String,
            '/voice_command',
            self.command_callback,
            10
        )

        # Predefined locations
        self.locations = {
            "kitchen": (3.0, 2.0),
            "living room": (1.0, 1.0),
            "bedroom": (5.0, 4.0),
        }

        self.get_logger().info('Voice-to-Action ready')

    def command_callback(self, msg):
        command_text = msg.data

        # Parse with LLM
        action = self.parse_command(command_text)

        self.get_logger().info(f'Executing: {action}')

        # Execute action
        if action["action"] == "navigate":
            self.navigate_to(action["params"]["location"])
        elif action["action"] == "pick":
            self.pick_object(action["params"]["object"])
        elif action["action"] == "search":
            self.search_object(action["params"]["object"])

    def parse_command(self, text):
        prompt = f"""Parse: "{text}"
Actions: navigate(location), pick(object), search(object)
JSON only:"""

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
            self.get_logger().info(f'Navigating to {location}')
        else:
            self.get_logger().warn(f'Unknown location: {location}')

    def pick_object(self, object_name):
        self.get_logger().info(f'Picking {object_name}')
        # Implement pick logic (Week 12)

    def search_object(self, object_name):
        self.get_logger().info(f'Searching for {object_name}')
        # Use CLIP to find object (Week 10)
```

[TRANSLATION_FAILED] ## Text-to-Speech Feedback

[TRANSLATION_FAILED] Provide voice feedback:

```python
from piper import PiperVoice

class VoiceFeedback:
    def __init__(self):
        self.voice = PiperVoice.load("en_US-lessac-medium")

    def speak(self, text):
        audio = self.voice.synthesize(text)
        # Play audio
        import sounddevice as sd
        sd.play(audio, samplerate=22050)
        sd.wait()

# In node
class VoiceToActionNode(Node):
    def __init__(self):
        # ...
        self.feedback = VoiceFeedback()

    def navigate_to(self, location):
        self.feedback.speak(f"Navigating to {location}")
        # ...
```

[TRANSLATION_FAILED] ## Wake Word Detection

[TRANSLATION_FAILED] Use voice activity detection:

```python
import webrtcvad

class WakeWordDetector:
    def __init__(self, wake_word="robot"):
        self.wake_word = wake_word
        self.vad = webrtcvad.Vad(3)  # Aggressiveness 0-3

    def is_wake_word(self, audio_chunk):
        # Simple implementation: use Whisper
        model = whisper.load_model("tiny")
        result = model.transcribe(audio_chunk)

        return self.wake_word.lower() in result["text"].lower()

# Usage
detector = WakeWordDetector(wake_word="hey robot")

while True:
    audio = record_audio(duration=2)
    if detector.is_wake_word(audio):
        print("Wake word detected!")
        command = record_audio(duration=5)
        # Process command
```

[TRANSLATION_FAILED] ## Complete Example Launch

```python
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        # Voice command listener
        Node(
            package='humanoid_voice',
            executable='voice_listener',
            name='voice_listener',
            output='screen'
        ),

        # Voice-to-action executor
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

        # Navigation (from Week 9)
        # CLIP detection (from Week 10)
    ])
```

[TRANSLATION_FAILED] ## Error Handling

```python
def command_callback(self, msg):
    try:
        action = self.parse_command(msg.data)
        self.execute_action(action)
    except json.JSONDecodeError:
        self.get_logger().error('Failed to parse command')
        self.feedback.speak("I didn't understand that")
    except KeyError as e:
        self.get_logger().error(f'Missing parameter: {e}')
        self.feedback.speak("I'm missing some information")
    except Exception as e:
        self.get_logger().error(f'Error: {e}')
        self.feedback.speak("Something went wrong")
```

[TRANSLATION_FAILED] ## Summary

[TRANSLATION_FAILED] This week you learned:

[TRANSLATION_FAILED] - Whisper for speech-to-text
[TRANSLATION_FAILED] - Real-time microphone input
[TRANSLATION_FAILED] - LLM command parsing
[TRANSLATION_FAILED] - Voice-to-action pipeline
[TRANSLATION_FAILED] - Text-to-speech feedback
[TRANSLATION_FAILED] - Wake word detection
[TRANSLATION_FAILED] - Complete ROS 2 integration

[TRANSLATION_FAILED] ## What's Next?

[TRANSLATION_FAILED] **Week 12: Humanoid Kinematics and Control** - Implement forward/inverse kinematics and whole-body control for manipulation.

[TRANSLATION_FAILED] **Next**: [Week 12: Humanoid Control →](./week12-humanoid.md)
