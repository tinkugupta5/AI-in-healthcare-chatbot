Use this in the current PowerShell session:
python -m pipenv run python create_memory_for_llm.py
Or activate the environment:
python -m pipenv shell

video link:
https://youtu.be/OP0FYjF-37c?list=PL_pAv_JZgZkFV1Ct2qPDeAkddyz2ahBUX&t=1183


======================== .venv ==================================================

.\.venv\Scripts\Activate.ps1
You should see:
(.venv) PS C:\Users\Tinku Gupta\OneDrive\Desktop\medical_chatboat>

Then verify it:
python -c "import sys; print(sys.executable)"


============================== finish =====================================

==========================How to run the project ==========================
pipenv run python .\create_memory_for_llm.py

====================end ================

Run this in the current window:
.\.venv-1\Scripts\activate.bat

Your prompt should become:
(.venv-1) C:\Users\Tinku Gupta\OneDrive\Desktop\medical_chatboat>

Alternatively, exit the current subshell:
exit

Then, in PowerShell, run:
.\.venv-1\Scripts\Activate.ps1

