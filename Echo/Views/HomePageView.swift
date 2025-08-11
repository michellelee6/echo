//
//  HomePageView.swift
//  EchoApp
//
//  Created by Michelle Lee on 7/24/25.
//

import SwiftUI
import Foundation
import AVFoundation

enum appTab: Hashable {
    case home
    case tutorial
    case faces
}

enum VibrationFeedbackMode: String, CaseIterable, Identifiable {
    case off, on
    var id: String { rawValue }
}

enum spatialaudioToggle: String, CaseIterable, Identifiable {
    case off, on
    var id: String { rawValue }
}

enum HapticStrength: String, CaseIterable, Identifiable {
    case low, medium, high
    var id: String { rawValue }
}

struct HomePage: View {
    @State private var selectedTab: appTab = .home
    @State private var tutorialPageIndex: Int = 0

    var body: some View {
        TabView(selection: $selectedTab) {
            HomePageView(selectedTab: $selectedTab)
                .tag(appTab.home)
                .tabItem {
                    Label("Home", systemImage: "house")
                }

            TutorialView (
                selectedTab: $selectedTab,
                tutorialPageIndex: $tutorialPageIndex
            )
            .tag(appTab.tutorial)
            .tabItem {
                Label("Tutorial", systemImage: "figure")
            }

            PeopleView()
                .tag(appTab.faces)
                .tabItem {
                    Label("My People", systemImage: "person.2")
                }
        }
        .onChange(of: selectedTab) {
            if selectedTab == .tutorial {
                tutorialPageIndex = 0
            }
        }
    }
}

struct HomePageView: View {
    @State var level: Float = 0.8
    @State var hapticstrength: HapticStrength = .medium
    @State var vibrationfeedback: VibrationFeedbackMode = .on
    @State var obstacleRange: Float = 4.0
    @Binding var selectedTab: appTab
    @State var spatialaudiotoggle: spatialaudioToggle = .on
    
    @StateObject var sessionManager = AccessorySessionManager()
    @StateObject var audioManager = SpatialAudioManager()
    
    // Needed to read aloud detected objects
    @State private var lastSpokenText: String = ""
    @State private var speechSynthesizer = AVSpeechSynthesizer()
    
    @State private var isDemoStarted = false
    @State private var startPing = false

