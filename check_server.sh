#!/bin/bash
#
#  Author      :: Robert Church ( rchurch@robertchurch.us )
#              ::
#  Description :: The purpose of this script is to perform a baseline validation of
#              :: a server to ensure it meets requirements for handoff.  Script will
#              :: utilize exit codes for automation purposes.
#  Updates     ::
#              :: 2017.04.10 - v0.1 - Initial concept converted into bash script
#              :: 2017.04.11 - v0.2 - Added registration, firewall verification
#              :: 2017.04.12 - v0.3 - Added yum, reboot, verification
#              :: 2017.04.12 - v0.4 - Added comments and blocking
#              :: 2017.04.12 - v1.0 - Script released to teams for build verifiation
#              :: 2017.04.13 - v1.1 - Added headers, added block for firewall validation
#              :: 2017.06.06 - v1.2 - Added Salt Verification
#              :: 2017.06.13 - v1.3 - Added Splunk forwarder Verification
#              ::
#  Usage       :: # ./check_server.sh
#              :: # echo $?
#              ::
#  Exit Codes  ::
#              :: Exit 0 = Server passed all checks
#              :: Exit 1 = Server did not pass one or more check
#              :: Exit 2 = Scripted exited in failed state
#              ::

#
# Script variables
#

ipatestaccount=testacct

#
# Display Functions
#

display_pass()
{
 echo -e "[     \e[32mPASS\e[0m ] - " $1;
}

display_nopass()
{
 echo -e "[  \e[31mNO PASS\e[0m ] - " $1;
}

exit_failure()
{
 echo -e "[     \e[31mFAIL\e[0m ] - " $1; 
 exit 2
}

#
# Script must be run as root
#

uid=$(id -u)
if [[ $uid != 0 ]]; then exit_failure "Script must be executed as root, exiting"; fi

#
# Check if server is registered to Satellite or not
#

command -v rhn_check > /dev/null 2>&1
rc=$?;
if [[ $rc != 0 ]];
 then
  display_nopass "Command rhn_check does not exist.";
  nopass=TRUE
 else
  rhn_check > /dev/null 2>&1
  rc=$?;
  if [[ $rc != 0 ]];
   then
    display_nopass "Problem detected with server registration.";
    nopass=TRUE
   else
    display_pass "Server registered to satellite.";
  fi
fi

#
# Check if selinux is set to Enforcing
#

command -v getenforce > /dev/null 2>&1
rc=$?;
if [[ $rc != 0 ]];
 then
  display_nopass "Selinux is not installed.";
  nopass=TRUE
 else
  getenforce | grep -q Enforcing > /dev/null 2>&1;
  rc=$?
  if [[ $rc != 0 ]];
   then
    display_nopass "Selinux not set to Enforcing.";
    nopass=TRUE
   else
    display_pass "Selinux set to Enforcing.";
  fi
fi

#
# If RHEL 6 :: Check iptables
# If RHEL 7 :: Check firewalld
#

command -v firewall-cmd > /dev/null 2>&1
rc=$?
if [[ $rc != 0 ]];
 then
  #
  # RHEL 6
  #
  chkconfig --list iptables | grep -q on > /dev/null 2>&1
  rc=$?
  if [[ $rc != 0 ]];
   then
    display_nopass "Iptables is not enabled.";
    nopass=TRUE
   else
    display_pass "Iptables is enabled.";
    #
    # Verify drop rule at end of chain
    #
  fi
 else
  #
  # RHEL 7
  #
  systemctl is-enabled firewalld > /dev/null 2>&1
  rc=$?
  if [[ $rc != 0 ]];
   then
    display_nopass "Firewalld is not enabled.";
    nopass=TRUE
   else
    display_pass "Firewalld is enabled.";
    #
    # Verify drop rule at end of chain
    #
  fi
fi

#
# Check IPA
#

command -v systemctl > /dev/null 2>&1
rc=$?
if [[ $rc != 0 ]];
 then
  #
  # RHEL 6
  #
  chkconfig --list sssd | grep -q on > /dev/null 2>&1
  rc=$?
  if [[ $rc != 0 ]];
   then
    display_nopass "sssd is not enabled.";
    nopass=TRUE
   else
    display_pass "sssd is enabled.";
    id ${ipatestaccount} > /dev/null 2>&1
    rc=$?;
    if [[ $rc != 0 ]];
     then
      display_nopass "sssd is not functioning as expected.";
      nopass=TRUE
     else
      display_pass "sssd is functioning as expected.";
    fi
  fi
 else
  #
  # RHEL 7
  #
  systemctl is-enabled sssd > /dev/null 2>&1
  rc=$?
  if [[ $rc != 0 ]];
   then
    display_nopass "sssd is not enabled.";
    nopass=TRUE
   else
    display_pass "sssd is enabled.";
    id bacontaco > /dev/null 2>&1
    rc=$?;
    if [[ $rc != 0 ]];
     then
      display_nopass "sssd is not functioning as expected.";
      nopass=TRUE
     else
      display_pass "sssd is functioning as expected.";
    fi
  fi
fi

#
# Check puppet
#

