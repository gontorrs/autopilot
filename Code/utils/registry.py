from dataclasses import dataclass
from typing import Optional


@dataclass
class ActionConfig:

    agents: list[str]
    item_type: Optional[str] = None
    target_param: Optional[str] = None


ACTION_REGISTRY: dict[str, ActionConfig] = {

    "open": ActionConfig(
        agents=["scout", "vision", "executor"],
        item_type="application",
        target_param="app_name",
    ),

    # target is resolved from pddl not from state.
    "navigate": ActionConfig(
        agents=["scout", "vision", "executor"],
        item_type="folder",
        target_param=None,
    ),

    "open_file": ActionConfig(
        agents=["scout", "vision", "executor"],
        item_type="file",
        target_param="file_name",
    ),

    "search_text": ActionConfig(
        agents=["executor"],
        item_type="text_content",
        target_param="content",
    ),

    "change_text": ActionConfig(
        agents=["executor"],
        target_param="style",
    ),

    "type": ActionConfig(
        agents=["executor"],
        target_param="content",
    ),
    
    "create_file": ActionConfig(
        agents=["scout", "vision", "executor"],
        item_type="button",
        target_param=None,
    ),

    "create_folder": ActionConfig(
        agents=["scout", "vision", "executor"],
        item_type="button",
        target_param=None,
    ),

    "final": ActionConfig(
        agents=["qa"],
        target_param="prompt",
    ),

    "navigate_back": ActionConfig(
        agents=["executor"],
        item_type="button",
        target_param=None,
    ),

    "click_new": ActionConfig(
        agents=["scout", "vision", "executor"],
        item_type="button",
        target_param=None,
    ),
 
    "select_type": ActionConfig(
        agents=["scout", "vision", "executor"],
        item_type="menu_option",
        target_param=None,
    ),
 
    "type_name": ActionConfig(
        agents=["executor"],
        target_param=None,
    ),

    "delete_text": ActionConfig(
        agents=["executor"],
        target_param="text",
    ),

}
