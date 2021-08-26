#!/bin/bash
secrets_file="./kubernetes/secrets.yaml"
while read -r line; do
    var="$(cut -d':' -f1 <<< "$line")"
    key="$(cut -d':' -f2- <<< "$line" | tr -d ' ' | base64 -d)"
    eval export $var=$key
done <<< "$(sed -n '/^data:$/,$p' $secrets_file | tail -n +2)"
