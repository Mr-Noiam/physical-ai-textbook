# -*- coding: utf-8 -*-
import os

target_dir = "C:/Users/parep/Desktop/Hackathon1/book_hackathon/docusaurus/i18n/ur/docusaurus-plugin-content-docs/current/module-4-vla"
os.makedirs(target_dir, exist_ok=True)

week10_path = os.path.join(target_dir, "week10-vla-intro.md")
with open(week10_path, 'w', encoding='utf-8') as f:
    f.write("# ہفتہ 10: Vision-Language-Action کا ملاپ\n")
print(f"Created {week10_path}")
