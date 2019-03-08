# BulkUploader
A python GUI program for uploading a file to multiple servers

Nothing too much here. Wrote this for work and though others may find it useful. Feel free to submit requests if you want something changes, or submit a PR if you have a change!

## Usage
Run the app! If using windows, see the binary executable compiled with py2exe.

Select a server list file to import. The file needs to be a text file with each line having servername serverip on the line.
Next, check whatever server you want to upload the file to.
Then, select a file to upload and press upload!

The app will generate a file to store the server list so you wont have to import it next time. Reimporting overwrites this file.

## Audience
This is mainly designed for system admins who need to push up files to servers via FTP for patching or other updates.

## Issues and Requirements
Written in Python 2.7 isomg tje standard library and modules.  

I think I tested for most obvious problems and issues, but feel free to open an issue if you need. I do support, and am not a professional programmer so I would value any feedback or requests.
