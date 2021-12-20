# This is so entrypoint "tf = timefred:main" can work
# from timefred.timefred import main
import builtins
import os
if os.getenv('TIMEFRED_BIRDSEYE'):
    
    from birdseye import BirdsEye
    
    eye = BirdsEye(num_samples=dict(
            big=dict(
                    attributes=1000,
                    dict=1000,
                    list=1000,
                    set=1000,
                    pandas_rows=20,
                    pandas_cols=100,
                    ),
            small=dict(
                    attributes=1000,
                    dict=1000,
                    list=1000,
                    set=1000,
                    pandas_rows=6,
                    pandas_cols=10,
                    ),
            )
            )
    import cheap_repr
    
    
    cheap_repr.max_cols = 1000
    cheap_repr.max_level = 1000
    cheap_repr.max_rows = 1000
    cheap_repr.suppression_threshold = 1000
else:
    def eye(fn):
        return fn
    
builtins.eye = eye
if os.getenv('TIMEFRED_RICH_TB', '').lower() in ('true', '1'):
    from rich import traceback
    traceback.install(extra_lines=5, show_locals=True)