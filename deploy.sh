#!/bin/bash

cp example.app.yaml app.yaml
sed -i 's/DB_URL: ""/DB_URL: ""/' app.yaml
sed -i 's/NYT_API_KEY: ""/NYT_API_KEY: ""/' app.yaml
sed -i 's/GOOGLE_API_KEY: ""/GOOGLE_API_KEY: ""/' app.yaml
