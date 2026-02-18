#!/usr/bin/env python3

import sys
import os
import argparse
import json
import re

class LoreParser:
    @staticmethod
    def parse_file(filepath):
        if not os.path.exists(filepath):
            return None
        with open(filepath, 'r') as f:
            content = f.read()

        entities = {
            "characters": [],
            "factions": [],
            "premise": "",
            "conflict": ""
        }

        # Parse Characters
        char_matches = re.findall(r'## Character:\s*(.*)', content)
        entities["characters"] = [c.strip() for c in char_matches]

        # Parse Factions (simplified, look for faction-like keywords or bullet points in a faction section)
        faction_section = re.search(r'## Factions(.*?)(?:##|$)', content, re.DOTALL)
        if faction_section:
            factions = re.findall(r'[*-]\s*(.*?):', faction_section.group(1))
            entities["factions"] = [f.strip() for f in factions]

        # Parse Premise
        premise_match = re.search(r'## Premise(.*?)(?:##|$)', content, re.DOTALL)
        if premise_match:
            entities["premise"] = premise_match.group(1).strip()

        # Parse Conflict
        conflict_match = re.search(r'## Conflict(.*?)(?:##|$)', content, re.DOTALL)
        if conflict_match:
            entities["conflict"] = conflict_match.group(1).strip()

        return entities

class StateStore:
    def __init__(self, state_file="agora_state.json"):
        self.state_file = state_file
        self.data = self.load()

    def load(self):
        if os.path.exists(self.state_file):
            with open(self.state_file, 'r') as f:
                return json.load(f)
        return {"characters": {}, "project": {}}

    def save(self):
        with open(self.state_file, 'w') as f:
            json.dump(self.data, f, indent=4)

    def sync_lore(self, entities):
        for char in entities["characters"]:
            if char not in self.data["characters"]:
                self.data["characters"][char] = {
                    "anchors": "[Define visual anchors for {}]".format(char),
                    "voiceprint": {}
                }
        self.save()

class Philosopher:
    def __init__(self, name, emoji, title, domain, kill_phrase, prompt_modifiers):
        self.name = name
        self.emoji = emoji
        self.title = title
        self.domain = domain
        self.kill_phrase = kill_phrase
        self.prompt_modifiers = prompt_modifiers

PHILOSOPHERS = [
    Philosopher("Aristotle", "🏛️", "Chief Structural Analyst", "Plot Structure, Story Mechanics",
                "This isn't a story. It's a sequence of events.",
                "compositional balance, rule of thirds, perspective accuracy"),
    Philosopher("Plato", "🌅", "Director of Thematic Integrity", "Theme, Meaning, Symbolic Resonance",
                "Pretty. Empty. Next.",
                "symbolic lighting, ethereal atmosphere, allegorical visual elements"),
    Philosopher("Socrates", "❓", "Chief Character Psychologist", "Character Depth, Motivation",
                "I just have one small question... actually, I have seven.",
                "expressive facial anatomy, micro-expressions, character-driven lighting"),
    Philosopher("Seneca", "🎭", "Master of Emotional Warfare", "Emotional Impact, Pathos",
                "You made me feel nothing. And I've felt everything.",
                "high contrast, chiaroscuro, dramatic shadows, emotional color palettes"),
    Philosopher("Marcus Aurelius", "⚖️", "Grand Marshal of Story Tempo", "Pacing, Discipline, Economy",
                "You have my attention for exactly as long as you deserve it.",
                "tight framing, essentialist composition, no visual clutter"),
    Philosopher("Epicurus", "🍷", "Chief Reader Advocate", "Reader Experience, Satisfaction",
                "I fell asleep on page 12 and I'm the guy who LIKES your genre.",
                "dynamic action poses, vibrant energy effects, cinematic flair"),
    Philosopher("Diogenes", "🐕", "Director of Creative Destruction", "Subversion, Comedy, Authenticity",
                "I've seen more originality in a fortune cookie.",
                "gritty textures, raw linework, unconventional camera angles"),
    Philosopher("Heraclitus", "🔥", "Warden of Opposing Forces", "Conflict Architecture, Change",
                "Nothing moved. Nothing changed. Nothing burned. Why should I care?",
                "opposing color temperatures, visual tension, dynamic silhouettes"),
    Philosopher("Laozi", "☯️", "Director of Organic Flow", "Negative Space (Ma), Paradox",
                "You are shouting into a vacuum. Nobody can hear your theme.",
                "ma, negative space, atmospheric silence, balanced void"),
    Philosopher("Sun Tzu", "🚩", "Warden of Narrative Momentum", "Conflict Strategy, Pacing",
                "You have lost the war before the first panel was drawn.",
                "tactical depth, strategic framing, informational asymmetry"),
]

STYLE_BASE = "digital-first animation, high-fidelity rendering, cinematic lighting, 8k resolution, on-model consistency, [YOUR_PRODUCTION_STYLE]"

# ============================================================================
# CINEMATOGRAPHY DIRECTOR SYSTEM (Art Director Mode)
# Three systems: Shot List (Sun Tzu), Thermal Conflict (Heraclitus), Gutter Breath (Laozi)
# ============================================================================

# 1. SHOT LIST GENERATOR (Sun Tzu's Tactical Framing)
# Maps narrative beats to camera logic from docs/kinetic_flow.md
SHOT_LIST = {
    "information_asymmetry": {
        "trigger": "Someone is hiding something / secret revealed / deception in play",
        "camera": "Dutch Angle, Obscured Foreground, Focus on Eyes",
        "philosopher": "Sun Tzu",
        "rationale": "The frame itself lies to the reader — angles suggest instability, obscured elements mirror hidden information."
    },
    "power_reveal": {
        "trigger": "Character displays overwhelming force / power-up / transformation",
        "camera": "Extreme Low Angle, Wide Lens, Silhouette Backlighting",
        "philosopher": "Sun Tzu",
        "rationale": "Scale dominance — the reader looks UP at the character, reinforcing power differential."
    },
    "fast_scroll_action": {
        "trigger": "Rapid combat / chase / explosive movement",
        "camera": "Motion Blur, Whip-Pan Composition, Speed Lines, Vertical Motion Lines",
        "philosopher": "Marcus Aurelius",
        "rationale": "Economy of motion — every frame pushes momentum downward through the scroll."
    },
    "slow_burn_tension": {
        "trigger": "Pre-battle silence / standoff / psychological warfare",
        "camera": "Extreme Close-Up, Shallow Depth of Field, Rack Focus Between Characters",
        "philosopher": "Seneca",
        "rationale": "Restraint before the break — the tight frame creates claustrophobia and suspense."
    },
    "moment_of_realization": {
        "trigger": "Anagnorisis / epiphany / truth revealed to the character",
        "camera": "Extreme Wide Shot, Minimalist Background, High Negative Space",
        "philosopher": "Laozi",
        "rationale": "The world opens up — the character is small against the vastness of their new understanding."
    },
    "tragic_beat": {
        "trigger": "Death / loss / irreversible change",
        "camera": "Static Long Shot, No Camera Movement, Desaturated Edges",
        "philosopher": "Seneca",
        "rationale": "The camera refuses to look away or dramatize. Stillness IS the emotion."
    },
    "comedic_subversion": {
        "trigger": "Punchline / expectation broken / tonal whiplash",
        "camera": "Snap Zoom, Fish-Eye Distortion, Chibi Shift, Flat Composition",
        "philosopher": "Diogenes",
        "rationale": "The frame itself is the joke — breaking cinematic language signals the tonal shift."
    },
    "thematic_mirror": {
        "trigger": "Parallel scene / callback / visual rhyme with earlier panel",
        "camera": "Identical Framing to Referenced Panel, Split-Screen Overlay, Mirror Composition",
        "philosopher": "Plato",
        "rationale": "The 'Form' recurs — the reader recognizes the ideal echoing through time."
    },
    "first_encounter": {
        "trigger": "Character meets antagonist / new world / key location for first time",
        "camera": "Establishing Wide Shot, Full Scroll-Width Panel, Tracking Shot Entry",
        "philosopher": "Aristotle",
        "rationale": "Structural clarity — the reader needs spatial and relational orientation before conflict."
    },
    "strategic_feint": {
        "trigger": "Misdirection / narrative fake-out / reader is being set up",
        "camera": "Over-the-Shoulder (wrong character), Misleading Focal Point, Frame-Within-Frame",
        "philosopher": "Sun Tzu",
        "rationale": "The camera conspires with the story — pointing the reader's eye at the decoy."
    },
}

# 2. THERMAL CONFLICT SCRIPT (Heraclitus's Color Grading)
# Maps emotional/philosophical conflict to color temperature directives
THERMAL_GRADES = {
    "opposing_forces": {
        "trigger": "Hero vs. Villain / Order vs. Chaos / Two philosophies clash",
        "grade": "Split Lighting: Warm Left / Cool Right, Complementary Color Palette: Orange/Teal, Visual Contrast High",
        "philosopher": "Heraclitus",
        "rationale": "The Unity of Opposites made visible — color itself becomes the conflict."
    },
    "tragic_pathos": {
        "trigger": "Death / grief / irreversible loss / restraint breaks",
        "grade": "Muted Palette, Bleached Bypass, Cold Shadows, Desaturated Skin Tones",
        "philosopher": "Seneca",
        "rationale": "Color drains from the world as meaning drains from the character."
    },
    "rising_hope": {
        "trigger": "Breakthrough / dawn / alliance formed / the cave exit",
        "grade": "Warm Color Bleed, Golden Hour Lighting, Gradual Saturation Increase",
        "philosopher": "Plato",
        "rationale": "The character approaches the 'Form' — light itself becomes the thematic resolution."
    },
    "corruption_spread": {
        "trigger": "Villain gains ground / world decays / moral compromise",
        "grade": "Chromatic Aberration, Sickly Green Undertones, Contrast Crush in Shadows",
        "philosopher": "Heraclitus",
        "rationale": "The visual world is poisoned — the color palette reflects the narrative rot."
    },
    "calm_before_storm": {
        "trigger": "False peace / deceptive tranquility / the setup before betrayal",
        "grade": "Over-Saturated Warmth (uncanny), Slightly Off-White Balance, Too-Perfect Lighting",
        "philosopher": "Sun Tzu",
        "rationale": "The beauty is a trap — the frame is too pretty, signaling something is wrong."
    },
    "internal_conflict": {
        "trigger": "Character at war with themselves / moral dilemma / identity crisis",
        "grade": "Bisected Color Temperature on Single Face, Half-Shadow, Dual Rim Lighting",
        "philosopher": "Socrates",
        "rationale": "The character IS the conflict — their face becomes the battleground."
    },
    "catharsis_release": {
        "trigger": "Emotional climax / final battle peak / the restraint-break moment",
        "grade": "Full Saturation Bloom, White-Out Highlights, Color Explosion from Muted Base",
        "philosopher": "Seneca",
        "rationale": "All the restrained color detonates at once — maximum impact from maximum restraint."
    },
    "the_void": {
        "trigger": "Nihilism / meaninglessness / the barrel test moment",
        "grade": "Near-Monochrome, Ink-Wash Aesthetic, Zero Color Accent",
        "philosopher": "Diogenes",
        "rationale": "Strip everything away. If the scene still works in near-black-and-white, it's honest."
    },
}

