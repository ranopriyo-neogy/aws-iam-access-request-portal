#!/bin/bash

set -e
PACKAGE_NAME="lambda_function.zip"
zip -g ${PACKAGE_NAME} lambda_function.py create_user.py