from pathlib import Path
import runpy
ROOT=Path(__file__).resolve().parent
runpy.run_path(str(ROOT/'portfolio-1-database-design'/'seed_data.py'), run_name='__main__')
runpy.run_path(str(ROOT/'portfolio-2-query-optimisation'/'performance_demo.py'), run_name='__main__')
runpy.run_path(str(ROOT/'portfolio-3-transactions-concurrency'/'transaction_demo.py'), run_name='__main__')
print('Local relational portfolio steps completed. See evidence/ folders for outputs.')
