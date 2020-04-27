#!/bin/bash

az group create --name PyconLab --location westus2
busName="PyconLabBus$(cat /dev/urandom | base64 | head -c6)"
az servicebus namespace create --name $busName --resource-group PyconLab
az servicebus queue create --name PyconLabQueue --resource-group PyconLab --namespace-name $busName
accessRule=$(az servicebus namespace authorization-rule list --namespace-name $busName \
    --resource-group PyconLab \
    --query '[0].name' \
    --output tsv)
SB_CONNECTION=$(az servicebus namespace authorization-rule keys list \
    --resource-group PyconLab \
    --namespace-name $busName \
    --name $accessRule \
    --query 'primaryConnectionString' \
    --output tsv)

echo $SB_CONNECTION | tee .servicebus.uri