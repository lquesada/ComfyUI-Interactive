ComfyUI-Interactive

Copyright (c) 2024, Luis Quesada Torres - https://github.com/lquesada | www.luisquesada.com

Check ComfyUI here: https://github.com/comfyanonymous/ComfyUI

# Overview

These nodes allow setting up interactive workflows.

Several "Interactive Selector" nodes may be plugged into an "Interactive Switch". Selector nodes contain a button that the user can press to select that path of execution and continue execution.

When a single "Interactive Selector" node is plugged into an "Interactive Switch" node, it can be used to disable or enable paths of the workflow.

The simple versions of the nodes show and pass an image. The "with parameters" versions of the nodes show and pass the image (optional), but also passes a latent, mask, string, int, and float.

If "propagate\_deselect" is enabled, any selector node that is deselected will automatically deselect any selector nodes further ahead in the workflow. This allows configuring how interactivity work at selector node level.

The "Interactive Save" node previews images and contains a button that triggers saving the image.

The "Interactive Seed" node provides seeds and contains a button that triggers generating a new seed.

The "Interactive Reset" node deselects all selectors.

The "String (for Interactive)", "Integer (for Interactive)" and "Float (for Interactive)" nodes allow defining literals, which may be used to pass through different triggers.

The "String Append (for Interactive)" node appends two strings together. Use this node to append strings (e.g. prompts) together in interactive workflows, see "Best Practices" section below.

These nodes do not require auto-enqueue but need an empty queue to work, so that ComfyUI is responsive.

# Video Tutorial

[![Video Tutorial](https://img.youtube.com/vi/9aFANkP1VTo/0.jpg)](https://www.youtube.com/watch?v=9aFANkP1VTo)

[(click to open in YouTube)](https://www.youtube.com/watch?v=9aFANkP1VTo)

## Example (Simple)

This example uses "Interactive Selector" and "Interactive Switch" nodes to propagate one chosen image forward, and an "Interactive Save" node to gate saving an image on a button click.

Download the example workflow from [here](interactive_example_workflow_simple.json) or drag and drop the screenshot into ComfyUI.

![Workflow](interactive_example_workflow_simple.png)

## Example (Parameters)

This example uses "Interactive Selector (with parameters)" and "Interactive Switch (with parameters)" nodes to propagate one chosen image forward together with the accompanying parameters, and an "Interactive Save" node to gate saving an image on a button click.

Download the example workflow from [here](interactive_example_workflow_with_parameters.json) or drag and drop the screenshot into ComfyUI.

![Workflow](interactive_example_workflow_with_parameters.png)

## Example (Full workflow with several options per step)

This example uses SDXL Turbo to quickly sample images, and uses several rounds of "Interactive Selector (with parameters)" and "Interactive Switch (with parameters)" nodes to allow the user to pick between three options, three times in a row.

This node requires the [Anything Everywhere](https://github.com/chrisgoringe/cg-use-everywhere) nodes to avoid plenty of manual connections. Note though that there must be a directly or indirectly linked path (i.e. without anything everywhere nodes) from interactive nodes so that they work properly.

Download the example workflow from [here](interactive_example_workflow_full.json) or drag and drop the screenshot into ComfyUI.

![Workflow](interactive_example_workflow_full.png)

## Example (Low-step preview before continuing sampling)

This example samples to 5 steps, then uses a single interactive selector to show a preview and block further sampling. If the results are satisfactory, the selector can be triggered to continue the sampling.

Download the example workflow from [here](interactive_example_workflow_preview.json) or drag and drop the screenshot into ComfyUI.

![Workflow](interactive_example_workflow_preview.png)

# Installation Instructions

Install via ComfyUI-Manager or go to the custom_nodes/ directory and run ```$ git clone https://github.com/lquesada/ComfyUI-Interactive.git```

## Best Practices
Keep an empty queue with auto-enqueue disabled while using interactive workflows.

Be aware that some nodes may not interact well with these interactive nodes. For example:
-   cg-use-everywhere "Anything Everywhere" nodes: if these nodes are used to connect between selectors and switches, interactive nodes may not be able to propagate state correctly.
-   Custom-Scripts "String Function" node: this node seems to have an issue when showing the concatenated text that makes it necessary to retrigger execution of some nodes. This slows down interactive workflows. Instead, use the "String Append" node included in this repository.

# Changelog
## 2024-11-15
- Enabled a single selector to be connected to a switch to block paths in the workflow, and corresponding example.
## 2024-11-14
- Initial commit.

# License
GNU GENERAL PUBLIC LICENSE Version 3, see [LICENSE](LICENSE)
