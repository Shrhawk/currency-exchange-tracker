# -*- coding: utf-8 -*-
import unittest
from unittest.mock import MagicMock, call
import json
from decimal import Decimal
from datetime import datetime
import requests
import requests_mock
import boto3

from src.fetch_exchange_rates.fetch_exchange_rates import (
    fetch_exchange_rates,
    parse_ecb_data,
)


class TestFetchExchangeRates(unittest.TestCase):
    """
    Tests for the fetch_exchange_rates and parse_ecb_data functions.
    """

    def setUp(self):
        """
        Sets up mock resources before each test.
        """
        self.mock_dynamodb_table = MagicMock()
        boto3.resource = MagicMock(
            return_value=MagicMock(Table=lambda table_name: self.mock_dynamodb_table)
        )

    def test_fetch_exchange_rates_successful(self):
        """
        Tests the successful fetching and storing of exchange rates in DynamoDB.
        """
        # Mock ECB API response
        mock_response_content = """
           <gesmes:Envelope xmlns:gesmes="http://www.gesmes.org/xml/2002-08-01">
               <Cube>
                   <Cube time="2024-06-16">
                       <Cube currency="USD" rate="1.2"/>
                       <Cube currency="GBP" rate="0.85"/>
                   </Cube>
               </Cube>
           </gesmes:Envelope>
       """
        with requests_mock.Mocker() as mock_requests:
            mock_requests.get(
                "https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml",
                text=mock_response_content,
            )

            event = {}
            context = {}
            response = fetch_exchange_rates(event, context)

            self.assertEqual(response["statusCode"], 200)
            self.assertEqual(
                json.loads(response["body"]),
                "Exchange rates fetched and stored successfully.",
            )

            # Verify DynamoDB interactions
            self.mock_dynamodb_table.batch_writer.assert_called_once()
            batch_writer_context = (
                self.mock_dynamodb_table.batch_writer.return_value.__enter__.return_value
            )
            put_item_calls = batch_writer_context.put_item.call_args_list

            expected_calls = [
                call(
                    Item={
                        "Currency": "USD",
                        "Rate": Decimal("1.2"),
                        "Timestamp": datetime.utcnow().date().isoformat(),
                    }
                ),
                call(
                    Item={
                        "Currency": "GBP",
                        "Rate": Decimal("0.85"),
                        "Timestamp": datetime.utcnow().date().isoformat(),
                    }
                ),
            ]

            self.assertEqual(put_item_calls, expected_calls)

    def test_fetch_exchange_rates_http_error(self):
        """
        Tests handling of an HTTP error when fetching exchange rates.
        """
        with requests_mock.Mocker() as mock_requests:
            mock_requests.get(
                "https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml",
                status_code=404,
            )

            event = {}
            context = {}
            with self.assertRaises(requests.exceptions.HTTPError):
                fetch_exchange_rates(event, context)

            # Ensure DynamoDB table interaction was not attempted
            self.mock_dynamodb_table.batch_writer.assert_not_called()

    def test_parse_ecb_data(self):
        """
        Tests parsing of ECB XML data.
        """
        mock_data = """
           <gesmes:Envelope xmlns:gesmes="http://www.gesmes.org/xml/2002-08-01">
               <Cube>
                   <Cube time="2024-06-16">
                       <Cube currency="USD" rate="1.2"/>
                       <Cube currency="GBP" rate="0.85"/>
                   </Cube>
               </Cube>
           </gesmes:Envelope>
       """
        expected_rates = {"USD": 1.2, "GBP": 0.85}
        rates = parse_ecb_data(mock_data)
        self.assertEqual(rates, expected_rates)
