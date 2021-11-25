from timefred.time import XArrow

print()
import os

os.environ['TIMEFRED_TESTING'] = '1'
TEST_START_ARROW: XArrow = XArrow.now()
