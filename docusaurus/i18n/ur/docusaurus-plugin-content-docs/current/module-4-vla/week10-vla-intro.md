# ہفتہ 10: وژن-لینگویج-ایکشن کنورجنس

## تعارف

**وژن-لینگویج-ایکشن (VLA)** ماڈلز کمپیوٹر وژن، قدرتی زبان کی پروسیسنگ، اور روبوٹ کنٹرول کے سنگم کی نمائندگی کرتے ہیں۔ اس ہفتے، آپ سیکھیں گے کہ CLIP، LLaVA، اور RT-2 جیسے ماڈلز کس طرح ہیومنائڈز کو بصری مناظر کو سمجھنے، احکامات کی تشریح کرنے، اور کاموں کو انجام دینے کے قابل بناتے ہیں۔

## VLA پیراڈائم

```
┌──────────┐    ┌──────────┐    ┌──────────────┐
│  وژن    │───>│  زبان   │───>│    ایکشن      │
│  (CLIP)  │    │  (LLM)   │    │ (پالیسیاں)   │
└──────────┘    └──────────┘    └──────────────┘
     ▲                                   │
     │           فیڈ بیک لوپ           │
     └───────────────────────────────────┘
```

**اجزاء**:
- **وژن انکوڈر**: CLIP, DINOv2, MAE
- **لینگویج ماڈل**: GPT-4, LLaMA, PaLM
- **ایکشن ڈیکوڈر**: ڈیفیوژن پالیسیاں، ٹرانسفارمرز
- **ایمباڈیڈ ریزننگ**: چین آف تھاٹ، پلاننگ

## زیرو شاٹ آبجیکٹ ریکگنیشن کے لیے CLIP

**CLIP** (کنٹراسٹو لینگویج-امیج پری ٹریننگ) تصاویر اور متن کو ایک مشترکہ ایمبیڈنگ اسپیس میں میپ کرتا ہے۔

### انسٹالیشن

```bash
pip install openai-clip torch torchvision
```

### بنیادی استعمال

```python
import torch
import clip
from PIL import Image

# ماڈل لوڈ کریں
device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load("ViT-B/32", device=device)

# تصویر لوڈ کریں
image = preprocess(Image.open("robot_view.jpg")).unsqueeze(0).to(device)

# ٹیکسٹ پرامپٹس
text = clip.tokenize(["a cup", "a chair", "a person"]).to(device)

# فیچرز کا حساب لگائیں
with torch.no_grad():
    image_features = model.encode_image(image)
    text_features = model.encode_text(text)

    # مماثلت کا حساب لگائیں
    logits_per_image = (image_features @ text_features.T) * 100
    probs = logits_per_image.softmax(dim=-1).cpu().numpy()

print(f"احتمالات: {probs}")
```

### ROS 2 انضمام

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

        # CLIP لوڈ کریں
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model, self.preprocess = clip.load("ViT-B/32", device=self.device)

        # کیمرہ کو سبسکرائب کریں
        self.subscription = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.image_callback,
            10
        )

        # پتہ لگانے کے لیے اشیاء
        self.objects = ["a bottle", "a cup", "a laptop", "a phone"]
        self.text = clip.tokenize(self.objects).to(self.device)

    def image_callback(self, msg):
        # ROS تصویر کو PIL میں تبدیل کریں
        cv_image = self.bridge.imgmsg_to_cv2(msg, "rgb8")
        pil_image = PILImage.fromarray(cv_image)

        # پری پروسیس
        image = self.preprocess(pil_image).unsqueeze(0).to(self.device)

        # پتہ لگائیں
        with torch.no_grad():
            image_features = self.model.encode_image(image)
            text_features = self.model.encode_text(self.text)

            similarity = (image_features @ text_features.T).softmax(dim=-1)
            values, indices = similarity[0].topk(3)

        # ٹاپ 3 پتہ لگائے گئے اشیاء کو لاگ کریں
        for value, index in zip(values, indices):
            self.get_logger().info(
                f"{self.objects[index]}: {value.item():.2%}"
            )
