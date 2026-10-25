# Kim Duy Vương
# 20237410

from __future__ import annotations

from lab_w07 import (
    AirConditionerRemote,
    AllocationService,
    DeviceStatus,
    DuplicateIdException,
    FirstAvailableStrategy,
    HighestPriorityStrategy,
    InMemoryRepository,
    NoSuitableItemException,
    ProjectorRemote,
    TeachingDevice,
    WirelessMicrophone,
)


def show_devices(devices: tuple[TeachingDevice, ...]) -> None:
    for device in devices:
        print(f"  {device}")


def main() -> None:
    print("LAB W07 - ĐA HÌNH VÀ GENERIC TRONG PYTHON")

    projectors = InMemoryRepository[ProjectorRemote]()
    air_conditioners = InMemoryRepository[AirConditionerRemote]()
    microphones = InMemoryRepository[WirelessMicrophone]()

    print("\n[1] Thêm 3 điều khiển máy chiếu, 2 điều hòa, 3 micro")
    for projector in (
        ProjectorRemote("PR01", "Điều khiển máy chiếu 1", "Tủ A", 50),
        ProjectorRemote("PR02", "Điều khiển máy chiếu 2", "Tủ A", 90),
        ProjectorRemote("PR03", "Điều khiển máy chiếu 3", "Tủ A", 10),
    ):
        projectors.add(projector)
    for air_conditioner in (
        AirConditionerRemote("AC01", "Điều khiển điều hòa 1", "Tủ B", {"A201", "A202"}),
        AirConditionerRemote("AC02", "Điều khiển điều hòa 2", "Tủ B", {"A203", "A204"}),
    ):
        air_conditioners.add(air_conditioner)
    for microphone in (
        WirelessMicrophone("MIC01", "Micro 1", "Tủ C", 20, 80),
        WirelessMicrophone("MIC02", "Micro 2", "Tủ C", 60, 60),
        WirelessMicrophone("MIC03", "Micro 3", "Tủ C", 90, 90),
    ):
        microphones.add(microphone)
    show_devices(projectors.get_all())
    show_devices(air_conditioners.get_all())
    show_devices(microphones.get_all())

    print("\n[2] Thử thêm thiết bị trùng mã PR01")
    try:
        projectors.add(ProjectorRemote("PR01", "Thiết bị trùng", "Tủ A", 100))
    except DuplicateIdException as error:
        print(f"  {type(error).__name__}: {error}")

    print("\n[3] Tìm thiết bị theo mã")
    print(f"  PR02: {projectors.find_by_id('PR02')}")
    print(f"  Không có mã UNKNOWN: {projectors.find_by_id('UNKNOWN')}")

    print("\n[4] Lọc thiết bị sẵn sàng bằng cùng một phương thức generic")
    print("  Máy chiếu:")
    show_devices(projectors.find_all(lambda device: device.is_ready_for_use()))
    print("  Micro:")
    show_devices(microphones.find_all(lambda device: device.is_ready_for_use()))

    print("\n[5] Cấp phát điều khiển máy chiếu có điểm cao nhất")
    projector_service = AllocationService[ProjectorRemote](
        projectors,
        HighestPriorityStrategy[ProjectorRemote](
            lambda device: device.get_default_priority_score()
        ),
    )
    selected_projector = projector_service.allocate()
    print(f"  Đã chọn: {selected_projector}")

    print("\n[6] Cấp phát điều khiển điều hòa tương thích phòng A203")
    room_id = "A203"
    air_service = AllocationService[AirConditionerRemote](
        air_conditioners,
        HighestPriorityStrategy[AirConditionerRemote](
            lambda device: device.get_priority_score_for_room(room_id)
        ),
    )
    selected_air = air_service.allocate(lambda device: device.is_compatible_with(room_id))
    print(f"  Đã chọn: {selected_air}")

    print("\n[7] Cấp phát micro đầu tiên sẵn sàng")
    micro_service = AllocationService[WirelessMicrophone](
        microphones, FirstAvailableStrategy[WirelessMicrophone]()
    )
    selected_micro = micro_service.allocate()
    print(f"  Đã chọn: {selected_micro}")

    print("\n[8] Đổi strategy khi chạy, so sánh trên cùng tập thiết bị sẵn sàng")
    # Trả MIC02 để hai strategy cùng so sánh MIC02 và MIC03.
    selected_micro.return_device()
    micro_service.change_strategy(
        HighestPriorityStrategy[WirelessMicrophone](
            lambda device: device.get_default_priority_score()
        )
    )
    highest_micro = micro_service.allocate()
    print(f"  FirstAvailable chọn {selected_micro.id}; HighestPriority chọn {highest_micro.id}.")

    print("\n[9] Cấp phát khi không có ứng viên phù hợp")
    try:
        air_service.allocate(lambda device: device.is_compatible_with("Z999"))
    except NoSuitableItemException as error:
        print(f"  {type(error).__name__}: {error}")

    print("\n[10] Thiết bị được chọn chuyển sang Borrowed, trả lại về Available")
    print(f"  {selected_projector.id}: {selected_projector.status.value}")
    if selected_projector.status is not DeviceStatus.Borrowed:
        raise RuntimeError("Thiết bị cấp phát phải ở trạng thái Borrowed.")
    selected_projector.return_device()
    print(f"  Sau khi trả: {selected_projector.status.value}")
    print(f"  Sẵn sàng trở lại: {selected_projector.is_ready_for_use()}")

    print("\n[11] Cùng InMemoryRepository[T] dùng cho ba loại thiết bị")
    print(f"  ProjectorRemote: {len(projectors.get_all())} phần tử")
    print(f"  AirConditionerRemote: {len(air_conditioners.get_all())} phần tử")
    print(f"  WirelessMicrophone: {len(microphones.get_all())} phần tử")
    print(f"  Xóa mã không tồn tại: {projectors.remove('UNKNOWN')}")


if __name__ == "__main__":
    main()