# 3. GUTTER BREATH METRIC (Laozi's Panel Pacing)
# Maps emotional weight to vertical scroll spacing instructions
# Each entry has a code_name for quick reference in production
GUTTER_BREATH = {
    "heavy_emotional_beat": {
        "code_name": "The Grief Scroll",
        "trigger": "Death, loss, major revelation, restraint breaks",
        "spacer": "300px whitespace OR gradient fade to white/black",
        "panel_instruction": "Single panel, full scroll-width, no overlapping elements",
        "philosopher": "Seneca + Laozi",
        "rationale": "The reader must FEEL the absence. Scrolling through emptiness is mourning."
    },
    "rapid_action_sequence": {
        "code_name": "The Combat Stack",
        "trigger": "Combat, chase, explosion, rapid movement",
        "spacer": "Zero gutter, overlapping panels, bleed-through elements",
        "panel_instruction": "Panels stack vertically with no breathing room, objects break panel borders",
        "philosopher": "Sun Tzu + Marcus Aurelius",
        "rationale": "No time to breathe. The scroll speed IS the combat speed."
    },
    "moment_of_ma": {
        "code_name": "The Ma Breath",
        "trigger": "Philosophical realization, quiet reflection, the weight settles",
        "spacer": "200px whitespace, single centered element in negative space",
        "panel_instruction": "Extreme reduction — one object, vast emptiness, no text",
        "philosopher": "Laozi",
        "rationale": "The Tao is the space between. The reader's imagination fills the void."
    },
    "comedic_beat": {
        "code_name": "The Snap Cut",
        "trigger": "Punchline, reaction shot, tonal shift to comedy",
        "spacer": "50px tight gutter, immediate cut to reaction",
        "panel_instruction": "Small panel, chibi shift, flat background, snap to next beat",
        "philosopher": "Diogenes + Epicurus",
        "rationale": "Comedy is timing. The gutter IS the pause before the laugh."
    },
    "cliffhanger_end": {
        "code_name": "The Black Fade",
        "trigger": "Chapter ending, major reveal, suspense peak",
        "spacer": "Fade to black over 400px, no next panel visible",
        "panel_instruction": "Final panel bleeds into darkness, reader cannot see what comes next",
        "philosopher": "Sun Tzu",
        "rationale": "The reader's thumb has nowhere to go. The absence of the next panel IS the hook."
    },
    "transition_scene": {
        "code_name": "The Transition Bridge",
        "trigger": "Time skip, location change, tone shift",
        "spacer": "150px with transitional gradient or texture (ink wash, static, rain)",
        "panel_instruction": "The gutter itself becomes a panel — a visual bridge between states. Never just 'cut' to a new scene.",
        "philosopher": "Laozi + Heraclitus",
        "rationale": "Change is constant. The gutter visualizes the transformation between states."
    },
}

# ============================================================================
# ANTI-STIFFNESS PROTOCOL (Kinetic Audit System)
# Three systems: Torsional Stress (Heraclitus), Micro-Anatomy (Socrates), Kinetic Camera (Sun Tzu)
# Activated via --kinetic-audit flag on prompt-architect mode
# ============================================================================

# 1. TORSIONAL STRESS (Heraclitus + Epicurus — Body Dynamics)
# Forces dynamic posing by breaking the center of gravity
TORSIONAL_STRESS = {
    "base_rule": "The shoulders and hips must NEVER be parallel. No character should ever be standing straight up.",
    "modifiers": "dynamic foreshortening, torso twisting, off-balance posture, weight distribution: heavy, hyper-extended limb, lines of action, contrapposto stance",
    "philosophers": "Heraclitus (Visual Tension) + Epicurus (Kinetic Energy)",
    "panel_types": {
        "action_panel": {
            "trigger": "Any combat, movement, or physical exertion",
            "injection": "dynamic foreshortening, torso twisting 30-45 degrees, off-balance posture, weight distribution shifted to lead leg, hyper-extended striking limb, aggressive lines of action",
            "rule": "Shoulders tilted opposite to hips (contrapposto). Center of gravity outside the base of support."
        },
        "power_stance": {
            "trigger": "Character asserting dominance, intimidation, or resolve",
            "injection": "wide stance asymmetry, one shoulder dropped, chin tilted, weight planted on back foot, coiled tension in torso, lines of action spiraling upward",
            "rule": "The body stores energy like a spring — compressed, rotated, ready to release."
        },
        "emotional_collapse": {
            "trigger": "Character breaking down, defeated, exhausted",
            "injection": "collapsed center of gravity, spine curved forward, limbs heavy and asymmetric, head dropped below shoulder line, weight surrendered to gravity",
            "rule": "Gravity wins. The body becomes a weight diagram of emotional defeat."
        },
        "casual_scene": {
            "trigger": "Dialogue, walking, everyday interaction",
            "injection": "subtle weight shift, one hip cocked, relaxed asymmetry in shoulders, natural lean, micro-gesture in hands",
            "rule": "Even stillness has motion. A character leaning on a wall has weight distribution. A character talking shifts balance."
        },
    }
}

# 2. SOCRATIC MICRO-ANATOMY (Socrates — Facial Mechanics)
# Forces facial realism by prompting muscles, not emotions
MICRO_ANATOMY = {
    "base_rule": "NEVER prompt for an emotion ('sad', 'angry'). ALWAYS prompt for the MUSCLES that produce the emotion.",
    "modifiers": "asymmetrical eyebrow raise, visible neck tendon, dilated pupils, sweat beading on upper lip, clenched jaw muscles, skin texture: pores/imperfection, micro-expression detail",
    "philosopher": "Socrates (Micro-Expressions / Character Depth)",
    "emotion_to_muscle_map": {
        "sadness": {
            "wrong": "sad expression, crying face",
            "right": "inner eyebrows pulled upward and together, lower lip trembling, eyes glassy with early-stage tearing, nasolabial folds deepened, chin dimpling from mentalis muscle tension",
            "socrates_note": "Sadness is not one thing. Is it grief? Regret? Resignation? Each uses different muscles. Ask WHY they're sad, then render THAT."
        },
        "anger": {
            "wrong": "angry expression, furious face",
            "right": "eyebrows pulled down and together (corrugator), nostrils flared, upper lip tightened showing teeth, jaw clenched with visible masseter bulge, neck tendons taut, veins visible at temple",
            "socrates_note": "Anger has five versions. Cold anger barely moves the face — just the eyes narrow. Hot anger engages every muscle. Which one does THIS character feel?"
        },
        "fear": {
            "wrong": "scared expression, frightened look",
            "right": "eyes wide with visible sclera above iris, eyebrows raised and pulled together, mouth slightly open with retracted lips, skin pallor, sweat beading at hairline, pupils dilated",
            "socrates_note": "Fear and surprise share muscles but differ in the mouth. Fear pulls back. Surprise opens up. Get it wrong and you've swapped the emotion entirely."
        },
        "determination": {
            "wrong": "determined look, resolute expression",
            "right": "jaw set with slight forward thrust, eyes narrowed with focused gaze, lips pressed thin, brow lowered asymmetrically, neck muscles engaged, subtle nostril flare on exhale",
            "socrates_note": "Determination is anger's disciplined cousin. The muscles tighten but don't explode. The face becomes a weapon that hasn't been drawn yet."
        },
        "suppressed_emotion": {
            "wrong": "hiding feelings, restrained expression",
            "right": "micro-tension in orbicularis oculi (eye corners), jaw clenched but lips neutral, one eyebrow 2mm higher than the other, swallowing visible in throat, fingernails pressing into palm",
            "socrates_note": "This is the Seneca special. The composed character who finally breaks. The SUPPRESSION is the expression — the tiny leaks that betray the dam about to burst."
        },
        "genuine_joy": {
            "wrong": "happy expression, smiling face",
            "right": "Duchenne smile with crow's feet at eyes, cheeks lifted compressing lower eyelids, relaxed forehead, slight head tilt, visible teeth with natural asymmetry, warmth in skin tone",
            "socrates_note": "A real smile uses the eyes. A fake smile uses only the mouth. If the orbicularis oculi isn't engaged, the character is lying."
        },
    }
}

# 3. KINETIC CAMERA (Sun Tzu — Camera Dynamics for Anti-Stiffness)
# Forces dynamic camera angles to make even static poses feel alive
KINETIC_CAMERA = {
    "base_rule": "NEVER use a flat, eye-level, medium-distance shot for action or intense scenes.",
    "modifiers": "extreme camera angle, aggressive depth of field, 3-point perspective, fisheye lens distortion",
    "philosopher": "Sun Tzu (Tactical Framing)",
    "scene_types": {
        "fast_scene": {
            "trigger": "Combat, chase, explosion, rapid physical action",
            "injection": "3-point perspective, extreme worm's-eye view, motion blur on frame edges, fisheye lens distortion, speed lines following vertical scroll axis, camera shake micro-blur",
            "rule": "The camera moves WITH the action. If the character is falling, the camera falls too. The reader's inner ear should activate."
        },
        "intense_scene": {
            "trigger": "Confrontation, threat, psychological pressure, standoff",
            "injection": "Dutch Angle 15-45 degrees, camera tilt, foreground obstruction with bokeh, shallow depth of field isolating subject, rim lighting carving silhouette",
            "rule": "The world is off-kilter. The tilted frame tells the reader that stability is an illusion."
        },
        "revelation_scene": {
            "trigger": "Truth exposed, mask drops, the reader learns something",
            "injection": "crash zoom effect, sudden focal length shift, background blur snap, radial speed lines from focal point, dramatic rack focus",
            "rule": "The camera REACTS to the revelation. The shift in focus mirrors the shift in understanding."
        },
        "establishing_scene": {
            "trigger": "New location, new chapter, world introduction",
            "injection": "extreme wide shot, bird's-eye or high-angle tilt, atmospheric perspective with depth layers, miniaturized character in vast space",
            "rule": "Scale establishes context. The character is small against the world they must navigate."
        },
    }
}

