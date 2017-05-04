#!/bin/bash

if [[ $EUID = 0 ]]; then
        echo -e "\nIsto NAO deve ser executado como root" 2>&1
        echo -e "\n" 2>&1
        exit 1
fi

PROJECT_DIR_ABSOLUTE_PATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
CURRENT_DIR="$(pwd)"
VIRTUALENV_NAME="procapi"

cd "${PROJECT_DIR_ABSOLUTE_PATH}"

echo -e "Ativando virtualenv: ${VIRTUALENV_NAME}"
source "${HOME}/.virtualenvs/${VIRTUALENV_NAME}/bin/activate"

pkill -9 -f 'celery (flower|beat|worker)' > /dev/null 2>&1 || {
        echo "Erro ao matar processos do celery: Nenhum processo encontrado.";
}

echo "reiniciando celery";

celery flower -A procapi.taskapp --port=5555 &
celery beat -A procapi.taskapp --loglevel=ERROR -S django --logfile "${PROJECT_DIR_ABSOLUTE_PATH}/log/celery_beat.log" &
celery worker -A procapi.taskapp --loglevel=ERROR --concurrency=8 -n worker1@%h --logfile "${PROJECT_DIR_ABSOLUTE_PATH}/log/celery_worker1.log" &
celery worker -A procapi.taskapp --loglevel=ERROR --concurrency=8 -n worker2@%h --logfile "${PROJECT_DIR_ABSOLUTE_PATH}/log/celery_worker2.log" &
celery worker -A procapi.taskapp --loglevel=ERROR --concurrency=8 -n worker3@%h --logfile "${PROJECT_DIR_ABSOLUTE_PATH}/log/celery_worker3.log" &
celery worker -A procapi.taskapp --loglevel=ERROR --concurrency=8 -n worker4@%h --logfile "${PROJECT_DIR_ABSOLUTE_PATH}/log/celery_worker4.log" &

echo -e "\n\n\nconcluido.";
cd "${CURRENT_DIR}"
