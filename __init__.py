from .comfyui_interactive import InteractiveTrigger
from .comfyui_interactive import InteractiveTriggerWithParameters
from .comfyui_interactive import InteractiveSelector
from .comfyui_interactive import InteractiveSelectorWithParameters
from .comfyui_interactive import InteractiveSwitch
from .comfyui_interactive import InteractiveSwitchWithParameters
from .comfyui_interactive import InteractiveSave
from .comfyui_interactive import InteractiveReset
from .comfyui_interactive import InteractiveSeed
from .comfyui_interactive import InteractiveStringAppend
from .comfyui_interactive import InteractiveString
from .comfyui_interactive import InteractiveStringMultiline
from .comfyui_interactive import InteractiveInteger
from .comfyui_interactive import InteractiveFloat

WEB_DIRECTORY = "js"

NODE_CLASS_MAPPINGS = {
    "InteractiveTrigger": InteractiveTrigger,
    "InteractiveTriggerWithParameters": InteractiveTriggerWithParameters,
    "InteractiveSelector": InteractiveSelector,
    "InteractiveSelectorWithParameters": InteractiveSelectorWithParameters,
    "InteractiveSwitch": InteractiveSwitch,
    "InteractiveSwitchWithParameters": InteractiveSwitchWithParameters,
    "InteractiveSave": InteractiveSave,
    "InteractiveReset": InteractiveReset,
    "InteractiveSeed": InteractiveSeed,
    "InteractiveStringAppend": InteractiveStringAppend,
    "InteractiveString": InteractiveString,
    "InteractiveStringMultiline": InteractiveStringMultiline,
    "InteractiveInteger": InteractiveInteger,
    "InteractiveFloat": InteractiveFloat,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "InteractiveTrigger": "Interactive Trigger",
    "InteractiveTriggerWithParameters": "Interactive Trigger (with parameters)",
    "InteractiveSelector": "Interactive Selector",
    "InteractiveSelectorWithParameters": "Interactive Selector (with parameters)",
    "InteractiveSwitch": "Interactive Switch",
    "InteractiveSwitchWithParameters": "Interactive Switch (with parameters)",
    "InteractiveSave": "Interactive Save",
    "InteractiveReset": "Interactive Reset",
    "InteractiveSeed": "Interactive Seed",
    "InteractiveStringAppend": "String Append (for Interactive)",
    "InteractiveString": "String (for Interactive)",
    "InteractiveStringMultiline": "StringMultiline (for Interactive)",
    "InteractiveInteger": "Integer (for Interactive)",
    "InteractiveFloat": "Float (for Interactive)",
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
