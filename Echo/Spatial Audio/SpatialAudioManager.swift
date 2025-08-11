//
//  SpatialAudioManager.swift
//  EchoApp
//
//  Created by Michelle Lee on 7/25/25.
//

// Uses array of distances to determine which ping to play (smallest distance in the distance array will play the corresponding ping)
import Foundation
import AVFoundation

class SpatialAudioManager: ObservableObject {
    private var players: [AVPlayer] = []
    private var lastPingTime = Date(timeIntervalSince1970: 0)
    
    // Only include the 5 relevant spatial directions based on your sensor layout
    // Index 0: Sensor 1 (far-right), sensor 2 (front-right), sensor 3 (front), sensor 4 (front-left), sensor 5 (far-left)
    private let pingFilenames = ["far-right_ping", "front-right_ping", "front_ping", "front-left_ping", "far-left_ping"]
    
    init() {
        setupAudioSession()
    }
    
    /*
    func playPingForClosestObject(distances: [Int]) {
        guard distances.count == 5 else {
            print("Error: Expected 5 distances, got \(distances.count)")
            return
        }
        
        // Find the index of the smallest (closest) distance
        if let minIndex = distances.enumerated().min(by: { $0.element < $1.element })?.offset {
            let soundName = pingFilenames[minIndex]
            print("Playing ping for sensor \(minIndex + 1): \(soundName)")
            playSound(named: soundName)
        }
    }
     */
    
    func playPing() {
        let hardcodedSoundName = "front_ping"   
        print("Playing hardcoded ping after 1.5s delay: \(hardcodedSoundName)")
        
        DispatchQueue.main.asyncAfter(deadline: .now() + 1.5) {
            self.playSound(named: hardcodedSoundName)
        }
    }
    
    func playPingForClosestObject(distances: [Int]) {
        // Prevent pings from playing too often (play ping once every 0.5 seconds)
        guard Date().timeIntervalSince(lastPingTime) > 0.5 else { return }
           lastPingTime = Date()
        
        guard distances.count == 5 else {
            print("Error: Expected 5 distances, got \(distances.count)")
            return
        }

        let threshold = 100 // cm — adjust based on your environment
        
        // Filter only distances below the threshold
        let closeObstacles = distances.enumerated().filter { $0.element < threshold }

        // Considers obstacles only within the threshold of 100 cm
        guard let (minIndex, _) = closeObstacles.min(by: { $0.element < $1.element }) else {
            print("No obstacle close enough to play sound.")
            return // nothing below the threshold, don't play sound
        }

        let soundName = pingFilenames[minIndex]
        print("Playing ping for sensor \(minIndex + 1): \(soundName)")
        playSound(named: soundName)
    }

    
    private func playSound(named name: String) {
        guard let url = Bundle.main.url(forResource: name, withExtension: "wav") else {
            print("Sound file '\(name).wav' not found")
            return
        }
        
        let playerItem = AVPlayerItem(url: url)
        let player = AVPlayer(playerItem: playerItem)
        players.append(player)  // Prevent premature deallocation
        player.play()
    }
    
    func stopAllSounds() {
        for player in players {
            player.pause()
        }
        players.removeAll()
    }
    
    private func setupAudioSession() {
        let session = AVAudioSession.sharedInstance()
        do {
            try session.setCategory(.playback, mode: .moviePlayback, options: [.allowAirPlay, .allowBluetoothA2DP])
            try session.setActive(true)
        } catch {
            print("Failed to set up audio session: \(error)")
        }
    }
}
