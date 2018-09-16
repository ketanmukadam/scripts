#!/usr/bin/python3
"""
Usage: bugz.py [options]

Options:
  -h, --help            show this help message and exit
  -u BZ_URL, --url=BZ_URL
                        Bugzilla URL
  -q Q_URL, --query=Q_URL
                        Bugzilla Query URL
  -b BUGID, --bugid=BUGID
                        Bug Id
  -v, --verbose         Enable Logs
   
"""
#
# Sanity Script
#
import os, sys, re, datetime, time
import bugzilla
from optparse import OptionParser

#defaults user configurable
LOCAL_LOG_FILE="bugz"

#Globals
DEVNULL=open(os.devnull, 'w')
LOG=None
LOCAL_LOG_FILE= os.getcwd() + "/" + LOCAL_LOG_FILE
LOCAL_BZ_FOLDER= os.getcwd() + "/" + "bug_attach"
BUGZILLA=None

def log_open(log_name):
    global LOG
    LOG=open(log_name, 'w')

def print_log(string):
    global LOG
    print(string)
    if LOG:
        LOG.write(string+ "\n")

def log_close():
    global LOG
    LOG.close()

def create_folder(dirname):
    try:
        if not os.path.exists(dirname):
            os.makedirs(dirname)
    except OSError:
        pass

def get_bug_all_attachments(bz,bug):
    if not bug : return
    print_log(str(bug.id)+" "+bug.summary+" "+bug.status)
    for x in bug.get_attachment_ids():
        att = bz.openattachment(x) 
        ofile = bz.util.open_without_clobber(att.name, "wb")
        print_log("Getting attachment %s (%d)" % (att.name, x))
        fsize = 4096
        data = att.read(4096)
        while data:
             ofile.write(data)
             data = att.read(4096)
             fsize = fsize + 4096
             print_log ("Wrote %d bytes in %s" % (fsize, ofile.name))

def run_main(options):
    if not options.bz_url : return
    print_log("Starting bugz script %s" % options.bz_url)
    BUGZILLA = bugzilla.Bugzilla(url=options.bz_url)
    if not BUGZILLA.logged_in:
        print_log("Unable to log into %s" % options.bz_url)
        BUGZILLA.interactive_login()
    t1 = time.time()
    if not options.bugid:
       print_log("Initiating Query %s" % options.q_url)
       query = BUGZILLA.url_to_query(options.q_url)
       query["include_fields"] = ["id", "summary", "status"]
       buglist = BUGZILLA.query(query)
       print_log ("The query returned %d Bugs" % len(buglist))
       create_folder(LOCAL_BZ_FOLDER) 
       os.chdir(LOCAL_BZ_FOLDER)
       count = len(buglist) - 1 
       for b in buglist:
         if count :
           print_log("Creating %d & downloading attachments..." % b.id)
           create_folder(str(b.id))
           os.chdir(str(b.id))
           get_bug_all_attachments(BUGZILLA,b)
           count = count - 1
           os.chdir(LOCAL_BZ_FOLDER)
    else:
       print_log ("Bug id = %d" % options.bugid)
       bug = BUGZILLA.getbug(options.bugid)
       get_bug_all_attachments(BUGZILLA,bug)
    t2 = time.time()
    print_log ("Processing Time : %s" % (t2 - t1))
    return 0

def argparser():
    """
    Option parsing of command line

    It will add the required arguments to OptionParser module
    Collects and parse the arguments

    Parameters
    ---------
    None

    Returns
    -------
    opts: Parsed arguments (or their defaults) returned in opts
    """
    parser = OptionParser(usage="usage: %prog [options]")
    parser.add_option(
        "-u","--url", dest="bz_url", help="Bugzilla URL", default="None")
    parser.add_option(
        "-q","--query", dest="q_url", help="Bugzilla Query URL", default="")
    parser.add_option(
        "-b","--bugid", dest="bugid", type="int", help="Bug Id", default=0)
    parser.add_option(
        "-v","--verbose", action="store_true", dest="verbose", help="Enable Logs", default=False)
    (opts, args) = parser.parse_args(sys.argv)
    return opts

if __name__ == "__main__":
    options = argparser()
    if (options.verbose) :
        TIMENOW = datetime.datetime.now().strftime('%m%d%Y-%H%M')
        log_open(LOCAL_LOG_FILE+"-"+TIMENOW+".log")
        print_log("\nTest Script")
        print_log("Invoked as (" + " ".join(sys.argv) + ")\n")
    if (run_main(options)):
        sys.exit(1)
    else:
        sys.exit(0)
