#!/bin/zsh

# notarize_sc.sh

# Based on a 2019 script by Armin Briegel - Scripting OS X

# place a copy of this script in in the project folder
# when run it will upload the pkg for notarization and 
# monitor the notarization status


K8S_SECRET_ALTOOL_ACCOUNT=""
K8S_SECRET_ALTOOL_PW=""
# the desired bundle identifier
identifier="computer.jc0b.softwarecenter"

# code starts here

projectdir=$(dirname $0)



# functions
requeststatus() { # $1: requestUUID
    requestUUID=${1?:"need a request UUID"}
    req_status=$(xcrun altool --notarization-info "$requestUUID" \
                              --username "$K8S_SECRET_ALTOOL_ACCOUNT" \
                              --password "$K8S_SECRET_ALTOOL_PW" 2>&1 \
                 | awk -F ': ' '/Status:/ { print $2; }' )
    echo "$req_status"
}

notarizefile() { # $1: path to file to notarize, $2: identifier
    filepath=${1:?"need a filepath"}
    identifier=${2:?"need an identifier"}
    
    # upload file
    echo "## uploading $filepath for notarization"
    echo $identifier
    echo $ALTOOL_ACCOUNT
    echo $ALTOOL_PW
    echo $filepath
    requestUUID=$(xcrun altool --notarize-app \
                               --primary-bundle-id "$identifier" \
                               --username "$K8S_SECRET_ALTOOL_ACCOUNT" \
                               --password "$K8S_SECRET_ALTOOL_PW" \
                               --file "$filepath" 2>&1 \
                  | awk '/RequestUUID/ { print $NF; }')
                               
    echo "Notarization RequestUUID: $requestUUID"
    
    if [[ $requestUUID == "" ]]; then 
        echo "could not upload for notarization"
        exit 1
    fi
        
    # wait for status to be not "in progress" any more
    request_status="in progress"
    while [[ "$request_status" == "in progress" ]]; do
        echo -n "waiting... "
        sleep 10
        request_status=$(requeststatus "$requestUUID")
        echo "$request_status"
    done
    
    # print status information
    xcrun altool --notarization-info "$requestUUID" \
                 --username "$K8S_SECRET_ALTOOL_ACCOUNT" \
                 --password "$K8S_SECRET_ALTOOL_PW"
    echo 
    
    if [[ $request_status != "success" ]]; then
        echo "## could not notarize $filepath"
        exit 1
    fi
    
}

notarizefile "$1" "$identifier"

# staple result
echo "## Stapling $pkgpath"
xcrun stapler staple "$pkgpath"

echo '## Done!'

exit 0


