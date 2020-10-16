#!/bin/bash
#
#  Author      :: Robert Church ( robert@robertchurch.us )
#              ::
#  Description :: The purpose of this script is to grab certificate information from
#              :: the supplied directory and output basic details in JSON format.
#              :: This script would be much better in Python, but Python is not
#              :: installed on 100% of the linux hosts Splunk monitors.
#              ::
#              ::
#  Usage       :: # ./check_certificate.sh
#              :: Script takes no input
#              ::
#  Exit Codes  ::
#              :: Exit 0 = Clean exit
#              :: Exit 1 = Unable to access directory
#              ::

#
# Define the directories to inspect certificates
#

cert_directories=("/var/www/certs/" "/var/www2/certs/")




###############################################
#   DO NOT EDIT ANYTHING BELOW THIS DIVIDER   #
###############################################

datetime=$(date '+%Y-%m-%d %T.%3N %z')

JSON_START='
{
  "datetime": "%s",
  "Certificate": [
  {'

JSON_MIDDLE='
  },
  {'

JSON_FMT='
    "cert_type": "%s",
    "cert_file": "%s",
    "cert_hash": "%s",
    "notBefore": "%s",
    "notAfter": "%s",
    "issuer": "%s",
    "subject": "%s",
    "signature_algorithm": "%s",
    "x509_subject_alternative_name": "%s",
    "x509_cert_Key_Usage": "%s",
    "x509_cert_Extended_Key_Usage": "%s",
    "x509_cert_Subject_Key_Identifier": "%s"'

JSON_END='
  }]
}'

#
# Build list of certificates to examin
#

certfiles=()

count=0

printf "$JSON_START" "${datetime}"

for input_directory in "${cert_directories[@]}"
do
   if [ -d "${input_directory}" ] && [ -x "${input_directory}" ]; then
       for certfile in `find ${input_directory} -type f -name "*-cert.pem"`
       do
           certfiles+=("$certfile")
       done
   fi
done

#
# Counter for determining position in array
# Determines if comma is needed or not in json
#

#
# validate every certificate found
#

for cert in ${certfiles[@]}
do
   #
   # File is readable
   #
   certIssuer=$(openssl x509 -issuer -noout -in ${cert}|cut -d= -f2- |sed "s/^[ \t]*//");
   certStart=$(openssl x509 -startdate -noout -in ${cert}|cut -d= -f2-);
   certExpiration=$(openssl x509 -enddate -noout -in ${cert}|cut -d= -f2-);
   certSubject=$(openssl x509 -subject -noout -in ${cert}|cut -d= -f2- |sed "s/^[ \t]*//");
   certAlgorithm=$(openssl x509 -in ${cert} -text |grep "Signature Algorithm"|head -1|cut -d: -f2|sed 's/ //g');
   certSubjectAlternativeName=$(openssl x509 -in ${cert} -text |grep DNS |sed 's/^[ \t]*//');
   certKeyUsage=$(openssl x509 -in ${cert} -text |grep -A1 "X509v3 Key Usage"|tail -1|sed "s/^[ \t]*//");
   certExtendedKeyUsage=$(openssl x509 -in ${cert} -text |grep -A1 "X509v3 Extended Key Usage"|tail -1|sed "s/^[ \t]*//");
   certSubjectKeyIdentifier=$(openssl x509 -in ${cert} -text |grep -A1 "X509v3 Subject Key Identifier"|tail -1|sed "s/^[ \t]*//");
   certHash=$(md5sum $cert|awk '{ print $1 }');
   printf "$JSON_FMT" 'Certificate' "${cert}" "${certHash}" "${certStart}" "${certExpiration}" "${certIssuer}" "${certSubject}" "${certAlgorithm}" "${certSubjectAlternativeName}" "${certKeyUsage}" "${certExtendedKeyUsage}" "${certSubjectKeyIdentifier}"

   count=$(expr $count + 1)
   if [ "$count" -ne "${#certfiles[@]}" ]
   then
     printf "$JSON_MIDDLE"
   fi
done

#
# Future release will validate the ca bundles
#

printf "$JSON_END"