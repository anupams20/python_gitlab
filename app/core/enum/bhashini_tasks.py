import enum


class BhashiniTasksEnum(str, enum.Enum):
    SPEECH_TO_TEXT = "asr"
    TRANSLATION = "translation"
    TEXT_TO_SPEECH = "tts"
