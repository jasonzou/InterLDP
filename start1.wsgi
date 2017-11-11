import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from index import app as application
sys.stdout = sys.stderr
