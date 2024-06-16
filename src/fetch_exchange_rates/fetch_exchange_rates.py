# -*- coding: utf-8 -*-
import json
import requests
import boto3
from datetime import datetime
from decimal import Decimal


def fetch_exchange_rates(event, context):
    """
    Fetches daily exchange rates from the European Central Bank (ECB) and stores them in DynamoDB.

    This function is triggered by an AWS Lambda event. It requests the latest exchange rates in XML format
    from the ECB, parses the XML data, and stores the exchange rates in a DynamoDB table.

    Args:
        event (dict): AWS Lambda event data.
        context (LambdaContext): AWS Lambda context object.

    Returns:
        dict: Response containing statusCode and body message.
    """
    url = "https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml"
    response = requests.get(url)
    response.raise_for_status()

    data = response.content
    exchange_rates = parse_ecb_data(data)

    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table("ExchangeRates")

    with table.batch_writer() as batch:
        for currency, rate in exchange_rates.items():
            batch.put_item(
                Item={
                    "Currency": currency,
                    "Rate": Decimal(str(rate)),
                    "Timestamp": datetime.utcnow().date().isoformat(),
                }
            )

    return {
        "statusCode": 200,
        "body": json.dumps("Exchange rates fetched and stored successfully."),
    }


def parse_ecb_data(data):
    """
    Parses the ECB XML data to extract exchange rates.

    Args:
        data (bytes): XML data received from ECB.

    Returns:
        dict: Dictionary containing currency codes as keys and their corresponding exchange rates as values.
    """
    import xmltodict

    exchange_rates = {}
    parsed = xmltodict.parse(data)
    for cube in parsed["gesmes:Envelope"]["Cube"]["Cube"]["Cube"]:
        currency = cube["@currency"]
        rate = float(cube["@rate"])
        exchange_rates[currency] = rate
    return exchange_rates
