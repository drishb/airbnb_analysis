"""
Single entry point. PRD req 65.
Usage: python run_analysis.py
"""
import random
import numpy as np

from src import config, ingest


def set_seeds():
    """PRD req 69: global seeds so repeated runs are identical."""
    random.seed(config.RANDOM_SEED)
    np.random.seed(config.RANDOM_SEED)


def main():
    set_seeds()
    config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    config.FIGURE_DIR.mkdir(parents=True, exist_ok=True)

    df = ingest.run()

    # Tasks 2.0-8.0 attach here.
    return df


if __name__ == "__main__":
    main()
