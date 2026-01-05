[TRANSLATION_FAILED] # Week 10: Vision-Language-Action Convergence

[TRANSLATION_FAILED] ## Introduction

[TRANSLATION_FAILED] **Vision-Language-Action (VLA)** models represent the convergence of computer vision, natural language processing, and robot control. This week, you'll learn how models like CLIP, LLaVA, and RT-2 enable humanoids to understand visual scenes, interpret commands, and execute tasks.

[TRANSLATION_FAILED] ## The VLA Paradigm

```
┌──────────┐    ┌──────────┐    ┌──────────────┐
│  Vision  │───>│ Language │───>│   Action     │
│  (CLIP)  │    │  (LLM)   │    │ (Policies)   │
└──────────┘    └──────────┘    └──────────────┘
     ▲                                   │
     │           Feedback Loop           │
     └───────────────────────────────────┘
```

[TRANSLATION_FAILED] **Components**:
[TRANSLATION_FAILED] - **Vision Encoder**: CLIP, DINOv2, MAE
[TRANSLATION_FAILED] - **Language Model**: GPT-4, LLaMA, PaLM
[TRANSLATION_FAILED] - **Action Decoder**: Diffusion policies, transformers
[TRANSLATION_FAILED] - **Embodied Reasoning**: Chain-of-thought, planning

[TRANSLATION_FAILED] ## CLIP for Zero-Shot Object Recognition

[TRANSLATION_FAILED] **CLIP** (Contrastive Language-Image Pre-training) maps images and text to a shared embedding space.

[TRANSLATION_FAILED] ### Installation

```bash
pip install openai-clip torch torchvision
```

[TRANSLATION_FAILED] ### Basic Usage

```python
import torch
import clip
from PIL import Image

# Load model
device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load("ViT-B/32", device=device)

# Load image
image = preprocess(Image.open("robot_view.jpg")).unsqueeze(0).to(device)

# Text prompts
text = clip.tokenize(["a cup", "a chair", "a person"]).to(device)

# Compute features
with torch.no_grad():
    image_features = model.encode_image(image)
    text_features = model.encode_text(text)

    # Compute similarity
    logits_per_image = (image_features @ text_features.T) * 100
    probs = logits_per_image.softmax(dim=-1).cpu().numpy()

print(f"Probabilities: {probs}")
```

[TRANSLATION_FAILED] ### ROS 2 Integration

```python
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import clip
import torch
from PIL import Image as PILImage
import numpy as np

class CLIPDetector(Node):
    def __init__(self):
        super().__init__('clip_detector')
        self.bridge = CvBridge()

        # Load CLIP
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model, self.preprocess = clip.load("ViT-B/32", device=self.device)

        # Subscribe to camera
        self.subscription = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.image_callback,
            10
        )

        # Objects to detect
        self.objects = ["a bottle", "a cup", "a laptop", "a phone"]
        self.text = clip.tokenize(self.objects).to(self.device)

    def image_callback(self, msg):
        # Convert ROS image to PIL
        cv_image = self.bridge.imgmsg_to_cv2(msg, "rgb8")
        pil_image = PILImage.fromarray(cv_image)

        # Preprocess
        image = self.preprocess(pil_image).unsqueeze(0).to(self.device)

        # Detect
        with torch.no_grad():
            image_features = self.model.encode_image(image)
            text_features = self.model.encode_text(self.text)

            similarity = (image_features @ text_features.T).softmax(dim=-1)
            values, indices = similarity[0].topk(3)

        # Log top 3 detections
        for value, index in zip(values, indices):
            self.get_logger().info(
                f"{self.objects[index]}: {value.item():.2%}"
            )
```

[TRANSLATION_FAILED] ## Open-Vocabulary Object Detection

[TRANSLATION_FAILED] Use CLIP for custom object queries:

