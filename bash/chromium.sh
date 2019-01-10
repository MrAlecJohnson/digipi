export DISPLAY=:0

DISPLAY=:0 chromium-browser --noerrdialogs \
	--disable-session-crashed-bubble \
	--disable-infobars \
	--kiosk \
	--allow-failed-policy-fetch-for-test \
	--password-store=basic \
https://datastudio.google.com/reporting/1S712euH7S8dprfCUwrMQaUcxtIJKjAE5/page/Q4cN \
https://datastudio.google.com/reporting/1cyiWdnfS0oZmhoKNnuOPMyzzwtL7CrBb/page/Q7XN \
https://datastudio.google.com/reporting/1cyiWdnfS0oZmhoKNnuOPMyzzwtL7CrBb/page/j7XN \
https://datastudio.google.com/reporting/1cyiWdnfS0oZmhoKNnuOPMyzzwtL7CrBb/page/F7bN \
