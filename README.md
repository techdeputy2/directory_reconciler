# VHS Band Directory / Mailing list reconciliation

The script, given a CSV export of the VHS Band directory will attempt to reconcile entries against the various parent/student mailing lists that exist in our band's domain.

## Pre-requisites

Currently, rather than connecting to the live spreadsheet, this script reads a CSV export of the band directory spreadsheet. The minimum expected columns are:
`Grade,Marching Instrument,Student Email,P1 Email,P2 Email`

other columns will not affect this script but these columns must be in the file. The columns should be fairly self-explanatory:
Grade - 9 thru 12 (without counter suffixes, e.g. 9 not 9th), required for every row
Marching Instrument - If "Vision" will go to vision mailing lists, otherwise will go to band mailing lists, required for every row
Student Email - email of the student, required for every row
P1 Email - email of 1st parent
P2 Email - email of 2nd parent
The script will deal gracefully when either P1 or P2 email is missing for a given row.

### GCP credentials.json file

You'll need a `credentials.json` file for running this. Go to the [Google Cloud Platform Console](https://console.cloud.google.com), login using admin credentials for vhsband.com, select `ggbackup` as the project and then click on *Left Nav -> API & Services -> Credentials*
download the credential for `DirectoryUpdater` and save the file as `credentials.json`

## Running the script

Once you've pulled the source down, the first thing to do is setup a pipenv enviroment. Do this by doing pipenv install. [Full documentation for pipenv](https://docs.pipenv.org/en/latest/)

Execute the script using `python dirupdate.py <options>`
valid `<options>` are:
```
-r or --report executes in reporting mode displaying differences
-g or --generate executes in generator mode which prints CSV import content appropriate for bulk-importing missing entries into the corresponding google group
```

The first time you run this, it will print a URL to complete the OAuth2 authentication process. Paste this URL into a browser, login using your vhsband.com credentials, accept the permissions that the program is requesting and you'll get back a token. Copy this token and paste it back into the program run and the program will proceed as usual. Subsequent runs will use the saved 
