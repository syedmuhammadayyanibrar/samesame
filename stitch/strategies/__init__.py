from stitch.strategies.base import Stitcher
from stitch.strategies.exact import ExactMatchStitcher
from stitch.strategies.fuzzy import FuzzyMatchStitcher
from stitch.strategies.embedding import EmbeddingMatchStitcher
from stitch.strategies.permission import PermissionAwareStitcher
from stitch.strategies.contact import ContactResolutionStitcher
from stitch.strategies.a2a import A2AStitcher
from stitch.strategies.memory import MemoryStitcher
from stitch.strategies.composite import CompositeStitcher

__all__ = [
    "Stitcher",
    "ExactMatchStitcher",
    "FuzzyMatchStitcher",
    "EmbeddingMatchStitcher",
    "PermissionAwareStitcher",
    "ContactResolutionStitcher",
    "A2AStitcher",
    "MemoryStitcher",
    "CompositeStitcher",
]
