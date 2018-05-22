#!/usr/bin/env bash
curl --user ${CIRCLE_TOKEN}: \
    --request POST \
    --form revision=f566464b2c856cdba33a8d4e9a85d091529cb1b2 \
    --form config=@config.yml \
    --form notify=false \
        https://circleci.com/api/v1.1/project/github/unicef/etools-permissions/tree/master
