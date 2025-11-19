import json
import re
from typing import List, Dict

class AudioSynchronizer:
    def __init__(self):
        pass

    def normalize_text(self, text: str) -> str:
        """
        Standard cleaning: removes punctuation, extra spaces, and lowercases.
        """
        # Clean punctuation and normalize spaces
        text = text.replace('—', ' ').replace('-', ' ').replace('\n', ' ')
        clean_text = re.sub(r'[^\w\s]', '', text.lower())
        return re.sub(r'\s+', ' ', clean_text).strip()

    def find_sequence_index(self, words_list: List[Dict], sequence_str: str, start_search_index: int) -> int:
        """
        Searches for a sequence of words (anchor) in the audio list starting from a specific index.
        Returns the index of the LAST word in the sequence.
        """
        normalized_seq = self.normalize_text(sequence_str)
        target_words = normalized_seq.split()
        
        if not target_words:
            return -1

        seq_len = len(target_words)
        # Limit search to avoid scanning the whole file if something is wrong (e.g., look ahead 100 words max)
        # You can remove the limit if segments are very long.
        search_limit = len(words_list) 

        for i in range(start_search_index, search_limit - seq_len + 1):
            match = True
            for j, target_word in enumerate(target_words):
                audio_word = self.normalize_text(words_list[i + j]['word'])
                if target_word != audio_word:
                    match = False
                    break
            
            if match:
                # Return the index of the LAST word in the matching sequence
                return i + seq_len - 1
        
        return -1

    def sync_segments(self, production_plan: Dict, timestamps: Dict) -> List[Dict]:
        visual_segments = production_plan.get('segments', [])
        audio_words = timestamps.get('words', [])
        
        if not visual_segments or not audio_words:
            print("Error: Missing segments or audio words.")
            return []

        synced_segments = []
        
        # THE CURSOR: This tracks exactly where we are in the audio file.
        # We only move this forward.
        audio_cursor = 0
        
        total_segments = len(visual_segments)

        for i, segment in enumerate(visual_segments):
            new_seg = segment.copy()
            
            # 1. DEFINE START
            # The start is simply where the cursor currently is.
            # This ensures continuity (no gaps).
            if audio_cursor >= len(audio_words):
                audio_cursor = len(audio_words) - 1
            
            start_index = audio_cursor
            new_seg['start'] = audio_words[start_index]['start']

            # 2. DEFINE END
            # Strategy: Look for the LAST 3 words of the current script part.
            script_text = segment['script_part']
            # Get last 3 words as the "Anchor"
            normalized_full = self.normalize_text(script_text)
            script_words = normalized_full.split()
            
            # Determine anchor length (use 3, or less if the sentence is short)
            anchor_len = min(3, len(script_words))
            anchor_phrase = " ".join(script_words[-anchor_len:])
            
            # Search for this anchor in the audio, starting from our cursor
            found_end_index = self.find_sequence_index(audio_words, anchor_phrase, audio_cursor)

            if found_end_index != -1:
                # HIT: We found the end words.
                end_index = found_end_index
            else:
                # MISS: We couldn't find the end words (maybe audio transcript is very different).
                # FALLBACK STRATEGY: 
                # Look for the START of the NEXT segment to define our boundary.
                print(f"⚠️ Warning: Could not find end anchor for segment {segment['segment_id']}. Trying next segment start...")
                
                if i < total_segments - 1:
                    next_segment_script = visual_segments[i+1]['script_part']
                    # Get first 3 words of NEXT segment
                    next_norm = self.normalize_text(next_segment_script)
                    next_start_words = " ".join(next_norm.split()[:3])
                    
                    next_start_idx = self.find_sequence_index(audio_words, next_start_words, audio_cursor)
                    
                    if next_start_idx != -1:
                        # The current segment ends right before the next one starts
                        # (next_start_idx returns the index of the 3rd word, so we subtract 3 to get to start, then -1)
                        end_index = max(audio_cursor, next_start_idx - 3) 
                    else:
                        # Total failure fallback: guess 15 words?
                        end_index = min(len(audio_words)-1, audio_cursor + 10)
                else:
                    # If it's the last segment and we didn't find the end, just use the end of audio
                    end_index = len(audio_words) - 1

            # Safety cap
            if end_index >= len(audio_words):
                end_index = len(audio_words) - 1
            
            # 3. ASSIGN END TIME
            new_seg['end'] = audio_words[end_index]['end']
            new_seg['duration'] = round(new_seg['end'] - new_seg['start'], 3)
            
            # 4. UPDATE CURSOR FOR NEXT LOOP
            # The next segment starts immediately after this word.
            audio_cursor = end_index + 1
            
            print(f"Segment {new_seg['segment_id']} | Words matched: {script_words[-anchor_len:]} | Time: {new_seg['start']} - {new_seg['end']}")
            
            synced_segments.append(new_seg)

        return synced_segments

# --- TEST IT ---
# (Assuming 'timestamps' and 'production_plan' variables contain your JSON data)
# synchronizer = AudioSynchronizer()
# final_segments = synchronizer.sync_segments(production_plan, timestamps)
# print(json.dumps(final_segments, indent=2))