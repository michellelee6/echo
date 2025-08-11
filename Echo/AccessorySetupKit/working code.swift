//
//  Untitled.swift
//  Echo
//
//  Created by Michelle Lee on 7/27/25.
//

// WORKING OBJECT DETECTION

/*
import Foundation
import AccessorySetupKit
import CoreBluetooth
import SwiftUI

@Observable
class AccessorySessionManager: NSObject, ObservableObject {
    var peripheralConnected = false
    var pickerDismissed = true
    var accessoryPaired = false

    var rawData: String?

    private var session = ASAccessorySession()
    private var currentAccessory: ASAccessory?
    private var manager: CBCentralManager?
    private var peripheral: CBPeripheral?
    private var distanceCharacteristic: CBCharacteristic?
    private var objectCharacteristic: CBCharacteristic?

    private static let yourServiceUUID = AccessoryModel.echo.serviceUUID
    // private static let distanceCharacteristicUUID = "12345678-1234-5678-1234-56789ABCDEF1"
    private static let objectCharacteristicUUID = "12345678-1234-5678-1234-56789ABCDEF1"
    
    var detectedObjects: [String] = []

    private static let pickerItem: ASPickerDisplayItem = {
        let descriptor = ASDiscoveryDescriptor()
        descriptor.bluetoothServiceUUID = AccessoryModel.echo.serviceUUID
        return ASPickerDisplayItem(
            name: AccessoryModel.echo.displayName,
            productImage: AccessoryModel.echo.accessoryImage,
            descriptor: descriptor
        )
    }()

    override init() {
        super.init()
        session.activate(on: DispatchQueue.main, eventHandler: handleSessionEvent)
    }

    func presentPicker() {
        session.showPicker(for: [Self.pickerItem]) { error in
            if let error {
                print("Picker failed: \(error.localizedDescription)")
            }
        }
    }

    func removeAccessory() {
        guard let currentAccessory else { return }

        if peripheralConnected {
            disconnect()
        }

        session.removeAccessory(currentAccessory) { _ in
            self.currentAccessory = nil
            self.manager = nil
            self.accessoryPaired = false
        }
    }
    
    func connect() {
        guard let manager = manager,
              let peripheral = peripheral,
              manager.state == .poweredOn else {
            print("Cannot connect: manager or peripheral not ready")
            return
        }
        print("User requested connection to peripheral \(peripheral.identifier)")
        manager.connect(peripheral)
    }

    func disconnect() {
        guard let peripheral, let manager else {
            print("Cannot disconnect: manager or peripheral nil")
            return
        }
        print("Disconnecting peripheral \(peripheral.identifier)")
        manager.cancelPeripheralConnection(peripheral)
    }


    private func handleSessionEvent(event: ASAccessoryEvent) {
        switch event.eventType {
        case .accessoryAdded, .accessoryChanged, .activated:
            guard let accessory = event.accessory ?? session.accessories.first else { return }
            currentAccessory = accessory
            accessoryPaired = true
            
            if accessoryPaired {
                DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) {
                    self.connect()
                    print("connect() method called")
                }
            }
            
            if manager == nil {
                manager = CBCentralManager(delegate: self, queue: nil)
            }
        case .accessoryRemoved:
            currentAccessory = nil
            manager = nil
            accessoryPaired = false
        case .pickerDidPresent:
            pickerDismissed = false
        case .pickerDidDismiss:
            pickerDismissed = true
        default:
            break
        }
    }
}

// MARK: - CBCentralManagerDelegate

extension AccessorySessionManager: CBCentralManagerDelegate {
    func centralManagerDidUpdateState(_ central: CBCentralManager) {
        print("Central manager did update state: \(central.state.rawValue)")
        guard central.state == .poweredOn else {
            peripheral = nil
            print("Bluetooth not powered on")
            return
        }

        if let uuid = currentAccessory?.bluetoothIdentifier {
            print("Retrieving peripheral with UUID: \(uuid)")
            peripheral = central.retrievePeripherals(withIdentifiers: [uuid]).first
            if let peripheral = peripheral {
                print("Peripheral found: \(peripheral.identifier)")
                peripheral.delegate = self
            } else {
                print("Peripheral not found")
            }
        }
    }

    func centralManager(_ central: CBCentralManager, didConnect peripheral: CBPeripheral) {
        print("Did connect to peripheral \(peripheral.identifier)")
        self.peripheralConnected = true
        peripheral.delegate = self
        peripheral.discoverServices(nil)
    }
    
    func centralManager(_ central: CBCentralManager, didFailToConnect peripheral: CBPeripheral, error: Error?) {
        print("Failed to connect: \(error?.localizedDescription ?? "unknown error")")
        peripheralConnected = false
    }

    func centralManager(_ central: CBCentralManager, didDisconnectPeripheral peripheral: CBPeripheral, error: Error?) {
        print("Disconnected from peripheral \(peripheral.identifier), error: \(error?.localizedDescription ?? "none")")
        self.peripheralConnected = false
    }
}

// MARK: - CBPeripheralDelegate

extension AccessorySessionManager: CBPeripheralDelegate {
    func peripheral(_ peripheral: CBPeripheral, didDiscoverServices error: Error?) {
        guard let services = peripheral.services else {
            print("No services found")
            return
        }
        
        print("services discovered")
        for service in services {
            print("  •", service.uuid)
            peripheral.discoverCharacteristics([CBUUID(string: Self.objectCharacteristicUUID)], for: service)
        }
    }

    func peripheral(_ peripheral: CBPeripheral, didDiscoverCharacteristicsFor service: CBService, error: Error?) {
        guard let characteristics = service.characteristics else {
            print("No characteristics for service \(service.uuid)")
            return
        }

        print("Characteristics discovered for \(service.uuid):")
        
        for characteristic in characteristics {
            if characteristic.uuid == CBUUID(string: Self.objectCharacteristicUUID) {
                print("[BLE] Subscribed to object detection notifications")
                objectCharacteristic = characteristic
                peripheral.setNotifyValue(true, for: characteristic)
                peripheral.readValue(for: characteristic)
            }
        }
    }
    
    func peripheral(_ peripheral: CBPeripheral, didUpdateValueFor characteristic: CBCharacteristic, error: Error?) {
        if let error = error {
            print("Error reading value:", error)
            return
        }

        if characteristic.uuid == CBUUID(string: Self.objectCharacteristicUUID) {
            guard let data = characteristic.value else {
                print("Error not able to get object")
                return
            }

            if let objectString = String(data: data, encoding: .utf8) {
                let objects = objectString
                    .split(separator: ",")
                    .map { String($0) }
                
                print("[BLE] Detected objects received:", objects)  // 👈 This line will print in Xcode's terminal
                
                // self.detectedObjects = objects
                DispatchQueue.main.async {
                    self.detectedObjects = objects
                }

            } else {
                print("Failed to decode object data")
            }
        }
    }
    
    func peripheral(_ peripheral: CBPeripheral, didUpdateNotificationStateFor characteristic: CBCharacteristic, error: Error?) {
        if let error = error {
            print("Failed to enable notifications:", error.localizedDescription)
        } else {
            print("Notifications enabled for:", characteristic.uuid)
        }
    }
}
 */

