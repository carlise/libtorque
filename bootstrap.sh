#!/bin/sh

# Create python virtualenv to run tests

# Check if .pyenv is made
# Outside Jenkins, workspace evaluates to nothing

PYENV_HOME=${WORKSPACE:-$PWD}/.pyenv

if [ -d $PYENV_HOME ] ; then
	rm -rf $PYENV_HOME
fi

# Create the virtual testing environment
virtualenv --no-site-packages .pyenv
. .pyenv/bin/activate
pip install --quiet nose2
pip install --quiet pylint
pip install --quiet cov-core

# Run test
pylint --msg-template="{path}:{line}: [{msg_id}({symbol}), {obj}] {msg}" \
		torquefilter > pylint.out || exit 0