command -v systemctl > /dev/null 2>&1
rc=$?
if [[ $rc != 0 ]];
 then
  #
  # RHEL 6
  #
  chkconfig --list puppet | grep -q on > /dev/null 2>&1
  rc=$?
  if [[ $rc != 0 ]];
   then
    display_nopass "Puppet is not enabled.";
    nopass=TRUE
   else
    display_pass "Puppet is enabled.";
    puppet status info > /dev/null 2>&1
    rc=$?;
    if [[ $rc != 0 ]];
     then
      display_nopass "Puppet agent not functional.";
      nopass=TRUE
     else
      display_pass "Puppet agent functional.";
    fi
  fi
 else
  #
  # RHEL 7
  #
  systemctl is-enabled puppet > /dev/null 2>&1
  rc=$?
  if [[ $rc != 0 ]];
   then
    display_nopass "Puppet is not enabled.";
    nopass=TRUE
   else
    display_pass "Puppet is enabled.";
    puppet status info > /dev/null 2>&1
    rc=$?;
    if [[ $rc != 0 ]];
     then
      display_nopass "Puppet agent not functional.";
      nopass=TRUE
     else
      display_pass "Puppet agent functional.";
    fi
  fi
fi

#
# Verify server is fully patched
#

command -v yum > /dev/null 2>&1
rc=$?;
if [[ $rc != 0 ]];
 then
  display_nopass "Command yum does not exist.";
  nopass=TRUE
 else
  yum check-update > /dev/null 2>&1
  rc=$?;
  if [[ $rc == 100 ]];
   then
    display_nopass "Server updates are avaialable, please run 'yum update'.";
    nopass=TRUE
   elif [[ $rc == 1 ]];
    then
     display_nopass "Server unable to check for updates, please run 'yum check-update'.";
     nopass=TRUE
   else
    display_pass "Server is currently up to date.";
  fi
fi

#
# Check Salt
#

command -v systemctl > /dev/null 2>&1
rc=$?
if [[ $rc != 0 ]];
 then
  #
  # RHEL 6
  #
  chkconfig --list salt-minion | grep -q on > /dev/null 2>&1
  rc=$?
  if [[ $rc != 0 ]];
   then
    display_nopass "salt-minion is not enabled.";
    nopass=TRUE
   else
    display_pass "salt-minion is enabled.";
    grep -q master.*com.* /etc/salt/minion > /dev/null 2>&1
    rc=$?;
    if [[ $rc != 0 ]];
     then
      display_nopass "salt-minion is configured.";
      nopass=TRUE
     else
      display_pass "salt-minion is configured.";
    fi
  fi
 else
  #
  # RHEL 7
  #
  systemctl is-enabled salt-minion > /dev/null 2>&1
  rc=$?
  if [[ $rc != 0 ]];
   then
    display_nopass "salt-minion is not enabled.";
    nopass=TRUE
   else
    display_pass "salt-minion is enabled.";
    grep -q master.*com.* /etc/salt/minion > /dev/null 2>&1
    rc=$?;
    if [[ $rc != 0 ]];
     then
      display_nopass "salt-minion is not configured.";
      nopass=TRUE
     else
      display_pass "salt-minion is configured.";
    fi
  fi
fi

#
# Check Splunk
#



command -v systemctl > /dev/null 2>&1
rc=$?
if [[ $rc != 0 ]];
 then
  #
  # RHEL 6
  #
  command -v /opt/splunkforwarder/bin/splunkd > /dev/null 2>&1
  rc=$?
  if [[ $rc != 0 ]];
   then
    #
    # Splunk not installed
    #
    display_nopass "Splunk forwarder is not installed.";
    nopass=TRUE
  else
   chkconfig --list | grep splunk | grep -q 3:on > /dev/null 2>&1
   rc=$?
   if [[ $rc != 0 ]];
    then
     display_nopass "Splunk forwarder is not enabled.";
     nopass=TRUE
    else
     display_pass "Splunk forwarder is enabled.";
     grep -q server.*com.* /opt/splunkforwarder/etc/apps/sendtoindexer_prod/local/outputs.conf > /dev/null 2>&1
     rc=$?;
     if [[ $rc != 0 ]];
      then
       display_nopass "Splunk forwarder not configured.";
       nopass=TRUE
      else
       display_pass "Splunk forwarder configured.";
     fi
   fi
  fi
  else
  #
  # RHEL 7
  #
  command -v /opt/splunkforwarder/bin/splunkd > /dev/null 2>&1
  rc=$?
  if [[ $rc != 0 ]];
   then
    #
    # Splunk not installed
    #
    display_nopass "Splunk forwarder is not installed.";
    nopass=TRUE
  else
   systemctl is-enabled splunk > /dev/null 2>&1
   rc=$?
   if [[ $rc != 0 ]];
    then
     display_nopass "Splunk forwarder is not enabled.";
     nopass=TRUE
    else
     display_pass "Splunk forwarder is enabled.";
     grep -q server.*com.* /opt/splunkforwarder/etc/apps/sendtoindexer_prod/local/outputs.conf > /dev/null 2>&1
     rc=$?;
     if [[ $rc != 0 ]];
      then
       display_nopass "Splunk forwarder not configured.";
       nopass=TRUE
      else
       display_pass "Splunk forwarder configured.";
     fi
   fi
  fi
fi

#
# Verify if reboot is required
#

if [ -f /var/run/reboot-required ]; then
 display_nopass "Reboot is required.  Please reboot and run script again"
 nopass=TRUE
fi

#
# Check if there were any NO PASS in test
#

if $NOPASS; then exit 1; else exit 0; fi
