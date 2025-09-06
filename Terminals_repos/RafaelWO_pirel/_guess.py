# proj_clean/pirel/_guess.py

import os
import csv
import random
import logging
from pathlib import Path
from .releases import PythonReleases
from ._cache import load, get_latest_cache_file

STATS_DIR = Path.home() / ".pirel_stats"
STATS_FILENAME = "quiz_stats.csv"
STATS_FIELDNAMES = ["question", "score"]
logger = logging.getLogger(__name__)

class Question:
    def __init__(self, releases):
        self.releases = releases
        self.target_release = random.choice(releases)
        self.choices = self.build_choices()

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.target_release.version}>"

    def ask(self):
        prompt = PirelPrompt(self.format_question(), choices=self.choices)
        answer = prompt()
        return answer == self.correct_answer

    def build_choices(self):
        choices = [self.correct_answer]
        choices.extend(self.generate_incorrect_choices())
        random.shuffle(choices)
        return choices

    @property
    def correct_answer(self):
        return self.get_target_field(self.target_release)

    def format_question(self):
        raise NotImplementedError

    def generate_incorrect_choices(self, k=3, remove_duplicates=True):
        incorrect_choices = [release for release in self.releases if release != self.target_release]
        random.shuffle(incorrect_choices)
        return [self.get_target_field(release) for release in incorrect_choices[:k]]

    def get_target_field(self, release):
        raise NotImplementedError

class DateVersionQuestion(Question):
    def __init__(self, releases):
        super().__init__(releases)
        self.get_target_field = lambda release: release.version

    def format_question(self):
        return f"What version of Python was released on {self.target_release.released}?"

class LatestVersionQuestion(Question):
    def __init__(self, releases):
        super().__init__(releases)
        self.target_release = max(releases, key=lambda r: r.version_tuple)
        self.get_target_field = lambda release: release.version

    def format_question(self):
        return "What is the latest stable version of Python?"

    def generate_incorrect_choices(self):
        return [release.version for release in self.releases if release.version.startswith("3") and release != self.target_release]

class ReleaseManagerVersionQuestion(Question):
    def __init__(self, releases):
        super().__init__(releases)
        self.get_target_field = lambda release: release._release_manager

    def format_question(self):
        return f"Who was the release manager for Python {self.target_release.version}?"

class VersionDateQuestion(Question):
    def __init__(self, releases):
        super().__init__(releases)
        self.get_target_field = lambda release: release.released

    def format_question(self):
        return f"When was Python {self.target_release.version} released?"

class PirelPrompt:
    def __init__(self, prompt, choices, console=None, password=False, case_sensitive=True, show_default=True):
        self.prompt = prompt
        self.choices = choices
        self.console = console
        self.password = password
        self.case_sensitive = case_sensitive
        self.show_default = show_default

    def __call__(self):
        print(self.prompt)
        for i, choice in enumerate(self.choices, 1):
            print(f"{chr(96 + i)}) {choice}")
        return input("> ")

def get_random_question():
    releases = PythonReleases().to_list()
    question_classes = [DateVersionQuestion, LatestVersionQuestion, ReleaseManagerVersionQuestion, VersionDateQuestion]
    return random.choice(question_classes)(releases)

def store_question_score(question, score):
    STATS_DIR.mkdir(parents=True, exist_ok=True)
    stats_file = STATS_DIR / STATS_FILENAME
    with open(stats_file, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=STATS_FIELDNAMES)
        if f.tell() == 0:
            writer.writeheader()
        writer.writerow({"question": repr(question), "score": score})