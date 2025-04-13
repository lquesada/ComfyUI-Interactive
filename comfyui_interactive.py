# https://github.com/lquesada/ComfyUI-Inpaint-Interactive
# Copyright (c) 2024, Luis Quesada Torres - https://github.com/lquesada | www.luisquesada.com

import folder_paths
import json
import nodes
import random
import os

from PIL import Image
from PIL.PngImagePlugin import PngInfo
from server import PromptServer

import numpy as np

from comfy.cli_args import args

import folder_paths


current_prompt = None

def onprompt(json_data):
    try:
        current_prompt = json_data
    except Exception as e:
        print(f"[WARN] ComfyUI-Interactive: Error loading prompt - interactive nodes will not work.\n{e}")

    return json_data

PromptServer.instance.add_on_prompt_handler(onprompt)

def workflow_to_map(workflow):
    nodes = {}
    links = {}
    for link in workflow['links']:
        links[link[0]] = link[1:]
    for node in workflow['nodes']:
        nodes[str(node['id'])] = node

    return nodes, links


class InteractiveReset:
    @classmethod
    def INPUT_TYPES(s):
        return {}

    @classmethod
    def IS_CHANGED(s):
        return 0 # Never re-execute!

    CATEGORY = "interactive"

    RETURN_TYPES = ()

    FUNCTION = "run"

    def run(self):
        return (None,)


class InteractiveSeed:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "seed_value": ("INT", { "default": 0 })
            }
        }

    @classmethod
    def IS_CHANGED(s, seed_value):
        return seed_value

    CATEGORY = "interactive"

    RETURN_TYPES = ("INT",)
    RETURN_NAMES = ("seed_value",)

    FUNCTION = "run"

    def run(self, seed_value):
        return (seed_value,)


class InteractiveSelectorWithParameters:
    def __init__(self):
        self.output_dir = folder_paths.get_temp_directory()
        self.type = "temp"
        self.prefix_append = "_temp_" + ''.join(random.choice("abcdefghijklmnopqrstupvxyz") for x in range(5))
        self.compress_level = 1

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required":{
                "propagate_deselect": ("BOOLEAN", {"default": True}),
                "selected": ("BOOLEAN", {"default": False}) # DO NOT REORDER SELECTED, MUST BE POSITION 1!!
            },
            "optional":{
                "images": ("IMAGE", ),
                "parameter_latent": ("LATENT", ),
                "parameter_mask": ("MASK", ),
                "parameter_string": ("STRING", {"forceInput": True}),
                "parameter_int": ("INT", {"forceInput": True}),
                "parameter_float": ("FLOAT", {"forceInput": True}),
            },
            "hidden": {
                "prompt": "PROMPT",
                "extra_pnginfo": "EXTRA_PNGINFO"
            },
        }

    @classmethod
    def IS_CHANGED(s, propagate_deselect, selected, images=None, parameter_latent=None, parameter_mask=None, parameter_string=None, parameter_int=None, parameter_float=None, prompt=None, extra_pnginfo=None):
        return 0 # Never re-execute!

    CATEGORY = "interactive"

    RETURN_TYPES = ("interactive_images",)
    RETURN_NAMES = ("selector",)

    OUTPUT_NODE = True

    FUNCTION = "run"

    def run(self, propagate_deselect, selected, images=None, parameter_latent=None, parameter_mask=None, parameter_string=None, parameter_int=None, parameter_float=None, prompt=None, extra_pnginfo=None):
        out = {}
        selector = {"selected": selected, "images": images, "parameter_latent": parameter_latent, "parameter_mask": parameter_mask, "parameter_string": parameter_string, "parameter_int": parameter_int, "parameter_float": parameter_float};
        if images is not None:
            results = save_images_with_metadata(images=images, output_dir=self.output_dir, save_type="temp", prompt=prompt, extra_pnginfo=extra_pnginfo, prefix=self.prefix_append, compress_level=self.compress_level)
            out["ui"] = { "images": results }
        out["result"] = (selector,)

        return out


