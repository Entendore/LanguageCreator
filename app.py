#!/usr/bin/env python3
"""
Conlang Creator — A Language Construction Learning App
Built with PySide6
"""

import sys
import json
import random
import os
from datetime import datetime

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QStackedWidget, QPushButton, QLabel, QLineEdit, QTextEdit,
    QComboBox, QCheckBox, QTableWidget, QTableWidgetItem,
    QTabWidget, QGroupBox, QScrollArea, QGridLayout,
    QListWidget, QListWidgetItem, QFileDialog, QMessageBox,
    QSpinBox, QHeaderView, QFrame, QSizePolicy, QSplitter,
    QDialog, QDialogButtonBox, QFormLayout
)
from PySide6.QtCore import Qt, QSize, Signal, Slot
from PySide6.QtGui import (
    QFont, QColor, QPalette, QPixmap, QPainter,
    QLinearGradient, QAction, QKeySequence, QShortcut
)

# ─── IPA DATA ───────────────────────────────────────────────────────────────

CONSONANT_PLACES = [
    "Bilabial", "Labiod.", "Dental", "Alveolar",
    "Post-alv.", "Retroflex", "Palatal", "Velar", "Uvular", "Glottal"
]
CONSONANT_MANNERS = [
    "Plosive", "Nasal", "Trill", "Tap/Flap",
    "Fricative", "Lat. Fric.", "Approx.", "Lat. Approx."
]

# (manner_idx, place_idx): [(symbol, name, voiced), ...]
CONSONANT_DATA = {
    (0,0):[("p","vl bilabial plosive",False),("b","vd bilabial plosive",True)],
    (0,3):[("t","vl alveolar plosive",False),("d","vd alveolar plosive",True)],
    (0,5):[("ʈ","vl retroflex plosive",False),("ɖ","vd retroflex plosive",True)],
    (0,6):[("c","vl palatal plosive",False),("ɟ","vd palatal plosive",True)],
    (0,7):[("k","vl velar plosive",False),("ɡ","vd velar plosive",True)],
    (0,8):[("q","vl uvular plosive",False),("ɢ","vd uvular plosive",True)],
    (0,9):[("ʔ","glottal stop",False)],
    (1,0):[("m","bilabial nasal",True)],
    (1,3):[("n","alveolar nasal",True)],
    (1,5):[("ɳ","retroflex nasal",True)],
    (1,6):[("ɲ","palatal nasal",True)],
    (1,7):[("ŋ","velar nasal",True)],
    (1,8):[("ɴ","uvular nasal",True)],
    (2,0):[("ʙ","bilabial trill",True)],
    (2,3):[("r","alveolar trill",True)],
    (2,8):[("ʀ","uvular trill",True)],
    (3,3):[("ɾ","alveolar tap",True)],
    (3,5):[("ɽ","retroflex flap",True)],
    (4,0):[("ɸ","vl bilabial fricative",False),("β","vd bilabial fricative",True)],
    (4,1):[("f","vl labiodental fricative",False),("v","vd labiodental fricative",True)],
    (4,2):[("θ","vl dental fricative",False),("ð","vd dental fricative",True)],
    (4,3):[("s","vl alveolar fricative",False),("z","vd alveolar fricative",True)],
    (4,4):[("ʃ","vl post-alveolar fricative",False),("ʒ","vd post-alveolar fricative",True)],
    (4,5):[("ʂ","vl retroflex fricative",False),("ʐ","vd retroflex fricative",True)],
    (4,6):[("ç","vl palatal fricative",False),("ʝ","vd palatal fricative",True)],
    (4,7):[("x","vl velar fricative",False),("ɣ","vd velar fricative",True)],
    (4,8):[("χ","vl uvular fricative",False),("ʁ","vd uvular fricative",True)],
    (4,9):[("h","vl glottal fricative",False),("ɦ","vd glottal fricative",True)],
    (5,3):[("ɬ","vl lat alveolar fricative",False),("ɮ","vd lat alveolar fricative",True)],
    (6,3):[("ɹ","alveolar approximant",True)],
    (6,5):[("ɻ","retroflex approximant",True)],
    (6,6):[("j","palatal approximant",True)],
    (6,7):[("ɰ","velar approximant",True)],
    (7,3):[("l","alveolar lat approximant",True)],
    (7,5):[("ɭ","retroflex lat approximant",True)],
    (7,6):[("ʎ","palatal lat approximant",True)],
    (7,7):[("ʟ","velar lat approximant",True)],
}

VOWEL_HEIGHTS = ["Close", "Near-close", "Close-mid", "Mid", "Open-mid", "Near-open", "Open"]
VOWEL_BACKNESSES = ["Front", "Central", "Back"]

# (height_idx, backness_idx): [(symbol, name, rounded), ...]
VOWEL_DATA = {
    (0,0):[("i","close front unrounded",False),("y","close front rounded",True)],
    (0,1):[("ɨ","close central unrounded",False),("ʉ","close central rounded",True)],
    (0,2):[("ɯ","close back unrounded",False),("u","close back rounded",True)],
    (1,0):[("ɪ","near-close front unrounded",False),("ʏ","near-close front rounded",True)],
    (1,1):[("ɨ̞","near-close central unrounded",False),("ʉ̞","near-close central rounded",True)],
    (1,2):[("ʊ","near-close back rounded",True)],
    (2,0):[("e","close-mid front unrounded",False),("ø","close-mid front rounded",True)],
    (2,1):[("ɘ","close-mid central unrounded",False),("ɵ","close-mid central rounded",True)],
    (2,2):[("ɤ","close-mid back unrounded",False),("o","close-mid back rounded",True)],
    (3,1):[("ə","mid central schwa",False)],
    (4,0):[("ɛ","open-mid front unrounded",False),("œ","open-mid front rounded",True)],
    (4,1):[("ɜ","open-mid central unrounded",False),("ɞ","open-mid central rounded",True)],
    (4,2):[("ʌ","open-mid back unrounded",False),("ɔ","open-mid back rounded",True)],
    (5,0):[("æ","near-open front unrounded",False)],
    (5,1):[("ɐ","near-open central unrounded",False)],
    (6,0):[("a","open front unrounded",False),("ɶ","open front rounded",True)],
    (6,2):[("ɑ","open back unrounded",False),("ɒ","open back rounded",True)],
}

# ─── LESSONS DATA ───────────────────────────────────────────────────────────