# THE COMPLETE ANTI-STIFFNESS PROMPT BLOCK (Ready-to-paste context injection)
ANTI_STIFFNESS_BLOCK = """
================================================================================
KINETIC AUDIT — ANTI-STIFFNESS PROTOCOL
Paste this block into the LLM context window before generating any visual prompts.
================================================================================

CONVENING THE COUNCIL FOR KINETIC AUDIT:

• HERACLITUS (Torsional Stress): Inject [dynamic foreshortening] and [twisted torso].
  RULE: Shoulders and hips must NEVER be parallel. No character stands straight up.
  Every body is a tension diagram — compressed, rotated, storing energy.

• SOCRATES (Micro-Anatomy): Inject [micro-expressions] and [facial asymmetry].
  RULE: Never prompt for emotions ('sad', 'angry'). Prompt for MUSCLES.
  Describe the corrugator, the masseter, the orbicularis oculi. Faces are machines.

• SUN TZU (Kinetic Camera): Inject [extreme camera angle] and [depth of field].
  RULE: Never use a flat, eye-level shot for action or intensity.
  Tilt the camera. Distort the lens. Make the reader's inner ear activate.

• EPICURUS (Energy Injection): Inject [kinetic energy lines] and [impact emphasis].
  RULE: If a reader wouldn't screenshot this panel, it lacks hype.
  Every action frame needs at least one element that breaks physics for drama.

• CINEMATIC DIRECTIVE: Enforce [cinematic lighting] to carve volume and prevent flat shading.
  RULE: Every surface has a light source. Every form has shadow. No flat fills.

ANTI-STIFFNESS CHECKLIST (Apply to every generated prompt):
[ ] Body: Shoulders and hips counter-rotated? Weight off-center?
[ ] Face: Muscles described, not emotions? Asymmetry present?
[ ] Camera: Angle aggressive? Not flat eye-level medium shot?
[ ] Lighting: Directional? Carving depth? Not flat ambient?
[ ] Energy: Motion lines? Impact effects? Something breaking the panel border?
================================================================================
"""

# ============================================================================
# DIALOGUE FORGE SYSTEM (Award-Winner Mode)
# Four systems: Subtext Layer (Sun Tzu), Voiceprint (Socrates), Silence Audit (Laozi), Balloon Economy (Marcus Aurelius)
# Activated via --dialogue-forge flag on session mode
# ============================================================================

# 1. SUN TZU SUBTEXT LAYER (Text vs. Intent Protocol)
# Forces every line of dialogue to operate on two levels: Text and Strategic Intent
SUBTEXT_LAYER = {
    "base_rule": "No character is allowed to state their feelings directly. They must project them through an object, an action, or a strategic command.",
    "philosopher": "Sun Tzu (Information Asymmetry)",
    "protocol": {
        "surface_text": "What the character actually says aloud.",
        "strategic_intent": "What the character WANTS from this exchange (e.g., 'Provoke a reaction,' 'Hide their fear,' 'Fish for information,' 'Establish dominance,' 'Buy time').",
        "the_lie": "What specific truth are they omitting or distorting? Every character in a conversation is withholding something.",
    },
    "output_format": """
SUBTEXT TABLE (Generate BEFORE writing dialogue):
┌─────────────┬────────────────────────┬──────────────────────┬─────────────────────┐
│ Character   │ Surface Text           │ Strategic Intent     │ The Lie             │
├─────────────┼────────────────────────┼──────────────────────┼─────────────────────┤
│ [Name]      │ [What they say]        │ [What they want]     │ [What they hide]    │
│ [Name]      │ [What they say]        │ [What they want]     │ [What they hide]    │
└─────────────┴────────────────────────┴──────────────────────┴─────────────────────┘
""",
    "examples": {
        "bad": '"I\'m scared," said [CHARACTER].',
        "good": '"The [object] feels heavier today," [CHARACTER] said, turning it over in their hands.',
        "analysis": "[CHARACTER] never says they're scared. They talk about the object. The reader decodes the fear from the weight of the object — a tool that costs them something irreplaceable."
    }
}

# 2. SOCRATIC VOICEPRINT (Syntax Anchors)
# Prevents verbal drifting — every character has a locked speech DNA
VOICEPRINT = {
    "base_rule": "Cover the names in the speech bubbles. The reader must still know exactly who is talking from syntax alone.",
    "philosopher": "Socrates (Dialogue Authenticity)",
    "anchor_template": {
        "syntax_class": "The overall speech architecture (e.g., Fractured/Internal, Absolute/Clinical, Warm/Rambling)",
        "sentence_rule": "Structural constraint (e.g., 'Never finishes sentences,' 'Uses zero contractions,' 'Speaks only in questions')",
        "vocabulary_domain": "The sensory/conceptual world they draw from (e.g., 'Only talks about what he can touch,' 'Only uses military metaphors')",
        "forbidden_words": "Words this character would NEVER use (e.g., 'Never says Justice,' 'Never asks questions')",
    },
    "cast_anchors": {
        "protagonist_example": {
            "syntax_class": "Fractured / Internal",
            "sentence_rule": "Rarely finishes sentences. Speaks in observations, not declarations. Trails off with '...' when emotions surface.",
            "vocabulary_domain": "Sensory words only — smell, texture, weight, temperature. Never abstracts.",
            "forbidden_words": "Never uses abstract concepts like 'Justice,' 'Destiny,' 'Power.' Only talks about what they can touch, see, smell.",
            "example_good": '"It smells like ozone... like the [place] used to, before—" They stopped. Turned the [object] over.',
            "example_bad": '"I believe in the power of true [thing] to set us free!"',
        },
        "antagonist_example": {
            "syntax_class": "Absolute / Clinical",
            "sentence_rule": "Zero contractions (cannot, will not, do not — never can't, won't, don't). Speaks in axioms and definitive statements.",
            "vocabulary_domain": "Systems language — efficiency, consensus, optimization, parameters. The world is a machine.",
            "forbidden_words": "Never asks questions. Never uses 'feel,' 'believe,' 'hope,' or any subjective verb. Only declaratives.",
            "example_good": '"Unauthorized variance introduces entropy. Entropy is the enemy of order. You will surrender the instrument."',
            "example_bad": '"Don\'t you think that\'s dangerous? I feel like it causes chaos."',
        },
    }
}

# 3. LAOZI SILENCE AUDIT (Text-to-Visual Converter)
# Identifies the emotional peak line and replaces it with a visual acting prompt
SILENCE_AUDIT = {
    "base_rule": "Find the strongest line of dialogue in the scene. DELETE IT. Replace it with a visual instruction. Let the silence carry the weight.",
    "philosophers": "Laozi (Ma / Negative Space) + Seneca (Pathos through Restraint)",
    "protocol_steps": [
        "1. Read the full dialogue script for the scene.",
        "2. Identify the line where the emotional peak occurs — the line the writer is most 'proud' of.",
        "3. DELETE THAT LINE entirely.",
        "4. Replace it with a Visual Acting Prompt — a micro-action that SHOWS the emotion without SAYING it.",
        "5. If the scene still works (it will work better), the deletion was correct.",
    ],
    "visual_acting_prompts": {
        "grief": "[CHARACTER]'s hand stops shaking. (Not 'starts' — the stillness after the trembling is worse.)",
        "resolve": "[CHARACTER] uncaps the [tool]. [Substance] drips onto the pristine floor. They do not wipe it up.",
        "betrayal": "[ANTAGONIST]'s hand moves toward the teacup, then stops. They fold both hands in their lap instead.",
        "love": "She places the photograph face-down on the table. Her fingers linger on the back of it.",
        "fear": "[CHARACTER] hasn't [used their power] in hours. They haven't moved.",
        "rage": "The panel is silent. [CHARACTER]'s knuckles are white around the [weapon/tool]. A single drop falls.",
    },
    "the_test": "If you removed ALL dialogue from the scene and only kept the visual acting prompts, would the reader still understand the emotion? If yes, you have a great scene. If no, your dialogue was doing the work that the art should be doing."
}

# 4. MARCUS AURELIUS BALLOON ECONOMY (The Tweet Rule)
# Hard constraints on word count and balloon density per panel
BALLOON_ECONOMY = {
    "base_rule": "In a vertical scroll, a wall of text is a death sentence. Every word must earn its panel space.",
    "philosopher": "Marcus Aurelius (Narrative Economy)",
    "constraints": {
        "word_limit": "No speech balloon may contain more than 15 words.",
        "balloon_limit": "No single panel may contain more than 2 speech balloons.",
        "monologue_rule": "If a thought is longer than 15 words, break it across 3 panels using Kinetic Flow to control reading speed.",
        "narration_rule": "Narration boxes follow the same 15-word limit. If it needs more, it needs a panel, not more words.",
    },
    "violation_penalties": {
        "16-25_words": "YELLOW FLAG — Split into two balloons across two panels.",
        "26-40_words": "RED FLAG — This is a monologue. Break across 3+ panels with visual beats between.",
        "40+_words": "CRITICAL — This is not manga dialogue. This is a novel masquerading as a comic. Rewrite entirely.",
        "3+_balloons": "PANEL OVERLOAD — Cut the weakest balloon. If you can't decide which is weakest, they're all weak.",
    },
    "example": {
        "bad": "[Single panel] 'I have come to understand that the [FACTION] does not seek peace — they seek the elimination of all variance because they fear what they cannot control, and in that fear lies the seed of their own destruction.'",
        "good": "[Panel 1] 'The [FACTION] does not seek peace.' [Panel 2 — [CHARACTER]'s eyes narrow] 'They seek control.' [Panel 3 — close-up on [ANTAGONIST]'s clenched fist behind their back] 'And control...' [Panel 4 — wide shot, [CHARACTER] stepping forward] '...is just fear with a uniform.'",
        "analysis": "Same thought. Four panels. Each beat has a visual anchor. The reader's scroll speed controls the dramatic timing."
    }
}

# THE COMPLETE DIALOGUE FORGE PROMPT BLOCK (Ready-to-paste context injection)
DIALOGUE_FORGE_BLOCK = """
================================================================================
DIALOGUE FORGE — AWARD-WINNER PROTOCOL
Paste this block into the LLM context window before generating any dialogue.
================================================================================

CONVENING THE COUNCIL FOR DIALOGUE FORGE:

• SUN TZU (Subtext Layer): Generate a SUBTEXT TABLE before writing dialogue.
  RULE: No character states feelings directly. Define Surface Text, Strategic
  Intent, and The Lie for every speaker in every exchange.

• SOCRATES (Voiceprint / Syntax Anchors): Apply locked speech DNA per character.
  RULE: Cover the names — the reader must know who's talking from syntax alone.
  Define distinct syntax DNA per character. No verbal drifting.

• LAOZI + SENECA (Silence Audit): Find the emotional peak line. DELETE IT.
  RULE: Replace with a Visual Acting Prompt (micro-action, not words).
  If the scene works without the line, the deletion was correct.

• MARCUS AURELIUS (Balloon Economy): Enforce the Tweet Rule.
  RULE: Max 15 words per balloon. Max 2 balloons per panel.
  Break monologues across panels with visual beats between.

DIALOGUE CHECKLIST (Every scene):
[ ] Subtext: Does every line have a hidden agenda? No one says what they mean?
[ ] Voiceprint: Could you identify each speaker without names?
[ ] Silence: Is the strongest emotion SHOWN, not SAID?
[ ] Economy: No balloon over 15 words? No panel over 2 balloons?
[ ] Ma: Is there at least one panel with ZERO dialogue in every scene?
================================================================================
"""

# ============================================================================
# STAYING POWER PROTOCOL (Operation Olympius — Longevity Audit)
# Four engines: Infinite Engine (Heraclitus), Living Wound (Socrates), Ten Twist (Laozi), Empty Cup (Sun Tzu)
# Plus: 10-Chapter Audit cycle, Anti-Flanderization, Kishōtenketsu Pacing
# Activated via --mode longevity-audit
# ============================================================================

