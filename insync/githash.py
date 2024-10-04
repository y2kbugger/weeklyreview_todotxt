from logging import getLogger
from pathlib import Path

logger = getLogger(__name__)


def githash() -> str:
    repo_path = Path()
    head_file = repo_path / '.git' / 'HEAD'

    try:
        with head_file.open('r') as f:
            ref = f.readline().strip()

        if ref.startswith('ref:'):
            ref_path = repo_path / '.git' / ref.split(' ')[1]
            with ref_path.open('r') as f:
                return f.readline().strip()
        else:
            print(f'2foundref {ref}')
            return ref
    except Exception as e:
        logger.exception(f"Unable to get githash: {e}")
        return 'githash_unknown'