LESSONS = [
    {
        "title": "1. Introduction to Conlanging",
        "content": """
<h2>What is a Constructed Language?</h2>
<p>A <b>constructed language</b> (or <b>conlang</b>) is a language whose phonology,
grammar, and vocabulary have been consciously devised rather than evolved naturally.</p>

<h3>Famous Conlangs</h3>
<ul>
<li><b>Tolkien's Elvish languages</b> (Quenya, Sindarin) — created for his legendarium</li>
<li><b>Klingon</b> — created for Star Trek by Marc Okrand</li>
<li><b>Dothraki & Valyrian</b> — created for Game of Thrones by David Peterson</li>
<li><b>Esperanto</b> — created by L.L. Zamenhof as an international auxiliary language</li>
<li><b>Na'vi</b> — created for Avatar by Paul Frommer</li>
<li><b>Lojban</b> — a logical language designed to remove ambiguity</li>
</ul>

<h3>Types of Conlangs</h3>
<ul>
<li><b>Artistic (Artlang)</b> — for fiction, worldbuilding, or aesthetic pleasure</li>
<li><b>Engineered (Engelang)</b> — to test linguistic hypotheses (e.g., Lojban)</li>
<li><b>Auxiliary (Auxlang)</b> — for international communication (e.g., Esperanto)</li>
<li><b>Personal (Pervolang)</b> — for private use or self-expression</li>
</ul>

<h3>The Language Construction Toolkit</h3>
<p>This app guides you through the major components of language design:</p>
<ol>
<li><b>Phonology</b> — the sound system</li>
<li><b>Grammar/Morphology</b> — how words are formed and combined</li>
<li><b>Syntax</b> — how sentences are structured</li>
<li><b>Lexicon</b> — the vocabulary</li>
<li><b>Writing System</b> — how the language is written</li>
</ol>

<p>Each section includes interactive tools and educational explanations.
Let's start building!</p>
"""
    },
    {
        "title": "2. Phonetics & Phonology",
        "content": """
<h2>Understanding Sound Systems</h2>
<p><b>Phonetics</b> studies the physical properties of speech sounds.
<b>Phonology</b> studies how sounds function within a particular language.</p>

<h3>Consonants</h3>
<p>Consonants are produced with some obstruction of the airstream.
They are described by three features:</p>
<ul>
<li><b>Place of articulation</b> — where in the mouth the sound is made
  (e.g., bilabial = both lips, alveolar = tongue on the alveolar ridge)</li>
<li><b>Manner of articulation</b> — how the airstream is modified
  (e.g., plosive = complete closure, fricative = narrow gap causing turbulence)</li>
<li><b>Voicing</b> — whether the vocal cords vibrate
  (e.g., /s/ is voiceless, /z/ is voiced)</li>
</ul>

<h3>Vowels</h3>
<p>Vowels are produced with a relatively open vocal tract.
They are described by:</p>
<ul>
<li><b>Height</b> — how high/low the tongue is (close → open)</li>
<li><b>Backness</b> — how far forward/back the tongue is (front → back)</li>
<li><b>Rounding</b> — whether the lips are rounded</li>
</ul>

<h3>Designing Your Phonology</h3>
<p>When selecting sounds for your conlang, consider:</p>
<ul>
<li><b>Naturalness</b> — most natural languages have 20-40 consonants and 5-10 vowels</li>
<li><b>Symmetry</b> — sound inventories tend to be balanced (e.g., if you have /p/, /t/, /k/,
  you probably also have /b/, /d/, /ɡ/)</li>
<li><b>Aesthetics</b> — what sounds fit the "feel" of your conlang?</li>
</ul>

<p>Use the <b>Phonology tab</b> to select sounds from the IPA charts!</p>
"""
    },
    {
        "title": "3. Syllable Structure & Phonotactics",
        "content": """
<h2>Building Syllables</h2>
<p><b>Phonotactics</b> are the rules governing how sounds can be combined in a language.</p>

<h3>Syllable Structure</h3>
<p>Every syllable has an <b>onset</b> (initial consonant(s)), a <b>nucleus</b> (vowel),
and a <b>coda</b> (final consonant(s)). We write:</p>
<ul>
<li><b>V</b> — vowel only (e.g., Japanese <i>a-i</i>)</li>
<li><b>CV</b> — consonant-vowel (e.g., Japanese, Hawaiian — very common)</li>
<li><b>CVC</b> — consonant-vowel-consonant (e.g., English <i>cat</i>)</li>
<li><b>CCV</b> — consonant cluster + vowel (e.g., English <i>stop</i>)</li>
<li><b>CCVCC</b> — complex (e.g., English <i>strength</i>)</li>
</ul>

<h3>Consonant Clusters</h3>
<p>Languages differ wildly in what clusters they allow:</p>
<ul>
<li><b>Hawaiian</b> allows no clusters at all (only CV, V)</li>
<li><b>Japanese</b> allows limited clusters via gemination</li>
<li><b>English</b> allows up to 3 consonants in onset, 4 in coda</li>
<li><b>Georgian</b> allows famous mega-clusters like <i>mcvrtneli</i></li>
</ul>

<h3>Tips for Your Conlang</h3>
<ul>
<li>Simpler syllable structures sound more "melodic" (CV — think Hawaiian, Japanese)</li>
<li>Complex structures sound "heavier" (CCVCC — think Georgian, Slavic languages)</li>
<li>Restricting codas gives a more "open" feel</li>
<li>Allowing many clusters gives a more "dense" feel</li>
</ul>
"""
    },
    {
        "title": "4. Morphology — Word Formation",
        "content": """
<h2>How Words Are Built</h2>
<p><b>Morphology</b> is the study of how words are formed from smaller meaningful
units called <b>morphemes</b>.</p>

<h3>Morphological Typology</h3>
<p>Languages fall on a spectrum:</p>
<ul>
<li><b>Isolating</b> — one morpheme per word (e.g., Mandarin Chinese, Vietnamese)
  <br>Words don't change form; grammar is expressed through word order and particles.</li>
<li><b>Agglutinative</b> — many morphemes, each with a clear meaning, stacked together
  <br>(e.g., Turkish, Finnish, Swahili, Japanese)
  <br>Turkish <i>ev-ler-iniz-den</i> = "house-PL-your-FROM" = "from your houses"</li>
<li><b>Fusional</b> — morphemes are fused together; one ending carries multiple meanings
  <br>(e.g., Latin, Russian, Spanish)
  <br>Latin <i>amō</i> = "I love" (1st person + singular + present + active — all in one suffix)</li>
<li><b>Polysynthetic</b> — extremely long words encoding entire sentences
  <br>(e.g., Inuktitut, Mohawk)
  <br>Inuktitut <i>tusaatsiarunnanngittualuujunga</i> = "I cannot hear very well"</li>
</ul>

<h3>Common Morphological Processes</h3>
<ul>
<li><b>Prefixation</b> — adding to the beginning (un-happy)</li>
<li><b>Suffixation</b> — adding to the end (walk-ed)</li>
<li><b>Infixation</b> — inserting inside (Tagalog <i>um-</i> inside verb roots)</li>
<li><b>Reduplication</b> — repeating part of the word (Indonesian <i>anak-anak</i> = "children")</li>
<li><b>Apophony/Ablaut</b> — vowel change (sing → sang → sung)</li>
<li><b>Suprasegmental</b> — tone, stress, or length changes</li>
</ul>

<p>Use the <b>Grammar tab</b> to define your conlang's morphological type!</p>
"""
    },
    {
        "title": "5. Syntax — Sentence Structure",
        "content": """
<h2>Word Order & Sentence Structure</h2>
<p><b>Syntax</b> is how words combine to form phrases and sentences.</p>

<h3>Basic Word Orders</h3>
<p>Every language has a dominant order for Subject (S), Verb (V), and Object (O):</p>
<table border="1" cellpadding="4">
<tr><th>Order</th><th>Frequency</th><th>Example Languages</th></tr>
<tr><td>SOV</td><td>~45%</td><td>Turkish, Japanese, Korean, Hindi</td></tr>
<tr><td>SVO</td><td>~42%</td><td>English, Mandarin, French, Swahili</td></tr>
<tr><td>VSO</td><td>~9%</td><td>Arabic, Welsh, Irish, Tagalog</td></tr>
<tr><td>VOS</td><td>~3%</td><td>Malagasy, Fijian</td></tr>
<tr><td>OVS</td><td>&lt;1%</td><td>Hixkaryana, Carib languages</td></tr>
<tr><td>OSV</td><td>&lt;1%</td><td>Warao, Nadëb</td></tr>
</table>

<h3>Other Syntactic Features</h3>
<ul>
<li><b>Adjective order</b> — before or after the noun?
  (English: "red car" vs. French: "voiture rouge")</li>
<li><b>Adposition type</b> — prepositions (English "in the house")
  vs. postpositions (Japanese "家で" = "house-in")</li>
<li><b>Question formation</b> — word order change? Question particles? Intonation?</li>
<li><b>Negation</b> — where does "not" go? Double negation?</li>
<li><b>Relative clauses</b> — how are "the man who..." structures formed?</li>
</ul>

<h3>Design Tips</h3>
<ul>
<li>SOV and SVO together cover ~87% of languages — they feel most "natural"</li>
<li>OSV and OVS are extremely rare — they'll make your conlang feel alien</li>
<li>Word order correlates with other features (e.g., SOV → postpositions, SVO → prepositions)</li>
</ul>
"""
    },
    {
        "title": "6. Building a Lexicon",
        "content": """
<h2>Creating Vocabulary</h2>
<p>The <b>lexicon</b> is the heart of your language — its word inventory.</p>

<h3>Semantic Domains</h3>
<p>Start with core vocabulary in these domains:</p>
<ul>
<li><b>Body parts</b> — head, hand, eye, mouth, etc.</li>
<li><b>Natural world</b> — sun, moon, water, fire, earth, sky</li>
<li><b>Basic actions</b> — go, come, eat, drink, see, say, give</li>
<li><b>Descriptors</b> — big, small, good, bad, hot, cold</li>
<li><b>Pronouns</b> — I, you, he/she/it, we, they</li>
<li><b>Numbers</b> — one through ten</li>
<li><b>Kinship</b> — mother, father, child, sibling</li>
</ul>

<h3>Strategies for Word Creation</h3>
<ul>
<li><b>From sound symbolism</b> — words whose sound suggests their meaning
  (e.g., "mama" for mother — common across languages because it's easy to babble)</li>
<li><b>From compounding</b> — combine existing words
  (German: Handschuh = "hand-shoe" = glove)</li>
<li><b>From derivation</b> — apply affixes to existing roots
  (English: teach → teacher → teaching)</li>
<li><b>From metaphor</b> — extend meaning of existing words
  (French: "ordinateur" from "ordonner" = to order/command)</li>
<li><b>Borrowing</b> — take words from other languages (very common in real languages)</li>
</ul>

<h3>Using the Word Generator</h3>
<p>The Lexicon tab includes a <b>word generator</b> that creates random words
following your phonology rules. This is great for:</p>
<ul>
<li>Getting inspiration when you're stuck</li>
<li>Filling out large vocabulary lists quickly</li>
<li>Ensuring words are phonotactically valid</li>
</ul>
"""
    },
    {
        "title": "7. Writing Systems",
        "content": """
<h2>Designing a Script</h2>
<p>A <b>writing system</b> is a method of visually representing language.</p>

<h3>Types of Writing Systems</h3>
<ul>
<li><b>Alphabet</b> — each symbol represents a consonant or vowel
  (Latin, Greek, Cyrillic)</li>
<li><b>Abjad</b> — symbols for consonants; vowels mostly omitted
  (Arabic, Hebrew)</li>
<li><b>Abugida</b> — consonant symbols with inherent vowels; vowel marks modify them
  (Devanagari, Ge'ez, Thai)</li>
<li><b>Syllabary</b> — each symbol represents a full syllable
  (Japanese kana, Cherokee)</li>
<li><b>Logographic</b> — each symbol represents a word or morpheme
  (Chinese characters, Egyptian hieroglyphs)</li>
<li><b>Featural</b> — symbol shapes encode phonetic features
  (Korean Hangul)</li>
</ul>

<h3>Design Considerations</h3>
<ul>
<li><b>Direction</b> — left-to-right, right-to-left, top-to-bottom, boustrophedon?</li>
<li><b>Stroke complexity</b> — simple (Latin) vs. complex (Chinese)</li>
<li><b>Consistency</b> — do similar sounds have similar-looking symbols?</li>
<li><b>Aesthetic</b> — angular (runic), curved (Arabic), geometric (Hangul)?</li>
<li><b>History</b> — was it carved? Written with a brush? Typed?</li>
</ul>

<h3>Using the Script Tab</h3>
<p>In the Script tab, you can assign custom characters to each phoneme
in your inventory. Type or paste Unicode characters, or use the
character picker to find symbols that match your aesthetic.</p>

<p>Tip: For a realistic-feeling script, maintain visual consistency —
similar sounds should have related-looking characters.</p>
"""
    },
    {
        "title": "8. Language Evolution & Realism",
        "content": """
<h2>Making Your Conlang Feel Real</h2>
<p>Natural languages are messy. Adding some irregularity makes your conlang
feel more authentic.</p>

<h3>Historical Sound Changes</h3>
<p>Real languages evolve through systematic sound changes:</p>
<ul>
<li><b>Lenition</b> — consonants weaken (p → b → β → ∅)</li>
<li><b>Assimilation</b> — sounds become more like neighbors (np → mp)</li>
<li><b>Metathesis</b> — sounds swap (aks → ask)</li>
<li><b>Grammaticalization</b> — content words become function words
  (Latin <i>habere</i> "to have" → Romance future tense suffix)</li>
</ul>

<h3>Irregularity</h3>
<ul>
<li>The most common words tend to be the most irregular (cf. English "go/went")</li>
<li>Older layers of the language may preserve archaic forms</li>
<li>Borrowed words may not follow all the rules</li>
</ul>

<h3>Semantic Shift</h3>
<p>Word meanings drift over time:</p>
<ul>
<li>English "silly" went from "blessed" → "happy" → "foolish"</li>
<li>French "chef" = "head" → "boss" → English borrowing "chef" (cook)</li>
</ul>

<h3>Registers & Dialects</h3>
<ul>
<li>Formal vs. informal speech</li>
<li>Male vs. female speech patterns (Japanese)</li>
<li>Regional dialects</li>
<li>Special vocabularies (slang, jargon, ritual language)</li>
</ul>

<h3>Final Tips</h3>
<ul>
<li>Don't try to create a "perfect" language — natural languages are full of quirks</li>
<li>Keep notes on <i>why</i> you made each decision</li>
<li>Test your language by translating texts</li>
<li>Be patient — real languages evolve over millennia!</li>
</ul>
"""
    },
]