/*
import Foundation
import AccessorySetupKit
import CoreBluetooth
import SwiftUI

@Observable
class AccessorySessionManager: NSObject, ObservableObject {
    var peripheralConnected = false
    var pickerDismissed = true
    var accessoryPaired = false

    var rawData: String?
    var distances: [Int] = []

    private var session = ASAccessorySession()
    private var currentAccessory: ASAccessory?
    private var manager: CBCentralManager?
    private var peripheral: CBPeripheral?
    private var distanceCharacteristic: CBCharacteristic?
    private var objectCharacteristic: CBCharacteristic?

    private static let yourServiceUUID = AccessoryModel.echo.serviceUUID
    private static let distanceCharacteristicUUID = "12345678-1234-5678-1234-56789ABCDEF1"

    private static let pickerItem: ASPickerDisplayItem = {
        let descriptor = ASDiscoveryDescriptor()
        descriptor.bluetoothServiceUUID = AccessoryModel.echo.serviceUUID
        return ASPickerDisplayItem(
            name: AccessoryModel.echo.displayName,
            productImage: AccessoryModel.echo.accessoryImage,
            descriptor: descriptor
        )
    }()

    override init() {
        super.init()
        session.activate(on: DispatchQueue.main, eventHandler: handleSessionEvent)
    }

    func presentPicker() {
        session.showPicker(for: [Self.pickerItem]) { error in
            if let error {
                print("Picker failed: \(error.localizedDescription)")
            }
        }
    }

    func removeAccessory() {
        guard let currentAccessory else { return }

        if peripheralConnected {
            disconnect()
        }

        session.removeAccessory(currentAccessory) { _ in
            self.currentAccessory = nil
            self.manager = nil
            self.accessoryPaired = false
        }
    }
    
    func connect() {
        guard let manager = manager,
              let peripheral = peripheral,
              manager.state == .poweredOn else {
            print("Cannot connect: manager or peripheral not ready")
            return
        }
        print("User requested connection to peripheral \(peripheral.identifier)")
        manager.connect(peripheral)
    }

    func disconnect() {
        guard let peripheral, let manager else {
            print("Cannot disconnect: manager or peripheral nil")
            return
        }
        print("Disconnecting peripheral \(peripheral.identifier)")
        manager.cancelPeripheralConnection(peripheral)
    }


    private func handleSessionEvent(event: ASAccessoryEvent) {
        switch event.eventType {
        case .accessoryAdded, .accessoryChanged, .activated:
            guard let accessory = event.accessory ?? session.accessories.first else { return }
            currentAccessory = accessory
            accessoryPaired = true
            
            if accessoryPaired {
                DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) {
                    self.connect()
                    print("connect() method called")
                }
            }
            
            if manager == nil {
                manager = CBCentralManager(delegate: self, queue: nil)
            }
        case .accessoryRemoved:
            currentAccessory = nil
            manager = nil
            accessoryPaired = false
        case .pickerDidPresent:
            pickerDismissed = false
        case .pickerDidDismiss:
            pickerDismissed = true
        default:
            break
        }
    }
}

// MARK: - CBCentralManagerDelegate

extension AccessorySessionManager: CBCentralManagerDelegate {
    func centralManagerDidUpdateState(_ central: CBCentralManager) {
        print("Central manager did update state: \(central.state.rawValue)")
        guard central.state == .poweredOn else {
            peripheral = nil
            print("Bluetooth not powered on")
            return
        }

        if let uuid = currentAccessory?.bluetoothIdentifier {
            print("Retrieving peripheral with UUID: \(uuid)")
            peripheral = central.retrievePeripherals(withIdentifiers: [uuid]).first
            if let peripheral = peripheral {
                print("Peripheral found: \(peripheral.identifier)")
                peripheral.delegate = self
            } else {
                print("Peripheral not found")
            }
        }
    }

    func centralManager(_ central: CBCentralManager, didConnect peripheral: CBPeripheral) {
        print("Did connect to peripheral \(peripheral.identifier)")
        self.peripheralConnected = true
        peripheral.delegate = self
        peripheral.discoverServices(nil)
    }
    
    func centralManager(_ central: CBCentralManager, didFailToConnect peripheral: CBPeripheral, error: Error?) {
        print("Failed to connect: \(error?.localizedDescription ?? "unknown error")")
        peripheralConnected = false
    }

    func centralManager(_ central: CBCentralManager, didDisconnectPeripheral peripheral: CBPeripheral, error: Error?) {
        print("Disconnected from peripheral \(peripheral.identifier), error: \(error?.localizedDescription ?? "none")")
        self.peripheralConnected = false
    }
}

// MARK: - CBPeripheralDelegate

extension AccessorySessionManager: CBPeripheralDelegate {
    func peripheral(_ peripheral: CBPeripheral, didDiscoverServices error: Error?) {
        guard let services = peripheral.services else {
            print("No services found")
            return
        }
        
        print("services discovered")
        for service in services {
            print("  •", service.uuid)
            peripheral.discoverCharacteristics([CBUUID(string: Self.distanceCharacteristicUUID)], for: service)
        }
    }

    func peripheral(_ peripheral: CBPeripheral, didDiscoverCharacteristicsFor service: CBService, error: Error?) {
        guard let characteristics = service.characteristics else {
            print("No characteristics for service \(service.uuid)")
            return
        }

        print("Characteristics discovered for \(service.uuid):")
        
        for characteristic in characteristics {
            if characteristic.uuid == CBUUID(string: Self.distanceCharacteristicUUID) {
                print("Found distance characteristic")
                distanceCharacteristic = characteristic
                peripheral.setNotifyValue(true, for: characteristic)
                peripheral.readValue(for: characteristic)
            }
        }

    }
    
    func peripheral(_ peripheral: CBPeripheral, didUpdateValueFor characteristic: CBCharacteristic, error: Error?) {
        if let error = error {
              print("Error reading value:", error)
              return
          }

        if characteristic.uuid == CBUUID(string: Self.distanceCharacteristicUUID) {
            guard let data = characteristic.value else {
                print("Error: no data in characteristic")
                return
            }

            if let distanceString = String(data: data, encoding: .utf8) {
                let distanceValues = distanceString
                    .split(separator: ",")
                    .compactMap { Int($0.trimmingCharacters(in: .whitespaces)) }

                if distanceValues.count == 5 {
                    self.distances = distanceValues
                    print("Updated distances: \(distanceValues)")
                } else {
                    print("Unexpected number of distances: \(distanceValues)")
                }
            } else {
                print("Failed to decode distance data")
            }
        }
    }
    
    func peripheral(_ peripheral: CBPeripheral, didUpdateNotificationStateFor characteristic: CBCharacteristic, error: Error?) {
        if let error = error {
            print("Failed to enable notifications:", error.localizedDescription)
        } else {
            print("Notifications enabled for:", characteristic.uuid)
        }
    }
}
*/