```

## اوپن وکیبلری آبجیکٹ ڈیٹیکشن

کسٹم آبجیکٹ سوالات کے لیے CLIP استعمال کریں:

```python
class OpenVocabularyDetector(Node):
    def __init__(self):
        super().__init__('ov_detector')

        # CLIP سیٹ اپ
        self.device = "cuda"
        self.model, self.preprocess = clip.load("ViT-L/14", device=self.device)

        # کسٹم سوالات کے لیے سروس
        self.srv = self.create_service(
            DetectObjects,
            'detect_objects',
            self.detect_callback
        )

    def detect_callback(self, request, response):
        # request.query_objects = ["red apple", "blue mug", ...]

        # تازہ ترین تصویر حاصل کریں
        image = self.get_latest_image()

        # سوالات کو ٹوکنائز کریں
        text = clip.tokenize(request.query_objects).to(self.device)

        with torch.no_grad():
            image_features = self.model.encode_image(image)
            text_features = self.model.encode_text(text)
            similarity = (image_features @ text_features.T).softmax(dim=-1)

        # پتہ لگائے گئے اشیاء کو واپس کریں
        response.objects = request.query_objects
        response.confidences = similarity[0].cpu().numpy().tolist()

        return response
```

## LLaVA: بصری سوالات کے جوابات

**LLaVA** VQA کے لیے LLaMA کے ساتھ وژن انکوڈر (CLIP) کو جوڑتا ہے۔

### انسٹالیشن

```bash
# LLaVA کلون کریں
git clone https://github.com/haotian-liu/LLaVA.git
cd LLaVA

# انسٹال کریں
pip install -e .
pip install transformers accelerate
```

### انفرنس

```python
from llava.model.builder import load_pretrained_model
from llava.mm_utils import get_model_name_from_path, process_images, tokenizer_image_token
from llava.constants import IMAGE_TOKEN_INDEX
from PIL import Image
import torch

# ماڈل لوڈ کریں
model_path = "liuhaotian/llava-v1.6-mistral-7b"
tokenizer, model, image_processor, context_len = load_pretrained_model(
    model_path, None, get_model_name_from_path(model_path)
)

# تصویر لوڈ کریں
image = Image.open("robot_view.jpg")
images_tensor = process_images([image], image_processor, model.config).to(model.device)

# سوال
prompt = "میز پر کون سی اشیاء ہیں؟ ان کی فہرست بنائیں۔"
input_ids = tokenizer_image_token(prompt, tokenizer, IMAGE_TOKEN_INDEX).unsqueeze(0).to(model.device)

# جواب تیار کریں
with torch.no_grad():
    output_ids = model.generate(
        input_ids,
        images=images_tensor,
        max_new_tokens=512,
        use_cache=True
    )

output = tokenizer.decode(output_ids[0], skip_special_tokens=True)
print(f"جواب: {output}")
```

### ROS 2 VQA سروس

```python
class VQAService(Node):
    def __init__(self):
        super().__init__('vqa_service')

        # LLaVA لوڈ کریں
        self.tokenizer, self.model, self.image_processor, _ = load_pretrained_model(
            "liuhaotian/llava-v1.6-mistral-7b", None, "llava-v1.6-mistral-7b"
        )

        # سروس
        self.srv = self.create_service(
            AskQuestion,
            'ask_question',
            self.answer_callback
        )

    def answer_callback(self, request, response):
        # request.question = "روبوٹ کیا پکڑے ہوئے ہے؟"
        # request.image = تصویر کا پیغام

        # تصویر کو تبدیل کریں
        cv_image = self.bridge.imgmsg_to_cv2(request.image, "rgb8")
        pil_image = PILImage.fromarray(cv_image)

        # پراسیس کریں
        images_tensor = process_images([pil_image], self.image_processor, self.model.config)

        # جواب تیار کریں
        input_ids = tokenizer_image_token(request.question, self.tokenizer, IMAGE_TOKEN_INDEX).unsqueeze(0)

        with torch.no_grad():
            output_ids = self.model.generate(input_ids, images=images_tensor, max_new_tokens=256)

        answer = self.tokenizer.decode(output_ids[0], skip_special_tokens=True)
        response.answer = answer

        return response
```

## RT-2: وژن-لینگویج-ایکشن ماڈل

**RT-2** براہ راست وژن اور زبان سے روبوٹ کے اعمال آؤٹ پٹ کرتا ہے۔

### تصوراتی فن تعمیر

```python
# سادہ RT-2 ساخت
class RT2Policy:
    def __init__(self):
        self.vision_encoder = CLIPVisionModel()  # وژن بیک بون
        self.language_model = T5Model()  # زبان + ایکشن ڈیکوڈر

    def predict_action(self, image, instruction):
        # تصویر کو انکوڈ کریں
        image_features = self.vision_encoder(image)

        # ہدایت کو انکوڈ کریں
        text_features = self.language_model.encode(instruction)

        # ایکشن کو ڈیکوڈ کریں (ٹوکنائزڈ)
        action_tokens = self.language_model.decode(
            image_features + text_features
        )

        # ٹوکنز کو مسلسل اعمال میں تبدیل کریں
        action = self.detokenize(action_tokens)
        return action  # [x, y, z, gripper]