# ─── STYLESHEET ─────────────────────────────────────────────────────────────

STYLESHEET = """
QMainWindow { background: #f0f2f5; }
QWidget { font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif; font-size: 13px; }

/* Sidebar */
#sidebar { background: #1a1a2e; border-right: 2px solid #16213e; }
#sidebar QPushButton {
    color: #a0a4b8; text-align: left; padding: 12px 18px;
    border: none; border-radius: 0px; font-size: 13px; font-weight: 500;
}
#sidebar QPushButton:hover { background: #16213e; color: #e0e0e0; }
#sidebar QPushButton:checked { background: #0f3460; color: #ffffff; border-left: 3px solid #e94560; }
#sidebar QLabel { color: #e94560; font-size: 16px; font-weight: 700; padding: 16px 18px 8px 18px; }

/* Pages */
QLabel#pageTitle { font-size: 22px; font-weight: 700; color: #1a1a2e; padding: 4px 0; }
QLabel#pageSubtitle { font-size: 13px; color: #666; padding-bottom: 12px; }

/* GroupBox */
QGroupBox { font-weight: 600; border: 1px solid #ddd; border-radius: 8px;
    margin-top: 12px; padding: 16px 12px 12px 12px; background: #fff; }
QGroupBox::title { subcontrol-origin: margin; left: 14px; padding: 0 6px; color: #1a1a2e; }

/* Phoneme buttons */
PhonemeButton { min-width: 38px; min-height: 30px; border: 1px solid #ccc;
    border-radius: 4px; background: #f8f8f8; color: #333; font-size: 13px; }
PhonemeButton:checked { background: #0f3460; color: #fff; border-color: #0f3460; }
PhonemeButton:hover { border-color: #e94560; }

/* Tables */
QTableWidget { border: 1px solid #ddd; border-radius: 6px; background: #fff;
    gridline-color: #eee; selection-background-color: #0f3460; }
QTableWidget::item { padding: 4px 8px; }
QHeaderView::section { background: #1a1a2e; color: #fff; padding: 6px;
    border: none; font-weight: 600; }

/* Buttons */
QPushButton#primaryBtn { background: #e94560; color: #fff; border: none;
    border-radius: 6px; padding: 8px 20px; font-weight: 600; font-size: 13px; }
QPushButton#primaryBtn:hover { background: #c73850; }
QPushButton#secondaryBtn { background: #0f3460; color: #fff; border: none;
    border-radius: 6px; padding: 8px 20px; font-weight: 600; font-size: 13px; }
QPushButton#secondaryBtn:hover { background: #0a2744; }
QPushButton#dangerBtn { background: #dc3545; color: #fff; border: none;
    border-radius: 6px; padding: 8px 20px; font-weight: 600; font-size: 13px; }
QPushButton#dangerBtn:hover { background: #b02a37; }
QPushButton#smallBtn { background: #e9ecef; color: #333; border: none;
    border-radius: 4px; padding: 4px 12px; font-size: 12px; }
QPushButton#smallBtn:hover { background: #d0d3d8; }

/* Inputs */
QLineEdit, QTextEdit, QComboBox {
    border: 1px solid #ccc; border-radius: 6px; padding: 6px 10px; background: #fff; }
QLineEdit:focus, QTextEdit:focus { border-color: #0f3460; }
QComboBox::drop-down { border: none; }

/* Lists */
QListWidget { border: 1px solid #ddd; border-radius: 6px; background: #fff; padding: 4px; }
QListWidget::item { padding: 6px; border-radius: 4px; }
QListWidget::item:selected { background: #0f3460; color: #fff; }

/* Scroll */
QScrollArea { border: none; background: transparent; }

/* Info labels */
QLabel#infoBox { background: #e8f4fd; border: 1px solid #b8daff; border-radius: 6px;
    padding: 10px; color: #004085; font-size: 12px; }
QLabel#tipBox { background: #fff3cd; border: 1px solid #ffc107; border-radius: 6px;
    padding: 10px; color: #856404; font-size: 12px; }
"""

# ─── DATA MODEL ─────────────────────────────────────────────────────────────

class ConlangData:
    """Holds all data for a single conlang project."""

    def __init__(self):
        self.name = "New Conlang"
        self.description = ""
        self.consonants = []
        self.vowels = []
        self.syllable_structures = ["CV"]
        self.phonotactics_notes = ""
        self.morphological_type = "Agglutinative"
        self.word_order = "SVO"
        self.adjective_order = "Noun-Adjective"
        self.adposition_type = "Prepositions"
        self.cases = []
        self.tenses = []
        self.aspects = []
        self.moods = []
        self.grammar_rules = []
        self.lexicon = []
        self.script_mappings = {}
        self.example_sentences = []

    def to_dict(self):
        return {
            "name": self.name, "description": self.description,
            "consonants": self.consonants, "vowels": self.vowels,
            "syllable_structures": self.syllable_structures,
            "phonotactics_notes": self.phonotactics_notes,
            "morphological_type": self.morphological_type,
            "word_order": self.word_order,
            "adjective_order": self.adjective_order,
            "adposition_type": self.adposition_type,
            "cases": self.cases, "tenses": self.tenses,
            "aspects": self.aspects, "moods": self.moods,
            "grammar_rules": self.grammar_rules,
            "lexicon": self.lexicon,
            "script_mappings": self.script_mappings,
            "example_sentences": self.example_sentences,
        }

    @classmethod
    def from_dict(cls, d):
        obj = cls()
        for k, v in d.items():
            if hasattr(obj, k):
                setattr(obj, k, v)
        return obj

    def generate_word(self, num_syllables=None):
        """Generate a random word based on the current phonology."""
        if not self.vowels or not self.syllable_structures:
            return ""
        if not num_syllables:
            num_syllables = random.randint(1, 3)
        syllables = []
        for _ in range(num_syllables):
            pattern = random.choice(self.syllable_structures)
            syl = ""
            for ch in pattern:
                if ch == "C":
                    if self.consonants:
                        syl += random.choice(self.consonants)
                    else:
                        syl += ""
                elif ch == "V":
                    syl += random.choice(self.vowels)
            syllables.append(syl)
        return "".join(syllables)


# ─── CUSTOM WIDGETS ─────────────────────────────────────────────────────────

