#!/bin/bash
# script for maintain wireguard end point addresses for mikrotik
# see https://github.com/pavlozt/admintools/wireguard-mikrotik-nat


PEER_TIMEOUT=180
SETTINGS_DIR=/var/www/html/wgpeerX487k3H/ # secret dir. change this

current_unixtime=`date +%s`
wg show all dump | while read ifname pubkey privkey  endpoint networks lasthandshake rx tx  keepalivesec
do
  if [ $privkey == "(none)"  ] ; then
     seconds_ago="$(($current_unixtime-$lasthandshake))"
     key_filename="${SETTINGS_DIR}/${pubkey}/addr.txt"
     key_dirname="${SETTINGS_DIR}/${pubkey}/"
     if  (( $seconds_ago < $PEER_TIMEOUT)); then
         # create peer file
         #echo create or update $endpoint $pubkey
         readarray -d : -t address <<<"$endpoint:"
         if [ ! -d "${key_dirname}" ] ; then
           mkdir -p "${key_dirname}"
         fi
         filecontent=$(<${key_filename})
         newcontent="${address[0]},${address[1]}"
         if [ "$filecontent" != "$newcontent" ] ; then
           #echo "update endpoint file"
           echo -n "$newcontent" > "${key_filename}"
         fi
         # maybe need json ?
         #echo -n "{\"host\":\"${address[0]}\",\"port\":\"${address[1]}\"}" > "$SETTINGS_DIR/$pubkey/addr.json"
         echo -n "${address[0]},${address[1]}" > "${key_filename}"
     else
        # try delete peer file
        if [ -f "${key_filename}" ] ; then
          echo delete $endpoint $pubkey
          rm "${key_filename}"
        fi
        if [ -d "${key_dirname}" ] ; then
          rmdir  -p "${key_dirname}"
        fi

     fi
  fi
done