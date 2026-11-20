python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -c "import mne; mne.sys_info()"
