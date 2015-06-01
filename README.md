# SQLAutomation
Simple automation routine for sql text (not SQL alchemy ORM language).  Let your team members easily process their existing SQL text w/out learning SQLAlchemy ORM.

Steps to use:

1. Prep your sql script for automation. To do this, take any sql script, and:

a. enter "go" between each block of code you want to run. "go" should be after each block you want to run, but extra use of this word won't hurt anything.
b.you can have comments between lines, or after a line of script on the same line. The comment MUST be indicated by a # of // c.for each "from" date in your script, substitute the word "lastdate". for each "to" date in your script, substitute the word "updatedate". This is how python will know where to change your daily dynamic date parameters when it does the update each day.
  i. if you just one to run a one-time update with static values, use "startdate1" for from dates, and "enddate1" for enddates.
  ii. Note that this implies that "startdate", "enddate", "startdate1", "enddate1" can't be used for anything else in your sql    script...treat them like reserved words. 
d. all of your drop table statements must be done as "dropifs", e.g. select dropif('a', 'markextempfti').
e.this is an example of the fact that your script must generate NO errors when it runs as normal sql. 
f. save the sql file as a .txt file. 

--that's it! any page of sql script formatted per these specs should run. The only thing I've found that didn't work so far (but works in regular ADS script runner) was a nested select of inner selects stacked with UNIONS. I'm not sure whether it was the sql itself or some python quirk.
2. prep your python script (insert your connectionstring):

All you really need to do here is put the connection string in this line:

    db = create_engine("postgresql+psycopg2://YOURUSERNAME:YOURPASSWORD@ipaddress:port/server") . I think you can also use the tableau credentials.
    the location of the json file, e.g. fileset=json.loads(open('/pathtojsonconfigfile/jsonconfigfile.json').read()) 

3. prep your json config file.

the json file (see attached below) is config file, and you put into it all the parameters you'll need for running the SQL script.

They are as follows:

{
"howtomakethisfile": "https://github.com/mgoold/SQLAutomation/edit/master/README.md",
"description":"a description of what this file is for, e.g. update executive summary",
"emailto":"the email you want to send alerts to",
"emailfrom":"youremailaddress",
"dateset":
{"startdate1":<insert date>,
"enddate1":<insert date>,
"startdate2":<insert date>,
"enddate2":<insert date>
},
"checkscript":a select statement that returns ONLY the max date from the table you want to update,
"files":
{
"1":["/pathtosqlyouwillrun/sqlfileyouwillrun.txt","update","drop all tables"]
}
}

Notes about this json file:

The start and end dates are dates you plug into the sql script using the same keywords (startdate1, enddate1 etc). When the python script runs, it will go through your file and replace all the keywords e.g. startdate1 with the date value. If you are updating the file, you don't need to use these parameters; the checkscript key value pair alone will do the date evaluations.

The "files" key returns a list of sql text you want to run. You could run a list of files if you wanted to. If you want to update (add data to) the file, use the "update" keyword. If you want to run the script just one time with fixed dates, use the keyword "sub" instead of "update".

{
"howtomakethisfile": "http://devilya01/foswiki/DataAnalyticsYou/UsingSQLAutomationScript",
"description":"engagement dashboard daily update",
"emailto":"mgoold@ancestry.com",
"emailfrom":"mgoold@ancestry.com",
"dateset":
{"startdate1":"2013-01-01",
"enddate1":"2013-01-02",
"startdate2":"2013-01-01",
"enddate2":"2013-01-02"
},
"checkscript":"select max(dayid) from a.markengexeccombined",
"files":
{
"1":["/home/mark/Documents/ReportAutomation/execengagementautomation.txt","update","drop all tables"]
}
}

The checkscript is a simple sqlstatement that you feed python; it should return the maximum date from the table you want to update. For example, suppose you have a column "dayid" in your table by which you break out your data. You know that unless today's date is at least one day greater than the max "dayid" value, there will be no point in updating your table. In that case, your checkscript should simply be "select max(dayid) from <YOURTABLENAME>". The single time data point resulting from this script will be evaluated by python to see if enough time has elapsed to make it worth running an update.
4. Set up a folder on the ubuntu box. It will need to have 3 things:

    your python script
    the json file
    the sql script you want to run 
    
5. Use gnome-scheduler (or launchd, or whatever you've got) to schedule your adapation of the python script in this project to run.  Try a one-time run to QA it, then schedule normally.  Blammo!  You've done your first home-spun ETL!
