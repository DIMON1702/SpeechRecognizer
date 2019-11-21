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

#   intro               Hi, this is Julia calling from Toyota. We have a sale going right now. Would you like to hear how you can save money on your car purchase today?
#   step2_accepted      great! here's how it works. a representative will call you to explain all the details right after this phone call. is it ok?
#   step3_accepted      Great, our manager will call you back now for further details.
#   reject              Excuse for troubling. Goodbye.
#   later               I'll call you back later.
#   silence             Sorry, I did not hear.
#   incorrect           Sorry, I do not understand what you said.