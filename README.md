## Qbyte.py
Data Visualization for Qbyte Processing

Steps to run locally:

1. Clone this directory onto your local machine
2. Configure your desired settings at the top of 'QByte.py'. The comments explain what each setting is.
3. Run 'QByte.py' from the command line as follows:

python QByte.py mode remarks

MODE: This can be 'static' or 'auto'. The only difference between the two is that the 'auto' mode will automatically switch views.

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

## Technologies Used

The web3.storage will be used in conjunction with our municipal art registry, which has been authorized for a grant by the NEAR foundation and is currently undergoing review by the city of Alameda, CA (see https://www.municipalartregistry.org/ - password 'halo'). Namely, an artist who submits a profile to the registry will automatically have their data uploaded to the decentralized web storage platform, and an NFT with that data will be created. The artist can mint additional NFTs by uploading their art in the integrated web3.storage. As an experimental aspect, QByte.py will be used in a myriad of ways, such as experiments to improve the mental "flow-states" in the creators who use our platform.

The Alameda Art Registry project has an ambitious but well-supported goal of onboarding 1000 artists and 100 small buisinesses, thereby turning Alameda into an international arts destination. With success, other municipalities can clone our repository and impliment the technology to improve their municipal art programs and policies.
