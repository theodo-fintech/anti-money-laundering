# Anti Money Laundering Dojo

## Requirements

- Python 3

## Installation

Launch the following script:

```bash
pip install -r requirements.txt
```

## Coding

In the `receiver.py` file, begin by changing the `TEAM_NAME` and `TEAM_PASSWORD` variables by your team name and password.

In this dojo, you will need to code the is_transaction_fraudulent method to state if a given transaction is fraudulent or not.

Once you are confident in this function, uncomment the `send_value(transaction['id'], is_fraud)` call line 54 so that our server can compute your score !
