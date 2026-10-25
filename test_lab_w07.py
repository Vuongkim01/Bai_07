# Kim Duy Vương
# 20237410
from __future__ import annotations

import unittest
from dataclasses import dataclass

from lab_w07 import (
    AirConditionerRemote,
    AllocationService,
    DeviceNotReadyException,
    DeviceStatus,
    DuplicateIdException,
    FirstAvailableStrategy,
    HighestPriorityStrategy,
    IIdentifiable,
    InMemoryRepository,
    ISelectionStrategy,
    NoSuitableItemException,
    ProjectorRemote,
    TeachingDevice,
    WirelessMicrophone,
)


def projector(device_id: str = "P1", battery: int = 60) -> ProjectorRemote:
    return ProjectorRemote(device_id, "Điều khiển máy chiếu", "Tủ A", battery)


def microphone(
    device_id: str = "M1", battery: int = 60, signal: int = 70
) -> WirelessMicrophone:
    return WirelessMicrophone(device_id, "Micro", "Tủ C", battery, signal)


def air_remote(device_id: str = "A1") -> AirConditionerRemote:
    return AirConditionerRemote(device_id, "Điều khiển điều hòa", "Tủ B", {"A203"})


class DeviceTests(unittest.TestCase):
    def test_base_class_is_abstract(self) -> None:
        with self.assertRaises(TypeError):
            TeachingDevice("D", "Thiết bị", "Tủ")

    def test_initial_status_and_identifiable_protocol(self) -> None:
        for device in (projector(), microphone(), air_remote()):
            with self.subTest(type=type(device).__name__):
                self.assertEqual(device.status, DeviceStatus.Available)
                self.assertIsInstance(device, IIdentifiable)

    def test_required_text_and_whitespace_normalization(self) -> None:
        for index in range(3):
            for invalid in ("", "  ", None, 123):
                args = ["P1", "Máy chiếu", "Tủ A"]
                args[index] = invalid
                with self.subTest(field=index, invalid=invalid):
                    with self.assertRaises(ValueError):
                        ProjectorRemote(*args, 50)
        device = ProjectorRemote(" P1 ", " Máy chiếu ", " Tủ A ", 50)
        self.assertEqual((device.id, device.name, device.storage_location),
                         ("P1", "Máy chiếu", "Tủ A"))

    def test_projector_battery_boundaries(self) -> None:
        for battery, expected in ((0, False), (19, False), (20, True), (100, True)):
            with self.subTest(battery=battery):
                self.assertEqual(projector(battery=battery).is_ready_for_use(), expected)

    def test_microphone_battery_and_signal_boundaries(self) -> None:
        for battery, signal, expected in (
            (29, 100, False), (100, 39, False), (30, 40, True), (100, 100, True)
        ):
            with self.subTest(battery=battery, signal=signal):
                self.assertEqual(microphone(battery=battery, signal=signal)
                                 .is_ready_for_use(), expected)

    def test_reject_invalid_percentage_fields(self) -> None:
        for invalid in (-1, 101, 50.5, True, "50", None):
            for field in ("projector", "micro_battery", "micro_signal"):
                with self.subTest(field=field, invalid=invalid):
                    with self.assertRaises(ValueError):
                        if field == "projector":
                            projector(battery=invalid)
                        elif field == "micro_battery":
                            microphone(battery=invalid)
                        else:
                            microphone(signal=invalid)

    def test_priority_scores_use_correct_formulas(self) -> None:
        self.assertEqual(projector(battery=75).get_default_priority_score(), 75.0)
        self.assertEqual(microphone(battery=70, signal=81)
                         .get_default_priority_score(), 75.5)
        self.assertEqual(air_remote().get_default_priority_score(), 100.0)

    def test_room_compatibility_and_contextual_score(self) -> None:
        device = air_remote()
        self.assertTrue(device.is_compatible_with(" A203 "))
        self.assertFalse(device.is_compatible_with("A204"))
        self.assertFalse(device.is_compatible_with("a203"))
        self.assertEqual(device.get_priority_score_for_room("A203"), 100.0)
        self.assertEqual(device.get_priority_score_for_room("A204"), 0.0)

    def test_compatible_rooms_are_an_immutable_copy(self) -> None:
        rooms = {"A203"}
        device = AirConditionerRemote("A1", "Điều hòa", "Tủ", rooms)
        rooms.add("A204")
        self.assertEqual(device.compatible_rooms, frozenset({"A203"}))
        with self.assertRaises(AttributeError):
            device.compatible_rooms.add("A205")

    def test_empty_compatible_rooms_follow_status_rule(self) -> None:
        device = AirConditionerRemote("A1", "Điều hòa", "Tủ", set())
        self.assertTrue(device.is_ready_for_use())
        self.assertFalse(device.is_compatible_with("A203"))
        self.assertEqual(device.get_default_priority_score(), 0.0)

    def test_invalid_room_collections_and_codes(self) -> None:
        for invalid in (None, "A203", b"A203"):
            with self.subTest(rooms=invalid):
                with self.assertRaises(TypeError):
                    AirConditionerRemote("A1", "Điều hòa", "Tủ", invalid)
        for rooms in ({""}, {" "}, {123}):
            with self.subTest(rooms=rooms):
                with self.assertRaises(ValueError):
                    AirConditionerRemote("A1", "Điều hòa", "Tủ", rooms)
        with self.assertRaises(ValueError):
            air_remote().is_compatible_with(" ")

    def test_borrow_and_return_lifecycle(self) -> None:
        for device in (projector(), microphone(), air_remote()):
            with self.subTest(type=type(device).__name__):
                device.borrow()
                self.assertEqual(device.status, DeviceStatus.Borrowed)
                self.assertFalse(device.is_ready_for_use())
                device.return_device()
                self.assertEqual(device.status, DeviceStatus.Available)
                self.assertTrue(device.is_ready_for_use())

    def test_borrow_rejects_insufficient_resources(self) -> None:
        for device in (projector(battery=19), microphone(battery=29),
                       microphone(signal=39)):
            with self.subTest(device=str(device)):
                with self.assertRaises(DeviceNotReadyException) as context:
                    device.borrow()
                self.assertEqual(context.exception.device_id, device.id)
                self.assertEqual(context.exception.current_status, DeviceStatus.Available)
                self.assertEqual(device.status, DeviceStatus.Available)

    def test_cannot_borrow_twice(self) -> None:
        device = projector()
        device.borrow()
        with self.assertRaises(DeviceNotReadyException) as context:
            device.borrow()
        self.assertEqual(context.exception.current_status, DeviceStatus.Borrowed)

    def test_return_requires_borrowed_state(self) -> None:
        device = projector()
        with self.assertRaises(RuntimeError):
            device.return_device()
        self.assertEqual(device.status, DeviceStatus.Available)
        device.borrow()
        device.return_device()
        with self.assertRaises(RuntimeError):
            device.return_device()

    def test_maintenance_blocks_all_device_types(self) -> None:
        for device in (projector(), microphone(), air_remote()):
            with self.subTest(type=type(device).__name__):
                # Thiết lập fixture trạng thái bảo trì; không thêm API ngoài đề.
                device._status = DeviceStatus.UnderMaintenance
                self.assertFalse(device.is_ready_for_use())
                with self.assertRaises(DeviceNotReadyException):
                    device.borrow()
                with self.assertRaises(RuntimeError):
                    device.return_device()
                self.assertEqual(device.status, DeviceStatus.UnderMaintenance)

    def test_public_properties_are_read_only(self) -> None:
        device = projector()
        for attribute, value in (("id", "OTHER"), ("name", "Other"),
                                 ("storage_location", "Tủ Z"),
                                 ("status", DeviceStatus.Borrowed), ("battery_level", 99)):
            with self.subTest(attribute=attribute):
                with self.assertRaises(AttributeError):
                    setattr(device, attribute, value)


class RepositoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repository = InMemoryRepository[ProjectorRemote]()
        self.first = projector("P1", 50)
        self.second = projector("P2", 90)
        self.repository.add(self.first)
        self.repository.add(self.second)

    def test_add_and_find_by_id(self) -> None:
        self.assertEqual(len(self.repository.get_all()), 2)
        self.assertIs(self.repository.find_by_id(" P2 "), self.second)
        self.assertIsNone(self.repository.find_by_id("UNKNOWN"))

    def test_duplicate_id_raises_without_changing_repository(self) -> None:
        with self.assertRaises(DuplicateIdException) as context:
            self.repository.add(projector(" P1 ", 100))
        self.assertEqual(context.exception.duplicate_id, "P1")
        self.assertEqual(len(self.repository.get_all()), 2)
        self.assertIs(self.repository.find_by_id("P1"), self.first)

    def test_reject_none_and_objects_without_valid_identity(self) -> None:
        with self.assertRaises(ValueError):
            self.repository.add(None)
        with self.assertRaises(TypeError):
            self.repository.add(object())

        @dataclass
        class InvalidItem:
            id: str = " "

        with self.assertRaises(ValueError):
            InMemoryRepository[InvalidItem]().add(InvalidItem())

    def test_remove_existing_and_missing_ids(self) -> None:
        self.assertTrue(self.repository.remove("P1"))
        self.assertIsNone(self.repository.find_by_id("P1"))
        self.assertFalse(self.repository.remove("P1"))
        self.assertEqual(self.repository.get_all(), (self.second,))

    def test_invalid_lookup_ids(self) -> None:
        for method in (self.repository.find_by_id, self.repository.remove):
            for invalid in ("", " ", None):
                with self.subTest(method=method.__name__, invalid=invalid):
                    with self.assertRaises(ValueError):
                        method(invalid)

    def test_get_all_returns_independent_tuple_snapshot(self) -> None:
        snapshot = self.repository.get_all()
        self.assertIsInstance(snapshot, tuple)
        copied = list(snapshot)
        copied.clear()
        self.assertEqual(len(self.repository.get_all()), 2)
        self.repository.add(projector("P3"))
        self.assertEqual(len(snapshot), 2)
        self.assertEqual(len(self.repository.get_all()), 3)

    def test_find_all_filters_without_modifying_storage(self) -> None:
        self.repository.add(projector("P3", 10))
        ready = self.repository.find_all(lambda device: device.is_ready_for_use())
        self.assertEqual(ready, (self.first, self.second))
        self.assertIsInstance(ready, tuple)
        self.assertEqual(len(self.repository.get_all()), 3)
        with self.assertRaises(TypeError):
            self.repository.find_all(None)

    def test_generic_repository_supports_other_device_type(self) -> None:
        microphones = InMemoryRepository[WirelessMicrophone]()
        device = microphone()
        microphones.add(device)
        self.assertIs(microphones.find_by_id("M1"), device)
        self.assertIs(self.repository.find_by_id("P1"), self.first)

    def test_generic_repository_supports_non_device_identifiable(self) -> None:
        @dataclass(frozen=True)
        class Book:
            id: str
            title: str

        books = InMemoryRepository[Book]()
        book = Book("B1", "Lập trình Python")
        books.add(book)
        self.assertIs(books.find_by_id("B1"), book)


