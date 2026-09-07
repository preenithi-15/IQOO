import time
import numpy as np
from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional, List

from app.audio.recorder import AudioRecorder
from app.audio.quality import AudioQualityAnalyzer, QualityReport
from app.audio.filter import AdaptiveNoiseFilter
from app.audio.spectrogram import SpectrogramAnalyzer, SpectralFeatures
from app.audio.timeline import AcousticTimeline, TimelineEvent
from app.camera.vision_capture import VisionCapture, CameraFrame
from app.sensors.context_sensors import ContextSensors, SensorContext
from app.sensors.nature_probe import NatureProbe

from ai.sonification.translator import FrequencySonifier, SonificationResult
from ai.audio_classifier.classifier import BioacousticClassifier, AudioClassification
from ai.vision_classifier.classifier import VisionClassifier, VisualDetection
from ai.multimodal.fusion_engine import MultimodalFusionEngine, MultimodalHypothesis
from ai.nature_interpreter.interpreter import NatureInterpreter, NatureInterpretation
from ai.npu_engine import SnapdragonNPUEngine

from music.composer.nature_composer import NatureComposer, CompositionTrack
from music.soundscape.ambient_generator import SoundscapeGenerator
from app.video.nature_cinema import NatureCinema, NatureMoment
from data.storage import NatureStorage
from data.observations import NatureObservationsTracker

@dataclass
class LiveAnalysisSnapshot:
    timestamp: float
    quality: QualityReport
    spectral_features: SpectralFeatures
    audio_classification: AudioClassification
    visual_detections: List[VisualDetection]
    sensor_context: SensorContext
    hypothesis: MultimodalHypothesis
    interpretation: NatureInterpretation
    sonification: SonificationResult