```

### موک RT-2 انضمام

چونکہ RT-2 اوپن سورس نہیں ہے، یہاں ایک پیٹرن ہے:

```python
class VLAController(Node):
    def __init__(self):
        super().__init__('vla_controller')

        # وژن
        self.clip_model, self.preprocess = clip.load("ViT-L/14")

        # زبان (GPT-4 API یا مقامی LLM استعمال کریں)
        self.llm = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        # ایکشن میپنگ
        self.action_primitives = {
            "pick": self.pick_object,
            "place": self.place_object,
            "navigate": self.navigate_to,
        }

    def execute_instruction(self, instruction, image):
        # 1. LLM کے ساتھ ہدایت کو سمجھیں
        response = self.llm.chat.completions.create(
            model="gpt-4",
            messages=[{
                "role": "user",
                "content": f"اس روبوٹ ہدایت کو ایکشن میں پارس کریں: '{instruction}'"
            }]
        )
        action_plan = response.choices[0].message.content

        # 2. CLIP کے ساتھ اشیاء کا پتہ لگائیں
        objects = self.detect_objects(image)

        # 3. ایکشن پریمیٹیو کو انجام دیں
        self.execute_action(action_plan, objects)

    def detect_objects(self, image):
        # CLIP آبجیکٹ ڈیٹیکشن
        # ...
        return detected_objects

    def execute_action(self, plan, objects):
        # نچلی سطح کے کنٹرولز پر میپ کریں
        # ...
        pass
```

## مکمل مثال: آبجیکٹ فیچ ٹاسک

```python
class ObjectFetcher(Node):
    def __init__(self):
        super().__init__('object_fetcher')

        # پتہ لگانے کے لیے CLIP
        self.clip_model, self.preprocess = clip.load("ViT-B/32")

        # نیویگیشن کلائنٹ
        self.nav_client = ActionClient(self, NavigateToPose, 'navigate_to_pose')

        # امیج سبسکرائبر
        self.subscription = self.create_subscription(Image, '/camera/image_raw', self.image_callback, 10)
        self.latest_image = None

    def fetch_object(self, object_name):
        # 1. آبجیکٹ کا پتہ لگائیں
        self.get_logger().info(f'{object_name} کی تلاش ہے')
        obj_location = self.detect_object(object_name)

        if obj_location is None:
            self.get_logger().warn('آبجیکٹ نہیں ملا')
            return

        # 2. آبجیکٹ پر نیویگیٹ کریں
        self.get_logger().info('آبجیکٹ پر نیویگیٹ کر رہا ہے')
        self.navigate_to(obj_location)

        # 3. پکڑنا (سادہ)
        self.get_logger().info('آبجیکٹ پکڑ رہا ہے')
        self.grasp()

    def detect_object(self, object_name):
        # آبجیکٹ تلاش کرنے کے لیے CLIP استعمال کریں
        text = clip.tokenize([object_name])

        with torch.no_grad():
            image_features = self.clip_model.encode_image(self.latest_image)
            text_features = self.clip_model.encode_text(text)
            similarity = (image_features @ text_features.T)

        if similarity > 0.25:  # حد
            return self.estimate_3d_location()
        return None
```

## خلاصہ

اس ہفتے آپ نے سیکھا:

- VLA پیراڈائم: وژن + زبان + ایکشن
- زیرو شاٹ آبجیکٹ ڈیٹیکشن کے لیے CLIP
- بصری سوالات کے جوابات کے لیے LLaVA
- RT-2 فن تعمیر کے تصورات
- VLMs کو ROS 2 کے ساتھ مربوط کرنا
- مکمل آبجیکٹ فیچنگ پائپ لائن

## آگے کیا ہے؟

**ہفتہ 11: وسپر کے ساتھ وائس ٹو ایکشن** - قدرتی زبان روبوٹ کنٹرول کے لیے اسپیچ ریکگنیشن شامل کریں۔

**آگے**: [ہفتہ 11: وائس کنٹرول →](./week11-voice.md)