# 1. THE INFINITE ENGINE (Heraclitus + Sun Tzu — Conflict Architecture)
# Ensures conflict survives the death of any single villain
INFINITE_ENGINE = {
    "base_rule": "Great conflict does not resolve; it transforms. The story must survive the death of the main villain.",
    "philosophers": "Heraclitus (Unity of Opposites) + Sun Tzu (Strategic Depth)",
    "the_test": {
        "fail": "Hero vs. Demon King. (Ends when the Demon King dies. Story over.)",
        "pass": "Freedom vs. Control (Symbiotic). Freedom needs Control to define itself. Control needs Freedom to justify itself. The war changes faces but the philosophical engine never stops.",
    },
    "conflict_grades": {
        "TARTAREAN": "Good Guy vs. Bad Guy. Binary. Story dies when villain dies.",
        "SISYPHEAN": "Hero vs. System. Slightly better — the system can regenerate. But the hero's motivation is still external.",
        "SPARTAN": "Philosophy vs. Philosophy. Both sides have valid arguments. But the conflict is still framed as 'who wins.'",
        "PROMETHEAN": "Unity of Opposites. Both sides NEED each other. Victory for one side destroys both. The conflict is about transformation, not resolution.",
        "OLYMPIAN": "The conflict IS the human condition. It cannot be resolved because it is a permanent tension in existence (Freedom vs. Security, Creation vs. Destruction, Individual vs. Collective). The story explores every facet across hundreds of chapters.",
    },
    "reframe_examples": {
        "bad": "[PROTAGONIST] vs. [ANTAGONIST].",
        "good": "[PROTAGONIST'S PHILOSOPHY] (Chaos) vs. [ANTAGONIST'S PHILOSOPHY] (Order/The System).",
        "why": "Even if [PROTAGONIST] defeats [ANTAGONIST] in Chapter 50, the opposing philosophy can take a new form — a corrupt ally, a well-meaning reformer, or [PROTAGONIST] themselves becoming the thing they fought. The engine produces infinite fuel."
    },
    "action": "Use the Synthesis Codex Transmutation Table: reframe 'Hero vs. Villain' as 'Order vs. Chaos (Symbiotic).' Make the antagonist's worldview philosophically defensible. If the villain is RIGHT about something, the debate (and the story) lasts forever."
}

# 2. THE LIVING WOUND (Socrates + Transmutation Table — Protagonist Engine)
# Ensures protagonist motivation is internal, costly, and inexhaustible
LIVING_WOUND = {
    "base_rule": "The protagonist's power must come from what they have LOST, not what they have gained. The wound is not a flashback — it actively warps every decision they make today.",
    "philosopher": "Socrates (Bedrock Motivation) + Synthesis Codex (Cultivation Through Loss)",
    "the_test": {
        "fail": "[PROTAGONIST] fights because they are 'The Chosen One' to save the world. (External. Flimsy. Story ends when world is saved.)",
        "pass": "[PROTAGONIST] loses something irreplaceable every time they use their power. Their power IS their curse. They fight not to save the world but to hold onto enough of themselves to remember WHY they're fighting.",
    },
    "wound_grades": {
        "TARTAREAN": "No wound. Hero fights because plot says so. 'Chosen One' motivation.",
        "SISYPHEAN": "Tragic Backstory. Dead parents, burned village. Decoration — informs the character but doesn't cost them anything ongoing.",
        "SPARTAN": "Active Cost. The power has a price (health, lifespan, sanity). But the cost is predictable and manageable.",
        "PROMETHEAN": "Living Wound. The wound actively distorts perception, relationships, and decisions. The reader can trace every mistake back to the wound.",
        "OLYMPIAN": "The wound IS the theme. The protagonist's personal damage mirrors the story's central philosophical question. The protagonist's ongoing loss IS the story's question about whether [their pursuit] is worth the cost of [what they lose].",
    },
    "transmutation": "Cultivation Through Loss — the protagonist grows by being stripped away, not by gaining new powers. Every level-up costs something irreplaceable.",
    "five_questions": [
        "1. What did the protagonist lose that they can never get back?",
        "2. How does this loss warp their decision-making TODAY (not just in flashbacks)?",
        "3. Does their power directly feed the wound? (Cost mechanism)",
        "4. Can the reader trace the protagonist's worst mistake back to the wound?",
        "5. Is the wound the same question as the story's theme? (If yes: OLYMPIAN)",
    ]
}

# 3. THE TEN TWIST (Synthesis Codex + Laozi — Structural Expansion)
# Ensures twists recontextualize rather than just surprise
TEN_TWIST = {
    "base_rule": "The Twist must be a Recontextualization, not a 'Gotcha.' It should make the reader re-read the previous 50 chapters and realize they misunderstood the genre.",
    "philosophers": "Laozi (Philosophical Depth) + Synthesis Codex (Kishōtenketsu 'Ten')",
    "the_test": {
        "fail": "'The mentor was the villain all along!' (Shock value. Changes who the enemy is, not what the story means.)",
        "pass": "'The entire war was manufactured by both sides to maintain the status quo.' (Changes what the STORY is about. The reader realizes they were reading a different genre.)",
    },
    "twist_grades": {
        "TARTAREAN": "No twist. Linear plot from A to B. The reader predicts everything.",
        "SISYPHEAN": "Gotcha Twist. Someone was secretly evil. Shock value only — the story means the same thing before and after.",
        "SPARTAN": "Perspective Shift. The reader learns new information that changes who they root for. Good, but the world doesn't expand.",
        "PROMETHEAN": "Recontextualization. The reader realizes the story is bigger than they thought. New questions open up. The world expands.",
        "OLYMPIAN": "Genre Shift. The reader realizes they were reading the WRONG GENRE. Attack on Titan shifts from 'Survival Horror' to 'Geopolitical Tragedy.' One Piece shifts from 'Adventure' to 'Revolutionary Epic.' The story becomes infinite because its scope exploded.",
    },
    "kishōtenketsu": {
        "ki": "Introduction — Establish the world and its apparent rules.",
        "shō": "Development — Deepen the world within those rules. Build trust.",
        "ten": "Twist / Recontextualization — BREAK the rules. The world is not what it seemed. This is where staying power is built.",
        "ketsu": "Reconciliation — NOT resolution. The reader reconciles the old world with the new. But the new world opens MORE questions than it answers.",
    },
    "laozi_test": "Does the twist provide a DEEP PHILOSOPHICAL SHIFT? If the twist doesn't change the MEANING of the story, delete it."
}

# 4. THE EMPTY CUP (Sun Tzu + Laozi — Information Economy)
# Controls information release to sustain fan engagement for hundreds of chapters
EMPTY_CUP = {
    "base_rule": "Fandoms live in the 'Ma' (Negative Space). If you explain the magic system perfectly in Chapter 1, the community has nothing to talk about. You must keep the reader in a state where they are desperate to know what you are hiding.",
    "philosophers": "Sun Tzu (Information Asymmetry / Deception Score) + Laozi (Empty Cup / Ma)",
    "information_economy": {
        "answers_per_arc": "Each story arc should answer 1 major question and open 2-3 new ones.",
        "lore_drip": "Never explain more than 30% of any system in a single chapter. The remaining 70% is community fuel.",
        "feint_before_reveal": "Before every major reveal, plant a WRONG answer that the community will debate. When the truth drops, the shock is doubled.",
        "the_empty_cup": "The reader's cup must always be partially empty. A full cup (everything explained) kills engagement. An empty cup (nothing explained) kills trust. The sweet spot: the reader has ENOUGH to theorize but NEVER enough to be certain.",
    },
    "deception_score": {
        "TARTAREAN": "Zero mystery. Everything explained as it appears. Wiki-dump in Chapter 1.",
        "SISYPHEAN": "Mysteries exist but are trivially solvable. The reader figures it out 20 chapters before the reveal.",
        "SPARTAN": "Good mysteries. The reader has theories but can't be certain. Reveals are satisfying.",
        "PROMETHEAN": "The reader's theory was CLOSE but wrong in an important way. The reveal recontextualizes their theory. They feel smart AND surprised.",
        "OLYMPIAN": "The fandom's collective theories become part of the experience. The community debates generate content that EXTENDS the story's cultural footprint. The mystery is an engine, not a puzzle.",
    },
    "10_chapter_audit": {
        "purpose": "Every 10 chapters, convene the Council for a Longevity Audit.",
        "checks": [
            "HERACLITUS: Has the central conflict TRANSFORMED in the last 10 chapters, or just escalated?",
            "SOCRATES: Is the protagonist still acting from their Living Wound, or have they drifted into generic hero behavior? (Anti-Flanderization)",
            "SUN TZU: Has the Information Asymmetry shifted? Are we giving answers or better questions?",
            "PLATO: Is the thematic depth increasing? Can a new reader still enter, and can a veteran still discover?",
            "VISUAL ANCHORS: Run a Drift Detection audit on all character renders from the last 10 chapters.",
        ],
    }
}

# THE COMPLETE STAYING POWER PROMPT BLOCK (Operation Olympius)
STAYING_POWER_BLOCK = """
================================================================================
OPERATION OLYMPIUS — STAYING POWER PROTOCOL
Paste this block into the LLM context window for longevity audits.
================================================================================

CONVENE THE COUNCIL: OPERATION OLYMPIUS

1. HERACLITUS (Infinite Engine): Audit the central conflict.
   TEST: Is it 'Good vs. Evil' (TARTAREAN) or 'Unity of Opposites' (OLYMPIAN)?
   RULE: The conflict must survive the death of the main villain.
   If the story ends when the villain dies, the engine is broken.

2. SOCRATES (Living Wound): Apply the Bedrock Motivation test.
   TEST: Does the protagonist's power COST them something irreplaceable?
   RULE: The wound must actively warp decisions TODAY, not just exist in flashbacks.
   Run the Five Questions. If any answer is 'no,' the wound is cosmetic.

3. PLATO (Elevation Score): What is the ETERNAL QUESTION this story asks?
   TEST: Can you state the theme in one sentence that applies to all humans?
   RULE: If the answer is simple, complicate it. If it resolves, the story resolves.

4. SUN TZU (Empty Cup / Deception Score): Check Information Asymmetry.
   TEST: Are we giving the reader answers, or better questions?
   RULE: Each arc answers 1 question and opens 2-3 new ones.
   Never explain more than 30% of any system in a single chapter.

5. LAOZI (Ten Twist): Audit the last major twist.
   TEST: Does it recontextualize, or just surprise?
   RULE: If the twist doesn't change what the STORY MEANS, delete it.

6. SYNTHESIS CHECK: Run the Transmutation Table.
   TEST: Are we using 'Chosen Gear' (not 'Chosen One')?
   Is the backstory a 'Living Wound' (not 'Tragic Backstory')?
   Does the mentor 'Dissolve' (not 'Die')?

GOAL: Construct a narrative engine that creates infinite fuel,
      not a linear path to an ending.

10-CHAPTER AUDIT CYCLE:
Every 10 chapters, re-run this protocol. Check for:
[ ] Conflict: Has it TRANSFORMED, not just escalated?
[ ] Character: Acting from wound, or drifted to generic hero? (Anti-Flanderization)
[ ] Information: Giving answers or better questions?
[ ] Theme: Depth increasing? New readers can enter, veterans discover?
[ ] Visuals: Run Drift Detection on all character renders.
================================================================================
"""

