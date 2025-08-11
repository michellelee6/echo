//
//  TutorialView2.swift
//  EchoApp
//
//  Created by Michelle Lee on 7/27/25.
//


import SwiftUI

struct TutorialView2: View {
    @Binding var selectedTab: appTab
    @Binding var tutorialPageIndex: Int
    
    var body: some View {
        NavigationStack {
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
                
                VStack {
                    HStack {
                        Text("Tutorial")
                            .font(.system(size: 35, weight: .bold))
                            //.padding(.top, 30)
                            .padding(.leading, 20)
                            
                        Spacer()
                        
                        Image("ProfilePhoto")
                            .resizable()
                            .aspectRatio(contentMode: .fill)
                            .frame(width: 45, height: 45)
                            .cornerRadius(25)
                            //.padding(.top, 30)
                            .offset(x: -30, y: -3)
                    }
                    .padding(.leading)
                    
                    ScrollView{
                        VStack {
                            Text("Place your AirPods into")
                            Text("your ears and")
                            Text("enable spatial audio.")
                                .fontWeight(.bold)
                        }
                        .font(.system(size: 25))
                        .multilineTextAlignment(.center)
                        .padding(.horizontal, 10)

                        Image("SpatialAudio")
                            .resizable()
                            .padding([.leading, .trailing])
                            .scaledToFit()
                            .frame(width: 375, height: 350)
                        
                   // Spacer()
                        
                        Text("Ensure that spatial audio is enabled on supported AirPods models.")
                            .fontWeight(.regular)
                            .foregroundColor(Color(red: 0.373, green: 0.373, blue: 0.373))
                            .frame(width: 270.0, height: 50.0)
                            .opacity(0.6)
                            .multilineTextAlignment(.center)
                            //.padding(.top, 10)
                            .padding(.bottom, 10)
                        
                            
                           
                        Button(action: {
                            // selectedTab = .home
                            tutorialPageIndex = 0
                        }) {
                            ZStack {
                                RoundedRectangle(cornerRadius: 26)
                                    .fill(Color(red: 0.0, green: 0.392, blue: 0.580))
                                    .opacity(0.5)
                                    .frame(width: 325, height: 55)
                                
                                Text("Done")
                                    .foregroundColor(.white)
                                    .fontWeight(.regular)
                                
                            }
                        }
                        
                    }
                }
                
            }
        }
    }
}
    
    //}
    #Preview {
        struct PreviewWrapper: View {
            @State private var index = 2
            var body: some View {
                TutorialView2(
                    selectedTab: .constant(.tutorial),
                    tutorialPageIndex: $index
                )
            }
        }
        return PreviewWrapper()
    }