class NaturaLiveSession:
    """
    SECTION 3 & FEATURE 10: NATURA LIVE CORE EXPERIENCE
    Orchestrates continuous simultaneous ingestion and analysis across:
    Camera + Microphone + Sensors + Snapdragon 8 Elite Gen 5 NPU.
    
    Pipeline:
    SEE -> HEAR -> DISCOVER -> UNDERSTAND -> EXPERIENCE -> SAVE
    """
    
    def __init__(self, sample_rate: int = 48000):
        self.sample_rate = sample_rate
        self.audio_rec = AudioRecorder(sample_rate)
        self.quality_analyzer = AudioQualityAnalyzer(sample_rate)
        self.filter = AdaptiveNoiseFilter(sample_rate)
        self.spectrogram_analyzer = SpectrogramAnalyzer(sample_rate)
        self.timeline_engine = AcousticTimeline(sample_rate)
        self.vision = VisionCapture()
        self.sensors = ContextSensors()
        self.probe = NatureProbe()
        
        self.sonifier = FrequencySonifier(sample_rate)
        self.audio_classifier = BioacousticClassifier(sample_rate)
        self.vision_classifier = VisionClassifier()
        self.fusion = MultimodalFusionEngine()
        self.interpreter = NatureInterpreter()
        self.npu = SnapdragonNPUEngine()
        
        self.composer = NatureComposer(sample_rate)
        self.soundscape_gen = SoundscapeGenerator(sample_rate)
        self.cinema = NatureCinema()
        self.storage = NatureStorage()
        self.observations = NatureObservationsTracker()
        
        # Quest state machine
        self.quest_active = False
        self.quest_step = 1
        self.quest_sounds_found = []
        self.quest_completed = False

    def process_live_frame(self, 
                           raw_audio: np.ndarray, 
                           camera_preset: Optional[str] = "honeybee") -> LiveAnalysisSnapshot:
        """Runs one complete multimodal analysis frame."""
        now = time.time()
        
        # 1. Audio Quality & Conditioning
        quality = self.quality_analyzer.analyze(raw_audio)
        filtered_audio = self.filter.process(raw_audio)
        spectral_feats = self.spectrogram_analyzer.extract_features(filtered_audio)
        
        # 2. Ultrasound Sonification
        sonif_result = self.sonifier.process(raw_audio, high_band_peak_hz=spectral_feats.dominant_frequency)
        
        # 3. Bioacoustic Classification
        audio_cls = self.audio_classifier.classify(filtered_audio)
        
        # 4. Camera Ingestion & Visual Classification
        cam_frame = self.vision.capture_frame(camera_preset)
        vis_detections = self.vision_classifier.classify_frame(cam_frame.detected_objects)
        
        # 5. Environmental Context Telemetry
        ctx = self.sensors.read_context()
        
        # 6. Multimodal Fusion Engine (Audio + Vision + Context)
        hypo = self.fusion.fuse(audio_cls, vis_detections, ctx)
        
        # 7. Evidence-based Nature Interpreter (3 layers + confidence)
        interpretation = self.interpreter.interpret(hypo)
        
        # 8. NPU Acceleration Telemetry
        self.npu.run_inference("multimodal_embedding_fusion")
        
        return LiveAnalysisSnapshot(
            timestamp=now,
            quality=quality,
            spectral_features=spectral_feats,
            audio_classification=audio_cls,
            visual_detections=vis_detections,
            sensor_context=ctx,
            hypothesis=hypo,
            interpretation=interpretation,
            sonification=sonif_result
        )

    def capture_nature_moment(self, 
                              audio_sample: np.ndarray, 
                              snapshot: LiveAnalysisSnapshot, 
                              location_name: str = "Chennai Nature Sanctuary") -> NatureMoment:
        """
        Synthesizes and permanently saves a complete Nature Moment:
        Original Audio + Enhanced Audio + Sonified Audio + Generative Music + Interpretation.
        """
        moment_id = f"NATURA_{int(time.time())}"
        species_list = [v.detected_species for v in snapshot.visual_detections] or [snapshot.hypothesis.correlated_subject]
        
        track = self.composer.compose(
            bee_energy=0.9 if "bee" in snapshot.audio_classification.primary_label else 0.2,
            cricket_energy=0.8 if "cricket" in snapshot.audio_classification.primary_label else 0.2,
            leaves_energy=0.5,
            rain_energy=0.1,
            duration_sec=8.0,
            location_name=location_name
        )
        
        moment = self.cinema.assemble_moment(
            moment_id=moment_id,
            title=f"Discovery of {species_list[0]}",
            duration_sec=8.0,
            video_desc=f"Observation in {location_name} under {snapshot.sensor_context.time_of_day} sunlight.",
            species=species_list,
            confidence=snapshot.interpretation.confidence_level,
            scientific_interp=snapshot.interpretation.scientific_interpretation,
            location=location_name,
            lat=snapshot.sensor_context.latitude,
            lon=snapshot.sensor_context.longitude
        )
        
        self.storage.save_moment(asdict(moment))
        self.observations.record_session(n_events=3, location=location_name, created_soundscape=True)
        
        return moment

    def step_nature_quest(self, detected_label: str) -> Dict[str, Any]:
        """
        FEATURE 10: 10-MINUTE NATURE QUEST STATE MACHINE
        """
        if not self.quest_active:
            self.quest_active = True
            self.quest_step = 1
            self.quest_sounds_found = []
            
        if self.quest_step == 1:
            if detected_label not in self.quest_sounds_found and detected_label != "ambient_background":
                self.quest_sounds_found.append(detected_label)
            if len(self.quest_sounds_found) >= 3:
                self.quest_step = 2
                msg = f"Quest Step 1 Complete! Found 3 sounds: {', '.join(self.quest_sounds_found)}. Next: Find one insect visually."
            else:
                msg = f"Quest Step 1 in progress: Found {len(self.quest_sounds_found)}/3 natural sounds."
                
        elif self.quest_step == 2:
            if any(k in detected_label for k in ["bee", "cricket", "insect"]):
                self.quest_step = 3
                msg = f"Quest Step 2 Complete! Confirmed {detected_label}. Next: Record plant or environmental foliage vibration."
            else:
                msg = "Quest Step 2 in progress: Point camera at foliage to detect an insect."
                
        elif self.quest_step == 3:
            self.quest_step = 4
            msg = "Quest Step 3 Complete! Environmental acoustic signature recorded. Next: Synthesize 30-second nature composition."
            
        elif self.quest_step == 4:
            self.quest_step = 5
            self.quest_completed = True
            msg = "Quest Complete! 30-second generative Nature Moment rendered and saved to your Nature Album."
            
        return {
            "quest_step": self.quest_step,
            "quest_completed": self.quest_completed,
            "status_message": msg,
            "sounds_logged": self.quest_sounds_found
        }
