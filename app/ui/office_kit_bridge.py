import json
import time
from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional

@dataclass
class OfficeKitBridgeState:
    bridge_mode: str  # RED_LIGHT (phone-only), GREEN_LIGHT (phone + laptop)
    iqoo_connected: bool
    laptop_synced: bool
    bandwidth_mbps: float
    latency_ms: float
    active_stream: str

class VivoOfficeKitBridge:
    """
    SECTIONS 18, 19, 20: VIVO OFFICE KIT BRIDGE
    - Red Light (Phone-First): Runs standalone on iQOO 15.
    - Green Light (Phone + Laptop): vivo Office Kit seamlessly connects
      iQOO 15 sensing to laptop display for deep spectrogram analysis and soundscape DAW export.
    """
    
    def __init__(self, mode: str = "GREEN_LIGHT"):
        self.mode = mode

    def get_bridge_status(self) -> OfficeKitBridgeState:
        return OfficeKitBridgeState(
            bridge_mode=self.mode,
            iqoo_connected=True,
            laptop_synced=(self.mode == "GREEN_LIGHT"),
            bandwidth_mbps=850.0 if self.mode == "GREEN_LIGHT" else 0.0,
            latency_ms=1.2,
            active_stream="Multimodal Biophony Stream (48kHz/24b + 1080p Video + Context Sensors)"
        )

    def switch_mode(self, new_mode: str) -> str:
        if new_mode in ["RED_LIGHT", "GREEN_LIGHT"]:
            self.mode = new_mode
            return f"vivo Office Kit bridge transitioned to {new_mode}."
        return "Invalid bridge mode."
