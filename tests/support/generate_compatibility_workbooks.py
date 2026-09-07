"""Fixtures for Microsoft's independent schema/semantic package validator."""
from pathlib import Path
import sys

from revenue_tool.adapters.excel_writer import ExcelOutputAdapter
from revenue_tool.config import load_config
from revenue_tool.domain.models import IssueLog
from tests.test_pipeline import CONFIG, _run, _write_sources
from tests.test_regional_summary import example_rows


def main():
    root = Path(sys.argv[1])
    root.mkdir(parents=True, exist_ok=True)
    source_dir = root / 'inputs'
    source_dir.mkdir(exist_ok=True)
    sources = _write_sources(source_dir, 'source', variant='first')
    _run(sources, root / 'pipeline.xlsx')
    config = load_config(CONFIG)
    for name, rows in [('edge-cases', example_rows()), ('empty', [])]:
        ExcelOutputAdapter().write(root / f'{name}.xlsx', rows, [], [], [], IssueLog(), config)



if __name__ == '__main__':
    main()
