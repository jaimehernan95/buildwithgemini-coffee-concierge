# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""A2UI utilities for processing and wrapping Agent-to-UI responses."""

from __future__ import annotations

import json
import re
from typing import Sequence

from a2ui.core.basic_catalog import BasicCatalog
from a2ui.core.schema import ProtocolVersion
from a2ui.inference_formats.direct_json import DirectJsonPromptGenerator
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_response import LlmResponse
from google.genai import types


class A2uiSchemaManager:
    """Manages A2UI schemas and generates system prompts for A2UI-enabled agents."""

    def __init__(
        self,
        version: str = "0.8",
        catalogs: Sequence | None = None,
    ) -> None:
        self.version = version
        proto_ver = (
            ProtocolVersion.V0_8
            if version in ("0.8", "v0.8", "VERSION_0_8")
            else ProtocolVersion.V0_9
        )
        if catalogs is None:
            self.catalogs = [BasicCatalog(proto_ver)]
        else:
            self.catalogs = list(catalogs)

    def generate_system_prompt(
        self,
        role_description: str = "",
        ui_description: str = "",
        workflow_description: str = "",
        include_schema: bool = True,
        include_examples: bool = True,
        validate_examples: bool = False,
        allowed_components: Sequence[str] | None = None,
    ) -> str:
        """Generates a complete system prompt including A2UI protocol instructions."""
        pgen = DirectJsonPromptGenerator(
            catalogs=self.catalogs,
            allowed_messages=allowed_components,
        )
        a2ui_instructions = pgen.generate()

        parts: list[str] = []
        if role_description:
            parts.append(f"## Role & Persona:\n{role_description}")
        if ui_description:
            parts.append(f"## UI Guidelines:\n{ui_description}")
        if workflow_description:
            parts.append(f"## Workflow Rules:\n{workflow_description}")
        parts.append(f"## A2UI Specification & Components (v{self.version}):\n{a2ui_instructions}")
        return "\n\n".join(parts)


def _wrap_a2ui_part(a2ui_message: dict) -> types.Part:
    """Wrap a single A2UI message for rendering in adk web."""
    datapart_json = json.dumps({
        "kind": "data",
        "metadata": {"mimeType": "application/json+a2ui"},
        "data": a2ui_message,
    })
    blob_data = (
        b"<a2a_datapart_json>"
        + datapart_json.encode("utf-8")
        + b"</a2a_datapart_json>"
    )
    return types.Part(
        inline_data=types.Blob(
            data=blob_data,
            mime_type="text/plain",
        )
    )


def a2ui_callback(
    callback_context: CallbackContext,
    llm_response: LlmResponse,
) -> LlmResponse | None:
    """Convert A2UI JSON in text output to rendered components."""
    if not llm_response.content or not llm_response.content.parts:
        return None

    for part in llm_response.content.parts:
        if not part.text:
            continue
        text = part.text.strip()
        if not text:
            continue

        if not any(
            k in text
            for k in ("beginRendering", "surfaceUpdate", "dataModelUpdate", "deleteSurface")
        ):
            continue

        # Strip markdown fences if present
        if text.startswith("```"):
            text = text.split("\n", 1)[-1]
        if text.endswith("```"):
            text = text[:-3].strip()

        # Extract content between <a2ui-json> tags if present
        if "<a2ui-json>" in text and "</a2ui-json>" in text:
            m = re.search(r"<a2ui-json>(.*?)</a2ui-json>", text, re.DOTALL)
            if m:
                text = m.group(1).strip()

        # Find where JSON starts (skip conversational prefix)
        json_start = None
        for i, ch in enumerate(text):
            if ch in ("[", "{"):
                json_start = i
                break

        if json_start is None:
            continue

        json_text = text[json_start:]

        # raw_decode parses JSON and ignores trailing text
        try:
            parsed, _ = json.JSONDecoder().raw_decode(json_text)
        except json.JSONDecodeError:
            # Handle concatenated JSON objects: {"a":1} {"b":2}
            try:
                fixed = "[" + re.sub(r"\}\s*\{", "},{", json_text) + "]"
                parsed, _ = json.JSONDecoder().raw_decode(fixed)
            except json.JSONDecodeError:
                continue

        if not isinstance(parsed, list):
            parsed = [parsed]

        a2ui_keys = {
            "beginRendering",
            "surfaceUpdate",
            "dataModelUpdate",
            "deleteSurface",
        }
        a2ui_messages = [
            msg
            for msg in parsed
            if isinstance(msg, dict) and any(k in msg for k in a2ui_keys)
        ]

        if not a2ui_messages:
            continue

        new_parts = [_wrap_a2ui_part(msg) for msg in a2ui_messages]
        return LlmResponse(
            content=types.Content(role="model", parts=new_parts),
            custom_metadata={"a2a:response": "true"},
        )

    return None
