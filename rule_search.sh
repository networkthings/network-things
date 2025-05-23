#!/bin/bash

# syntax rule_search.sh "<search string>". i
# When logged into AWS account this will search all AWS managed NWFW rule groups for the keywork in the Suricata ruleset.

# Check if search term is provided
if [ -z "$1" ]; then
  echo "Usage: $0 <search_term>"
  echo "Example: $0 log4j"
  exit 1
fi

SEARCH_TERM="$1"

# Get all managed rule groups
rule_groups=$(aws network-firewall list-rule-groups --type STATEFUL --scope MANAGED --query 'RuleGroups[*].Arn' --output text)

echo "Searching for '$SEARCH_TERM' in AWS managed rule groups (case insensitive)..."
echo "----------------------------------------------------"

# Loop through each rule group and search for the term
for arn in $rule_groups; do
  group_name=$(basename "$arn")
  echo "Checking rule group: $group_name"
  
  # First try with describe-rule-group
  rules=$(aws network-firewall describe-rule-group \
    --rule-group-arn "$arn" \
    --query 'RuleGroup.RulesSource.RulesString' \
    --output text 2>/dev/null)
  
  # If that fails, try with describe-rule-group-metadata
  if [ $? -ne 0 ] || [ -z "$rules" ]; then
    rules=$(aws network-firewall describe-rule-group-metadata \
      --rule-group-arn "$arn" \
      --query 'RuleGroupResponse.RuleGroup.RulesSource.RulesString' \
      --output text 2>/dev/null)
  fi
  
  # If rules were retrieved successfully, search for the term (case insensitive)
  if [ -n "$rules" ]; then
    match=$(echo "$rules" | grep -i "$SEARCH_TERM")
    
    # If term is found, print the rule group name and matching rules
    if [ -n "$match" ]; then
      echo "✓ Found '$SEARCH_TERM' in rule group: $group_name"
      echo "Matching rules:"
      echo "$rules" | grep -i "$SEARCH_TERM"
      echo "----------------------------------------------------"
    fi
  fi
done

echo "Search complete."

