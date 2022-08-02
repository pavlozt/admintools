:do {
 :local peerpubkey "XXXXXXXXXXXX=";
 :local baseurl "http://site.url/wgpeerX487k3H/"
 :local lasthandshake [/interface/wireguard/peers get [find public-key=($peerpubkey)] last-handshake];
 :local max_sec_timeout 180
 :local mintimeout [:tonum [:pick ($lasthandshake)  3 5 ]]
 :local sectimeout [:tonum [:pick ($lasthandshake)  6 8 ]]
 :if ( ($lasthandshake = []) || ($mintimeout =[]) || ( $mintimeout*60+$sectimeout > $max_sec_timeout ) ) do={
 #:log info ("timeout condition came. run wireguard sync.")
 :do {
   :local url  ( $baseurl . $peerpubkey . "/addr.txt" )
   :local result [/tool fetch url=$url as-value output=user];
   :if ($result->"status" = "finished") do={
      #:log info ("result: " . $result->"data")
      :local peeraddr [:toarray ( $result->"data" ) ]
      :local pdisabled [/interface/wireguard/peers get [find public-key=($peerpubkey)] disabled];
      :local paddress [/interface/wireguard/peers get [find public-key=($peerpubkey)] endpoint-address];
      :local pport [/interface/wireguard/peers get [find public-key=($peerpubkey)] endpoint-port];
      :if ( ($paddress != $peeraddr->0) || ( $pport != $peeraddr->1 ) || ($pdisabled != false)) do={
            :log info ("change peer to " . $peeraddr->0 . ":" . $peeraddr->1)
           /interface/wireguard/peers set [ find public-key=($peerpubkey) ] disabled=no endpoint-address=($peeraddr->0) endpoint-port=($peeraddr->1)
      }
    } 
   }
  }
  } on-error={
       :local pdisabled [/interface/wireguard/peers get [find public-key=($peerpubkey)] disabled];
       :if ($pdisabled != true ) do={
         :log info ("disable wireguard peer due error")
         /interface/wireguard/peers set [ find public-key=($peerpubkey)  ] disabled=yes
  }
}
