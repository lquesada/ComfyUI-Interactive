// https://github.com/lquesada/ComfyUI-Inpaint-Interactive
// Copyright (c) 2024, Luis Quesada Torres - https://github.com/lquesada | www.luisquesada.com

import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";


const activeColor = "#335533"
const inactiveColor = "#444444"
const tooManyColor = "#553333"
const selectColor = "#555533"
const textSelect = "👤 Select"
const textDeselect = "✖️  Deselect"

function getNodeConnections(node) {
    const inputs = [];
    const outputs = [];

    const nodeId = node.id
    const links = node.graph.links
    const nodesById = node.graph._nodes_by_id

    links.forEach(link => {
        if (link.origin_id === nodeId) {
            // If the current node is the origin of the link, add the target node to outputs
            const targetNode = nodesById[link.target_id];
            if (targetNode) outputs.push(targetNode);
        } else if (link.target_id === nodeId) {
            // If the current node is the target of the link, add the origin node to inputs
            const originNode = nodesById[link.origin_id];
            if (originNode) inputs.push(originNode);
        }
    });

    return { inputs, outputs };
}

let origProps = {};

const findButtonWidget = (node) => {
    return node.widgets ? node.widgets.find((w) => w.type == "button") : null;
};

const findWidgetByName = (node, name) => {
    return node.widgets ? node.widgets.find((w) => w.name === name) : null;
};

const doesInputWithNameExist = (node, name) => {
    return node.inputs ? node.inputs.some((input) => input.name === name) : false;
};

const getRandomNumber = (min, max) => {
  return Math.floor(Math.random() * (max - min + 1)) + min;
};

const HIDDEN_TAG = "tschide";

// Toggle Widget + change size
function toggleWidget(node, widget, show = false, suffix = "") {
    if (!widget || doesInputWithNameExist(node, widget.name)) return;

    // Store the original properties of the widget if not already stored
    if (!origProps[widget.name]) {
        origProps[widget.name] = { origType: widget.type, origComputeSize: widget.computeSize };
    }

    const origSize = node.size;

    // Set the widget type and computeSize based on the show flag
    widget.type = show ? origProps[widget.name].origType : HIDDEN_TAG + suffix;
    widget.computeSize = show ? origProps[widget.name].origComputeSize : () => [0, -4];

    // Recursively handle linked widgets if they exist
    widget.linkedWidgets?.forEach(w => toggleWidget(node, w, ":" + widget.name, show));

    // Calculate the new height for the node based on its computeSize method
    const newHeight = node.computeSize()[1];
    node.setSize([node.size[0], newHeight]);
}

function hasBlockedSwitchesBefore(node, visited = new Set()) {
    // Avoid infinite recursion by keeping track of visited nodes
    if (visited.has(node.id)) return false;
    visited.add(node.id);

    const connections = getNodeConnections(node);
    
    for (let input of connections.inputs) {
        // If the input node is a switch
        if (input.type === "InteractiveSwitch" || input.type === "InteractiveSwitchWithParameters") {
            const selectorInputs = getNodeConnections(input).inputs.filter(selInput => 
                selInput.type === "InteractiveSelector" || selInput.type === "InteractiveSelectorWithParameters"
            );
            
            const selectedSelectors = selectorInputs.filter(sel => 
                findWidgetByName(sel, "selected")?.value === true
            );

            // If this switch has no selected selectors, it is blocked
            if (selectedSelectors.length === 0) {
                return true;
            }
        }

        // Recursively check if this input node has any blocked switches before it
        if (hasBlockedSwitchesBefore(input, visited)) {
            return true;
        }
    }
    return false;
}


