rasa run --enable-api --cors "*" -vv > run.log 2>&1&
rasa run actions -vv > actions.log 2>&1 &
