from pathlib import Path
from typing import List, Dict, Any
import yaml
from dataclasses import dataclass


@dataclass
class Answer:
    keyword: List[str]
    say: str = None
    cmd: str = None


@dataclass
class Step:
    step: int
    tag: str
    answers: List[Answer]


def parse_answers(data: Dict[int, Any]) -> Dict[int, Step]:
    answers_dict = {}
    for i, item in data.items():
        answers = [Answer(**a) for a in item['answer']]
        step = Step(i, item['tag'], answers)
        answers_dict[i] = step
    return answers_dict
