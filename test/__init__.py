from timefred.time import XArrow

print()
import os

os.environ.setdefault('TIMEFRED_TESTING', '1')
print(f"{os.environ['TIMEFRED_TESTING'] = }")
TEST_START_ARROW: XArrow = XArrow.now()
