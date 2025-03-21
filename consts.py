
file_seg_before_uuid = """
{"version": 182, "time": {"meter": [{"index": 0, "numerator": 4, "denominator": 4}], "tempo": [{"position": 0, "bpm": 120.0}]}, "library": [{"name": "未命名音轨", "uuid": "
""".strip()

file_seg_after_uuid = """
", "parameters": {"pitchDelta": {"mode": "cubic", "points": []}, "vibratoEnv": {"mode": "cubic", "points": []}, "loudness": {"mode": "cubic", "points": []}, "tension": {"mode": "cubic", "points": []}, "breathiness": {"mode": "cubic", "points": []}, "voicing": {"mode": "cubic", "points": []}, "gender": {"mode": "cubic", "points": []}, "toneShift": {"mode": "cubic", "points": []}, "mouthOpening": {"mode": "cubic", "points": []}}, "vocalModes": {}, "pitchControls": [
""".strip()

file_seg_pitch_ctrl_meta = """
{{"pos": {}, "pitch": {}, "id": "{}", "type": "curve", "points":
""".strip()

file_seg_pitch_ctrl_end = "}"

file_seg_end_before_main_group_uuid1 = """
], "notes": [{"musicalType": "singing", "onset": 705600000, "duration": 705600000, "lyrics": "la", "phonemes": "", "accent": "", "pitch": 60, "detune": 0, "attributes": {"evenSyllableDuration": true}, "takes": {"activeTakeId": 0, "takes": [{"id": 0, "seedDuration": 0, "seedPitch": 0, "seedTimbre": 0, "liked": false}]}}]}], "tracks": [{"name": "未命名音轨", "dispColor": "ff7db235", "dispOrder": 0, "renderEnabled": false, "mixer": {"gainDecibel": 0.0, "pan": 0.0, "mute": false, "solo": false, "display": true}, "mainGroup": {"name": "main", "uuid": "
""".strip()

file_seg_end_after_main_group_uuid1 = """
",
""".strip()

file_seg_end_before_main_group_uuid2 = """
"parameters": {"pitchDelta": {"mode": "cubic", "points": []}, "vibratoEnv": {"mode": "cubic", "points": []}, "loudness": {"mode": "cubic", "points": []}, "tension": {"mode": "cubic", "points": []}, "breathiness": {"mode": "cubic", "points": []}, "voicing": {"mode": "cubic", "points": []}, "gender": {"mode": "cubic", "points": []}, "toneShift": {"mode": "cubic", "points": []}, "mouthOpening": {"mode": "cubic", "points": []}}, "vocalModes": {}, "pitchControls": [], "notes": []}, "mainRef": {"groupID": "
"""

file_seg_end_after_main_group_uuid2 = """
", 
"""

file_seg_end_before_group_uuid = """
"blickAbsoluteBegin": 0, "blickAbsoluteEnd": -1, "blickOffset": 0, "pitchOffset": 0, "isInstrumental": false, "database": {"name": "", "language": "", "phoneset": "", "languageOverride": "", "phonesetOverride": "", "backendType": "", "version": "-2"}, "dictionary": "", "voice": {"vocalModeInherited": true, "vocalModePreset": "", "vocalModeParams": {}}, "takes": {"activeTakeId": 0, "takes": [{"id": 0, "seedDuration": 0, "seedPitch": 0, "seedTimbre": 0, "liked": false}]}},
"groups": [{"groupID": "
""".strip()

file_seg_end_after_group_uuid = """
", "blickAbsoluteBegin": 0, "blickAbsoluteEnd": 22579200000, "blickOffset": 0, "pitchOffset": 0, "isInstrumental": false, "database": {"name": "", "language": "", "phoneset": "", "languageOverride": "", "phonesetOverride": "", "backendType": "", "version": "-2"}, "dictionary": "", "voice": {"vocalModeInherited": true, "vocalModePreset": "", "vocalModeParams": {}}, "takes": {"activeTakeId": 0, "takes": [{"id": 0, "seedDuration": 0, "seedPitch": 0, "seedTimbre": 0, "liked": false}]}}]}], "renderConfig": {"destination": "", "filename": "未命名", "numChannels": 1, "aspirationFormat": "noAspiration", "bitDepth": 16, "sampleRate": 44100, "exportMixDown": true, "exportPitch": false}}
""".strip()