class PhonemeButton(QPushButton):
    """Toggle button for selecting a phoneme."""

    def __init__(self, symbol, name, parent=None):
        super().__init__(symbol, parent)
        self.symbol = symbol
        self.phoneme_name = name
        self.setCheckable(True)
        self.setFixedSize(42, 32)
        self.setToolTip(f"/{symbol}/ — {name}")
        self.setCursor(Qt.PointingHandCursor)


class AddItemDialog(QDialog):
    """Simple dialog to add an item with a name and optional description."""

    def __init__(self, title="Add Item", label="Name:", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumWidth(350)
        layout = QFormLayout(self)
        self.name_edit = QLineEdit()
        self.desc_edit = QLineEdit()
        layout.addRow(label, self.name_edit)
        layout.addRow("Description (optional):", self.desc_edit)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def get_values(self):
        return self.name_edit.text().strip(), self.desc_edit.text().strip()


# ─── OVERVIEW PAGE ──────────────────────────────────────────────────────────

class OverviewPage(QWidget):
    def __init__(self, data: ConlangData, parent=None):
        super().__init__(parent)
        self.data = data
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)

        lbl = QLabel("Project Overview")
        lbl.setObjectName("pageTitle")
        layout.addWidget(lbl)
        sub = QLabel("Set up your conlang's basic information and see a summary.")
        sub.setObjectName("pageSubtitle")
        layout.addWidget(sub)

        # Project info
        info_group = QGroupBox("Project Information")
        form = QFormLayout(info_group)
        self.name_edit = QLineEdit(self.data.name)
        self.name_edit.textChanged.connect(lambda t: setattr(self.data, 'name', t))
        form.addRow("Language Name:", self.name_edit)
        self.desc_edit = QTextEdit(self.data.description)
        self.desc_edit.setMaximumHeight(80)
        self.desc_edit.textChanged.connect(
            lambda: setattr(self.data, 'description', self.desc_edit.toPlainText()))
        form.addRow("Description:", self.desc_edit)
        layout.addWidget(info_group)

        # Summary
        self.summary_group = QGroupBox("Language Summary")
        self.summary_layout = QVBoxLayout(self.summary_group)
        self.summary_label = QLabel()
        self.summary_label.setWordWrap(True)
        self.summary_label.setTextFormat(Qt.RichText)
        self.summary_layout.addWidget(self.summary_label)
        layout.addWidget(self.summary_group)

        # Quick stats
        self.stats_group = QGroupBox("Quick Statistics")
        self.stats_layout = QGridLayout(self.stats_group)
        self.stat_labels = {}
        for i, (key, label) in enumerate([
            ("consonants", "Consonants"), ("vowels", "Vowels"),
            ("words", "Lexicon Size"), ("cases", "Cases"),
            ("tenses", "Tenses"), ("rules", "Grammar Rules")
        ]):
            lbl = QLabel(label)
            lbl.setStyleSheet("font-weight:600; color:#666;")
            val = QLabel("0")
            val.setStyleSheet("font-size:24px; font-weight:700; color:#0f3460;")
            self.stats_layout.addWidget(lbl, i // 3, (i % 3) * 2)
            self.stats_layout.addWidget(val, i // 3, (i % 3) * 2 + 1)
            self.stat_labels[key] = val
        layout.addWidget(self.stats_group)

        # Export button
        btn_layout = QHBoxLayout()
        export_btn = QPushButton("📄  Export Language Document")
        export_btn.setObjectName("primaryBtn")
        export_btn.clicked.connect(self.export_document)
        btn_layout.addWidget(export_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        layout.addStretch()
        self.refresh()

    def refresh(self):
        d = self.data
        self.name_edit.setText(d.name)
        self.desc_edit.setText(d.description)
        self.stat_labels["consonants"].setText(str(len(d.consonants)))
        self.stat_labels["vowels"].setText(str(len(d.vowels)))
        self.stat_labels["words"].setText(str(len(d.lexicon)))
        self.stat_labels["cases"].setText(str(len(d.cases)))
        self.stat_labels["tenses"].setText(str(len(d.tenses)))
        self.stat_labels["rules"].setText(str(len(d.grammar_rules)))

        self.summary_label.setText(
            f"<b>{d.name}</b><br>"
            f"Morphology: {d.morphological_type} | Word Order: {d.word_order}<br>"
            f"Consonants: {len(d.consonants)} | Vowels: {len(d.vowels)}<br>"
            f"Cases: {', '.join(d.cases) if d.cases else 'None defined'}<br>"
            f"Tenses: {', '.join(d.tenses) if d.tenses else 'None defined'}<br>"
            f"Aspects: {', '.join(d.aspects) if d.aspects else 'None defined'}<br>"
            f"Moods: {', '.join(d.moods) if d.moods else 'None defined'}<br>"
            f"Syllable patterns: {', '.join(d.syllable_structures)}"
        )

    def export_document(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Language Document", f"{self.data.name}.txt",
            "Text Files (*.txt);;All Files (*)")
        if not path:
            return
        d = self.data
        lines = [
            f"=== {d.name} ===",
            f"Description: {d.description}",
            "",
            "--- PHONOLOGY ---",
            f"Consonants ({len(d.consonants)}): {' '.join('/' + c + '/' for c in d.consonants)}",
            f"Vowels ({len(d.vowels)}): {' '.join('/' + v + '/' for v in d.vowels)}",
            f"Syllable Structures: {', '.join(d.syllable_structures)}",
            f"Phonotactics Notes: {d.phonotactics_notes}",
            "",
            "--- GRAMMAR ---",
            f"Morphological Type: {d.morphological_type}",
            f"Word Order: {d.word_order}",
            f"Adjective Order: {d.adjective_order}",
            f"Adpositions: {d.adposition_type}",
            f"Cases: {', '.join(d.cases) if d.cases else 'None'}",
            f"Tenses: {', '.join(d.tenses) if d.tenses else 'None'}",
            f"Aspects: {', '.join(d.aspects) if d.aspects else 'None'}",
            f"Moods: {', '.join(d.moods) if d.moods else 'None'}",
            "",
            "--- GRAMMAR RULES ---",
        ]
        for i, rule in enumerate(d.grammar_rules, 1):
            lines.append(f"  {i}. {rule}")
        lines.append("")
        lines.append("--- LEXICON ---")
        lines.append(f"{'Word':<20} {'Meaning':<20} {'POS':<12} {'Category':<12} {'Notes'}")
        lines.append("-" * 80)
        for entry in d.lexicon:
            lines.append(
                f"{entry.get('word',''):<20} {entry.get('meaning',''):<20} "
                f"{entry.get('pos',''):<12} {entry.get('category',''):<12} "
                f"{entry.get('notes','')}")
        lines.append("")
        lines.append("--- EXAMPLE SENTENCES ---")
        for s in d.example_sentences:
            lines.append(f"  {s.get('conlang','')} = {s.get('translation','')}")
            if s.get('notes'):
                lines.append(f"    ({s['notes']})")

        with open(path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        QMessageBox.information(self, "Export Complete",
                                f"Language document exported to:\n{path}")


# ─── PHONOLOGY PAGE ─────────────────────────────────────────────────────────

class PhonologyPage(QWidget):
    def __init__(self, data: ConlangData, parent=None):
        super().__init__(parent)
        self.data = data
        self.consonant_buttons = {}
        self.vowel_buttons = {}

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)

        lbl = QLabel("Phonology Builder")
        lbl.setObjectName("pageTitle")
        layout.addWidget(lbl)
        sub = QLabel("Select sounds from the IPA charts to build your conlang's phoneme inventory.")
        sub.setObjectName("pageSubtitle")
        layout.addWidget(sub)

        # Info box
        info = QLabel("💡 Click cells in the charts to toggle sounds on/off. "
                      "Selected sounds (dark blue) are part of your conlang's inventory.")
        info.setObjectName("infoBox")
        info.setWordWrap(True)
        layout.addWidget(info)

        # Tabs for consonants and vowels
        tabs = QTabWidget()

        # ── Consonant Chart ──
        cons_scroll = QScrollArea()
        cons_scroll.setWidgetResizable(True)
        cons_widget = QWidget()
        cons_layout = QGridLayout(cons_widget)
        cons_layout.setSpacing(2)

        # Header row — places
        cons_layout.addWidget(QLabel(""), 0, 0)
        for j, place in enumerate(CONSONANT_PLACES):
            lbl = QLabel(place)
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet("font-weight:700; font-size:11px; color:#0f3460; padding:4px 2px;")
            cons_layout.addWidget(lbl, 0, j + 1)

        # Rows — manners
        for i, manner in enumerate(CONSONANT_MANNERS):
            lbl = QLabel(manner)
            lbl.setStyleSheet("font-weight:600; font-size:11px; color:#1a1a2e; padding-right:8px;")
            lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            cons_layout.addWidget(lbl, i + 1, 0)

            for j in range(len(CONSONANT_PLACES)):
                key = (i, j)
                if key in CONSONANT_DATA:
                    cell_w = QWidget()
                    cell_l = QHBoxLayout(cell_w)
                    cell_l.setContentsMargins(1, 1, 1, 1)
                    cell_l.setSpacing(1)
                    for sym, name, voiced in CONSONANT_DATA[key]:
                        btn = PhonemeButton(sym, name)
                        btn.setChecked(sym in self.data.consonants)
                        btn.toggled.connect(lambda checked, s=sym: self._toggle_consonant(s, checked))
                        self.consonant_buttons[sym] = btn
                        cell_l.addWidget(btn)
                    cons_layout.addWidget(cell_w, i + 1, j + 1)

        cons_scroll.setWidget(cons_widget)
        tabs.addTab(cons_scroll, "Consonants")

        # ── Vowel Chart ──
        vow_scroll = QScrollArea()
        vow_scroll.setWidgetResizable(True)
        vow_widget = QWidget()
        vow_layout = QGridLayout(vow_widget)
        vow_layout.setSpacing(2)

        vow_layout.addWidget(QLabel(""), 0, 0)
        for j, backness in enumerate(VOWEL_BACKNESSES):
            lbl = QLabel(backness)
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet("font-weight:700; font-size:11px; color:#0f3460; padding:4px 2px;")
            vow_layout.addWidget(lbl, 0, j + 1)

        for i, height in enumerate(VOWEL_HEIGHTS):
            lbl = QLabel(height)
            lbl.setStyleSheet("font-weight:600; font-size:11px; color:#1a1a2e; padding-right:8px;")
            lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            vow_layout.addWidget(lbl, i + 1, 0)

            for j in range(len(VOWEL_BACKNESSES)):
                key = (i, j)
                if key in VOWEL_DATA:
                    cell_w = QWidget()
                    cell_l = QHBoxLayout(cell_w)
                    cell_l.setContentsMargins(1, 1, 1, 1)
                    cell_l.setSpacing(1)
                    for sym, name, rounded in VOWEL_DATA[key]:
                        btn = PhonemeButton(sym, name)
                        btn.setChecked(sym in self.data.vowels)
                        btn.toggled.connect(lambda checked, s=sym: self._toggle_vowel(s, checked))
                        self.vowel_buttons[sym] = btn
                        cell_l.addWidget(btn)
                    vow_layout.addWidget(cell_w, i + 1, j + 1)

        vow_scroll.setWidget(vow_widget)
        tabs.addTab(vow_scroll, "Vowels")

        layout.addWidget(tabs, stretch=1)

        # ── Syllable Structure ──
        syl_group = QGroupBox("Syllable Structure & Phonotactics")
        syl_layout = QVBoxLayout(syl_group)

        syl_top = QHBoxLayout()
        syl_top.addWidget(QLabel("Syllable patterns (C=Consonant, V=Vowel):"))
        self.syl_combo = QComboBox()
        self.syl_combo.setEditable(True)
        self.syl_combo.addItems(["V", "CV", "CVC", "CCV", "CCVC", "CVCC", "CCVCC"])
        self.syl_combo.currentTextChanged.connect(self._update_syllables)
        syl_top.addWidget(self.syl_combo)
        add_syl_btn = QPushButton("+ Add Pattern")
        add_syl_btn.setObjectName("smallBtn")
        add_syl_btn.clicked.connect(self._add_syllable_pattern)
        syl_top.addWidget(add_syl_btn)
        syl_top.addStretch()
        syl_layout.addLayout(syl_top)

        self.syl_list = QListWidget()
        self.syl_list.setMaximumHeight(80)
        self._refresh_syllable_list()
        syl_layout.addWidget(self.syl_list)

        syl_notes_layout = QHBoxLayout()
        syl_notes_layout.addWidget(QLabel("Phonotactics notes:"))
        self.phonotactics_edit = QTextEdit()
        self.phonotactics_edit.setMaximumHeight(60)
        self.phonotactics_edit.setPlaceholderText(
            "e.g., No consonant clusters word-initially. /ŋ/ only syllable-final...")
        self.phonotactics_edit.setText(self.data.phonotactics_notes)
        self.phonotactics_edit.textChanged.connect(
            lambda: setattr(self.data, 'phonotactics_notes', self.phonotactics_edit.toPlainText()))
        syl_notes_layout.addWidget(self.phonotactics_edit)
        syl_layout.addLayout(syl_notes_layout)

        layout.addWidget(syl_group)

        # ── Inventory summary ──
        self.inv_label = QLabel()
        self.inv_label.setWordWrap(True)
        self.inv_label.setStyleSheet(
            "background:#fff; border:1px solid #ddd; border-radius:6px; padding:10px;")
        layout.addWidget(self.inv_label)
        self._update_inventory_label()

    def _toggle_consonant(self, symbol, checked):
        if checked and symbol not in self.data.consonants:
            self.data.consonants.append(symbol)
        elif not checked and symbol in self.data.consonants:
            self.data.consonants.remove(symbol)
        self._update_inventory_label()

    def _toggle_vowel(self, symbol, checked):
        if checked and symbol not in self.data.vowels:
            self.data.vowels.append(symbol)
        elif not checked and symbol in self.data.vowels:
            self.data.vowels.remove(symbol)
        self._update_inventory_label()

    def _update_inventory_label(self):
        d = self.data
        self.inv_label.setText(
            f"<b>Inventory:</b> {len(d.consonants)} consonants, {len(d.vowels)} vowels, "
            f"{len(d.consonants) + len(d.vowels)} total phonemes<br>"
            f"<b>Consonants:</b> {' '.join(d.consonants) if d.consonants else 'None selected'}<br>"
            f"<b>Vowels:</b> {' '.join(d.vowels) if d.vowels else 'None selected'}"
        )

    def _add_syllable_pattern(self):
        text = self.syl_combo.currentText().strip().upper()
        if text and text not in self.data.syllable_structures:
            if all(c in 'CV' for c in text) and 'V' in text:
                self.data.syllable_structures.append(text)
                self._refresh_syllable_list()
            else:
                QMessageBox.warning(self, "Invalid Pattern",
                                    "Syllable patterns must use only 'C' and 'V', "
                                    "and contain at least one 'V'.")

    def _update_syllables(self, text):
        pass  # handled by add button

    def _refresh_syllable_list(self):
        self.syl_list.clear()
        for s in self.data.syllable_structures:
            item = QListWidgetItem(s)
            self.syl_list.addItem(item)

    def refresh(self):
        for sym, btn in self.consonant_buttons.items():
            btn.blockSignals(True)
            btn.setChecked(sym in self.data.consonants)
            btn.blockSignals(False)
        for sym, btn in self.vowel_buttons.items():
            btn.blockSignals(True)
            btn.setChecked(sym in self.data.vowels)
            btn.blockSignals(False)
        self.phonotactics_edit.setText(self.data.phonotactics_notes)
        self._refresh_syllable_list()
        self._update_inventory_label()


# ─── GRAMMAR PAGE ───────────────────────────────────────────────────────────

class GrammarPage(QWidget):
    def __init__(self, data: ConlangData, parent=None):
        super().__init__(parent)
        self.data = data
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)

        lbl = QLabel("Grammar Designer")
        lbl.setObjectName("pageTitle")
        layout.addWidget(lbl)
        sub = QLabel("Define your conlang's morphological type, word order, and grammatical categories.")
        sub.setObjectName("pageSubtitle")
        layout.addWidget(sub)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        clayout = QVBoxLayout(content)

        # ── Core Typology ──
        typo_group = QGroupBox("Core Typology")
        typo_form = QFormLayout(typo_group)

        self.morph_combo = QComboBox()
        self.morph_combo.addItems(["Isolating", "Agglutinative", "Fusional", "Polysynthetic"])
        self.morph_combo.setCurrentText(self.data.morphological_type)
        self.morph_combo.currentTextChanged.connect(
            lambda t: setattr(self.data, 'morphological_type', t))
        typo_form.addRow("Morphological Type:", self.morph_combo)

        self.order_combo = QComboBox()
        self.order_combo.addItems(["SVO", "SOV", "VSO", "VOS", "OVS", "OSV", "Free"])
        self.order_combo.setCurrentText(self.data.word_order)
        self.order_combo.currentTextChanged.connect(
            lambda t: setattr(self.data, 'word_order', t))
        typo_form.addRow("Word Order:", self.order_combo)

        self.adj_combo = QComboBox()
        self.adj_combo.addItems(["Noun-Adjective", "Adjective-Noun", "Both"])
        self.adj_combo.setCurrentText(self.data.adjective_order)
        self.adj_combo.currentTextChanged.connect(
            lambda t: setattr(self.data, 'adjective_order', t))
        typo_form.addRow("Adjective Position:", self.adj_combo)

        self.adp_combo = QComboBox()
        self.adp_combo.addItems(["Prepositions", "Postpositions", "Both", "None"])
        self.adp_combo.setCurrentText(self.data.adposition_type)
        self.adp_combo.currentTextChanged.connect(
            lambda t: setattr(self.data, 'adposition_type', t))
        typo_form.addRow("Adpositions:", self.adp_combo)

        clayout.addWidget(typo_group)

        # ── Grammatical Categories ──
        cats_group = QGroupBox("Grammatical Categories")
        cats_layout = QGridLayout(cats_group)

        self.cases_list = self._make_category_list(
            "Cases", self.data.cases, cats_layout, 0)
        self.tenses_list = self._make_category_list(
            "Tenses", self.data.tenses, cats_layout, 1)
        self.aspects_list = self._make_category_list(
            "Aspects", self.data.aspects, cats_layout, 2)
        self.moods_list = self._make_category_list(
            "Moods", self.data.moods, cats_layout, 3)

        clayout.addWidget(cats_group)

        # ── Grammar Rules ──
        rules_group = QGroupBox("Grammar Rules & Notes")
        rules_layout = QVBoxLayout(rules_group)

        rule_input_layout = QHBoxLayout()
        self.rule_edit = QLineEdit()
        self.rule_edit.setPlaceholderText("Enter a grammar rule or note...")
        rule_input_layout.addWidget(self.rule_edit)
        add_rule_btn = QPushButton("+ Add Rule")
        add_rule_btn.setObjectName("smallBtn")
        add_rule_btn.clicked.connect(self._add_rule)
        rule_input_layout.addWidget(add_rule_btn)
        rules_layout.addLayout(rule_input_layout)

        self.rules_table = QTableWidget(0, 2)
        self.rules_table.setHorizontalHeaderLabels(["Rule", ""])
        self.rules_table.horizontalHeader().setStretchLastSection(True)
        self.rules_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.rules_table.setMaximumHeight(200)
        rules_layout.addWidget(self.rules_table)
        self._refresh_rules()

        clayout.addWidget(rules_group)

        # ── Example Sentences ──
        sent_group = QGroupBox("Example Sentences")
        sent_layout = QVBoxLayout(sent_group)

        sent_input = QHBoxLayout()
        self.sent_conlang = QLineEdit()
        self.sent_conlang.setPlaceholderText("Conlang sentence")
        self.sent_translation = QLineEdit()
        self.sent_translation.setPlaceholderText("Translation")
        self.sent_notes = QLineEdit()
        self.sent_notes.setPlaceholderText("Notes (optional)")
        add_sent_btn = QPushButton("+ Add")
        add_sent_btn.setObjectName("smallBtn")
        add_sent_btn.clicked.connect(self._add_sentence)
        sent_input.addWidget(self.sent_conlang)
        sent_input.addWidget(self.sent_translation)
        sent_input.addWidget(self.sent_notes)
        sent_input.addWidget(add_sent_btn)
        sent_layout.addLayout(sent_input)

        self.sent_table = QTableWidget(0, 4)
        self.sent_table.setHorizontalHeaderLabels(["Conlang", "Translation", "Notes", ""])
        self.sent_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.sent_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.sent_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.sent_table.setMaximumHeight(180)
        sent_layout.addWidget(self.sent_table)
        self._refresh_sentences()

        clayout.addWidget(sent_group)
        clayout.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll, stretch=1)

    def _make_category_list(self, title, data_list, parent_layout, col):
        group = QWidget()
        vlayout = QVBoxLayout(group)
        vlayout.setContentsMargins(4, 4, 4, 4)
        header = QHBoxLayout()
        header.addWidget(QLabel(f"<b>{title}</b>"))
        add_btn = QPushButton("+")
        add_btn.setObjectName("smallBtn")
        add_btn.setFixedSize(28, 24)
        add_btn.clicked.connect(lambda _, dl=data_list: self._add_category_item(dl, lw))
        header.addWidget(add_btn)
        vlayout.addLayout(header)

        lw = QListWidget()
        lw.setMaximumHeight(140)
        for item in data_list:
            lw.addItem(item if isinstance(item, str) else item)
        lw.itemDoubleClicked.connect(lambda it, dl=data_list, l=lw: self._remove_category_item(it, dl, l))
        vlayout.addWidget(lw)

        tip = QLabel("Double-click to remove")
        tip.setStyleSheet("color:#999; font-size:10px;")
        vlayout.addWidget(tip)

        parent_layout.addWidget(group, 0, col)
        return lw

    def _add_category_item(self, data_list, list_widget):
        dialog = AddItemDialog(f"Add {list_widget.item(0).text() if list_widget.count() > 0 else 'Item'}",
                               "Name:", self)
        if dialog.exec() == QDialog.Accepted:
            name, desc = dialog.get_values()
            if name:
                data_list.append(name if not desc else f"{name} ({desc})")
                list_widget.addItem(name if not desc else f"{name} ({desc})")

    def _remove_category_item(self, item, data_list, list_widget):
        row = list_widget.row(item)
        if row >= 0:
            text = item.text()
            list_widget.takeItem(row)
            if text in data_list:
                data_list.remove(text)

    def _add_rule(self):
        text = self.rule_edit.text().strip()
        if text:
            self.data.grammar_rules.append(text)
            self.rule_edit.clear()
            self._refresh_rules()

    def _refresh_rules(self):
        self.rules_table.setRowCount(len(self.data.grammar_rules))
        for i, rule in enumerate(self.data.grammar_rules):
            self.rules_table.setItem(i, 0, QTableWidgetItem(rule))
            del_btn = QPushButton("✕")
            del_btn.setObjectName("dangerBtn")
            del_btn.setFixedSize(32, 24)
            del_btn.clicked.connect(lambda _, idx=i: self._remove_rule(idx))
            self.rules_table.setCellWidget(i, 1, del_btn)

    def _remove_rule(self, idx):
        if 0 <= idx < len(self.data.grammar_rules):
            self.data.grammar_rules.pop(idx)
            self._refresh_rules()

    def _add_sentence(self):
        cl = self.sent_conlang.text().strip()
        tr = self.sent_translation.text().strip()
        nt = self.sent_notes.text().strip()
        if cl and tr:
            self.data.example_sentences.append(
                {"conlang": cl, "translation": tr, "notes": nt})
            self.sent_conlang.clear()
            self.sent_translation.clear()
            self.sent_notes.clear()
            self._refresh_sentences()

    def _refresh_sentences(self):
        self.sent_table.setRowCount(len(self.data.example_sentences))
        for i, s in enumerate(self.data.example_sentences):
            self.sent_table.setItem(i, 0, QTableWidgetItem(s.get("conlang", "")))
            self.sent_table.setItem(i, 1, QTableWidgetItem(s.get("translation", "")))
            self.sent_table.setItem(i, 2, QTableWidgetItem(s.get("notes", "")))
            del_btn = QPushButton("✕")
            del_btn.setObjectName("dangerBtn")
            del_btn.setFixedSize(32, 24)
            del_btn.clicked.connect(lambda _, idx=i: self._remove_sentence(idx))
            self.sent_table.setCellWidget(i, 3, del_btn)

    def _remove_sentence(self, idx):
        if 0 <= idx < len(self.data.example_sentences):
            self.data.example_sentences.pop(idx)
            self._refresh_sentences()

    def refresh(self):
        self.morph_combo.setCurrentText(self.data.morphological_type)
        self.order_combo.setCurrentText(self.data.word_order)
        self.adj_combo.setCurrentText(self.data.adjective_order)
        self.adp_combo.setCurrentText(self.data.adposition_type)
        # Refresh category lists
        for lw, dl in [(self.cases_list, self.data.cases),
                       (self.tenses_list, self.data.tenses),
                       (self.aspects_list, self.data.aspects),
                       (self.moods_list, self.data.moods)]:
            lw.clear()
            for item in dl:
                lw.addItem(item if isinstance(item, str) else item)
        self._refresh_rules()
        self._refresh_sentences()


# ─── LEXICON PAGE ───────────────────────────────────────────────────────────

class LexiconPage(QWidget):
    def __init__(self, data: ConlangData, parent=None):
        super().__init__(parent)
        self.data = data
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)

        lbl = QLabel("Lexicon Manager")
        lbl.setObjectName("pageTitle")
        layout.addWidget(lbl)
        sub = QLabel("Build your conlang's vocabulary. Add words manually or generate them from your phonology.")
        sub.setObjectName("pageSubtitle")
        layout.addWidget(sub)

        # ── Add word section ──
        add_group = QGroupBox("Add Word")
        add_layout = QGridLayout(add_group)

        add_layout.addWidget(QLabel("Word:"), 0, 0)
        self.word_edit = QLineEdit()
        self.word_edit.setPlaceholderText("Conlang word")
        add_layout.addWidget(self.word_edit, 0, 1)

        add_layout.addWidget(QLabel("IPA:"), 0, 2)
        self.ipa_edit = QLineEdit()
        self.ipa_edit.setPlaceholderText("/ipa/")
        add_layout.addWidget(self.ipa_edit, 0, 3)

        add_layout.addWidget(QLabel("Meaning:"), 1, 0)
        self.meaning_edit = QLineEdit()
        self.meaning_edit.setPlaceholderText("English meaning")
        add_layout.addWidget(self.meaning_edit, 1, 1)

        add_layout.addWidget(QLabel("POS:"), 1, 2)
        self.pos_combo = QComboBox()
        self.pos_combo.setEditable(True)
        self.pos_combo.addItems([
            "Noun", "Verb", "Adjective", "Adverb", "Pronoun",
            "Preposition", "Conjunction", "Particle", "Numeral", "Other"
        ])
        add_layout.addWidget(self.pos_combo, 1, 3)

        add_layout.addWidget(QLabel("Category:"), 2, 0)
        self.cat_combo = QComboBox()
        self.cat_combo.setEditable(True)
        self.cat_combo.addItems([
            "General", "Body", "Nature", "Action", "Descriptor",
            "Pronoun", "Number", "Kinship", "Food", "Abstract", "Technical"
        ])
        add_layout.addWidget(self.cat_combo, 2, 1)

        add_layout.addWidget(QLabel("Notes:"), 2, 2)
        self.notes_edit = QLineEdit()
        self.notes_edit.setPlaceholderText("Optional notes")
        add_layout.addWidget(self.notes_edit, 2, 3)

        btn_row = QHBoxLayout()
        add_btn = QPushButton("➕ Add Word")
        add_btn.setObjectName("primaryBtn")
        add_btn.clicked.connect(self._add_word)
        btn_row.addWidget(add_btn)

        gen_btn = QPushButton("🎲 Generate Random Word")
        gen_btn.setObjectName("secondaryBtn")
        gen_btn.clicked.connect(self._generate_word)
        btn_row.addWidget(gen_btn)

        gen5_btn = QPushButton("🎲 Generate 5 Words")
        gen5_btn.setObjectName("secondaryBtn")
        gen5_btn.clicked.connect(lambda: self._generate_words(5))
        btn_row.addWidget(gen5_btn)

        btn_row.addStretch()
        add_layout.addLayout(btn_row, 3, 0, 1, 4)
        layout.addWidget(add_group)

        # ── Filter ──
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Filter:"))
        self.filter_edit = QLineEdit()
        self.filter_edit.setPlaceholderText("Search words or meanings...")
        self.filter_edit.textChanged.connect(self._filter_lexicon)
        filter_layout.addWidget(self.filter_edit)

        filter_layout.addWidget(QLabel("POS:"))
        self.filter_pos = QComboBox()
        self.filter_pos.addItem("All")
        self.filter_pos.addItems([
            "Noun", "Verb", "Adjective", "Adverb", "Pronoun",
            "Preposition", "Conjunction", "Particle", "Numeral", "Other"
        ])
        self.filter_pos.currentTextChanged.connect(self._filter_lexicon)
        filter_layout.addWidget(self.filter_pos)

        layout.addLayout(filter_layout)

        # ── Dictionary table ──
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(
            ["Word", "IPA", "Meaning", "POS", "Category", "Notes"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.DoubleClicked)
        self.table.cellChanged.connect(self._cell_edited)
        layout.addWidget(self.table, stretch=1)

        # ── Bottom buttons ──
        bottom = QHBoxLayout()
        del_btn = QPushButton("🗑 Delete Selected")
        del_btn.setObjectName("dangerBtn")
        del_btn.clicked.connect(self._delete_selected)
        bottom.addWidget(del_btn)

        count_label = QLabel()
        self.count_label = count_label
        count_label.setStyleSheet("color:#666; font-style:italic;")
        bottom.addWidget(count_label)
        bottom.addStretch()
        layout.addLayout(bottom)

        self._refresh_table()

    def _add_word(self):
        word = self.word_edit.text().strip()
        meaning = self.meaning_edit.text().strip()
        if not word or not meaning:
            QMessageBox.warning(self, "Missing Info", "Word and meaning are required.")
            return
        entry = {
            "word": word,
            "ipa": self.ipa_edit.text().strip(),
            "meaning": meaning,
            "pos": self.pos_combo.currentText(),
            "category": self.cat_combo.currentText(),
            "notes": self.notes_edit.text().strip(),
        }
        self.data.lexicon.append(entry)
        self.word_edit.clear()
        self.ipa_edit.clear()
        self.meaning_edit.clear()
        self.notes_edit.clear()
        self._refresh_table()

    def _generate_word(self):
        w = self.data.generate_word()
        if w:
            self.word_edit.setText(w)
            self.ipa_edit.setText("/" + w + "/")

    def _generate_words(self, n):
        generated = 0
        for _ in range(n * 3):  # try up to 3n times
            if generated >= n:
                break
            w = self.data.generate_word()
            if not w:
                break
            # Check not duplicate
            existing_words = [e["word"] for e in self.data.lexicon]
            if w not in existing_words:
                self.data.lexicon.append({
                    "word": w, "ipa": f"/{w}/",
                    "meaning": "(unassigned)", "pos": "Noun",
                    "category": "General", "notes": "auto-generated"
                })
                generated += 1
        self._refresh_table()
        if generated == 0:
            QMessageBox.information(self, "Cannot Generate",
                                    "Make sure you have selected consonants, vowels, "
                                    "and syllable structures in the Phonology tab.")

    def _refresh_table(self):
        self.table.blockSignals(True)
        self.table.setRowCount(len(self.data.lexicon))
        for i, entry in enumerate(self.data.lexicon):
            self.table.setItem(i, 0, QTableWidgetItem(entry.get("word", "")))
            self.table.setItem(i, 1, QTableWidgetItem(entry.get("ipa", "")))
            self.table.setItem(i, 2, QTableWidgetItem(entry.get("meaning", "")))
            self.table.setItem(i, 3, QTableWidgetItem(entry.get("pos", "")))
            self.table.setItem(i, 4, QTableWidgetItem(entry.get("category", "")))
            self.table.setItem(i, 5, QTableWidgetItem(entry.get("notes", "")))
        self.table.blockSignals(False)
        self.count_label.setText(f"{len(self.data.lexicon)} words")

    def _cell_edited(self, row, col):
        if 0 <= row < len(self.data.lexicon):
            keys = ["word", "ipa", "meaning", "pos", "category", "notes"]
            item = self.table.item(row, col)
            if item:
                self.data.lexicon[row][keys[col]] = item.text()

    def _delete_selected(self):
        rows = set(i.row() for i in self.table.selectedItems())
        if not rows:
            return
        for row in sorted(rows, reverse=True):
            if 0 <= row < len(self.data.lexicon):
                self.data.lexicon.pop(row)
        self._refresh_table()

    def _filter_lexicon(self):
        text = self.filter_edit.text().lower()
        pos = self.filter_pos.currentText()
        for i, entry in enumerate(self.data.lexicon):
            match_text = (text == "" or
                          text in entry.get("word", "").lower() or
                          text in entry.get("meaning", "").lower())
            match_pos = (pos == "All" or entry.get("pos", "") == pos)
            self.table.setRowHidden(i, not (match_text and match_pos))

    def refresh(self):
        self._refresh_table()


# ─── SCRIPT PAGE ────────────────────────────────────────────────────────────

class ScriptPage(QWidget):
    def __init__(self, data: ConlangData, parent=None):
        super().__init__(parent)
        self.data = data
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)

        lbl = QLabel("Script Designer")
        lbl.setObjectName("pageTitle")
        layout.addWidget(lbl)
        sub = QLabel("Map each phoneme to a custom character to create your writing system.")
        sub.setObjectName("pageSubtitle")
        layout.addWidget(sub)

        tip = QLabel("💡 Enter any Unicode character for each phoneme. "
                     "You can find Unicode symbols at unicode-table.com or use an IME.")
        tip.setObjectName("tipBox")
        tip.setWordWrap(True)
        layout.addWidget(tip)

        # Script type
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Script Type:"))
        self.script_type_combo = QComboBox()
        self.script_type_combo.addItems([
            "Alphabet", "Abjad", "Abugida", "Syllabary", "Logographic", "Featural"
        ])
        type_layout.addWidget(self.script_type_combo)
        type_layout.addWidget(QLabel("Direction:"))
        self.dir_combo = QComboBox()
        self.dir_combo.addItems(["Left-to-Right", "Right-to-Left", "Top-to-Bottom"])
        type_layout.addWidget(self.dir_combo)
        type_layout.addStretch()
        layout.addLayout(type_layout)

        # Mapping table
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Phoneme", "Custom Character", "Name"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        layout.addWidget(self.table, stretch=1)

        # Auto-fill button
        btn_layout = QHBoxLayout()
        autofill_btn = QPushButton("🔄 Auto-Fill from Phonology")
        autofill_btn.setObjectName("secondaryBtn")
        autofill_btn.clicked.connect(self._autofill)
        btn_layout.addWidget(autofill_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        # Preview
        preview_group = QGroupBox("Text Preview")
        preview_layout = QVBoxLayout(preview_group)
        self.preview_input = QLineEdit()
        self.preview_input.setPlaceholderText("Type IPA text to see it in your script...")
        self.preview_input.textChanged.connect(self._update_preview)
        preview_layout.addWidget(self.preview_input)
        self.preview_output = QLabel()
        self.preview_output.setStyleSheet(
            "font-size: 28px; padding: 16px; background: #fff; "
            "border: 1px solid #ddd; border-radius: 6px; min-height: 60px;")
        self.preview_output.setWordWrap(True)
        preview_layout.addWidget(self.preview_output)
        layout.addWidget(preview_group)

    def _autofill(self):
        all_phonemes = self.data.consonants + self.data.vowels
        existing = set()
        for i in range(self.table.rowCount()):
            p_item = self.table.item(i, 0)
            if p_item:
                existing.add(p_item.text())

        for p in all_phonemes:
            if p not in existing:
                row = self.table.rowCount()
                self.table.setRowCount(row + 1)
                self.table.setItem(row, 0, QTableWidgetItem(p))
                self.table.setItem(row, 1, QTableWidgetItem(""))
                self.table.setItem(row, 2, QTableWidgetItem(""))
                self.data.script_mappings[p] = ""
                existing.add(p)

    def _update_preview(self):
        text = self.preview_input.text()
        # Build mapping from table
        mapping = {}
        for i in range(self.table.rowCount()):
            p_item = self.table.item(i, 0)
            c_item = self.table.item(i, 1)
            if p_item and c_item and c_item.text():
                mapping[p_item.text()] = c_item.text()
                self.data.script_mappings[p_item.text()] = c_item.text()

        result = ""
        i = 0
        while i < len(text):
            matched = False
            for length in range(min(3, len(text) - i), 0, -1):
                substr = text[i:i + length]
                if substr in mapping:
                    result += mapping[substr]
                    i += length
                    matched = True
                    break
            if not matched:
                result += text[i]
                i += 1
        self.preview_output.setText(result if result else "<i>Enter IPA text above to preview</i>")

    def refresh(self):
        self.table.setRowCount(0)
        all_phonemes = self.data.consonants + self.data.vowels
        for p in all_phonemes:
            row = self.table.rowCount()
            self.table.setRowCount(row + 1)
            self.table.setItem(row, 0, QTableWidgetItem(p))
            custom = self.data.script_mappings.get(p, "")
            self.table.setItem(row, 1, QTableWidgetItem(custom))
            self.table.setItem(row, 2, QTableWidgetItem(""))


# ─── LEARNING PAGE ──────────────────────────────────────────────────────────

class LearningPage(QWidget):
    def __init__(self, data: ConlangData, parent=None):
        super().__init__(parent)
        self.data = data
        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)

        # Lesson list
        left = QVBoxLayout()
        lbl = QLabel("Learning Center")
        lbl.setObjectName("pageTitle")
        left.addWidget(lbl)
        sub = QLabel("Interactive lessons on linguistics and language construction.")
        sub.setObjectName("pageSubtitle")
        left.addWidget(sub)

        self.lesson_list = QListWidget()
        self.lesson_list.setMaximumWidth(280)
        for lesson in LESSONS:
            self.lesson_list.addItem(lesson["title"])
        self.lesson_list.currentRowChanged.connect(self._show_lesson)
        left.addWidget(self.lesson_list)

        # Quick quiz button
        quiz_btn = QPushButton("🧠 Quick Quiz")
        quiz_btn.setObjectName("secondaryBtn")
        quiz_btn.clicked.connect(self._show_quiz)
        left.addWidget(quiz_btn)
        left.addStretch()

        layout.addLayout(left)

        # Lesson content
        self.content_area = QTextEdit()
        self.content_area.setReadOnly(True)
        self.content_area.setStyleSheet(
            "QTextEdit { background: #fff; border: 1px solid #ddd; border-radius: 8px; "
            "padding: 20px; font-size: 14px; line-height: 1.6; }")
        self.content_area.setOpenExternalLinks(True)
        layout.addWidget(self.content_area, stretch=1)

        # Show first lesson
        self.lesson_list.setCurrentRow(0)

    def _show_lesson(self, row):
        if 0 <= row < len(LESSONS):
            self.content_area.setHtml(LESSONS[row]["content"])

    def _show_quiz(self):
        questions = [
            ("What does 'phonology' study?",
             ["How sounds function in a language", "How words are formed",
              "How sentences are structured", "How writing systems work"], 0),
            ("Which word order is most common across languages?",
             ["SVO", "VSO", "SOV", "OSV"], 2),
            ("In an agglutinative language, morphemes are:",
             ["Fused together", "Each with a clear separate meaning",
              "Non-existent", "Only suffixes"], 1),
            ("What is a 'phoneme'?",
             ["A letter in an alphabet", "The smallest meaningful sound unit in a language",
              "A type of vowel", "A grammatical category"], 1),
            ("An 'abjad' is a writing system that:",
             ["Has symbols for consonants and vowels",
              "Has symbols only for consonants, vowels mostly omitted",
              "Has symbols for whole syllables",
              "Has symbols for whole words"], 1),
            ("Which is an example of a fusional language?",
             ["Turkish", "Mandarin Chinese", "Latin", "Hawaiian"], 2),
            ("What is 'phonotactics'?",
             ["The study of meaning", "Rules governing sound combinations",
              "The study of word order", "The study of tone"], 1),
            ("What percentage of languages use SOV or SVO order?",
             ["About 50%", "About 65%", "About 87%", "About 95%"], 2),
        ]
        random.shuffle(questions)
        q = questions[0]
        options = "\n".join(f"  {chr(65+i)}. {opt}" for i, opt in enumerate(q[1]))
        answer, ok = QMessageBox.question(
            self, "🧠 Quick Quiz",
            f"{q[0]}\n\n{options}",
            QMessageBox.StandardButton(QMessageBox.Yes | QMessageBox.No),
            QMessageBox.Yes
        )
        # For a richer quiz, we'd need a custom dialog, but this gives the idea
        correct_letter = chr(65 + q[2])
        QMessageBox.information(
            self, "Answer",
            f"The correct answer is {correct_letter}. {q[1][q[2]]}")