```python
class OpenVocabularyDetector(Node):
    def __init__(self):
        super().__init__('ov_detector')

        # CLIP setup
        self.device = "cuda"
        self.model, self.preprocess = clip.load("ViT-L/14", device=self.device)

        # Service for custom queries
        self.srv = self.create_service(
            DetectObjects,
            'detect_objects',
            self.detect_callback
        )

    def detect_callback(self, request, response):
        # request.query_objects = ["red apple", "blue mug", ...]

        # Get latest image
        image = self.get_latest_image()

        # Tokenize queries
        text = clip.tokenize(request.query_objects).to(self.device)

        with torch.no_grad():
            image_features = self.model.encode_image(image)
            text_features = self.model.encode_text(text)
            similarity = (image_features @ text_features.T).softmax(dim=-1)

        # Return detections
        response.objects = request.query_objects
        response.confidences = similarity[0].cpu().numpy().tolist()

        return response
```

[TRANSLATION_FAILED] ## LLaVA: Visual Question Answering

[TRANSLATION_FAILED] **LLaVA** combines vision encoder (CLIP) with LLaMA for VQA.

[TRANSLATION_FAILED] ### Installation

```bash
# Clone LLaVA
git clone https://github.com/haotian-liu/LLaVA.git
cd LLaVA

# Install
pip install -e .
pip install transformers accelerate
```

[TRANSLATION_FAILED] ### Inference

```python
from llava.model.builder import load_pretrained_model
from llava.mm_utils import get_model_name_from_path, process_images, tokenizer_image_token
from llava.constants import IMAGE_TOKEN_INDEX
from PIL import Image
import torch

# Load model
model_path = "liuhaotian/llava-v1.6-mistral-7b"
tokenizer, model, image_processor, context_len = load_pretrained_model(
    model_path, None, get_model_name_from_path(model_path)
)

# Load image
image = Image.open("robot_view.jpg")
images_tensor = process_images([image], image_processor, model.config).to(model.device)

# Question
prompt = "What objects are on the table? List them."
input_ids = tokenizer_image_token(prompt, tokenizer, IMAGE_TOKEN_INDEX).unsqueeze(0).to(model.device)

# Generate answer
with torch.no_grad():
    output_ids = model.generate(
        input_ids,
        images=images_tensor,
        max_new_tokens=512,
        use_cache=True
    )

output = tokenizer.decode(output_ids[0], skip_special_tokens=True)
print(f"Answer: {output}")
```

[TRANSLATION_FAILED] ### ROS 2 VQA Service

```python
class VQAService(Node):
    def __init__(self):
        super().__init__('vqa_service')

        # Load LLaVA
        self.tokenizer, self.model, self.image_processor, _ = load_pretrained_model(
            "liuhaotian/llava-v1.6-mistral-7b", None, "llava-v1.6-mistral-7b"
        )

        # Service
        self.srv = self.create_service(
            AskQuestion,
            'ask_question',
            self.answer_callback
        )

    def answer_callback(self, request, response):
        # request.question = "What is the robot holding?"
        # request.image = Image message

        # Convert image
        cv_image = self.bridge.imgmsg_to_cv2(request.image, "rgb8")
        pil_image = PILImage.fromarray(cv_image)

        # Process
        images_tensor = process_images([pil_image], self.image_processor, self.model.config)

        # Generate answer
        input_ids = tokenizer_image_token(request.question, self.tokenizer, IMAGE_TOKEN_INDEX).unsqueeze(0)

        with torch.no_grad():
            output_ids = self.model.generate(input_ids, images=images_tensor, max_new_tokens=256)

        answer = self.tokenizer.decode(output_ids[0], skip_special_tokens=True)
        response.answer = answer

        return response
```

[TRANSLATION_FAILED] ## RT-2: Vision-Language-Action Model

[TRANSLATION_FAILED] **RT-2** directly outputs robot actions from vision and language.

[TRANSLATION_FAILED] ### Conceptual Architecture