function updateInteractive() {
    const graph = app.graph;

    // Loop through nodes in order
    graph._nodes_in_order.forEach(node => {
        if (node.type === "InteractiveSelector" || node.type === "InteractiveSelectorWithParameters") {
            const connections = getNodeConnections(node);
            const switchOutputs = connections.outputs.filter(input => 
                input.type === "InteractiveSwitch" || input.type == "InteractiveSwitchWithParameters"
            );
            if (switchOutputs.length == 0) {
                const isSelected = findWidgetByName(node, "selected")?.value;
                node.bgcolor = isSelected ? activeColor : inactiveColor;
                node.color = isSelected ? activeColor : inactiveColor;
                findButtonWidget(node).name = isSelected ? textDeselect : textSelect;
            }
        }
        if (node.type === "InteractiveSwitch" || node.type === "InteractiveSwitchWithParameters") {
            // Get all inputs for the current switch node
            const connections = getNodeConnections(node);
            const selectorInputs = connections.inputs.filter(input => 
                input.type === "InteractiveSelector" || input.type == "InteractiveSelectorWithParameters"
            );

            // Check if any input selector is selected
            const selectedSelectors = selectorInputs.filter(input => 
                findWidgetByName(input, "selected")?.value === true
            );

            if (selectedSelectors.length > 1) {
                // More than one selector is selected: set color to tooManyColor
                selectorInputs.forEach(selector => {
                    const isSelected = findWidgetByName(selector, "selected")?.value;
                    selector.bgcolor = isSelected ? tooManyColor : inactiveColor;
                    selector.color = isSelected ? tooManyColor : inactiveColor;
                    findButtonWidget(selector).name = isSelected ? textDeselect : textSelect;
                });
            } else if (selectedSelectors.length === 1) {
                // Exactly one selector is selected: set colors accordingly
                selectorInputs.forEach(selector => {
                    const isSelected = findWidgetByName(selector, "selected")?.value;
                    selector.bgcolor = isSelected ? activeColor : inactiveColor;
                    selector.color = isSelected ? activeColor : inactiveColor;
                    findButtonWidget(selector).name = isSelected ? textDeselect : textSelect;
                });
            } else if (selectorInputs.length === 1) {
                // Only one selector connected, acts as trigger/gate, always mark as selectable now
                selectorInputs.forEach(selector => {
                    selector.bgcolor = selectColor;
                    selector.color = selectColor;
                    findButtonWidget(selector).name = textSelect;
                });
            } else if (!hasBlockedSwitchesBefore(node)) {
                // No selectors are selected in this switch, and no blocking switches before
                selectorInputs.forEach(selector => {
                    selector.bgcolor = selectColor;
                    selector.color = selectColor;
                    findButtonWidget(selector).name = textSelect;
                });
            } else {
                // For other switches with no selected inputs, set all to inactiveColor
                selectorInputs.forEach(selector => {
                    selector.bgcolor = inactiveColor;
                    selector.color = inactiveColor;
                    findButtonWidget(selector).name = textSelect;
                });
            }
        }
    });
    app.graph.setDirtyCanvas(true);
}


function isBlockingInteractiveSelector(node) {
    const connections = getNodeConnections(node);
    const switchOutputs = connections.outputs.filter(output => output.type === "InteractiveSwitch" || output.type === "InteractiveSwitchWithParameters");

    if (switchOutputs.length === 0) {
        return false;
    }

    for (let sw of switchOutputs) {
        const switchConnections = getNodeConnections(sw);
        const selectorInputs = switchConnections.inputs.filter(input => input.type === "InteractiveSelector" || input.type == "InteractiveSelectorWithParameters");
        const selectedSelectors = selectorInputs.filter(selector => findWidgetByName(selector, "selected").value === true);

        if (selectedSelectors.length > 0) {
            return false;
        }
    }

    if (hasBlockingSwitchInChain(node)) {
        return false;
    }
    return true;
}

function hasBlockingSwitchInChain(sw) {
    const stack = [sw];
    const visited = new Set();

    while (stack.length > 0) {
        const currentNode = stack.pop();

        if (visited.has(currentNode.id)) {
            continue;
        }
        visited.add(currentNode.id);

        const connections = getNodeConnections(currentNode);
        const switchInputs = connections.inputs.filter(input => input.type === "InteractiveSwitch" || input.type === "InteractiveSwitchWithParameters");

        for (let inputSwitch of switchInputs) {
            const switchConnections = getNodeConnections(inputSwitch);
            const selectorInputs = switchConnections.inputs.filter(input => input.type === "InteractiveSelector" || input.type == "InteractiveSelectorWithParameters");
            const selectedSelectors = selectorInputs.filter(selector => findWidgetByName(selector, "selected").value === true);

            if (selectedSelectors.length === 0) {
                return true;
            }

            stack.push(inputSwitch);
        }
    }
    return false;
}

