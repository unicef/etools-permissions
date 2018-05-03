#!/usr/bin/env bash
curl --user ${CIRCLE_TOKEN}: \
    --request POST \
    --form revision=532b5ef3a88b6b9bd990371d4404f34b2b9812db \
    --form config=@config.yml \
    --form notify=false \
        https://circleci.com/api/v1.1/project/github/unicef/etools-permissions/tree/master
