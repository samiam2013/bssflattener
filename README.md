# bssflattener 
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

it should be noted that this idea is indefinitely mothballed because of new developments to address these issues in the closed source software itself. 

a hallucination of a vision of a hope that I can parse and edit CSS and HTML from bootstrap studio dynamically

currently the JS file download and replacement is fine. The CSS seems to be parsed twice, probably something that can be fixed

but the primary problem is that the Google Fonts API may not be usable if I don't force cookie and tracking consent on users. I don't want to track them, I don't want to know who they are because I don't need to for multiple sites

- [x] research using google webfonts helper API to handle just the google fonts links (cancelled - bss 6.0 added this feature)
- [ ] consider moving this tool to go because python environments have been an issue
- [ ] fix the tests so that they work when this repo is downloaded (`pytest tests.py`)
