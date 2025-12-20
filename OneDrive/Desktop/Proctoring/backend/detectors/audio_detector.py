# import webrtcvad
# import numpy as np
# import sounddevice as sd
# import time

# class AudioDetector:
#     def __init__(self,
#                  sample_rate=16000,
#                  frame_duration_ms=30,
#                  rms_threshold=0.02,
#                  speech_frames_threshold=10):

#         self.vad = webrtcvad.Vad(2)  # aggressiveness 0–3
#         self.sample_rate = sample_rate
#         self.frame_size = int(sample_rate * frame_duration_ms / 1000)

#         self.rms_threshold = rms_threshold
#         self.speech_frames_threshold = speech_frames_threshold
#         self.speech_frame_count = 0

#     def process_audio(self, audio_frame):
#         rms = np.sqrt(np.mean(audio_frame ** 2))

#         # ---- Noise spike detection ----
#         if rms > self.rms_threshold:
#             return True, "RMS_SPIKE", rms

#         # ---- Speech detection (VAD) ----
#         pcm = (audio_frame * 32768).astype(np.int16).tobytes()
#         is_speech = self.vad.is_speech(pcm, self.sample_rate)

#         if is_speech:
#             self.speech_frame_count += 1
#             if self.speech_frame_count >= self.speech_frames_threshold:
#                 return True, "CONTINUOUS_SPEECH", rms
#         else:
#             self.speech_frame_count = 0

#         return False, None, rms
import numpy as np
import time





class AudioDetector:
    def __init__(self,
                 sample_rate=16000,
                 frame_duration_ms=30,
                 rms_threshold=0.02,
                 continuous_frames=15):

        self.sample_rate = sample_rate
        self.frame_duration_ms = frame_duration_ms

        # frame size in samples (VERY IMPORTANT)
        self.frame_size = int(sample_rate * frame_duration_ms / 1000)

        self.rms_threshold = rms_threshold
        self.continuous_frames = continuous_frames
        self.high_audio_count = 0

    def process_audio(self, audio_frame):
        rms = np.sqrt(np.mean(audio_frame ** 2))

        if rms > self.rms_threshold:
            self.high_audio_count += 1
            if self.high_audio_count >= self.continuous_frames:
                return True, "CONTINUOUS_AUDIO", rms
            return True, "AUDIO_SPIKE", rms
        else:
            self.high_audio_count = 0

        return False, None, rms
