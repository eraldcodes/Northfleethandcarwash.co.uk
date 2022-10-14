#!/usr/bin/perl -w
use strict;
eval {
  require BSD::Resource;
  BSD::Resource::setrlimit(BSD::Resource::RLIMIT_AS(), 128000000, 1280000000);
  BSD::Resource::setrlimit(BSD::Resource::RLIMIT_CPU(), 120, 120);
};
use CGI;
use Cwd 'getcwd';
use IO::Handle;
STDOUT->autoflush(1);
my $cwd=getcwd();
my $root_path;
if($cwd=~m#^(/home/(?:sites|cluster-sites/\d+)/[\w\.\-]+/)#) {
	$root_path=$1;
} elsif($cwd=~m#^(.*?/)(?:public_html|web/content)#) {
	$root_path=$1;
} else {
	die
}

# Adjust the initial analysis start date to be about six months ago so that new
# installations get six months or more of data by default.  Customers can adjust
# it manually after installation to an earlier date which may analyse more
# information if earlier logs exist.
my $cache_marker_file = $cwd . '/dnscachelastupdate.txt' ;
my ( $year, $month, $day ) = ( localtime )[ 5, 4, 3 ] ;
use Time::Local ;
my $now = timelocal( 0, 0, 0, $day, $month, $year ) ;    # epoch seconds
my $then = $now - ( 183 * 24 * 3600 ) ;                  # epoch seconds
use Time::localtime ;
my $tm = localtime( $then ) ;
my $six_months_ago = sprintf( "%4d-%02d-%02d", $tm->year + 1900, $tm->mon + 1, $tm->mday ) ;
warn "six_months_ago = $six_months_ago " ;

`touch -d \'$six_months_ago\' $cache_marker_file` ;

$0 = "awstats";

my $cgi=new CGI;
%ENV=(PATH=>'/bin:/usr/bin:/usr/local/bin', HTTP_HOST=>$ENV{HTTP_HOST});

$|=1;

print $cgi->header("text/html");
print "<html><head><title>AWStats</title></head><body>";
print "<p>Generating stats for the first time. Please wait, this can take a while.</p><p>";

my $pid=fork();
die unless defined $pid;

if(!$pid) {
	# child
  open(STDOUT, ">&STDERR");
	exec("./awstats.pl","-config=northfleethandcarwash.co.uk", "-update");
	exit 1;
}
use POSIX ":sys_wait_h";
my $i = 0;
while(waitpid(-1, WNOHANG) <= 0) {
  $i++;
  print ".";
  if($i % 100 == 0) {
    print "<br/>\n";
  }
  sleep 1;
}
print "</p><p>Complete. You will be redirected to <a href='awstats.pl'>the stats page</a> in a moment.</p>";
print "<script type='text/javascript'>function onward() {location.href='awstats.pl'} setTimeout(onward, 3000)</script>";
print "</body></html>";
