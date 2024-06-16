# -*- coding: utf-8 -*-
import unittest
from unittest.mock import MagicMock
import json
from datetime import datetime, timedelta
from decimal import Decimal
from boto3.dynamodb.conditions import Key

import boto3

from src.get_exchange_rates.get_exchange_rates import (
    get_exchange_rates,
    get_rates_for_date,
    calculate_changes,
)


class TestGetExchangeRates(unittest.TestCase):
    """
    Tests for the get_exchange_rates module.
    """

    def setUp(self):
        """
        Sets up mock resources before each test.
        """
        # Mock DynamoDB resource and table
        self.mock_dynamodb_table = MagicMock()
        self.mock_dynamodb = MagicMock()
        self.mock_dynamodb.Table = MagicMock(return_value=self.mock_dynamodb_table)
        boto3.resource = MagicMock(return_value=self.mock_dynamodb)

    def test_get_exchange_rates_success(self):
        """
        Tests the successful retrieval of exchange rates and calculation of changes.
        """
        # Mock DynamoDB query response for today's and yesterday's rates
        mock_today_date = datetime.utcnow().date().isoformat()
        mock_yesterday_date = (datetime.utcnow().date() - timedelta(days=1)).isoformat()
        mock_today_rates = {"USD": float("1.2"), "GBP": float("0.85")}
        mock_yesterday_rates = {"USD": float("1.1"), "GBP": float("0.86")}

        self.mock_dynamodb_table.query.side_effect = [
            {
                "Items": [
                    {"Currency": "USD", "Rate": Decimal("1.2")},
                    {"Currency": "GBP", "Rate": Decimal("0.85")},
                ]
            },
            {
                "Items": [
                    {"Currency": "USD", "Rate": Decimal("1.1")},
                    {"Currency": "GBP", "Rate": Decimal("0.86")},
                ]
            },
        ]

        event = {}
        context = {}
        response = get_exchange_rates(event, context)

        self.assertEqual(response["statusCode"], 200)

        body = json.loads(response["body"])
        self.assertIn("current_rates", body)
        self.assertIn("previous_rates", body)
        self.assertIn("changes", body)

        self.assertEqual(body["current_rates"], mock_today_rates)
        self.assertEqual(body["previous_rates"], mock_yesterday_rates)

        # Verify DynamoDB interactions
        self.mock_dynamodb.Table.assert_called_with("ExchangeRates")
        self.mock_dynamodb_table.query.assert_any_call(
            IndexName="TimestampIndex",
            KeyConditionExpression=Key("Timestamp").eq(mock_today_date),
        )
        self.mock_dynamodb_table.query.assert_any_call(
            IndexName="TimestampIndex",
            KeyConditionExpression=Key("Timestamp").eq(mock_yesterday_date),
        )

    def test_get_rates_for_date(self):
        """
        Tests the retrieval of exchange rates for a specific date from DynamoDB.
        """
        mock_date = datetime.utcnow().date().isoformat()
        mock_response = {
            "Items": [
                {"Currency": "USD", "Rate": Decimal("1.2")},
                {"Currency": "GBP", "Rate": Decimal("0.85")},
            ]
        }

        self.mock_dynamodb_table.query.return_value = mock_response

        rates = get_rates_for_date(self.mock_dynamodb_table, mock_date)

        expected_rates = {"USD": 1.2, "GBP": 0.85}
        self.assertEqual(rates, expected_rates)

        # Verify DynamoDB query parameters
        self.mock_dynamodb_table.query.assert_called_once_with(
            IndexName="TimestampIndex",
            KeyConditionExpression=Key("Timestamp").eq(mock_date),
        )

    def test_get_rates_for_date_no_items(self):
        """
        Tests scenario where no exchange rates are found for a specific date in DynamoDB.
        """
        mock_date = datetime.utcnow().date().isoformat()
        self.mock_dynamodb_table.query.return_value = {"Items": []}

        rates = get_rates_for_date(self.mock_dynamodb_table, mock_date)
        self.assertEqual(rates, {})

    def test_calculate_changes(self):
        """
        Tests calculation of changes between today's and yesterday's exchange rates.
        """
        today_rates = {"USD": Decimal("1.2"), "GBP": Decimal("0.85")}
        yesterday_rates = {"USD": Decimal("1.1"), "GBP": Decimal("0.86")}

        changes = calculate_changes(today_rates, yesterday_rates)
        expected_changes = {"USD": Decimal("0.1"), "GBP": Decimal("-0.01")}

        self.assertEqual(changes, expected_changes)

    def test_calculate_changes_missing_currency(self):
        """
        Tests calculation of changes when yesterday's rates are missing a currency.
        """
        today_rates = {"USD": Decimal("1.2"), "GBP": Decimal("0.85")}
        yesterday_rates = {"USD": Decimal("1.1")}  # Missing GBP rate

        changes = calculate_changes(today_rates, yesterday_rates)
        expected_changes = {"USD": Decimal("0.1")}  # GBP rate change is missing

        self.assertEqual(changes, expected_changes)

    def test_calculate_changes_empty_yesterday_rates(self):
        """
        Tests calculation of changes when yesterday's rates are empty.
        """
        today_rates = {"USD": Decimal("1.2"), "GBP": Decimal("0.85")}
        yesterday_rates = {}  # Empty yesterday rates

        changes = calculate_changes(today_rates, yesterday_rates)
        expected_changes = {}  # No changes expected

        self.assertEqual(changes, expected_changes)
