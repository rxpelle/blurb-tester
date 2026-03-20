"""Shared test fixtures for series-bible-generator."""

import os
import tempfile
from pathlib import Path

import pytest

from series_bible_generator.config import Config


@pytest.fixture
def tmp_dir():
    """Create a temporary directory for test data."""
    with tempfile.TemporaryDirectory() as d:
        yield Path(d)


@pytest.fixture
def config(tmp_dir):
    """Create a test config with temp data directory."""
    return Config(
        anthropic_api_key=None,
        data_dir=tmp_dir / "data",
    )


@pytest.fixture
def config_with_db(config):
    """Config with initialized database."""
    from series_bible_generator.db import get_connection
    conn = get_connection(config)
    conn.close()
    return config


@pytest.fixture
def sample_bloodline_md(tmp_dir):
    """Create a sample bloodline tracker file."""
    content = """# GENESIS PROTOCOL SERIES BIBLE
## BLOODLINE TRACKER: Tausret → Sarah (112 Generations, 3,208 Years)

**Purpose:** Track defensive Protocol carrier bloodline

---

## BLOODLINE OVERVIEW

**Total Span:** 1189 BCE → 2019 CE (3,208 years)
**Total Generations:** 112 generations

---

### **Generation 1: Pharaoh Tausret (Twosret)**
**Dates:** ~1191-1189 BCE
**Role:** Last pharaoh of 19th Dynasty

---

### **Generation 2: Tausret's Daughter**
**Dates:** ~1189-1120 BCE
**Role:** First carrier

---

### **Generation 42: Jesus of Nazareth**
**Dates:** ~4 BCE-30 CE
**Role:** Unique carrier - accessed Protocol without key
"""
    path = tmp_dir / "SERIES_BIBLE_bloodline_tracker.md"
    path.write_text(content)
    return path


@pytest.fixture
def sample_timeline_md(tmp_dir):
    """Create a sample timeline file."""
    content = """# GENESIS PROTOCOL SERIES BIBLE
## MASTER TIMELINE: 1189 BCE → 2100 CE

**Purpose:** Central continuity reference

---

## ERA 1: BRONZE AGE

### **Chapter 1: The Physician's Witness (1189 BCE)**

**Location:** Pi-Ramesses, Egypt

**Key Characters:**
- **Tausret:** Last pharaoh of 19th Dynasty
- **Nefertari:** Physician, defensive Protocol creator
- **Amenhotep:** Scholar, offensive Protocol creator

### **Chapter 2: The Split (1188 BCE)**

**Location:** Memphis, Egypt

Nefertari creates seven bronze keys.

## ERA 2: ROMAN WORLD

### **The Nazarene Connection (28 CE)**

**Location:** Judea

**Jesus** accesses genetic memory without key.
"""
    path = tmp_dir / "SERIES_BIBLE_master_timeline.md"
    path.write_text(content)
    return path


@pytest.fixture
def sample_terminology_md(tmp_dir):
    """Create a sample terminology glossary."""
    content = """# GENESIS PROTOCOL SERIES BIBLE
## TERMINOLOGY GLOSSARY

---

### **Genesis Protocol**
**Definition:** Genetic memory encoding system created by Nefertari in 1188 BCE

**Consistent Usage:**
- "Genesis Protocol" (capitalized)
- "the Protocol" (capitalized P)

**NEVER:**
- "genesis program"
- "protocol system"

- **Book 3:** Show creation
- **Book 1:** Thomas finds corruption

---

### **The Order**
**Definition:** Offensive network's institutional form

**Consistent Usage:**
- "the Order" (capital O)

**NEVER:**
- "The ORDER"
- "the order"

---

### **Defensive Mode**
**Definition:** Genesis Protocol's original purpose
"""
    path = tmp_dir / "SERIES_BIBLE_terminology_glossary.md"
    path.write_text(content)
    return path


@pytest.fixture
def sample_keys_md(tmp_dir):
    """Create a sample seven keys tracker."""
    content = """# GENESIS PROTOCOL SERIES BIBLE
## SEVEN KEYS MOVEMENT LOG

---

## DEFENSIVE KEYS

### **DEFENSIVE KEY 1: "The Living Key"**
**Description:** "The flesh made cipher, memory in blood"
**Function:** Authentication, proves carrier legitimacy

### **DEFENSIVE KEY 2: "The Scholar's Map"**
**Description:** Bronze tablet with encoded locations
**Function:** Reveals hidden caches

## OFFENSIVE KEYS

### **OFFENSIVE KEY 1: "The Breeding Ledger"**
**Description:** Genealogical records of controlled bloodlines
**Function:** Track and manage breeding programs
"""
    path = tmp_dir / "SERIES_BIBLE_seven_keys_tracker.md"
    path.write_text(content)
    return path


@pytest.fixture
def sample_bible_dir(tmp_dir, sample_bloodline_md, sample_timeline_md,
                     sample_terminology_md, sample_keys_md):
    """Directory containing all sample bible files."""
    return tmp_dir


@pytest.fixture
def sample_manuscript_dir(tmp_dir):
    """Create a sample manuscript directory with chapters."""
    ms_dir = tmp_dir / "manuscript"
    ms_dir.mkdir()

    ch1 = """# Chapter 1: The Physician's Witness

Nefertari pressed her fingers against Tausret's wrist, searching for the pulse that had already stopped. The pharaoh was dead. Outside the palace walls, the Sea Peoples' ships darkened the horizon like a second coastline.

"The Order will come for us," Amenhotep said from the doorway. His voice was steady, but his left hand reached across the empty space between them.

Nefertari stood. "Then we make sure they find nothing worth taking."

The Genesis Protocol had to survive. Not the offensive version Amenhotep wanted—control through collapse—but the defensive truth: that patterns could be read, that civilizations need not fall.

She gathered the seven bronze keys from the workbench, each one inscribed with her careful hieroglyphics. Four for the defensive network. Three she would never see again.

"Do that again," Amenhotep whispered, watching her hands.

"There's no time," she said, but her breathing had already synced with his.
"""

    ch2 = """# Chapter 2: The Split

Six months after Tausret's death, the genesis protocol was complete. Nefertari encoded the defensive mode into the bloodline—pattern recognition, systems thinking, the ability to see collapse before it arrived.

Amenhotep encoded something else entirely. His offensive Protocol didn't prevent collapse. It survived it. Controlled it. Used it.

"You've corrupted everything we built," Nefertari said.

"I've ensured we survive," he answered. "Your way—distributing knowledge, trusting the many—it's naive."

She placed the Living Key—herself, her blood, the first of seven—into the hands of Tausret's daughter. The girl was twelve. The weight of 3,000 years of memory settled onto shoulders that didn't yet understand what they carried.
"""

    (ms_dir / "chapter_01.md").write_text(ch1)
    (ms_dir / "chapter_02.md").write_text(ch2)
    return ms_dir


@pytest.fixture
def sample_manuscript_with_issues(tmp_dir):
    """Manuscript with deliberate bible violations."""
    ms_dir = tmp_dir / "bad_manuscript"
    ms_dir.mkdir()

    ch = """# Chapter 1: TODO Fix Title

The genesis program activated. Nefertari had created the order's system long ago.

PLACEHOLDER text here. TBD on the details.

The ORDER sent their agents to find the protocol system. It was hidden in the order's vault.
"""
    (ms_dir / "chapter_01.md").write_text(ch)
    return ms_dir
