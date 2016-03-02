# Simple make file for AIR target
ROOT_DIR=../../..

OFTEST_PATH=${ROOT_DIR}/submodules/oftest
OFTEST_PYTHON=${OFTEST_PATH}/src/python
PYPATH=PYTHONPATH=${ROOT_DIR}/:${OFTEST_PYTHON}

start: submodule
	sudo ${PYPATH} ./start.py -v profile_1.yml simple.yml

start-l3: submodule
	sudo ${PYPATH} ./start.py -v profile_0.yml l3.yml

start-vxlan: submodule
	sudo ${PYPATH} ./start.py -v profile_1.yml vxlan/*.yml

submodule:
	git submodule update --init

help:
	@echo "Run PifIR code. Targets:"
	@echo "  start:     Start the switch with code from START_YML env var"
	@echo "  start-l3:  Start the switch with simple L3 switch"

.PHONY: submodule start start-l3 help

