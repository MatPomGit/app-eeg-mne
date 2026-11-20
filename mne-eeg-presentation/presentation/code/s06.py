import numpy as np
import matplotlib.pyplot as plt
import mne
from mne.datasets import eegbci
from mne.io import (concatenate_raws,
                    read_raw_edf)

mne.set_log_level("WARNING")
print("MNE", mne.__version__)
print("NumPy", np.__version__)
