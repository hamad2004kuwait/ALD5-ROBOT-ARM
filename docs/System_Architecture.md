# System architecture

Keyboard A/B/C or microphone → transcription → AI classifier → local command validation → calibration/holding/confirmation gates → SSC-32U serial controller → five arm joints and gripper.

LEDs indicate retrieval (red), return (yellow) and sequence completion (green). No AI-generated servo coordinates are accepted. The controller is open-loop: completion is not proof that a key is held. The supplied code uses SSC-32U protocol, not an Arduino firmware implementation.

## Safety boundaries
Software pulse limits are protocol checks only, not verified joint travel limits. A physical disconnect or interruption can leave servos powered or executing the last command. Never rely on software as an emergency stop. Use a supervised, accessible power isolation procedure and a clear work envelope.
