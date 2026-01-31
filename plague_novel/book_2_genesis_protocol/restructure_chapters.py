#!/usr/bin/env python3
"""
Script to restructure Book 2 manuscript:
1. Delete Chapter 14 (THE EXTRACTION TEAM)
2. Reorder remaining chapters chronologically
3. Renumber all chapters sequentially
"""

import re

# Read the manuscript
with open('BOOK_2_REVISION_v11.md', 'r', encoding='utf-8') as f:
    content = f.read()

# Split into sections based on chapter headings
# Pattern matches: # PROLOGUE, # CHAPTER N, # APPENDIX
chapter_pattern = r'^(# (?:PROLOGUE|CHAPTER|APPENDIX).*?)$'
splits = re.split(chapter_pattern, content, flags=re.MULTILINE)

# Extract sections
sections = {}
current_heading = None
header = splits[0]  # Everything before PROLOGUE

for i in range(1, len(splits), 2):
    if i+1 < len(splits):
        heading = splits[i].strip()
        body = splits[i+1]

        # Determine section key
        if 'PROLOGUE' in heading:
            sections['PROLOGUE'] = (heading, body)
        elif 'APPENDIX' in heading:
            sections['APPENDIX'] = (heading, body)
        elif 'CHAPTER' in heading:
            # Extract chapter number
            match = re.search(r'CHAPTER\s+(\d+)', heading)
            if match:
                ch_num = int(match.group(1))
                sections[f'CH{ch_num}'] = (heading, body)

# Print what we found
print(f"Found {len(sections)} sections:")
for key in sorted(sections.keys()):
    heading, body = sections[key]
    print(f"  {key}: {heading[:60]}")

# Delete Chapter 14
if 'CH14' in sections:
    print("\nDeleting CH14: THE EXTRACTION TEAM")
    del sections['CH14']

# Define the new order according to the restructuring plan
# Current → New Position mapping
reorder_map = {
    'PROLOGUE': 'PROLOGUE',
    'CH1': 1,   # Keep
    'CH2': 2,   # Keep
    'CH3': 3,   # Keep
    'CH4': 4,   # Keep
    'CH8': 5,   # Coffee and Timelines → Ch 5
    'CH12': 6,  # Morrison's Crisis → Ch 6
    'CH6': 7,   # The Inside Game → Ch 7
    'CH11': 8,  # Quantum Mechanics → Ch 8
    'CH7': 9,   # The Offer → Ch 9
    'CH9': 10,  # The Almost Kiss → Ch 10
    'CH10': 11, # The External War → Ch 11
    'CH15': 12, # The Defector → Ch 12
    'CH5': 13,  # The Fragmentation → Ch 13
    'CH13': 14, # The Convergence → Ch 14
    'CH16': 15, # The Impossible Choice → Ch 15
    'CH18': 16, # David's Letter → Ch 16
    'CH17': 17, # The Breakout → Ch 17
    'CH19': 18, # Victory → Ch 18
    'CH20': 19, # The Cost of Choices → Ch 19
    'CH21': 20, # The Trial → Ch 20
    'APPENDIX': 'APPENDIX'
}

# Reconstruct the manuscript in new order
output = header

# Add PROLOGUE
if 'PROLOGUE' in sections:
    heading, body = sections['PROLOGUE']
    output += heading + '\n' + body

# Create reverse mapping: new_num -> old_key
new_to_old = {}
for old_key, new_num in reorder_map.items():
    if old_key not in ['PROLOGUE', 'APPENDIX']:
        new_to_old[new_num] = old_key

# Add chapters in new numerical order (1, 2, 3, ...)
for new_num in sorted(new_to_old.keys()):
    old_key = new_to_old[new_num]

    if old_key in sections:
        heading, body = sections[old_key]

        # Extract the title (everything after the dash or colon)
        title_match = re.search(r'CHAPTER\s+\d+\s*[-:]\s*(.+)$', heading)
        if title_match:
            title = title_match.group(1).strip()
            # Create new heading with correct chapter number
            new_heading = f'# CHAPTER {new_num} - {title}'
        else:
            # Fallback if pattern doesn't match
            new_heading = f'# CHAPTER {new_num}'

        output += new_heading + '\n' + body
        print(f"Mapped {old_key} → Chapter {new_num}: {title if title_match else 'No title'}")

# Add APPENDIX
if 'APPENDIX' in sections:
    heading, body = sections['APPENDIX']
    output += heading + '\n' + body

# Write the restructured manuscript
output_file = 'BOOK_2_REVISION_v12.md'
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(output)

print(f"\nRestructured manuscript written to: {output_file}")
print(f"Original line count: {len(content.splitlines())}")
print(f"New line count: {len(output.splitlines())}")