class StrategyTests(unittest.TestCase):
    def test_highest_priority_and_first_strategy_give_different_results(self) -> None:
        candidates = [projector("P1", 50), projector("P2", 90)]
        highest = HighestPriorityStrategy[ProjectorRemote](
            lambda device: device.get_default_priority_score()
        )
        self.assertIs(highest.select(candidates), candidates[1])
        self.assertIs(FirstAvailableStrategy[ProjectorRemote]().select(candidates), candidates[0])

    def test_both_strategies_reject_empty_candidates(self) -> None:
        strategies = (FirstAvailableStrategy[int](), HighestPriorityStrategy[int](float))
        for strategy in strategies:
            with self.subTest(strategy=type(strategy).__name__):
                with self.assertRaises(NoSuitableItemException):
                    strategy.select([])

    def test_strategies_do_not_modify_input(self) -> None:
        candidates = [3, 1, 7, 2]
        original = candidates.copy()
        self.assertEqual(HighestPriorityStrategy[int](float).select(candidates), 7)
        self.assertEqual(candidates, original)
        FirstAvailableStrategy[int]().select(candidates)
        self.assertEqual(candidates, original)

    def test_equal_scores_choose_first_candidate(self) -> None:
        first, second = projector("P1", 80), projector("P2", 80)
        strategy = HighestPriorityStrategy[ProjectorRemote](
            lambda device: device.get_default_priority_score()
        )
        self.assertIs(strategy.select((first, second)), first)

    def test_invalid_score_selector(self) -> None:
        with self.assertRaises(TypeError):
            HighestPriorityStrategy[int](None)


class AllocationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repository = InMemoryRepository[ProjectorRemote]()
        for device in (projector("P1", 50), projector("P2", 90), projector("P3", 10)):
            self.repository.add(device)
        self.service = AllocationService[ProjectorRemote](
            self.repository, FirstAvailableStrategy[ProjectorRemote]()
        )

    def test_allocate_highest_projector_and_update_same_object(self) -> None:
        self.service.change_strategy(HighestPriorityStrategy[ProjectorRemote](
            lambda device: device.get_default_priority_score()
        ))
        selected = self.service.allocate()
        self.assertEqual(selected.id, "P2")
        self.assertEqual(selected.status, DeviceStatus.Borrowed)
        self.assertIs(self.repository.find_by_id("P2"), selected)

    def test_allocate_only_compatible_air_conditioner(self) -> None:
        repository = InMemoryRepository[AirConditionerRemote]()
        repository.add(AirConditionerRemote("A1", "Điều hòa 1", "Tủ", {"A201"}))
        repository.add(AirConditionerRemote("A2", "Điều hòa 2", "Tủ", {"A203"}))
        service = AllocationService[AirConditionerRemote](
            repository, FirstAvailableStrategy[AirConditionerRemote]()
        )
        selected = service.allocate(lambda device: device.is_compatible_with("A203"))
        self.assertEqual(selected.id, "A2")
        self.assertEqual(selected.status, DeviceStatus.Borrowed)
        with self.assertRaises(NoSuitableItemException):
            service.allocate(lambda device: device.is_compatible_with("Z999"))

    def test_first_microphone_skips_unready_candidates(self) -> None:
        repository = InMemoryRepository[WirelessMicrophone]()
        for device in (microphone("M1", 20, 80), microphone("M2", 60, 60),
                       microphone("M3", 90, 90)):
            repository.add(device)
        service = AllocationService[WirelessMicrophone](
            repository, FirstAvailableStrategy[WirelessMicrophone]()
        )
        self.assertEqual(service.allocate().id, "M2")

    def test_change_strategy_at_runtime_on_same_ready_set(self) -> None:
        first = self.service.allocate()
        self.assertEqual(first.id, "P1")
        first.return_device()
        self.service.change_strategy(HighestPriorityStrategy[ProjectorRemote](
            lambda device: device.get_default_priority_score()
        ))
        self.assertEqual(self.service.allocate().id, "P2")

    def test_optional_condition_can_be_omitted_or_none(self) -> None:
        first = self.service.allocate()
        first.return_device()
        self.assertIs(self.service.allocate(None), first)

    def test_additional_condition_filters_before_selection(self) -> None:
        self.assertEqual(self.service.allocate(lambda device: device.battery_level > 80).id,
                         "P2")

    def test_additional_condition_is_only_called_for_ready_devices(self) -> None:
        visited = []

        def condition(device: ProjectorRemote) -> bool:
            visited.append(device.id)
            return True

        self.service.allocate(condition)
        self.assertEqual(visited, ["P1", "P2"])

    def test_empty_or_exhausted_repository_raises(self) -> None:
        empty_service = AllocationService[ProjectorRemote](
            InMemoryRepository[ProjectorRemote](), FirstAvailableStrategy[ProjectorRemote]()
        )
        with self.assertRaises(NoSuitableItemException):
            empty_service.allocate()
        self.service.allocate()
        self.service.allocate()
        with self.assertRaises(NoSuitableItemException):
            self.service.allocate()

    def test_unsuitable_filter_leaves_all_states_unchanged(self) -> None:
        with self.assertRaises(NoSuitableItemException):
            self.service.allocate(lambda device: False)
        self.assertTrue(all(device.status is DeviceStatus.Available
                            for device in self.repository.get_all()))

    def test_returned_device_can_be_allocated_again(self) -> None:
        device = self.service.allocate()
        device.return_device()
        self.assertIs(self.service.allocate(), device)

    def test_invalid_service_arguments(self) -> None:
        with self.assertRaises(ValueError):
            AllocationService(None, FirstAvailableStrategy())
        with self.assertRaises(ValueError):
            AllocationService(self.repository, None)
        with self.assertRaises(ValueError):
            self.service.change_strategy(None)
        with self.assertRaises(TypeError):
            self.service.allocate("không phải hàm")

    def test_new_device_type_works_without_changing_service(self) -> None:
        class InteractiveDisplayRemote(TeachingDevice):
            def is_ready_for_use(self) -> bool:
                return self.status is DeviceStatus.Available

            def get_default_priority_score(self) -> float:
                return 75.0

        repository = InMemoryRepository[InteractiveDisplayRemote]()
        new_device = InteractiveDisplayRemote("D1", "Điều khiển màn hình", "Tủ D")
        repository.add(new_device)
        service = AllocationService[InteractiveDisplayRemote](
            repository, FirstAvailableStrategy[InteractiveDisplayRemote]()
        )
        self.assertIs(service.allocate(), new_device)
        self.assertEqual(new_device.status, DeviceStatus.Borrowed)

    def test_new_strategy_works_without_changing_service(self) -> None:
        class LowestPriorityStrategy(ISelectionStrategy[ProjectorRemote]):
            def select(self, candidates):
                if not candidates:
                    raise NoSuitableItemException()
                return min(candidates, key=lambda device: device.get_default_priority_score())

        self.service.change_strategy(LowestPriorityStrategy())
        self.assertEqual(self.service.allocate().id, "P1")

    def test_mixed_device_repository_uses_polymorphic_rules(self) -> None:
        repository = InMemoryRepository[TeachingDevice]()
        repository.add(projector("P1", 19))
        repository.add(microphone("M1", 30, 40))
        repository.add(air_remote("A1"))
        service = AllocationService[TeachingDevice](
            repository, FirstAvailableStrategy[TeachingDevice]()
        )
        self.assertEqual(service.allocate().id, "M1")
        self.assertEqual(service.allocate().id, "A1")
        with self.assertRaises(NoSuitableItemException):
            service.allocate()


if __name__ == "__main__":
    unittest.main(verbosity=2)