function resetInteractiveForward(node) {
    const connectionsNode = getNodeConnections(node);
    const stack = connectionsNode.outputs;
    const visited = new Set();

    while (stack.length > 0) {
        const currentNode = stack.pop();

        if (visited.has(currentNode.id)) {
            continue;
        }
        visited.add(currentNode.id);

        if (currentNode.type === "InteractiveSelector" || currentNode.type == "InteractiveSelectorWithParameters") {
            findWidgetByName(currentNode, "selected").value = false;
            currentNode.imgs = [];
        }

        const connections = getNodeConnections(currentNode);
        connections.outputs.forEach(outputNode => {
            if (!visited.has(outputNode.id)) {
                stack.push(outputNode);
            }
        });
    }
}

app.registerExtension({
    name: "interactive.showbutton",
    nodeCreated(node) {
        if (node.comfyClass == "InteractiveSelector" || node.comfyClass == "InteractiveSelectorWithParameters") {
            toggleWidget(node, findWidgetByName(node, "selected"), false);
            node.addWidget("button", textSelect, "", () => {
                var runPrompt = false;
                const selected = findWidgetByName(node, "selected");
                const selectedValue = selected.value;
                const connections = getNodeConnections(node);
                if (!selectedValue) {
                    const blocking = isBlockingInteractiveSelector(node);
                    var changed = false;
                    connections.outputs.forEach(sw => {
                        if (sw.type == "InteractiveSwitch" || sw.type === "InteractiveSwitchWithParameters") {
                            const otherInputs = getNodeConnections(sw);
                            otherInputs.inputs.forEach(selector => {
                                if (selector.type == "InteractiveSelector" || selector.type == "InteractiveSelectorWithParameters") {
                                    const selWidget = findWidgetByName(selector, "selected")
                                    if (selWidget.value) {
                                        changed = true;
                                    }
                                    selWidget.value = false;
                                }
                            })
                        }
                    });
                    selected.value = true;
                    if (blocking || changed) {
                        runPrompt = true;
                    }
                }
                else {
                    selected.value = false;
                    if (findWidgetByName(node, "propagate_deselect").value) {
                        resetInteractiveForward(node);
                    }
                }
                updateInteractive();
                if (runPrompt) {
                    app.queuePrompt(0, 1);
                }
            });
        }
        if (node.comfyClass == "InteractiveSave") {
            node.bgcolor = inactiveColor;
            node.color = inactiveColor;
            toggleWidget(node, findWidgetByName(node, "save_trigger"), false);
            node.addWidget("button","👤 Save Image", "", () => {
                const saveTriggerWidget = findWidgetByName(node, "save_trigger");
                saveTriggerWidget.value = (saveTriggerWidget.value + 1) % 1000;
                app.queuePrompt(0, 1);
            });
        }
        if (node.comfyClass == "InteractiveSeed") {
            node.bgcolor = inactiveColor;
            node.color = inactiveColor;
            node.addWidget("button","👤 New Random Seed", "", () => {
                findWidgetByName(node, "seed_value").value = getRandomNumber(0, 1125899906842624)
                app.queuePrompt(0, 1);
            });
        }
        if (node.comfyClass == "InteractiveReset") {
            node.bgcolor = inactiveColor;
            node.color = inactiveColor;
            node.addWidget("button","👤 Reset selections", "", () => {
                app.graph._nodes_in_order.forEach(node => {
                    if (node.type === "InteractiveSelector" || node.type == "InteractiveSelectorWithParameters") {
                        findWidgetByName(node, "selected").value = false;
                        resetInteractiveForward(node);
                    }
                });
                updateInteractive();
            });
        }
    },
});

app.registerExtension({
    name: "interactive.updatebuttons",
    loadedGraphNode(node, app) {
        if (node.comfyClass == "InteractiveSelector" || node.comfyClass == "InteractiveSelectorWithParameters") {
            findButtonWidget(node).name = findWidgetByName(node, "selected").value ? textDeselect : textSelect;
        }
        if (node.comfyClass == "InteractiveSwitch" || node.comfyClass == "InteractiveSwitchWithParameters") {
            updateInteractive();
        }
    }
});

api.addEventListener("graphChanged", updateInteractive);