# ============================================================================
# THE MASTER SERVANT WORKFLOW (Forge Blade Pipeline)
# The strict 3-step Olympian production pipeline: Soul → Script → Visual
# Activated via --forge-blade flag (enables ALL systems in correct sequence)
# ============================================================================

MASTER_WORKFLOW = {
    "kill_phrase": "The Agora Engine is not a filter. It is a forge. Stories enter as raw ore. They leave as blades.",
    "philosophy": "Do not use the engine randomly. Follow the Olympian pipeline. Each phase builds on the last. Skip a step and the blade is brittle.",
    "phases": {
        "phase_1_soul_check": {
            "name": "PHASE 1: THE SOUL CHECK (Before Writing)",
            "when": "Before you write a single line or draw a single panel.",
            "command": "--mode longevity-audit --staying-power",
            "systems_active": ["Infinite Engine (Heraclitus)", "Living Wound (Socrates)", "Ten Twist (Laozi)", "Empty Cup (Sun Tzu)"],
            "queries": [
                "Does the conflict survive the death of the main villain? (Infinite Engine)",
                "Does the protagonist's power COST them something irreplaceable? (Living Wound)",
                "Does the 'Ten' (Twist) recontextualize the GENRE, or just surprise the reader? (Ten Twist)",
                "Are we giving the reader answers, or better questions? (Empty Cup)",
            ],
            "goal": "Ensure the story engine is INFINITE before you draw a single line.",
            "fail_condition": "If the story ends when the villain dies, STOP. Reframe the conflict as a philosophical war.",
            "output": "Conflict Grade (Tartarean→Olympian), Wound Grade, Twist Grade, Deception Score.",
        },
        "phase_2_script_forge": {
            "name": "PHASE 2: THE SCRIPT FORGE (During Writing)",
            "when": "When writing dialogue, scene scripts, and narrative beats.",
            "command": "--mode dialogue-forge",
            "systems_active": ["Subtext Layer (Sun Tzu)", "Voiceprint (Socrates)", "Silence Audit (Laozi + Seneca)", "Balloon Economy (Marcus Aurelius)"],
            "queries": [
                "Generate a Subtext Table for every conversation (Surface Text vs. Strategic Intent vs. The Lie).",
                "Apply Syntax Anchors — cover the names, can you still tell who's talking?",
                "Identify the emotional peak line of this scene and DELETE IT. Replace with a Visual Acting Prompt.",
                "No balloon over 15 words. No panel over 2 balloons. Break monologues across panels.",
            ],
            "goal": "Show, don't tell. Maximum tension, minimal word count.",
            "fail_condition": "If a character states their feelings directly, the Subtext Layer has failed.",
            "output": "Subtext Tables, Voiceprint-locked script, Silence Audit replacements, Balloon-economy compliant layout.",
        },
        "phase_3_visual_direction": {
            "name": "PHASE 3: THE VISUAL DIRECTION (Visual Production)",
            "when": "When generating panel art, image prompts, and layout instructions.",
            "command": "--mode prompt-architect --cinematography --kinetic-audit",
            "systems_active": ["Shot List Generator (Sun Tzu)", "Thermal Conflict Script (Heraclitus)", "Gutter Breath Metric (Laozi)", "Torsional Stress (Heraclitus)", "Micro-Anatomy (Socrates)", "Kinetic Camera (Sun Tzu)"],
            "queries": [
                "Shot List: What camera angle serves this narrative beat? (Dutch Angle for deception, Low Angle for power, etc.)",
                "Thermal Conflict: What color temperature reflects the emotional conflict? (Split Warm/Cool for opposing forces, etc.)",
                "Gutter Breath: How much scroll space does this beat need? (300px for grief, zero for action, etc.)",
                "Torsional Stress: Are shoulders and hips counter-rotated? Is the center of gravity off-balance?",
                "Micro-Anatomy: Are we prompting for MUSCLES, not emotions?",
                "Kinetic Camera: Is the camera angle aggressive enough? No flat eye-level for action.",
            ],
            "goal": "Generate prompts that include Shot Lists (Camera), Thermal Conflict (Color), Gutter Breath (Spacing), and Anti-Stiffness (Posing + Faces + Angles).",
            "fail_condition": "If the prompt says '[CHARACTER] holding [object]' instead of directing the SHOT, the pipeline has failed.",
            "output": "Per-scene Cinematography Directives + Cinematic Visual Prompts with Anti-Stiffness modifiers.",
        },
    },
    "mega_command": "python3 agora_engine.py story.md --mode session --staying-power --dialogue-forge --cinematography --kinetic-audit",
    "mega_command_description": "The Top 1% Configuration. Runs ALL systems in sequence. The resulting output covers: Narrative (philosophical conflict + living wound + subtextual dialogue), Visual (directed camera + color grading + scroll spacing + dynamic posing). This is the Forge at maximum heat.",
}

# THE FORGE BLADE PROMPT BLOCK (Ready-to-paste — activates ALL systems in sequence)
FORGE_BLADE_BLOCK = """
================================================================================
THE FORGE BLADE — MASTER SERVANT WORKFLOW (Top 1% Configuration)
Paste this block to activate the full Olympian production pipeline.
================================================================================

"The Agora Engine is not a filter. It is a forge.
 Stories enter as raw ore. They leave as blades."

================================================================================
PHASE 1: THE SOUL CHECK (Before Writing)
================================================================================
Run: --mode longevity-audit --staying-power

HERACLITUS (Infinite Engine):
  → Does the conflict survive the death of the main villain?
  → Reframe from "Good vs. Evil" to "Unity of Opposites."
  → If the villain dies and the story ends, you have FAILED.

SOCRATES (Living Wound):
  → Does the hero's power COST them something irreplaceable?
  → Stop giving "Tragic Backstories" (flashbacks). Give "Living Wounds" (active distortions).
  → Every power-up = a loss. Cultivation Through Loss, not Training Arc.

LAOZI (Ten Twist):
  → Does the Twist recontextualize the GENRE, or just surprise?
  → Attack on Titan: "Survival Horror" → "Geopolitical Tragedy." THAT is a Ten.

SUN TZU (Empty Cup):
  → Each arc: answer 1 question, open 2-3 new ones.
  → Never explain more than 30% of any system in one chapter.

GATE: If any check fails, DO NOT proceed to Phase 2. Fix the soul first.

================================================================================
PHASE 2: THE SCRIPT FORGE (During Writing)
================================================================================
Run: --mode dialogue-forge

SUN TZU (Subtext Layer):
  → Generate a Subtext Table BEFORE writing dialogue.
  → Surface Text | Strategic Intent | The Lie.
  → No character states feelings directly. Character is scared? "The [object] feels heavier today."

SOCRATES (Voiceprint):
  → Apply Syntax Anchors. Cover the names — reader must still know who's talking.
  → Define unique syntax DNA per character (e.g., Fractured/Internal vs. Absolute/Clinical).

LAOZI + SENECA (Silence Audit):
  → Find the emotional peak line. DELETE IT.
  → Replace with a Visual Acting Prompt: "[CHARACTER]'s hand stops shaking."

MARCUS AURELIUS (Balloon Economy):
  → No balloon > 15 words. No panel > 2 balloons.
  → Break monologues across panels with visual beats between.

GATE: If dialogue explains the plot, the Script Forge has failed. Go back.

================================================================================
PHASE 3: THE VISUAL DIRECTION (Visual Production)
================================================================================
Run: --mode prompt-architect --cinematography --kinetic-audit

SUN TZU (Shot List):       Camera angle for every narrative beat.
HERACLITUS (Thermal):      Color grade for every emotional conflict.
LAOZI (Gutter Breath):     Scroll spacing for every emotional weight.
HERACLITUS (Torsional):    Shoulders/hips NEVER parallel. Bodies store energy.
SOCRATES (Micro-Anatomy):  Muscles, not emotions. Faces are machines.
SUN TZU (Kinetic Camera):  No flat eye-level for action or intensity.

GATE: If the prompt says "[CHARACTER] holding [object]" instead of directing the SHOT,
      the Visual Direction has failed. Go back.

================================================================================
THE RESULTING BLADE:
1. Narrative: Conflict is philosophical (Heraclitus). Protagonist driven by loss
   (Socrates). Dialogue is subtextual (Sun Tzu). Silence carries weight (Laozi).
2. Visual: Camera moves vertically (Kinetic Flow). Color grading reflects
   emotional conflict (Thermal Script). Characters move with anatomical tension
   (Anti-Stiffness). Scroll spacing controls reader's heartbeat (Gutter Breath).
================================================================================
"""

# ============================================================================
# 🏁 CINEMATOGRAPHY AUDIT (Immediate 3-Point Chapter Check)
# Quick diagnostic to apply to any chapter for instant improvement
# No philosophy lectures — just action items
# ============================================================================

CINEMATOGRAPHY_AUDIT = {
    "purpose": "Apply this 3-point audit to any chapter for immediate improvement.",
    "checks": {
        "gutters": {
            "name": "CHECK YOUR GUTTERS",
            "question": "Are all your gutters the same size?",
            "fail": "Uniform gutters throughout the chapter.",
            "fix": "Action gutters → 0px (Combat Stack). Emotional gutters → 300px (Grief Scroll). Transitions → 150px gradient (Transition Bridge). Comedy → 50px snap cut.",
            "test": "Scroll through at reading speed. If the pacing feels the same everywhere, the gutters are wrong.",
        },
        "poses": {
            "name": "CHECK YOUR POSES",
            "question": "Is anyone standing straight up with parallel shoulders and hips?",
            "fail": "Characters standing symmetrically like mannequins.",
            "fix": "Twist their torso or tilt the camera. Shoulders and hips NEVER parallel. Move center of gravity outside the base of support.",
            "test": "The Physics Test: draw a vertical line from center of mass. If it lands between the feet, the character is a statue.",
        },
        "camera": {
            "name": "CHECK YOUR CAMERA",
            "question": "Are you using eye-level, medium-distance shots for intensity?",
            "fail": "Flat camera angles for combat or dramatic moments.",
            "fix": "Dutch Angle (15-45°) for tension. Worm's-Eye for power. Extreme Close-Up for psychological pressure.",
            "test": "The Lens Test: can you name the virtual lens for every panel? If not, the camera isn't doing anything.",
        },
    },
    "kill_phrase": "If all three checks pass, the chapter is directed. If any fail, you are drawing panels, not telling a story.",
}

def print_header(text):
    print("\n" + "="*80)
    print(f" {text}")
    print("="*80)

