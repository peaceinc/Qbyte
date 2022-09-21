## Qbyte.py
Data Visualization for Hybrid-Quantum Clock featuring Q-Byte Processing

By activating this on your desktop you will have a functioning clock featuring UTC time with Q-Byte Processing and with our data visualization features you get to experience the spatial qualites of time. This clock unifies the laws of quantum tunneling mechanics and relativity. For further detailed explantion you can download our white paper here: www.halo.computer

Review Dr. Samantha Caputi's explanation video here: https://www.youtube.com/watch?v=3XkcAKzz61Q&t=2s

Steps to run locally:

1. Clone this directory onto your local machine
2. Run 'pip install -r requirements.txt'
3. Configure your desired settings at the top of 'QByte.py'. The comments explain what each setting is.
4. Run 'QByte.py' from the command line as follows:

$ python QByte.py mode remarks

MODE: This can be 'static' or 'auto'. The only difference between the two is that the 'auto' mode will automatically switch views every 10 minutes.

REMARKS: This is an easy way to remember your session. You can input anything without spaces.
  
Examples:

python QByte.py static BirthdayParty

python QByte.py auto FamilyGathering
  
As you run a session, two files are produced that are timestamped with the initialization. The one labeled '*_C.txt' contains any comments you entered, and the other contains the raw data.

# Stable Diffusion

Q-Byte Processing can be run with Stable Diffusion, a new AI image generating module. This will create images of the words that appear when the colors change. Stable diffusion can be ontained from the github repo: https://github.com/CompVis/stable-diffusion

The model checkpoints can be obtained using a Curl command:

$ curl https://www.googleapis.com/storage/v1/b/aai-blog-files/o/sd-v1-4.ckpt?alt=media > sd-v1-4.ckpt

You will need to provide a path to your local stable diffusion directory in the QByte.py configuration.

We've created a conda enviornment, qbenv.yaml, which works with both QByte and Stable Diffusion. To create this enviornment:

$ conda env create -f qbenv.yaml

Then activate it:

$ conda activate ldmqb

Then run the python QByte.py command as described above.

## QBread.py

To re-analyze the raw data from a prior session, run 'QBread.py' as follows:

python QBread.py input_file
  
Example:

$ python QBread.py QB_1630886880_BirthdayParty.txt

## MakeWordclouds.py

This script will create words from a given run. Input a filename and username. Example:

$ python MakeWordclouds.py Samantha QB_xxx.txt
