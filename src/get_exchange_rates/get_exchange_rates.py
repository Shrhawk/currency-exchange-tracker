# -*- coding: utf-8 -*-
import json
import boto3
from datetime import datetime, timedelta
from boto3.dynamodb.conditions import Key


def get_exchange_rates(event, context):
    """
    Retrieves current and previous day's exchange rates from DynamoDB and calculates changes.

    This function is triggered by an AWS Lambda event. It queries DynamoDB for the current and previous day's
    exchange rates and calculates the changes.

    Args:
        event (dict): AWS Lambda event data.
        context (LambdaContext): AWS Lambda context object.

    Returns:
        dict: Response containing statusCode and body with current rates, previous rates, and changes.
    """
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table("ExchangeRates")

    today = datetime.utcnow().date().isoformat()
    yesterday = (datetime.utcnow().date() - timedelta(days=1)).isoformat()

    today_rates = get_rates_for_date(table, today)
    yesterday_rates = get_rates_for_date(table, yesterday)

    response = {
        "current_rates": today_rates,
        "previous_rates": yesterday_rates,
        "changes": calculate_changes(today_rates, yesterday_rates),
    }

    return {"statusCode": 200, "body": json.dumps(response)}


def get_rates_for_date(table, date):
    """
    Retrieves exchange rates for a specific date from DynamoDB.

    Args:
        table (boto3.DynamoDB.Table): DynamoDB table resource.
        date (str): The date in ISO format to retrieve rates for.

    Returns:
        dict: Dictionary containing currency codes as keys and their corresponding exchange rates as values.
    """
    response = table.query(
        IndexName="TimestampIndex", KeyConditionExpression=Key("Timestamp").eq(date)
    )
    return {item["Currency"]: float(item["Rate"]) for item in response["Items"]}


def calculate_changes(today_rates, yesterday_rates):
    """
    Calculates the changes in exchange rates between two dates.

    Args:
        today_rates (dict): Dictionary of today's exchange rates.
        yesterday_rates (dict): Dictionary of yesterday's exchange rates.

    Returns:
        dict: Dictionary containing currency codes as keys and the difference in rates as values.
    """
    changes = {}
    for currency, rate in today_rates.items():
        previous_rate = yesterday_rates.get(currency)
        if previous_rate is not None:
            changes[currency] = rate - previous_rate
    return changes