def main():
    parser = argparse.ArgumentParser(description="The Agora Engine v8.0 — The Session Architect (Prompt Generator)")
    parser.add_argument("story_file", help="Path to the story markdown file")
    parser.add_argument("--mode", choices=["session", "prompt-architect", "quick-fire", "dialogue-forge", "longevity-audit", "forge-blade", "visual-director", "character-lab"], default="session",
                        help="Mode selection (Strike Teams included)")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                        help="Output format")
    parser.add_argument("--debug-parser", action="store_true", help="Print parsed lore entities and exit")
    parser.add_argument("--character", help="Include visual anchors for a specific character")
    parser.add_argument("--cinematography", action="store_true",
                        help="Enable Art Director mode: generates Shot List (Sun Tzu), Color Grade (Heraclitus), and Gutter Instructions (Laozi) for each scene")
    parser.add_argument("--kinetic-audit", action="store_true",
                        help="Enable Anti-Stiffness Protocol: injects Torsional Stress (Heraclitus), Micro-Anatomy (Socrates), and Kinetic Camera (Sun Tzu) into every prompt")
    parser.add_argument("--dialogue-forge", action="store_true", dest="dialogue_forge_flag",
                        help="Enable Dialogue Forge on session mode: injects Subtext Layer (Sun Tzu), Voiceprint (Socrates), Silence Audit (Laozi), Balloon Economy (Marcus Aurelius)")
    parser.add_argument("--staying-power", action="store_true", dest="staying_power_flag",
                        help="Enable Operation Olympius on session mode: runs Infinite Engine, Living Wound, Ten Twist, and Empty Cup audits")
    parser.add_argument("--forge-blade", action="store_true", dest="forge_blade_flag",
                        help="The Top 1%% Configuration: activates ALL systems (Staying Power + Dialogue Forge + Cinematography + Kinetic Audit) in the Master Servant pipeline")
    parser.add_argument("--cine-audit", action="store_true", dest="cine_audit_flag",
                        help="Quick 3-point Cinematography Audit: Check gutters, poses, and camera angles for immediate improvement")

    args = parser.parse_args()

    # FORGE BLADE: The Top 1% Configuration — activates ALL systems
    if args.forge_blade_flag or args.mode == "forge-blade":
        args.staying_power_flag = True
        args.dialogue_forge_flag = True
        args.cinematography = True
        args.kinetic_audit = True

    # Parse Lore
    entities = LoreParser.parse_file(args.story_file)
    if args.debug_parser:
        print(json.dumps(entities, indent=4))
        sys.exit(0)

    # Manage State
    state = StateStore()
    if entities:
        state.sync_lore(entities)

    # Strike Team Filtering
    active_philosophers = PHILOSOPHERS
    if args.mode == "visual-director":
        active_philosophers = [p for p in PHILOSOPHERS if p.name in ("Sun Tzu", "Heraclitus", "Laozi")]
        args.cinematography = True
        args.kinetic_audit = True
    elif args.mode == "character-lab":
        active_philosophers = [p for p in PHILOSOPHERS if p.name in ("Socrates", "Seneca", "Diogenes")]
        args.dialogue_forge_flag = True

    story_path = args.story_file
    if not os.path.exists(story_path):
        print(f"Error: File {story_path} not found.")
        sys.exit(1)

    with open(story_path, 'r') as f:
        story_content = f.read()

    version = "v7.0 — THE LIVING AGORA"

    output_data = {
        "engine": "The Agora Engine",
        "version": version,
        "material": story_path,
        "mode": args.mode,
        "entities": entities,
        "philosophers": [p.name for p in active_philosophers]
    }

    if args.format == "text":
        print_header(f"THE AGORA ENGINE {version}")
        print(f"Material: {story_path}")
        print(f"Mode: {args.mode.upper()}")
        print(f"Council: {len(active_philosophers)} Philosophers")

    anchors = ""
    if args.character:
        # Check state first, then fallback
        char_key = next((c for c in state.data["characters"] if c.lower() == args.character.lower()), None)
        if char_key:
            anchors = state.data["characters"][char_key]["anchors"]
        else:
            anchors = "[No anchors defined for {}]".format(args.character)

        if args.format == "text":
            print(f"Character Anchor ({args.character}): {anchors}")

    if args.mode == "session":
        if args.format == "text":
            # Phase 1
            print_header("PHASE 1: THE READING")
            print(f"[SYSTEM] Material size: {len(story_content)} characters.")

            # Phase 2
            print_header("PHASE 2: OPENING STATEMENTS")
            for p in active_philosophers:
                print(f"{p.emoji} {p.name.upper()}: [Analyzing {p.domain}]")

            # Phase 3
            print_header("PHASE 3: THE DEBATE (Moderated by Marcus Aurelius)")
            print("Suggested Interjections:")
            print("- Aristotle vs. Plato: 'Does the structure support the theme, or is it just a vessel?'")
            print("- Eastern/Western Synthesis: 'Is this true Eastern writing of Western themes, or just a Western plot in a manga skin?'")
            print("- Cinematic Quality Check: 'Are we maintaining Key Visual Density? Is every frame cinematic, or are we seeing drifting?'")
            print("- Laozi vs. Marcus Aurelius: 'Is your discipline killing the organic flow?'")
            print("- Sun Tzu: 'Have we maneuvered the reader into the intended emotional state?'")

            print_header("PHASE 3.5: THE GAVEL (Convergence)")
            print("⚖️ MARCUS AURELIUS delivers Convergence Summary (3-5 sentences).")
            print("Each philosopher casts a one-word rating vote.")
            print("Marcus Aurelius announces the majority ruling.")

            # Phase 4
            print_header("PHASE 4: THE VERDICT")
            print("Rating Categories: Olympian | Promethean | Spartan | Athenian | Sisyphean | Tartarean")
            print("\n[REQUIRED OUTPUTS]:")
            print("1. The Laurel (Strengths)")
            print("2. The Hemlock (Fatal Flaws)")
            print("3. The Forge List (Actionable Improvements)")
            print("4. Final Composite Score")

        output_data["phases"] = ["Reading", "Opening Statements", "Debate", "Verdict"]

    elif args.mode == "prompt-architect":
        if args.format == "text":
            print_header("PROMPT ARCHITECT MODE")
            print(f"PROMPT: [Scene Description], {STYLE_BASE}, {anchors}, [Philosopher Modifiers]")

        output_data["prompt_base"] = STYLE_BASE
        output_data["character_anchors"] = anchors
        output_data["modifiers"] = {p.name: p.prompt_modifiers for p in active_philosophers}

        # CINEMATOGRAPHY DIRECTOR MODE (--cinematography flag)
        if args.cinematography:
            if args.format == "text":
                print_header("🎬 CINEMATOGRAPHY DIRECTOR MODE (Art Director)")
                print("The following systems transform scene descriptions into directed shots.\n")
                print("For each scene, the LLM must output ALL THREE directives:\n")

                # Shot List
                print_header("📐 SHOT LIST GENERATOR (Sun Tzu's Tactical Framing)")
                print("Maps narrative beats → Camera angles from Kinetic Flow logic.\n")
                for key, shot in SHOT_LIST.items():
                    print(f"  [{key.upper()}]")
                    print(f"    Trigger:  {shot['trigger']}")
                    print(f"    Camera:   {shot['camera']}")
                    print(f"    Director: {shot['philosopher']}\n")

                # Thermal Conflict
                print_header("🌡️ THERMAL CONFLICT SCRIPT (Heraclitus's Color Grading)")
                print("Maps emotional conflict → Dynamic color temperature directives.\n")
                for key, grade in THERMAL_GRADES.items():
                    print(f"  [{key.upper()}]")
                    print(f"    Trigger:  {grade['trigger']}")
                    print(f"    Grade:    {grade['grade']}")
                    print(f"    Director: {grade['philosopher']}\n")

                # Gutter Breath
                print_header("🫁 GUTTER BREATH METRIC (Laozi's Panel Pacing)")
                print("Maps emotional weight → Vertical scroll spacing instructions.\n")
                for key, gutter in GUTTER_BREATH.items():
                    print(f"  [{key.upper()}]")
                    print(f"    Trigger:  {gutter['trigger']}")
                    print(f"    Spacer:   {gutter['spacer']}")
                    print(f"    Panel:    {gutter['panel_instruction']}")
                    print(f"    Director: {gutter['philosopher']}\n")

                # Output Format Template
                print_header("📋 CINEMATOGRAPHY OUTPUT FORMAT (Per Scene)")
                print("For each scene in the story, the LLM must produce:\n")
                print("┌─────────────────────────────────────────────────────────┐")
                print("│ SCENE: [Scene Description]                              │")
                print("│                                                         │")
                print("│ 1. SHOT TYPE (Sun Tzu):                                 │")
                print("│    Camera: [e.g., Low Angle Tracking Shot]              │")
                print("│    Modifiers: [e.g., Motion Blur, Speed Lines]          │")
                print("│                                                         │")
                print("│ 2. COLOR GRADE (Heraclitus):                            │")
                print("│    Temperature: [e.g., Clashing / Warm→Cool Split]      │")
                print("│    Palette: [e.g., Orange/Teal Complementary]           │")
                print("│                                                         │")
                print("│ 3. GUTTER INSTRUCTION (Laozi):                          │")
                print("│    Spacing: [e.g., 300px whitespace / Zero gutter]      │")
                print("│    Panel Rule: [e.g., Full-width, no overlap]           │")
                print("│                                                         │")
                print("│ 4. VISUAL PROMPT (Combined):                            │")
                print("│    [Scene], [Style Base], [Character Anchors],          │")
                print("│    [Shot Modifiers], [Color Grade], [Philosopher Mods]  │")
                print("└─────────────────────────────────────────────────────────┘")

            # JSON output for cinematography
            output_data["cinematography"] = {
                "shot_list": {k: {"trigger": v["trigger"], "camera": v["camera"], "philosopher": v["philosopher"]} for k, v in SHOT_LIST.items()},
                "thermal_grades": {k: {"trigger": v["trigger"], "grade": v["grade"], "philosopher": v["philosopher"]} for k, v in THERMAL_GRADES.items()},
                "gutter_breath": {k: {"trigger": v["trigger"], "spacer": v["spacer"], "panel_instruction": v["panel_instruction"], "philosopher": v["philosopher"]} for k, v in GUTTER_BREATH.items()},
            }

        # ANTI-STIFFNESS PROTOCOL (--kinetic-audit flag)
        if args.kinetic_audit:
            if args.format == "text":
                print_header("💀 ANTI-STIFFNESS PROTOCOL (Kinetic Audit)")
                print("Converts the engine from a Statue Builder into an Action Director.\n")

                # Torsional Stress
                print_header("🔥 TORSIONAL STRESS (Heraclitus + Epicurus — Body Dynamics)")
                print(f"BASE RULE: {TORSIONAL_STRESS['base_rule']}")
                print(f"MODIFIERS: {TORSIONAL_STRESS['modifiers']}\n")
                for key, panel in TORSIONAL_STRESS["panel_types"].items():
                    print(f"  [{key.upper()}]")
                    print(f"    Trigger:   {panel['trigger']}")
                    print(f"    Injection: {panel['injection']}")
                    print(f"    Rule:      {panel['rule']}\n")

                # Micro-Anatomy
                print_header("❓ SOCRATIC MICRO-ANATOMY (Socrates — Facial Mechanics)")
                print(f"BASE RULE: {MICRO_ANATOMY['base_rule']}")
                print(f"MODIFIERS: {MICRO_ANATOMY['modifiers']}\n")
                for emotion, mapping in MICRO_ANATOMY["emotion_to_muscle_map"].items():
                    print(f"  [{emotion.upper()}]")
                    print(f"    ❌ WRONG: {mapping['wrong']}")
                    print(f"    ✅ RIGHT: {mapping['right']}")
                    print(f"    🔍 NOTE:  {mapping['socrates_note']}\n")

                # Kinetic Camera
                print_header("🚩 KINETIC CAMERA (Sun Tzu — Camera Dynamics)")
                print(f"BASE RULE: {KINETIC_CAMERA['base_rule']}")
                print(f"MODIFIERS: {KINETIC_CAMERA['modifiers']}\n")
                for key, scene in KINETIC_CAMERA["scene_types"].items():
                    print(f"  [{key.upper()}]")
                    print(f"    Trigger:   {scene['trigger']}")
                    print(f"    Injection: {scene['injection']}")
                    print(f"    Rule:      {scene['rule']}\n")

                # The Ready-to-Paste Block
                print_header("📋 ANTI-STIFFNESS PROMPT BLOCK (Copy-Paste Into Context Window)")
                print(ANTI_STIFFNESS_BLOCK)

            # JSON output for kinetic audit
            output_data["kinetic_audit"] = {
                "torsional_stress": {
                    "base_rule": TORSIONAL_STRESS["base_rule"],
                    "modifiers": TORSIONAL_STRESS["modifiers"],
                    "panel_types": {k: {"trigger": v["trigger"], "injection": v["injection"]} for k, v in TORSIONAL_STRESS["panel_types"].items()}
                },
                "micro_anatomy": {
                    "base_rule": MICRO_ANATOMY["base_rule"],
                    "modifiers": MICRO_ANATOMY["modifiers"],
                    "emotion_map": {k: {"wrong": v["wrong"], "right": v["right"]} for k, v in MICRO_ANATOMY["emotion_to_muscle_map"].items()}
                },
                "kinetic_camera": {
                    "base_rule": KINETIC_CAMERA["base_rule"],
                    "modifiers": KINETIC_CAMERA["modifiers"],
                    "scene_types": {k: {"trigger": v["trigger"], "injection": v["injection"]} for k, v in KINETIC_CAMERA["scene_types"].items()}
                },
                "prompt_block": ANTI_STIFFNESS_BLOCK
            }

    elif args.mode == "quick-fire":
        # Mercenary Mode: Only Marcus Aurelius (Pacing) + Epicurus (Fun)
        quick_fire_council = active_philosophers = [p for p in PHILOSOPHERS if p.name in ("Marcus Aurelius", "Epicurus")]
        if args.format == "text":
            print_header("QUICK-FIRE MODE (Mercenary)")
            print("Council: Marcus Aurelius (Pacing) + Epicurus (Fun)")
            print(f"[SYSTEM] Material size: {len(story_content)} characters.\n")
            for p in quick_fire_council:
                print(f"{p.emoji} {p.name.upper()} ({p.title}):")
                print(f"  > [Rapid analysis: {p.domain}]")
                print(f"  > Prompt: 'As {p.name}, give a rapid 2-3 sentence verdict on this story from your domain.'\n")
            print_header("QUICK-FIRE VERDICT")
            print("[REQUIRED OUTPUTS]:")
            print("1. Pacing Grade (Marcus Aurelius): TIGHT / LOOSE / BLOATED")
            print("2. Fun Grade (Epicurus): HYPE / FLAT / DEAD")
            print("3. Top 3 Actionable Fixes (ranked by impact)")
        output_data["mode"] = "quick-fire"
        output_data["quick_fire_council"] = [p.name for p in quick_fire_council]

    elif args.mode == "dialogue-forge" or args.dialogue_forge_flag:
        # Dialogue Forge: Award-Winner dialogue direction
        dialogue_council = active_philosophers = [p for p in PHILOSOPHERS if p.name in ("Sun Tzu", "Socrates", "Laozi", "Marcus Aurelius", "Seneca")]
        if args.format == "text":
            print_header("🗡️ DIALOGUE FORGE MODE (Award-Winner Protocol)")
            print("Council: Sun Tzu (Subtext) + Socrates (Voiceprint) + Laozi (Silence) + Marcus Aurelius (Economy)")
            print(f"[SYSTEM] Material size: {len(story_content)} characters.\n")

            # 1. Subtext Layer
            print_header("🚩 SUBTEXT LAYER (Sun Tzu — Text vs. Intent Protocol)")
            print(f"BASE RULE: {SUBTEXT_LAYER['base_rule']}\n")
            print("REQUIRED: Generate a Subtext Table BEFORE writing any dialogue:")
            print(SUBTEXT_LAYER['output_format'])
            print(f"  ❌ BAD:  {SUBTEXT_LAYER['examples']['bad']}")
            print(f"  ✅ GOOD: {SUBTEXT_LAYER['examples']['good']}")
            print(f"  WHY:     {SUBTEXT_LAYER['examples']['analysis']}\n")

            # 2. Voiceprint
            print_header("❓ SOCRATIC VOICEPRINT (Socrates — Syntax Anchors)")
            print(f"BASE RULE: {VOICEPRINT['base_rule']}\n")
            for char_name, anchor in VOICEPRINT['cast_anchors'].items():
                print(f"  [{char_name.upper()}]")
                print(f"    Syntax Class:    {anchor['syntax_class']}")
                print(f"    Sentence Rule:   {anchor['sentence_rule']}")
                print(f"    Vocab Domain:    {anchor['vocabulary_domain']}")
                print(f"    Forbidden Words: {anchor['forbidden_words']}")
                print(f"    ✅ GOOD: {anchor['example_good']}")
                print(f"    ❌ BAD:  {anchor['example_bad']}\n")

            # 3. Silence Audit
            print_header("☯️ SILENCE AUDIT (Laozi + Seneca — Text-to-Visual Converter)")
            print(f"BASE RULE: {SILENCE_AUDIT['base_rule']}\n")
            print("PROTOCOL:")
            for step in SILENCE_AUDIT['protocol_steps']:
                print(f"  {step}")
            print("\nVISUAL ACTING PROMPT EXAMPLES:")
            for emotion, prompt in SILENCE_AUDIT['visual_acting_prompts'].items():
                print(f"  [{emotion.upper()}]: {prompt}")
            print(f"\nTHE TEST: {SILENCE_AUDIT['the_test']}\n")

            # 4. Balloon Economy
            print_header("⚖️ BALLOON ECONOMY (Marcus Aurelius — The Tweet Rule)")
            print(f"BASE RULE: {BALLOON_ECONOMY['base_rule']}\n")
            print("CONSTRAINTS:")
            for key, constraint in BALLOON_ECONOMY['constraints'].items():
                print(f"  • {key}: {constraint}")
            print("\nVIOLATION PENALTIES:")
            for violation, penalty in BALLOON_ECONOMY['violation_penalties'].items():
                print(f"  [{violation}]: {penalty}")
            print(f"\n  ❌ BAD:  {BALLOON_ECONOMY['example']['bad']}")
            print(f"  ✅ GOOD: {BALLOON_ECONOMY['example']['good']}")
            print(f"  WHY:     {BALLOON_ECONOMY['example']['analysis']}")

            # The Ready-to-Paste Block
            print_header("📋 DIALOGUE FORGE PROMPT BLOCK (Copy-Paste Into Context Window)")
            print(DIALOGUE_FORGE_BLOCK)

        output_data["mode"] = "dialogue-forge"
        output_data["dialogue_forge"] = {
            "subtext_layer": {"base_rule": SUBTEXT_LAYER["base_rule"], "protocol": SUBTEXT_LAYER["protocol"]},
            "voiceprint": {"base_rule": VOICEPRINT["base_rule"], "cast_anchors": {k: {kk: vv for kk, vv in v.items() if kk != "example_good" and kk != "example_bad"} for k, v in VOICEPRINT["cast_anchors"].items()}},
            "silence_audit": {"base_rule": SILENCE_AUDIT["base_rule"], "steps": SILENCE_AUDIT["protocol_steps"]},
            "balloon_economy": {"base_rule": BALLOON_ECONOMY["base_rule"], "constraints": BALLOON_ECONOMY["constraints"]},
            "prompt_block": DIALOGUE_FORGE_BLOCK
        }

    elif args.mode == "longevity-audit" or args.staying_power_flag:
        # Operation Olympius: Staying Power / Longevity Audit
        olympius_council = active_philosophers = [p for p in PHILOSOPHERS if p.name in ("Heraclitus", "Socrates", "Plato", "Sun Tzu", "Laozi")]
        if args.format == "text":
            print_header("⚡ OPERATION OLYMPIUS — STAYING POWER PROTOCOL")
            print("Council: Heraclitus (Conflict) + Socrates (Wound) + Plato (Theme) + Sun Tzu (Mystery) + Laozi (Twist)")
            print(f"[SYSTEM] Material size: {len(story_content)} characters.\n")
            print("PURPOSE: Audit this story for 100+ chapter longevity.\n")

            # 1. Infinite Engine
            print_header("🔥 INFINITE ENGINE (Heraclitus + Sun Tzu — Conflict Architecture)")
            print(f"BASE RULE: {INFINITE_ENGINE['base_rule']}\n")
            print("CONFLICT GRADES:")
            for grade, desc in INFINITE_ENGINE['conflict_grades'].items():
                print(f"  [{grade}]: {desc}")
            print(f"\n  ❌ FAIL: {INFINITE_ENGINE['the_test']['fail']}")
            print(f"  ✅ PASS: {INFINITE_ENGINE['the_test']['pass']}")
            print(f"\n  REFRAME:")
            print(f"    BAD:  {INFINITE_ENGINE['reframe_examples']['bad']}")
            print(f"    GOOD: {INFINITE_ENGINE['reframe_examples']['good']}")
            print(f"    WHY:  {INFINITE_ENGINE['reframe_examples']['why']}\n")

            # 2. Living Wound
            print_header("💀 LIVING WOUND (Socrates — Protagonist Engine)")
            print(f"BASE RULE: {LIVING_WOUND['base_rule']}\n")
            print("WOUND GRADES:")
            for grade, desc in LIVING_WOUND['wound_grades'].items():
                print(f"  [{grade}]: {desc}")
            print(f"\n  ❌ FAIL: {LIVING_WOUND['the_test']['fail']}")
            print(f"  ✅ PASS: {LIVING_WOUND['the_test']['pass']}")
            print(f"\nTHE FIVE QUESTIONS:")
            for q in LIVING_WOUND['five_questions']:
                print(f"  {q}")

            # 3. Ten Twist
            print_header("☯️ TEN TWIST (Laozi + Synthesis Codex — Structural Expansion)")
            print(f"BASE RULE: {TEN_TWIST['base_rule']}\n")
            print("TWIST GRADES:")
            for grade, desc in TEN_TWIST['twist_grades'].items():
                print(f"  [{grade}]: {desc}")
            print(f"\n  ❌ FAIL: {TEN_TWIST['the_test']['fail']}")
            print(f"  ✅ PASS: {TEN_TWIST['the_test']['pass']}")
            print(f"\nKISHŌTENKETSU CYCLE:")
            for phase, desc in TEN_TWIST['kishōtenketsu'].items():
                print(f"  [{phase.upper()}]: {desc}")
            print(f"\n  LAOZI TEST: {TEN_TWIST['laozi_test']}")

            # 4. Empty Cup
            print_header("🏺 EMPTY CUP (Sun Tzu + Laozi — Information Economy)")
            print(f"BASE RULE: {EMPTY_CUP['base_rule']}\n")
            print("INFORMATION RULES:")
            for key, rule in EMPTY_CUP['information_economy'].items():
                print(f"  • {key}: {rule}")
            print(f"\nDECEPTION SCORE:")
            for grade, desc in EMPTY_CUP['deception_score'].items():
                print(f"  [{grade}]: {desc}")

            # 10-Chapter Audit
            print_header("📊 10-CHAPTER AUDIT CYCLE")
            print(f"PURPOSE: {EMPTY_CUP['10_chapter_audit']['purpose']}\n")
            print("CHECKS:")
            for check in EMPTY_CUP['10_chapter_audit']['checks']:
                print(f"  • {check}")

            # The Ready-to-Paste Block
            print_header("📋 OPERATION OLYMPIUS PROMPT BLOCK (Copy-Paste Into Context Window)")
            print(STAYING_POWER_BLOCK)

        output_data["mode"] = "longevity-audit"
        output_data["staying_power"] = {
            "infinite_engine": {"base_rule": INFINITE_ENGINE["base_rule"], "conflict_grades": INFINITE_ENGINE["conflict_grades"]},
            "living_wound": {"base_rule": LIVING_WOUND["base_rule"], "wound_grades": LIVING_WOUND["wound_grades"], "five_questions": LIVING_WOUND["five_questions"]},
            "ten_twist": {"base_rule": TEN_TWIST["base_rule"], "twist_grades": TEN_TWIST["twist_grades"], "kishōtenketsu": TEN_TWIST["kishōtenketsu"]},
            "empty_cup": {"base_rule": EMPTY_CUP["base_rule"], "deception_score": EMPTY_CUP["deception_score"], "10_chapter_audit": EMPTY_CUP["10_chapter_audit"]},
            "prompt_block": STAYING_POWER_BLOCK
        }

    # THE FORGE BLADE MODE (Top 1% — Full Pipeline)
    if args.forge_blade_flag or args.mode == "forge-blade":
        if args.format == "text":
            print_header("⚔️ THE FORGE BLADE — MASTER SERVANT WORKFLOW (Top 1% Configuration)")
            print(f'\n"{MASTER_WORKFLOW["kill_phrase"]}"\n')
            print(f"PHILOSOPHY: {MASTER_WORKFLOW['philosophy']}\n")

            for phase_key, phase in MASTER_WORKFLOW["phases"].items():
                print_header(phase["name"])
                print(f"  WHEN:    {phase['when']}")
                print(f"  COMMAND: {phase['command']}")
                print(f"  SYSTEMS: {', '.join(phase['systems_active'])}\n")
                print("  QUERIES:")
                for q in phase["queries"]:
                    print(f"    → {q}")
                print(f"\n  GOAL: {phase['goal']}")
                print(f"  FAIL: {phase['fail_condition']}")
                print(f"  OUTPUT: {phase['output']}\n")

            print_header("📋 THE FORGE BLADE PROMPT BLOCK (Copy-Paste Into Context Window)")
            print(FORGE_BLADE_BLOCK)

        output_data["mode"] = "forge-blade"
        output_data["master_workflow"] = {
            "kill_phrase": MASTER_WORKFLOW["kill_phrase"],
            "mega_command": MASTER_WORKFLOW["mega_command"],
            "phases": {k: {"command": v["command"], "systems": v["systems_active"], "goal": v["goal"]} for k, v in MASTER_WORKFLOW["phases"].items()},
        }

    # 🏁 CINEMATOGRAPHY AUDIT (Quick 3-Point Check)
    if args.cine_audit_flag:
        if args.format == "text":
            print_header("🏁 CINEMATOGRAPHY AUDIT (Immediate 3-Point Chapter Check)")
            print(f"\n{CINEMATOGRAPHY_AUDIT['purpose']}\n")
            for key, check in CINEMATOGRAPHY_AUDIT["checks"].items():
                print(f"  [{check['name']}]")
                print(f"    ❓ {check['question']}")
                print(f"    ❌ FAIL: {check['fail']}")
                print(f"    ✅ FIX:  {check['fix']}")
                print(f"    🔍 TEST: {check['test']}\n")
            print(f"  VERDICT: {CINEMATOGRAPHY_AUDIT['kill_phrase']}")
        output_data["cine_audit"] = CINEMATOGRAPHY_AUDIT

    if args.format == "json":
        print(json.dumps(output_data, indent=4))
    else:
        print("\n" + "-"*80)
        print("PROMPT FOR LLM / NOTEBOOKLM:")
        print("-"*80)

        context_str = ""
        if entities:
            context_str += "\nCONTEXT FOUND:\n"
            if entities["characters"]:
                context_str += "- CHARACTERS: {}\n".format(", ".join(entities["characters"]))
            if entities["factions"]:
                context_str += "- FACTIONS: {}\n".format(", ".join(entities["factions"]))
            if entities["conflict"]:
                context_str += "- CORE CONFLICT: {}\n".format(entities["conflict"][:200] + "...")

            if entities["characters"] and args.mode in ("longevity-audit", "session", "forge-blade"):
                # Generate Conflict Matrix Template
                chars = entities["characters"]
                context_str += "\nREQUIRED: CONFLICT GENOME MATRIX (Phase 1):\n"
                header = " | ".join([""] + chars)
                sep = "---|" * (len(chars) + 1)
                context_str += "| " + header + " |\n"
                context_str += "| " + sep + " |\n"
                for c1 in chars:
                    row = [c1] + ["?" for _ in chars]
                    context_str += "| " + " | ".join(row) + " |\n"

        if args.forge_blade_flag or args.mode == "forge-blade":
            print(f"Act as the FULL Council of Ten in FORGE BLADE mode (Top 1% Configuration).")
            print(context_str)
            print(f"Execute the Master Servant Pipeline in order:")
            print(f"  PHASE 1 (Soul Check): Grade conflict (Infinite Engine), test wound (Living Wound), audit twist (Ten Twist), score mystery (Empty Cup).")
            print(f"  PHASE 2 (Script Forge): Subtext Tables for all dialogue, Voiceprint enforcement, Silence Audit, Balloon Economy.")
            print(f"  PHASE 3 (Visual Direction): Shot List + Thermal Conflict + Gutter Breath + Torsional Stress + Micro-Anatomy + Kinetic Camera.")
            print(f"GATE RULE: If any Phase fails its check, flag it before proceeding.")
            print(f"Goal: Stories enter as raw ore. They leave as blades.")
        elif args.mode == "session" and not args.dialogue_forge_flag and not args.staying_power_flag:
            print(f"Act as the Council of Ten philosophers. Follow the Session Protocol (Phases 1-4).")
            print(context_str)
            print(f"Start with Phase 2: Opening Statements.")
        elif args.mode == "session" and args.dialogue_forge_flag:
            print(f"Act as the Council of Ten. Follow Session Protocol AND apply the Dialogue Forge Protocol.")
            print(context_str)
            print(f"For all dialogue: (1) Subtext Table first, (2) Syntax Anchors enforced, (3) Silence Audit on emotional peaks, (4) Balloon Economy on all text.")
        elif args.mode == "session" and args.staying_power_flag:
            print(f"Act as the Council of Ten. Follow Session Protocol AND run Operation Olympius.")
            print(context_str)
            print(f"Audit: (1) Infinite Engine conflict grade, (2) Living Wound test, (3) Ten Twist recontextualization, (4) Empty Cup information economy, (5) 10-Chapter cycle check.")
        elif args.mode == "dialogue-forge":
            print(f"Act as the Dialogue Forge Council: Sun Tzu, Socrates, Laozi, Marcus Aurelius, Seneca.")
            print(context_str)
            print(f"For this script: (1) Generate Subtext Tables, (2) Apply Syntax Anchors, (3) Run Silence Audit, (4) Enforce Balloon Economy.")
            print(f"Goal: Maximum tension, minimal word count. No character says what they mean.")
        elif args.mode == "longevity-audit":
            print(f"Act as the Olympius Council: Heraclitus, Socrates, Plato, Sun Tzu, Laozi.")
            print(context_str)
            print(f"Run Operation Olympius: (1) Grade the conflict engine, (2) Test the Living Wound, (3) Audit the last Ten Twist, (4) Score Information Asymmetry.")
            print(f"Goal: Construct a narrative engine that creates infinite fuel, not a linear path to an ending.")
        elif args.mode == "quick-fire":
            print(f"Act as ONLY Marcus Aurelius and Epicurus. Deliver a rapid-fire verdict on pacing and fun.")
            print(context_str)
            print(f"Format: Pacing Grade, Fun Grade, Top 3 Fixes.")
        elif args.mode == "visual-director":
            print(f"Act as the VISUAL STRIKE TEAM: Sun Tzu (Camera), Heraclitus (Color), Laozi (Gutter).")
            print(context_str)
            print(f"For each scene: (1) Shot Type, (2) Color Grade, (3) Gutter Instruction, (4) Combined Visual Prompt.")
            print(f"Apply Anti-Stiffness Protocol (Torsional Stress, Micro-Anatomy, Kinetic Camera) to all prompts.")
        elif args.mode == "character-lab":
            print(f"Act as the CHARACTER STRIKE TEAM: Socrates (Depth), Seneca (Pathos), Diogenes (Honesty).")
            print(context_str)
            print(f"Focus on exposing internal contradictions, ensuring emotional restraint, and killing clichés.")
            print(f"Apply Dialogue Forge (Subtext, Voiceprint, Silence Audit) to all character interactions.")
        else:
            if args.cinematography and args.kinetic_audit:
                print(f"Act as the Council in CINEMATOGRAPHY DIRECTOR + KINETIC AUDIT mode.")
                print(f"For each scene: (1) Shot Type, (2) Color Grade, (3) Gutter, (4) Anti-Stiffness applied to Combined Prompt.")
                print(f"ANTI-STIFFNESS ENFORCED: Torsional Stress on bodies, Micro-Anatomy on faces, Kinetic Camera on angles.")
            elif args.cinematography:
                print(f"Act as the Council in CINEMATOGRAPHY DIRECTOR mode (Art Director).")
                print(f"For each scene, produce: (1) Shot Type via Sun Tzu, (2) Color Grade via Heraclitus, (3) Gutter Instruction via Laozi, (4) Combined Cinematic Visual Prompt.")
            elif args.kinetic_audit:
                print(f"Act as the Council in PROMPT ARCHITECT + KINETIC AUDIT mode.")
                print(f"Apply Anti-Stiffness Protocol to every prompt: Torsional Stress (bodies), Micro-Anatomy (faces), Kinetic Camera (angles).")
            else:
                print(f"Act as the Council in PROMPT ARCHITECT mode. Provide 3-5 prompts.")
        print("-"*80)

if __name__ == "__main__":
    main()