class InteractiveSelector(InteractiveSelectorWithParameters):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required":{
                "propagate_deselect": ("BOOLEAN", {"default": True}),
                "selected": ("BOOLEAN", {"default": False}) # DO NOT REORDER SELECTED, MUST BE POSITION 1
            },
            "optional":{
                "images": ("IMAGE", ),
            },
            "hidden": {
                "prompt": "PROMPT",
                "extra_pnginfo": "EXTRA_PNGINFO"
            },
        }

   
class InteractiveSwitchWithParameters:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "optional": {
                "selector1": ("interactive_images", ),
                "selector2": ("interactive_images", ),
                "selector3": ("interactive_images", ),
                "selector4": ("interactive_images", ),
                "selector5": ("interactive_images", ),
                "selector6": ("interactive_images", ),
                "selector7": ("interactive_images", ),
                "selector8": ("interactive_images", ),
            },
            "hidden": {
                "unique_id": "UNIQUE_ID",
            },
        }

    @classmethod
    def IS_CHANGED(s, selector1=None, selector2=None, selector3=None, selector4=None, selector5=None, selector6=None, selector7=None, selector8=None, unique_id=None):
        try:
            workflow = current_prompt['extra_data']['extra_pnginfo']['workflow']
        except:
            print("Interactive - Error obtaining current_prompt workflow. This may still work.")
            return 0

        nodes, links = workflow_to_map(workflow)
        any_selected = False
        for inp in nodes[unique_id]['inputs']:
            link = inp['link']
            if link is not None:
                input_node = nodes[str(links[link][0])]
                if input_node['widgets_values'][1]: # THIS IS WHY DO NOT REORDER SELECTED!
                    any_selected = True
        if not any_selected:
            # Must repeat execution until some are selected.
            return float("NaN")
        # If any is selected, do not repeat execution - will repeat if inputs change.
        return 0

    CATEGORY = "interactive"

    RETURN_TYPES = ("IMAGE", "LATENT", "MASK", "STRING", "INT", "FLOAT")
    RETURN_NAMES = ("images", "parameter_latent", "parameter_mask", "parameter_string", "parameter_int", "parameter_float")

    FUNCTION = "run"

    def formatOutput(self, selector):
        return (selector["images"], selector["parameter_latent"], selector["parameter_mask"], selector["parameter_string"], selector["parameter_int"], selector["parameter_float"])

    def run(self, selector1=None, selector2=None, selector3=None, selector4=None, selector5=None, selector6=None, selector7=None, selector8=None, unique_id=None):
        selectors = [selector1, selector2, selector3, selector4, selector5, selector6, selector7, selector8]
        active = 0
        for selector in selectors:
            if selector and selector.get('selected', False):
                active += 1
        assert active<=1, "Too many inputs are active"
        for selector in selectors:
            if selector and selector.get('selected', False):
                return self.formatOutput(selector)
        # None selected nor available, stop
        nodes.interrupt_processing();
        return (None,)


class InteractiveSwitch(InteractiveSwitchWithParameters):
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("images",)

    def formatOutput(self, selector):
        return (selector["images"],)


