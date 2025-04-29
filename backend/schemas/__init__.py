# Import all schema classes to make them accessible from the schemas package
from .user_schema import UserCreate, UserRead, UserUpdate
from .speech_schema import SpeechCreate, SpeechRead, SpeechUpdate
from .analysis_schema import SpeechAnalysisCreate, AnalysisResult, AnalysisResponse

# Optionally, define __all__ to explicitly specify what is exported
__all__ = [
    "UserCreate",
    "UserRead",
    "UserUpdate",
    "SpeechCreate",
    "SpeechRead",
    "SpeechUpdate",
    "SpeechAnalysisCreate",
    "AnalysisResult",
    "AnalysisResponse",
]