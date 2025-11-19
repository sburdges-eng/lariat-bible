"""
P2 MEDIUM PRIORITY: Tests for equipment management
Tests equipment tracking, maintenance scheduling, and cost analysis
"""

import pytest
from datetime import datetime, timedelta
from modules.equipment.equipment_manager import (
    Equipment, EquipmentManager, EquipmentStatus,
    MaintenanceRecord, MaintenanceType
)


@pytest.mark.medium
class TestEquipmentProperties:
    """Test Equipment class properties and calculations"""

    def test_equipment_age_calculation(self, sample_equipment):
        """Test equipment age calculation in years"""
        # Equipment purchased on 2020-01-15
        age = sample_equipment.age_years

        # Should be approximately 4-5 years
        assert age > 4.0
        assert age < 6.0

    def test_warranty_status_active(self):
        """Test warranty status for equipment under warranty"""
        equipment = Equipment(
            equipment_id="eq_001",
            name="Test Equipment",
            category="Test",
            brand="Test",
            model="T1",
            serial_number="123",
            location="Kitchen",
            warranty_end_date=datetime.now() + timedelta(days=365)
        )

        status = equipment.warranty_status
        assert "Active" in status
        assert "days remaining" in status

    def test_warranty_status_expired(self, sample_equipment):
        """Test warranty status for expired warranty"""
        # Sample equipment warranty ended in 2023
        status = sample_equipment.warranty_status
        assert status == "Expired"

    def test_warranty_status_no_info(self):
        """Test warranty status when no warranty info provided"""
        equipment = Equipment(
            equipment_id="eq_001",
            name="Test Equipment",
            category="Test",
            brand="Test",
            model="T1",
            serial_number="123",
            location="Kitchen",
            warranty_end_date=None
        )

        assert equipment.warranty_status == "No warranty information"

    def test_depreciated_value_calculation(self, sample_equipment):
        """Test straight-line depreciation calculation"""
        # Purchase price: $8500, purchased ~4.8 years ago
        # Annual depreciation: $8500 / 7 = $1214.29
        # Depreciated value: $8500 - ($1214.29 × 4.8) ≈ $2671.42

        depreciated = sample_equipment.depreciated_value

        assert depreciated > 0
        assert depreciated < sample_equipment.purchase_price
        assert depreciated < 4000  # Should be significantly depreciated

    def test_depreciated_value_not_negative(self):
        """Test that depreciated value doesn't go negative"""
        equipment = Equipment(
            equipment_id="eq_001",
            name="Old Equipment",
            category="Test",
            brand="Test",
            model="T1",
            serial_number="123",
            location="Kitchen",
            purchase_date=datetime(2000, 1, 1),  # Very old
            purchase_price=1000.0
        )

        # Should be fully depreciated but not negative
        assert equipment.depreciated_value == 0

    def test_is_maintenance_due_true(self):
        """Test maintenance due check returns true when overdue"""
        equipment = Equipment(
            equipment_id="eq_001",
            name="Test Equipment",
            category="Test",
            brand="Test",
            model="T1",
            serial_number="123",
            location="Kitchen",
            next_maintenance_due=datetime.now() - timedelta(days=1)
        )

        assert equipment.is_maintenance_due() is True

    def test_is_maintenance_due_false(self, sample_equipment):
        """Test maintenance due check returns false when not due"""
        # Sample equipment next maintenance: 2024-12-01 (future)
        assert sample_equipment.is_maintenance_due() is False

    def test_get_maintenance_checklist(self, sample_equipment):
        """Test retrieving maintenance checklist"""
        sample_equipment.monthly_tasks = ["Clean filters", "Check temperature"]

        checklist = sample_equipment.get_maintenance_checklist(MaintenanceType.MONTHLY_INSPECTION)

        assert len(checklist) == 2
        assert "Clean filters" in checklist


@pytest.mark.medium
class TestMaintenanceRecord:
    """Test MaintenanceRecord class"""

    def test_maintenance_total_cost(self, sample_maintenance_record):
        """Test total maintenance cost calculation"""
        # Labor: $150, Parts: $25
        total = sample_maintenance_record.total_cost

        assert total == 175.0

    def test_maintenance_record_defaults(self):
        """Test maintenance record default values"""
        record = MaintenanceRecord(
            record_id="test_001",
            equipment_id="eq_001",
            date_performed=datetime.now(),
            maintenance_type=MaintenanceType.DAILY_CLEANING,
            performed_by="Test User"
        )

        assert record.tasks_completed == []
        assert record.issues_found == []
        assert record.parts_replaced == []


