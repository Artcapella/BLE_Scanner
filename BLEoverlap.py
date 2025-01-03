import asyncio
from bleak import BleakScanner

def calculate_distance(rssi, tx_power=-59):
    """
    Estimate distance using RSSI and a reference power value.
    tx_power: RSSI at 1 meter (default is -59 for BLE devices).
    """
    if rssi == 0:
        return -1  # Exception for undetermined distance
    n = 2  # Path-loss exponent (2 for free space)
    distance = 10 ** ((tx_power - rssi) / (10 * n))
    return round(distance, 2)

async def scan_ble_devices():
    print("Scanning for BLE devices...")
    devices = await BleakScanner.discover()

    if not devices:
        print("No devices found.")
        return []

    print(f"Found {len(devices)} devices:")

    devices_distance = []
    for device in devices:
        # retrieve RSSI directly from the BLEDevice object
        rssi = device.rssi

        # estimate distance
        distance = calculate_distance(rssi)

        devices_distance.append((device.address, device.name or "Unknown", rssi, distance))

    # sort by distance
    devices_distance.sort(key=lambda x: x[3])

    # device info ordered by distance
    for address, name, rssi, distance in devices_distance:
        print(f"  Device: {name} - Address: {address}")
        print(f"  RSSI: {rssi} dBm")
        print(f"  Estimated Distance: {distance} meters")
        print()

    return devices_distance

async def main():
    print("Starting first scan...")
    scan1 = await scan_ble_devices()

    print("Waiting before starting second scan...")
    await asyncio.sleep(5)  # waiting 5 seconds before the second scan

    print("Starting second scan...")
    scan2 = await scan_ble_devices()

    addresses_scan1 = {device[0] for device in scan1}
    addresses_scan2 = {device[0] for device in scan2}

    overlapping_addresses = addresses_scan1 & addresses_scan2

    if overlapping_addresses:
        print("\nDevices found in both scans:")
        for address in overlapping_addresses:
            device1 = next(d for d in scan1 if d[0] == address)
            device2 = next(d for d in scan2 if d[0] == address)

            print(f"  Address: {address}")
            print(f"    Scan 1 - Name: {device1[1]}, RSSI: {device1[2]} dBm, Estimated Distance: {device1[3]} meters")
            print(f"    Scan 2 - Name: {device2[1]}, RSSI: {device2[2]} dBm, Estimated Distance: {device2[3]} meters")
            print()
    else:
        print("\nNo overlapping devices found between scans.")

if __name__ == "__main__":
    asyncio.run(main())