
PYPATH=../../../
LOG_FILE=tests.log

test:
	rm -f ${LOG_FILE}
	PYTHONPATH=${PYPATH} ../objects/simple_queue.py ${LOG_FILE}
	PYTHONPATH=${PYPATH} ../objects/field.py ${LOG_FILE}
	PYTHONPATH=${PYPATH} ../objects/header.py ${LOG_FILE}
	PYTHONPATH=${PYPATH} ../instance.py ${LOG_FILE}
	PYTHONPATH=${PYPATH} ../objects/table_entry.py ${LOG_FILE}
	PYTHONPATH=${PYPATH} ../objects/action.py ${LOG_FILE}
	PYTHONPATH=${PYPATH} ../objects/table.py ${LOG_FILE}
	PYTHONPATH=${PYPATH} ../objects/parsed_packet.py ${LOG_FILE}
	PYTHONPATH=${PYPATH} ../objects/parser.py ${LOG_FILE}
	PYTHONPATH=${PYPATH} ../objects/parser.py ${LOG_FILE} unit_test.yml
	PYTHONPATH=${PYPATH} ../objects/parser.py ${LOG_FILE} profile_1.yml simple.yml
	PYTHONPATH=${PYPATH} ../objects/parser.py ${LOG_FILE} profile_0.yml l3.yml
	PYTHONPATH=${PYPATH} ../objects/pipeline.py ${LOG_FILE}

clean:
	rm ${LOG_FILE}