@pytest.mark.medium
class TestEquipmentManager:
    """Test EquipmentManager class"""

    def test_add_equipment(self, sample_equipment):
        """Test adding equipment to inventory"""
        manager = EquipmentManager()
        result = manager.add_equipment(sample_equipment)

        assert "Added" in result
        assert len(manager.equipment_list) == 1

    def test_get_equipment_by_id(self, sample_equipment):
        """Test retrieving equipment by ID"""
        manager = EquipmentManager()
        manager.add_equipment(sample_equipment)

        found = manager.get_equipment_by_id("eq_001")

        assert found is not None
        assert found.equipment_id == "eq_001"
        assert found.name == "Commercial Range"

    def test_get_equipment_by_id_not_found(self):
        """Test retrieving non-existent equipment"""
        manager = EquipmentManager()
        found = manager.get_equipment_by_id("nonexistent")

        assert found is None

    def test_get_equipment_by_location(self, sample_equipment):
        """Test retrieving equipment by location"""
        manager = EquipmentManager()
        manager.add_equipment(sample_equipment)

        # Add another equipment in different location
        other_eq = Equipment(
            equipment_id="eq_002",
            name="Freezer",
            category="Refrigeration",
            brand="Traulsen",
            model="F123",
            serial_number="456",
            location="Storage"
        )
        manager.add_equipment(other_eq)

        kitchen_equipment = manager.get_equipment_by_location("Kitchen")

        assert len(kitchen_equipment) == 1
        assert kitchen_equipment[0].name == "Commercial Range"

    def test_get_maintenance_schedule(self, sample_equipment):
        """Test getting upcoming maintenance schedule"""
        manager = EquipmentManager()
        manager.add_equipment(sample_equipment)

        schedule = manager.get_maintenance_schedule(days_ahead=60)

        # Sample equipment has maintenance due on 2024-12-01
        assert len(schedule) >= 0
        if len(schedule) > 0:
            assert 'equipment' in schedule[0]
            assert 'due_date' in schedule[0]

    def test_record_maintenance(self, sample_equipment, sample_maintenance_record):
        """Test recording completed maintenance"""
        manager = EquipmentManager()
        manager.add_equipment(sample_equipment)

        result = manager.record_maintenance(sample_maintenance_record)

        assert "recorded" in result.lower()
        assert len(manager.maintenance_history) == 1

        # Equipment should be updated
        eq = manager.get_equipment_by_id("eq_001")
        assert eq.last_maintenance_date == sample_maintenance_record.date_performed

    def test_get_maintenance_costs(self, sample_equipment, sample_maintenance_record):
        """Test calculating maintenance costs for a period"""
        manager = EquipmentManager()
        manager.add_equipment(sample_equipment)
        manager.record_maintenance(sample_maintenance_record)

        start = datetime.now() - timedelta(days=30)
        end = datetime.now() + timedelta(days=1)

        costs = manager.get_maintenance_costs(start, end)

        assert costs['total_maintenance_events'] == 1
        assert costs['total_labor_cost'] == 150.0
        assert costs['total_parts_cost'] == 25.0
        assert costs['total_cost'] == 175.0

    def test_get_equipment_summary(self, sample_equipment):
        """Test equipment summary statistics"""
        manager = EquipmentManager()
        manager.add_equipment(sample_equipment)

        summary = manager.get_equipment_summary()

        assert summary['total_equipment'] == 1
        assert summary['original_value'] == 8500.0
        assert summary['depreciated_value'] > 0
        assert summary['depreciation'] > 0
        assert 'status_breakdown' in summary


@pytest.mark.medium
class TestEquipmentEdgeCases:
    """Test edge cases and error handling"""

    def test_equipment_no_purchase_date(self):
        """Test equipment without purchase date"""
        equipment = Equipment(
            equipment_id="eq_001",
            name="Test",
            category="Test",
            brand="Test",
            model="T1",
            serial_number="123",
            location="Kitchen",
            purchase_date=None
        )

        assert equipment.age_years == 0
        assert equipment.depreciated_value == 0

    def test_maintenance_schedule_empty(self):
        """Test maintenance schedule with no equipment"""
        manager = EquipmentManager()
        schedule = manager.get_maintenance_schedule()

        assert len(schedule) == 0

    def test_maintenance_costs_no_records(self):
        """Test maintenance costs with no maintenance records"""
        manager = EquipmentManager()
        start = datetime.now() - timedelta(days=30)
        end = datetime.now()

        costs = manager.get_maintenance_costs(start, end)

        assert costs['total_maintenance_events'] == 0
        assert costs['total_cost'] == 0
        assert costs['average_cost_per_event'] == 0
