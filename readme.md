**Reboot, LLC Website**

The Reboot, LLC website Flask stack, built on Python 3.5.2. An outline 
of current stack functionality as well as further ideas for development 
is below:

1. Login Functionality
    * Login
    * Logout
    * Create Profile
    * Edit Profile
    * Remove Profile
    * Change Password
    * Reset Password
        * *Non-operational; Requires MalGun config.*
    * Further Ideas:
        * User Roles (i.e. admin, client, team leader, etc.)
            * *Required for expanded support ticket functionality (i.e. tie a ticket to a specific user)*
2. Emails with MailGun
    * Send Email 
        * *Non-operational; Requires MailGun config.*
3. Support
    * Create Ticket
    * Resolve Ticket
    * Further Ideas:
        * Modify Ticket: *Is this needed?*
4. Slack Integration
    * KPIs
        * Communication: *Reports communication frequency.*
        * Sentiment: *Reports organizational positivity*.
            * *Alpha, in testing.*
        * Further Ideas:
            * Optimization: *Current scripts could have cleaner code.*
            * KPI Database: *Capture KPI metrics for later analysis.*
                * *Easy to do, just question on if its a priority.*
            * Bank Account Balance
                * *Requires Xero API*
            * 30 day: Revenue, Expense, (profit / loss)
                * *Requires Xero API*
            * Support
                * *Report on support ticket frequency, avg response time, etc.*
            * Site Traffic
                * *Requires Google Analytics API*
    * Support Bot
        * *Sends a message on #support if a ticket has been issued or resolved.*
        * *Currently needs completion of urgency evaluation from issue category.*
    * Reboot Internal: *Let's come up with a great name!*
        * *A means of resolving support tickets and other tasks that interface with our internal database.*
        * Further Ideas:
            * Resolve a support ticket using a command + ticket #.
            * Activate a KPI 
            * Communicate directly with clients through Slack to SMS functionality.
                * *Requires user roles, Twilio API, websocket functionality.*
            * *We need more ideas for this! :)*
5. Blogging: *Currently text-only functionality.*
    * Create Post (text-only)
        * Further Ideas:
            * Add Images
                * *Requires Amazon S3 integration.*
            * Fancy Text Formatting
            * Save for Later
            * Autosave
    * Edit Post
    * Delete Post
6. Databases
    * MongoDB
        * *Create collection to store KPI information.*
    * Further Ideas:
        * SQL
            * *Requires creation of database classes for core db functions.*
        * Elastic Search
7. Further Ideas for Core Functionality
    * Prediction API (Pandas + SciPy + *some nice viz library*)
    
            



Non-native python dependencies:
* pymongo
* flask
* flask-login
* flask-bcrypt
* requests
* cffi
* slacker
* APScheduler
* twython
* nltk
