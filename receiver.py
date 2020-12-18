#!/usr/bin/env python
import asyncio
import websockets
import requests
import json
import urllib.parse
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn import metrics

API_HOST = "aml.sipios.com"
API_PORT = "8080"
API_ENDPOINT_SCORE = "/transaction-validation"
API_WEBSOCKET_TRANSACTION = "ws://" + API_HOST + ":" + API_PORT + "/transaction-stream/username/"

TEAM_NAME = "??"
TEAM_PASSWORD = "??"


def parse_dataset_card_type(x):
    card_type = {"gold": 1, "silver": 2, "platinium": 3}
    for x_value in x:
        x_value[2] = card_type[x_value[2]]
    return x


def hash_transaction_for_position_check(transaction):
    return hash(
        transaction["lastName"] + transaction["firstName"] + str(transaction["iban"]) + str(transaction["amount"]) +
        transaction[
            "idCard"])


def hash_transaction_for_amount_check(transaction):
    return hash(
        transaction["lastName"] + transaction["firstName"] + str(transaction["iban"]) + str(transaction["idCard"]))


def train_model(model):
    dataset = pd.read_csv("transactions_samples.csv")
    X = dataset.iloc[:, 2:8].values
    y = dataset.iloc[:, 0].values
    X = parse_dataset_card_type(X)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    print("Accuracy:", metrics.accuracy_score(y_test, y_pred))
    return model


model = RandomForestClassifier()
model = train_model(model)


def send_value(transaction_id, is_fraudulent):
    url = "http://" + API_HOST + ":" + API_PORT + API_ENDPOINT_SCORE
    params = {
        'username': TEAM_NAME,
        'password': TEAM_PASSWORD
    }
    queryParams = urllib.parse.urlencode(params)
    url += "?" + queryParams

    # data to be sent to api
    data = {
        'fraudulent': is_fraudulent,
        'transaction': {
            'id': transaction_id
        }
    }

    # sending post request and saving response as response object
    requests.post(url=url, json=data, )


async def receive_transaction():
    uri = API_WEBSOCKET_TRANSACTION + TEAM_NAME
    async with websockets.connect(uri) as websocket:
        while True:
            try:
                received = json.loads(await websocket.recv())
                process_transactions(received)
            except Exception as e:
                print(e)
                print('Reconnecting')
                websocket = await websockets.connect(uri)


def process_transactions(transactions):
    fraudulent_transactions = set().union(machine_learning_check(transactions), position_fraud_check(transactions),
                                          amount_fraud_check(transactions), check_simple_frauds(transactions))

    for transaction in transactions:
        if transaction["id"] in fraudulent_transactions:
            send_value(transaction["id"], True)
        else:
            send_value(transaction["id"], False)


def machine_learning_check(transactions):
    transaction_dataset = pd.json_normalize(transactions)
    column_list = ["merchantId", "merchantCodeCategory", "cardType",
                   "transactionProcessingDuration", "bitcoinPriceAtTransactionTime", "ethPriceAtTransactionTime"]
    transaction_dataset = transaction_dataset[column_list]
    transaction_dataset.head()
    x = transaction_dataset.iloc[:, :].values
    x = parse_dataset_card_type(x)
    prediction = model.predict(x)
    fraudulent_transactions = set()
    for i, t in enumerate(prediction):
        if t:
            fraudulent_transactions.add(transactions[i]['id'])
    print("ml fraud", fraudulent_transactions)
    return fraudulent_transactions


def position_fraud_check(transactions):
    current_transaction_dict = {}
    fraudulent_transactions = set()
    for transaction in transactions:
        hashed_transaction = hash_transaction_for_position_check(transaction)
        if hashed_transaction in current_transaction_dict:
            fraudulent_transactions.add(transaction["id"])
            fraudulent_transactions.add(current_transaction_dict[hashed_transaction])
        else:
            current_transaction_dict[hashed_transaction] = transaction["id"]
    print("position fraud", fraudulent_transactions)
    return fraudulent_transactions


def amount_fraud_check(transactions):
    fraudulent_transactions = set()
    previous_transaction = None
    for current_transaction in transactions:
        if previous_transaction is None:
            previous_transaction = current_transaction
            continue

        if hash_transaction_for_amount_check(current_transaction) == hash_transaction_for_amount_check(
                previous_transaction):
            current_amount_diff = previous_transaction["amount"] - current_transaction["amount"]
            if current_amount_diff != 0:
                fraudulent_transactions.add(previous_transaction["id"])
                fraudulent_transactions.add(current_transaction["id"])
        previous_transaction = current_transaction
    print("amount fraud", fraudulent_transactions)
    return fraudulent_transactions


def check_simple_frauds(transactions):
    fraudulent_transactions = set()
    for transaction in transactions:
        if is_name_fraud(transaction["firstName"]) or is_name_fraud(transaction["lastName"]) or is_position_fraud(
                transaction["latitude"], transaction["longitude"]):
            fraudulent_transactions.add(transaction["id"])
    print("simple fraud", fraudulent_transactions)
    return fraudulent_transactions


def is_name_fraud(name):
    return name in ["fraud", "frauder", "superman", "robinwood", "picsou"]


def is_position_fraud(latitude, longitude):
    if latitude == 39.01 and longitude == 125.73:
        return True
    elif latitude == 6.46 and longitude == 3.24:
        return True
    elif latitude == 12.97 and longitude == 77.58:
        return True
    return False


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(receive_transaction())
