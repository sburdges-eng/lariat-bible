"""
P2 MEDIUM PRIORITY: Tests for email order parsing
Tests email parsing and order data extraction
"""

import pytest
from modules.email_parser.email_parser import PackSizeNormalizer, EmailOrderParser, OrderItem


@pytest.mark.medium
class TestOrderItemDataclass:
    """Test OrderItem dataclass"""

    def test_order_item_creation(self):
        """Test creating an order item"""
        from datetime import datetime
        item = OrderItem(
            vendor='SYSCO',
            order_number='12345',
            date=datetime.now(),
            item_code='SYS001',
            description='BLACK PEPPER',
            pack_size='6/1LB',
            quantity_ordered=2.0,
            unit_price=298.95,
            extension=597.90
        )

        assert item.vendor == 'SYSCO'
        assert item.item_code == 'SYS001'


@pytest.mark.medium
class TestEmailOrderParserRegex:
    """Test email parsing regex patterns"""

    def test_extract_order_number_sysco(self):
        """Test extracting SYSCO order number"""
        parser = EmailOrderParser("test@test.com", "password")
        email_body = "Order #: 123456\nThank you for your order"

        order_num = parser._extract_order_number(email_body, 'SYSCO')
        assert order_num == '123456'

    def test_extract_order_number_shamrock(self):
        """Test extracting Shamrock order number"""
        parser = EmailOrderParser("test@test.com", "password")
        email_body = "Confirmation #: 789012\nYour order is confirmed"

        order_num = parser._extract_order_number(email_body, 'Shamrock')
        assert order_num == '789012'

    def test_extract_order_number_not_found(self):
        """Test handling when order number not found"""
        parser = EmailOrderParser("test@test.com", "password")
        email_body = "No order number here"

        order_num = parser._extract_order_number(email_body, 'SYSCO')
        assert order_num == 'UNKNOWN'


@pytest.mark.medium
class TestEmailParserIntegration:
    """Integration tests for email parsing (mocked)"""

    @pytest.mark.skip(reason="Requires IMAP connection - implement with mock")
    def test_connect_to_email_server(self):
        """Test connecting to email server (would need mock)"""
        pass

    @pytest.mark.skip(reason="Requires email fixtures")
    def test_parse_sysco_email_full(self):
        """Test parsing complete SYSCO email (would need fixtures)"""
        pass

    @pytest.mark.skip(reason="Requires email fixtures")
    def test_parse_shamrock_email_full(self):
        """Test parsing complete Shamrock email (would need fixtures)"""
        pass


# Note: Email parser tests are intentionally limited since they require
# either mock IMAP connections or sample email fixtures. The critical
# pack size parsing is already thoroughly tested in test_pack_size_normalizer.py
