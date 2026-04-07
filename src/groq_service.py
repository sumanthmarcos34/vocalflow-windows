"""Groq Service - LLM post-processing for transcription correction and enhancement"""

import requests
import json
from typing import Callable, Optional, List
from dataclasses import dataclass
from config import GROQ_MODEL, GROQ_CORRECTION_ENABLED, GROQ_GRAMMAR_ENABLED


@dataclass
class GroqModel:
    """Represents a Groq model."""
    id: str
    display_name: str

    def __hash__(self):
        return hash(self.id)


@dataclass
class GroqProcessingOptions:
    """Options for Groq text processing."""
    code_mix: Optional[str] = None
    fix_spelling: bool = False
    fix_grammar: bool = False
    target_language: Optional[str] = None

    def has_any_step(self) -> bool:
        return (self.code_mix is not None or 
                self.fix_spelling or 
                self.fix_grammar or 
                self.target_language is not None)


CODE_MIX_STYLES = {
    "Hinglish", "Tanglish", "Benglish", "Kanglish", "Tenglish",
    "Minglish", "Punglish", "Spanglish", "Franglais", "Portunol",
    "Chinglish", "Japlish", "Konglish", "Arabizi", "Sheng", "Camfranglais"
}


class GroqService:
    """Handles API communication with Groq for text post-processing."""
    
    def __init__(self):
        self.api_key: Optional[str] = None
        
    def set_api_key(self, api_key: str) -> None:
        """Set the Groq API key."""
        self.api_key = api_key
    
    def fetch_models(self, api_key: str = None) -> List[GroqModel]:
        """Fetch available Groq models."""
        api_key = api_key or self.api_key
        models = []
        if not api_key:
            return models
            
        try:
            response = requests.get(
                "https://api.groq.com/openai/v1/models",
                headers={"Authorization": f"Bearer {api_key}"}
            )
            if response.status_code == 200:
                data = response.json()
                for entry in data.get("data", []):
                    if entry.get("object") == "model":
                        models.append(GroqModel(
                            id=entry["id"],
                            display_name=entry["id"]
                        ))
        except Exception as e:
            print(f"Error fetching Groq models: {e}")
        return sorted(models, key=lambda m: m.id)
    
    def process_text(self, text: str, options: GroqProcessingOptions,
                     api_key: str = None, model: str = None,
                     completion: Callable[[str], None] = None) -> str:
        """Process text through Groq LLM for correction/enhancement."""
        api_key = api_key or self.api_key
        model = model or GROQ_MODEL
        
        if not api_key or not model or not options.has_any_step():
            if completion:
                completion(text)
            return text
        
        # Build instruction steps
        instructions = []
        step_num = 1
        
        if options.code_mix:
            instructions.append(
                f"{step_num}. The input is in {options.code_mix}. Transliterate any "
                f"non-Roman script (such as Devanagari, Tamil, etc.) to Roman script. "
                f"Keep English words as-is. Do not translate - preserve the original meaning."
            )
            step_num += 1
        
        if options.fix_spelling:
            instructions.append(
                f"{step_num}. Fix any spelling mistakes. Do not change meaning or structure."
            )
            step_num += 1
        
        if options.fix_grammar:
            instructions.append(
                f"{step_num}. Fix any grammar mistakes. Do not change meaning or add content."
            )
            step_num += 1
        
        if options.target_language:
            if options.target_language in CODE_MIX_STYLES:
                instructions.append(
                    f"{step_num}. Rewrite the text in {options.target_language} style: "
                    f"keep English words as-is, and transliterate any non-Roman script "
                    f"to Roman script. Do not translate - preserve the original meaning."
                )
            else:
                instructions.append(
                    f"{step_num}. Translate the entire text to {options.target_language}."
                )
        
        system_prompt = (
            "Process the following text by applying these steps in order:\n"
            + "\n".join(instructions)
            + "\nReturn only the final processed text with no explanation."
        )
        
        try:
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": text}
                    ],
                    "temperature": 0
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()["choices"][0]["message"]["content"]
                if completion:
                    completion(result.strip())
                return result.strip()
        except Exception as e:
            print(f"Error processing text with Groq: {e}")
        
        if completion:
            completion(text)
        return text
