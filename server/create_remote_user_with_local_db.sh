#!/bin/bash
# Usage: ./add_test_user.sh <username> <name> <password> <path_to_anki2_file>
USERNAME=$1
NAME=$2
PASSWORD=$3
ANKI_FILE=$4

RESPONSE=$(curl -s -X POST https://study-amigo.app/register \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"$USERNAME\", \"name\":\"$NAME\", \"password\":\"$PASSWORD\"}")

USER_ID=$(echo "$RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin)['userId'])")

scp -i ~/.ssh/study-amigo-aws "$ANKI_FILE" "/opt/study-amigo/server/user_dbs/user_${USER_ID}.db"
echo "User $USERNAME (ID: $USER_ID) created with database from $ANKI_FILE"
