# Qbyte
Data Visualization for Qbyte Processing

Steps to run locally:
1. Clone this directory onto your local machine
2. Configure your desired settings at the top of 'QByte.py'. The comments explain what each setting is.
3. Run 'QByte.py' from the command line as follows:
  python QByte.py <mode> <remarks>
  MODE: This can be 'static' or 'auto'. The only difference between the two is that the 'auto' mode will automatically switch views.
  REMARKS: This is an easy way to remember your session. You can input anything without spaces.
  
  Examples:
  python QByte.py static BirthdayParty
  python QByte.py auto FamilyGathering
  
As you run a session, two files are produced that are timestamped with the initialization. The one labeled '*_C.txt' contains any comments you entered, and the other contains the raw data.
  
To re-analyze the raw data from a prior session, run 'QBread.py' as follows:
python QBread.py <input file>
  
Example:
  
python QBread.py QB_1630886880_BirthdayParty.txt
