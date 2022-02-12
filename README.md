## Qbyte.py
Data Visualization for Hybrid-Quantum Clock featuring Q-Byte Processing

By activating this on your desktop you will have a functioning clock featuring UTC time with Q-Byte Processing and with our data visualization features you get to experience the spatial qualites of time. This clock unifies the laws of quantum tunneling mechanics and relativity. For further detailed explantion you can download our white paper here: www.halo.computer

Review Dr. Caputi's explanation video here: https://www.youtube.com/watch?v=3XkcAKzz61Q&t=2s

Steps to run locally:

1. Clone this directory onto your local machine
2. Run 'pip install -r requirements.txt'
3. Configure your desired settings at the top of 'QByte.py'. The comments explain what each setting is.
4. Run 'QByte.py' from the command line as follows:

python QByte.py mode remarks

MODE: This can be 'static' or 'auto'. The only difference between the two is that the 'auto' mode will automatically switch views every 10 minutes.

REMARKS: This is an easy way to remember your session. You can input anything without spaces.
  
Examples:

python QByte.py static BirthdayParty

python QByte.py auto FamilyGathering
  
As you run a session, two files are produced that are timestamped with the initialization. The one labeled '*_C.txt' contains any comments you entered, and the other contains the raw data.

## QBread.py

To re-analyze the raw data from a prior session, run 'QBread.py' as follows:

python QBread.py input_file
  
Example:

python QBread.py QB_1630886880_BirthdayParty.txt
