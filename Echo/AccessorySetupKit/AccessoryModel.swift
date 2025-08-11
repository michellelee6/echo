//
//  AccessoryModel.swift
//  EchoApp
//
//  Created by Michelle Lee on 7/25/25.
//

import Foundation
import CoreBluetooth
import UIKit

enum AccessoryModel {
    case echo
    
    var accessoryName: String {
        switch self {
            case .echo: "Echo"
        }
    }
    
    var displayName: String {
        switch self {
            case .echo: "Belt"
        }
    }
    
    var serviceUUID: CBUUID {
        switch self {
            case .echo: CBUUID(string: "12345678-1234-5678-1234-56789ABCDEF0")
        }
    }
    
    var accessoryImage: UIImage {
        switch self {
            case .echo: UIImage(named: "Belt") ?? UIImage()
        }
    }
}