```python
# Simplified RT-2 structure
class RT2Policy:
    def __init__(self):
        self.vision_encoder = CLIPVisionModel()  # Vision backbone
        self.language_model = T5Model()  # Language + action decoder

    def predict_action(self, image, instruction):
        # Encode image
        image_features = self.vision_encoder(image)

        # Encode instruction
        text_features = self.language_model.encode(instruction)

        # Decode action (tokenized)
        action_tokens = self.language_model.decode(
            image_features + text_features
        )

        # Convert tokens to continuous actions
        action = self.detokenize(action_tokens)
        return action  # [x, y, z, gripper]
```

[TRANSLATION_FAILED] ### Mock RT-2 Integration

[TRANSLATION_FAILED] Since RT-2 is not open-source, here's a pattern:

```python
class VLAController(Node):
    def __init__(self):
        super().__init__('vla_controller')

        # Vision
        self.clip_model, self.preprocess = clip.load("ViT-L/14")

        # Language (use GPT-4 API or local LLM)
        self.llm = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        # Action mapping
        self.action_primitives = {
            "pick": self.pick_object,
            "place": self.place_object,
            "navigate": self.navigate_to,
        }

    def execute_instruction(self, instruction, image):
        # 1. Understand instruction with LLM
        response = self.llm.chat.completions.create(
            model="gpt-4",
            messages=[{
                "role": "user",
                "content": f"Parse this robot instruction into action: '{instruction}'"
            }]
        )
        action_plan = response.choices[0].message.content

        # 2. Detect objects with CLIP
        objects = self.detect_objects(image)

        # 3. Execute action primitive
        self.execute_action(action_plan, objects)

    def detect_objects(self, image):
        # CLIP object detection
        # ...
        return detected_objects

    def execute_action(self, plan, objects):
        # Map to low-level controls
        # ...
        pass
```

[TRANSLATION_FAILED] ## Complete Example: Object Fetch Task

```python
class ObjectFetcher(Node):
    def __init__(self):
        super().__init__('object_fetcher')

        # CLIP for detection
        self.clip_model, self.preprocess = clip.load("ViT-B/32")

        # Navigation client
        self.nav_client = ActionClient(self, NavigateToPose, 'navigate_to_pose')

        # Image subscriber
        self.subscription = self.create_subscription(Image, '/camera/image_raw', self.image_callback, 10)
        self.latest_image = None

    def fetch_object(self, object_name):
        # 1. Detect object
        self.get_logger().info(f'Looking for {object_name}')
        obj_location = self.detect_object(object_name)

        if obj_location is None:
            self.get_logger().warn('Object not found')
            return

        # 2. Navigate to object
        self.get_logger().info('Navigating to object')
        self.navigate_to(obj_location)

        # 3. Grasp (simplified)
        self.get_logger().info('Grasping object')
        self.grasp()

    def detect_object(self, object_name):
        # Use CLIP to find object
        text = clip.tokenize([object_name])

        with torch.no_grad():
            image_features = self.clip_model.encode_image(self.latest_image)
            text_features = self.clip_model.encode_text(text)
            similarity = (image_features @ text_features.T)

        if similarity > 0.25:  # Threshold
            return self.estimate_3d_location()
        return None
```

[TRANSLATION_FAILED] ## Summary

[TRANSLATION_FAILED] This week you learned:

[TRANSLATION_FAILED] - VLA paradigm: Vision + Language + Action
[TRANSLATION_FAILED] - CLIP for zero-shot object detection
[TRANSLATION_FAILED] - LLaVA for visual question answering
[TRANSLATION_FAILED] - RT-2 architecture concepts
[TRANSLATION_FAILED] - Integrating VLMs with ROS 2
[TRANSLATION_FAILED] - Complete object fetching pipeline

[TRANSLATION_FAILED] ## What's Next?

[TRANSLATION_FAILED] **Week 11: Voice-to-Action with Whisper** - Add speech recognition for natural language robot control.

[TRANSLATION_FAILED] **Next**: [Week 11: Voice Control →](./week11-voice.md)
