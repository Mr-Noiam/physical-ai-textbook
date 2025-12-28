from pathlib import Path

# Read file
input_file = Path('../docusaurus/docs/module-1-ros2/week1-intro.md')
with open(input_file, 'r', encoding='utf-8') as f:
    content = f.read()

print(f'Total file size: {len(content)} chars')

# Split frontmatter
parts = content.split('---', 2)
if len(parts) >= 3 and content.startswith('---'):
    frontmatter = f"---{parts[1]}---"
    main_content = parts[2]
else:
    main_content = content

# Count lines
lines = main_content.split('\n')
print(f'Total lines in main content: {len(lines)}')
print(f'Main content size: {len(main_content)} chars')

# Simulate buffer logic
text_buffer = []
chunk_num = 0

for i, line in enumerate(lines):
    # Check for code blocks
    if line.strip().startswith('```'):
        if text_buffer:
            buffer_size = sum(len(l) for l in text_buffer)
            chunk_num += 1
            print(f'Chunk {chunk_num} (before code block): {len(text_buffer)} lines, {buffer_size} chars')
            text_buffer.clear()
        continue

    # Skip empty lines
    if not line.strip():
        if text_buffer:
            buffer_size = sum(len(l) for l in text_buffer)
            chunk_num += 1
            print(f'Chunk {chunk_num} (at empty line {i}): {len(text_buffer)} lines, {buffer_size} chars')
            text_buffer.clear()
        continue

    # Skip markdown syntax
    if all(c in '-*_= ' for c in line.strip()):
        if text_buffer:
            buffer_size = sum(len(l) for l in text_buffer)
            chunk_num += 1
            print(f'Chunk {chunk_num} (at syntax line {i}): {len(text_buffer)} lines, {buffer_size} chars')
            text_buffer.clear()
        continue

    # Add to buffer
    text_buffer.append(line)

    # Check if should flush
    buffer_size = sum(len(l) for l in text_buffer)
    if len(text_buffer) >= 15 or buffer_size > 3000:
        chunk_num += 1
        print(f'Chunk {chunk_num} (at line {i}): {len(text_buffer)} lines, {buffer_size} chars - FLUSH!')
        text_buffer.clear()

# Final flush
if text_buffer:
    buffer_size = sum(len(l) for l in text_buffer)
    chunk_num += 1
    print(f'Chunk {chunk_num} (final): {len(text_buffer)} lines, {buffer_size} chars')

print(f'\nTotal chunks: {chunk_num}')
