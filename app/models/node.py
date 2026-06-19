from dataclasses import dataclass
from typing import Optional


@dataclass
class Node:

    node_id: str

    node_type: str

    page: int

    content: Optional[str] = None

    image_path: Optional[str] = None

    source_document: Optional[str] = None

    unit: Optional[str] = None

    title: Optional[str] = None

    caption: Optional[str] = None

    table_data: Optional[str] = None

    ocr_text: Optional[str] = None

    # Text found next to a figure on the page (its real caption/labels),
    # used to make figures findable by their actual content rather than the
    # weak BLIP caption.
    context_text: Optional[str] = None

    # Explicit figure caption line, e.g. "Figure 3.2: Structure of the neuron".
    # Extracted when the page contains a labelled caption matching a figure
    # pattern (Figure/Fig/Diagram/Chart + number). Stored as metadata so
    # queries that reference the figure by number or topic can be boosted.
    figure_label: Optional[str] = None