# ─── MAIN WINDOW ────────────────────────────────────────────────────────────

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Conlang Creator — Language Construction Toolkit")
        self.setMinimumSize(1100, 700)
        self.resize(1280, 800)
        self.data = ConlangData()

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ── Sidebar ──
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(220)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        brand = QLabel("🌍 Conlang\n   Creator")
        brand.setObjectName("sidebar")  # for styling
        sidebar_layout.addWidget(brand)

        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color: #333355;")
        sidebar_layout.addWidget(sep)

        self.nav_buttons = []
        nav_items = [
            ("🏠  Overview", 0),
            ("🔤  Phonology", 1),
            ("📝  Grammar", 2),
            ("📖  Lexicon", 3),
            ("✍️  Script", 4),
            ("🎓  Learn", 5),
        ]
        for text, idx in nav_items:
            btn = QPushButton(text)
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda checked, i=idx: self._switch_page(i))
            sidebar_layout.addWidget(btn)
            self.nav_buttons.append(btn)

        sidebar_layout.addStretch()

        # Save/Load buttons at bottom
        sep2 = QFrame()
        sep2.setFrameShape(QFrame.HLine)
        sep2.setStyleSheet("color: #333355;")
        sidebar_layout.addWidget(sep2)

        save_btn = QPushButton("💾  Save Project")
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.clicked.connect(self._save_project)
        sidebar_layout.addWidget(save_btn)

        load_btn = QPushButton("📂  Load Project")
        load_btn.setCursor(Qt.PointingHandCursor)
        load_btn.clicked.connect(self._load_project)
        sidebar_layout.addWidget(load_btn)

        new_btn = QPushButton("📄  New Project")
        new_btn.setCursor(Qt.PointingHandCursor)
        new_btn.clicked.connect(self._new_project)
        sidebar_layout.addWidget(new_btn)

        main_layout.addWidget(sidebar)

        # ── Content Stack ──
        self.stack = QStackedWidget()
        self.pages = [
            OverviewPage(self.data),
            PhonologyPage(self.data),
            GrammarPage(self.data),
            LexiconPage(self.data),
            ScriptPage(self.data),
            LearningPage(self.data),
        ]
        for page in self.pages:
            self.stack.addWidget(page)

        main_layout.addWidget(self.stack, stretch=1)

        # Select first page
        self._switch_page(0)

        # Keyboard shortcuts
        QShortcut(QKeySequence("Ctrl+S"), self, self._save_project)
        QShortcut(QKeySequence("Ctrl+O"), self, self._load_project)
        QShortcut(QKeySequence("Ctrl+N"), self, self._new_project)

    def _switch_page(self, idx):
        self.stack.setCurrentIndex(idx)
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == idx)
        # Refresh the target page
        self.pages[idx].refresh()

    def _save_project(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Conlang Project", f"{self.data.name}.json",
            "JSON Files (*.json);;All Files (*)")
        if path:
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    json.dump(self.data.to_dict(), f, indent=2, ensure_ascii=False)
                self.statusBar().showMessage(f"Project saved to {path}", 3000)
            except Exception as e:
                QMessageBox.critical(self, "Save Error", f"Could not save: {e}")

    def _load_project(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Load Conlang Project", "",
            "JSON Files (*.json);;All Files (*)")
        if path:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    d = json.load(f)
                self.data = ConlangData.from_dict(d)
                # Update all pages
                for page in self.pages:
                    page.data = self.data
                current = self.stack.currentIndex()
                self.pages[current].refresh()
                self.statusBar().showMessage(f"Project loaded from {path}", 3000)
            except Exception as e:
                QMessageBox.critical(self, "Load Error", f"Could not load: {e}")

    def _new_project(self):
        reply = QMessageBox.question(
            self, "New Project",
            "Create a new project? Unsaved changes will be lost.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.data = ConlangData()
            for page in self.pages:
                page.data = self.data
            self._switch_page(0)


# ─── ENTRY POINT ────────────────────────────────────────────────────────────

def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLESHEET)

    # Set application-wide font
    font = QFont("Segoe UI", 10)
    app.setFont(font)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()