class InteractiveSave:
    def __init__(self):
        self.prefix_append = "_save_" + ''.join(random.choice("abcdefghijklmnopqrstupvxyz") for _ in range(5))
        self.compress_level = 4
        self.type = "output"
        self.last_save_trigger = 0;

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "images": ("IMAGE", {"tooltip": "The images to save."}),
                "filename_prefix": ("STRING", {"default": "ComfyUI", "tooltip": "The prefix for the file to save. This may include formatting information such as %date:yyyy-MM-dd% or %Empty Latent Image.width% to include values from nodes."}),
                "save_trigger": ("INT", {"default": 0,}) 
            },
            "hidden": {
                "prompt": "PROMPT",
                "extra_pnginfo": "EXTRA_PNGINFO"
            },
        }

    @classmethod
    def IS_CHANGED(s, images, filename_prefix="ComfyUI", save_trigger=0, prompt=None, extra_pnginfo=None):
        return filename_prefix

    RETURN_TYPES = ()
    FUNCTION = "save_images"

    OUTPUT_NODE = True

    CATEGORY = "interactive"
    DESCRIPTION = "Saves the input images to your ComfyUI output directory."

    def save_images(self, images, filename_prefix="ComfyUI", save_trigger=0, prompt=None, extra_pnginfo=None):
        if images is None:
            return { "ui": { "images": list() } }
        # Only save in output directory if save_trigger is set to True
        if save_trigger != self.last_save_trigger:
            self.last_save_trigger = save_trigger;
            output_dir = folder_paths.get_output_directory();
            self.type = "output";
        else:
            output_dir = folder_paths.get_temp_directory();
            self.type = "temp";
            filename_prefix += self.prefix_append;

        # From ComfyUI Core Node SaveImage
        full_output_folder, filename, counter, subfolder, filename_prefix = folder_paths.get_save_image_path(filename_prefix, output_dir, images[0].shape[1], images[0].shape[0])
        results = list()
        for (batch_number, image) in enumerate(images):
            i = 255. * image.cpu().numpy()
            img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
            metadata = None
            if not args.disable_metadata:
                metadata = PngInfo()
                if prompt is not None:
                    metadata.add_text("prompt", json.dumps(prompt))
                if extra_pnginfo is not None:
                    for x in extra_pnginfo:
                        metadata.add_text(x, json.dumps(extra_pnginfo[x]))

            filename_with_batch_num = filename.replace("%batch_num%", str(batch_number))
            file = f"{filename_with_batch_num}_{counter:05}_.png"
            img.save(os.path.join(full_output_folder, file), pnginfo=metadata, compress_level=self.compress_level)
            results.append({
                "filename": file,
                "subfolder": subfolder,
                "type": self.type
            })
            counter += 1

        return { "ui": { "images": results } }


class InteractiveStringAppend:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "join_prompt_using": (["comma and space", "space", "enter"], {"default": "comma and space"})
            },
            "optional": {
                "input1": ("STRING", {"default": '', "forceInput": True, "multiline": True}),
                "input2": ("STRING", {"default": '', "multiline": True})
            }
        }
        return {}

    CATEGORY = "interactive"
    DESCRIPTION = "Appends strings, compatible with Interactive nodes."

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("output",)

    FUNCTION = "run"

    def run(self, join_prompt_using, input1=None, input2=None):
        if join_prompt_using == "comma and space":
            use = ', '
        elif join_prompt_using == "space":
            use = ' '
        else:  # "enter"
            use = '\n'

        if not input1:
            input1 = "" 
        if not input2:
            input2 = "" 
        if not input1 and not input2:
            output = ""
        elif not input1:
            output = input2
        elif not input2:
            output = input1
        else:
            output = input1 + use + input2

        return (output,)


class InteractiveString:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "string": ("STRING", { "default": "" })
            }
        }

    CATEGORY = "interactive"

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("string",)

    FUNCTION = "run"

    def run(self, string):
        return (string,)


class InteractiveStringMultiline:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "string": ("STRING", { "default": "", "multiline": True })
            }
        }

    CATEGORY = "interactive"

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("string",)

    FUNCTION = "run"

    def run(self, string):
        return (string,)


class InteractiveInteger:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "integer": ("INT", { "default": 0 })
            }
        }

    CATEGORY = "interactive"

    RETURN_TYPES = ("INT",)
    RETURN_NAMES = ("integer",)

    FUNCTION = "run"

    def run(self, integer):
        return (integer,)


class InteractiveFloat:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "float": ("FLOAT", { "default": 0 })
            }
        }

    CATEGORY = "interactive"

    RETURN_TYPES = ("FLOAT",)
    RETURN_NAMES = ("float",)

    FUNCTION = "run"

    def run(self, float):
        return (float,)