    var body: some View {
        ZStack {
            LinearGradient(
                gradient: Gradient(colors: [
                    Color(red: 0.0, green: 0.392, blue: 0.580).opacity(0.3),
                    Color(red: 0.0, green: 0.392, blue: 0.580)
                ]),
                startPoint: .top,
                endPoint: .bottom
            )
            .ignoresSafeArea()
            .opacity(0.2)
            
            VStack(alignment: .leading) {
                HStack(alignment: .center) {
                    Text("Welcome back, Michelle!")
                        .font(.system(size: 24, weight: .bold))
                        .foregroundColor(Color(red: 0.0, green: 0.392, blue: 0.580))
                        .padding(.top, 40)
                        .padding(.bottom, 20)
                        .offset(x: -8)
                    
                    // Hidden button to indicate that demo has started (double tap header to start demo)
                        .onTapGesture(count: 2) {
                            isDemoStarted = true
                            print("Demo has started")
                        }
                    
                    Spacer()
                    
                    Image("ProfilePhoto")
                        .resizable()
                        .aspectRatio(contentMode: .fill)
                        .frame(width: 45, height: 45)
                        .cornerRadius(25)
                        .offset(y: 10)
                    
                    // Hidden button to indicate that demo has started (double tap header to start demo)
                        .onTapGesture(count: 2) {
                            startPing = true
                            print("play ping")
                        }
                }
                .padding(.top, 10) // Apply top padding to the entire HStack
                .padding(.horizontal)
                
                HStack {
                    VStack(alignment: .leading) {
                        Text("Michelle's Belt")
                            .font(.system(size: 20))
                        Text("Connected")
                            .font(.system(size: 17))
                            .foregroundColor(.gray)
                    }
                    
                    Spacer()
                    
                    VStack(alignment: .trailing) {
                        Image(systemName: "battery.75percent")
                        
                        Text("80%")
                            .font(.system(size: 18))
                            .foregroundColor(.gray)
                            .padding(.bottom, 10.0)
                            .offset(y: 8)
                    }
                }
                .padding()
                .background(Color.white)
                .cornerRadius(20)
                
                Group {
                    VStack(alignment: .leading) {
                        Text("Vibration Feedback")
                            .font(.headline)
                        Picker("Vibration Feedback", selection: $vibrationfeedback) {
                            Text("Off").tag(VibrationFeedbackMode.off)
                            Text("On").tag(VibrationFeedbackMode.on)
                        }
                        .pickerStyle(SegmentedPickerStyle())
                    }
                    
                    VStack(alignment: .leading) {
                        Text("Haptic Strength")
                            .font(.headline)
                        Picker("Haptic Strength", selection: $hapticstrength) {
                            Text("Low").tag(HapticStrength.low)
                            Text("Medium").tag(HapticStrength.medium)
                            Text("High").tag(HapticStrength.high)
                        }
                        .pickerStyle(SegmentedPickerStyle())
                    }
                    
                    VStack(alignment: .leading) {
                        Text("Spatial Audio")
                            .font(.headline)
                        Picker("Spatial Audio", selection: $spatialaudiotoggle) {
                            Text("Off").tag(spatialaudioToggle.off)
                            Text("On").tag(spatialaudioToggle.on)
                        }
                        .pickerStyle(SegmentedPickerStyle())
                    }
                    
                    VStack(alignment: .leading) {
                        Text("Obstacle Range")
                            .font(.headline)
                        Slider(value: $obstacleRange, in: 1...5, step: 0.5)
                    }
                }
                .padding()
                .background(Color.white)
                .cornerRadius(20)
                
                Spacer()
                
                /*
                // DELETE
                if isDemoStarted {
                    Text("detected objects: " + sessionManager.detectedObjects.joined(separator: ", "))
                }
                 */
            }
            .padding()
        }
        .onChange(of: vibrationfeedback) {
            if vibrationfeedback == .off {
                spatialaudiotoggle = .on
            }
        }
        .onChange(of: spatialaudiotoggle) {
            if spatialaudiotoggle == .off {
                vibrationfeedback = .on
            }
        }
        
        /*
         .onChange(of: sessionManager.distances) { newDistances in
         if isDemoStarted {
         audioManager.playPingForClosestObject(distances: newDistances)
         print("Playing audio for distances: \(newDistances)")
            }
         }
         */
        
        .onAppear {
            do {
                try AVAudioSession.sharedInstance().setCategory(.playback, mode: .default, options: [.duckOthers, .defaultToSpeaker])
                try AVAudioSession.sharedInstance().setActive(true)
                print("Audio session configured to use iPhone speaker.")
            } catch {
                print("Failed to configure AVAudioSession: \(error)")
            }
        }
        
        .onChange(of: sessionManager.detectedObjects) { newObjects in
            guard isDemoStarted else { return }
            
            print("reading aloud objects now....")

            let string = newObjects.joined(separator: ", ")
            if !string.isEmpty && string != lastSpokenText {
                lastSpokenText = string
                let utterance = AVSpeechUtterance(string: string)
                utterance.voice = AVSpeechSynthesisVoice(language: "en-US")
                speechSynthesizer.speak(utterance)
                
                audioManager.playPing()
                
                /*
                // Add ping after the utterance finishes
                DispatchQueue.main.asyncAfter(deadline: .now() + utterance.expectedSpeechDuration) {
                    // Simulate ping based on object's rough direction
                    // For now, just default to front direction
                    audioManager.playPing()
                    print("Played spatial audio ping after speech.")
                }
                 */
            }
            /*
            if (startPing) {
                audioManager.playPing()
            }
             */
        }
    }
}

#Preview {
    HomePage()
}
