# Import all schema classes to make them accessible from the schemas package
from .user_schema import UserCreate, UserRead, UserUpdate
from .speech_schema import SpeechCreate, SpeechRead, SpeechAnalysisRead
from .analysis_schema import AnalysisCreate, AnalysisRead

# Optionally, define __all__ to explicitly specify what is exported
__all__ = [
    "UserCreate",
    "UserRead",
    "UserUpdate",
    "SpeechCreate",
    "SpeechRead",
    "SpeechAnalysisRead",
    "AnalysisCreate",
    "AnalysisRead",
]