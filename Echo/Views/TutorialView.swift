//
//  TutorialView.swift
//  EchoApp
//
//  Created by Michelle Lee on 7/24/25.
//

/*
import SwiftUI

struct TutorialView: View {
    @Binding var selectedTab: appTab
    @Binding var tutorialPageIndex: Int
    @State private var goBackToFirstPage = false

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
                    // Header with conditional back button
                    HStack {
                        if tutorialPageIndex == 1 {
                            Button(action: {
                                tutorialPageIndex = 0
                            }) {
                                Image(systemName: "chevron.left")
                                    .font(.system(size: 20, weight: .medium))
                                    .foregroundColor(.blue)
                            }
                            .padding(.leading, 10)
                        }

                        Text("Tutorial")
                            .font(.system(size: 43, weight: .bold))
                            .padding(.top, 50.0)
                            .padding(.leading, 10.0)

                        Spacer()

                        Image("profilePhoto")
                            .resizable()
                            .aspectRatio(contentMode: .fill)
                            .frame(width: 50, height: 50)
                            .cornerRadius(25)
                    }
                    .padding(.horizontal)

                    ScrollView {
                        VStack(spacing: 10) {
                            if tutorialPageIndex == 0 {
                                tutorialPage1Content
                            } else if tutorialPageIndex == 1 {
                                tutorialPage2Content
                            }
                        }
                        .padding(.horizontal, 10)
                        .padding(.top, 10)
                        .multilineTextAlignment(.center)
                        .font(.system(size: 25))
                    }

                    Spacer()

                    if tutorialPageIndex == 0 {
                        Text("Adjust the belt snugly and ensure that belt is facing forward.")
                            .font(.system(size: 14))
                            .foregroundColor(Color(red: 0.373, green: 0.373, blue: 0.373))
                            .opacity(0.6)
                            .multilineTextAlignment(.center)
                            .padding(.horizontal, 20)
                            .padding(.bottom, 20)
                    } else {
                        Text("Ensure that spatial audio is enabled on supported AirPods models.")
                            .font(.system(size: 14))
                            .foregroundColor(Color(red: 0.373, green: 0.373, blue: 0.373))
                            .opacity(0.6)
                            .multilineTextAlignment(.center)
                            .padding(.horizontal, 20)
                            .padding(.bottom, 20)
                    }

                    Button(action: {
                        if tutorialPageIndex == 0 {
                            tutorialPageIndex = 1
                        } else {
                            tutorialPageIndex = 0
                            goBackToFirstPage = true
                        }
                    }) {
                        ZStack {
                            RoundedRectangle(cornerRadius: 26)
                                .fill(Color(red: 0.0, green: 0.392, blue: 0.580))
                                .opacity(0.5)
                                .frame(width: 325, height: 55)

                            Text(tutorialPageIndex == 0 ? "Next" : "Done")
                                .foregroundColor(.white)
                                .fontWeight(.regular)
                        }
                    }
                    .padding(.bottom, 20)
                }
            }
        }
        .onChange(of: tutorialPageIndex) { newValue in
            if newValue == 0 {
                goBackToFirstPage = false
            }
        }
    }

    // MARK: - Page 1 Content
    private var tutorialPage1Content: some View {
        VStack(spacing: 0) {
            Text("Place the sensor belt")
            Text("on your waist")
            Text("on top of any clothing.")
                .fontWeight(.bold)
        }
    }

    // MARK: - Page 2 Content
    private var tutorialPage2Content: some View {
        VStack(spacing: 0) {
            Text("Place your AirPods into")
            Text("your ears and")
            Text("enable spatial audio.")
                .fontWeight(.bold)
        }
    }
}

#Preview {
    struct PreviewWrapper: View {
        @State private var index = 0
        var body: some View {
            TutorialView(
                selectedTab: .constant(.tutorial),
                tutorialPageIndex: $index
            )
        }
    }
    return PreviewWrapper()
}
*/

import SwiftUI

struct TutorialView: View {
    @Binding var selectedTab: appTab
    @Binding var tutorialPageIndex: Int
    @State private var goToNextPage = false
    
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
                            .padding(.top, 30)
                            .padding(.leading, 20)
                            
                        Spacer()
                        
                        Image("ProfilePhoto")
                            .resizable()
                            .aspectRatio(contentMode: .fill)
                            .frame(width: 45, height: 45)
                            .cornerRadius(25)
                            .padding(.top, 30)
                            .offset(x: -40)
                    }
                    .padding(.leading)
                    
               
                        VStack {
                            Text("Place the belt")
                                .font(.system(size: 25))
                                .multilineTextAlignment(.center)
                                .padding(.horizontal, 10)
                            Text("on your waist")
                                .font(.system(size: 25))
                                .multilineTextAlignment(.center)
                                .padding(.horizontal, 10)

                            Text("on top of any clothing.")
                                .font(.system(size: 25))
                                .fontWeight(.bold)
                                .multilineTextAlignment(.center)

                            Image("PersonWithBelt")
                                .resizable()
                                .padding([.leading, .bottom, .trailing])
                                .scaledToFit()
                                .frame(width: 375, height: 350)
                        }
                    

                    NavigationLink(
                        destination:
                            TutorialView2(selectedTab: $selectedTab, tutorialPageIndex: $tutorialPageIndex ),
                        
                        isActive: $goToNextPage
                    ) {
                        EmptyView()
                    }
                    
                    Text("Adjust the belt snugly and ensure that the belt is facing forward.")
                        .fontWeight(.regular)
                        .foregroundColor(Color(red: 0.373, green: 0.373, blue: 0.373))
                        .frame(width: 300.0, height: 50.0)
                        .opacity(0.6)
                        .multilineTextAlignment(.center)
                        .padding(.horizontal, 30)
                        .padding(.bottom, 20)
                    
                    Button(action: {
                        tutorialPageIndex = 1
                        goToNextPage = true
                    }) {
                        ZStack {
                            RoundedRectangle(cornerRadius: 26)
                                .fill(Color(red: 0.0, green: 0.392, blue: 0.580))
                                .opacity(0.5)
                                .frame(width: 325, height: 55)
                            
                            Text("Next")
                                .foregroundColor(.white)
                                .fontWeight(.regular)
                            
                                .padding(.horizontal, 30)
                        }
                    }
                }
                .padding(.bottom, 20)
            }
        }
        .onChange(of: tutorialPageIndex) {
            if tutorialPageIndex == 0 {
                goToNextPage = false
            }
        }
    }
}
    
    //}
    #Preview{
        struct PreviewWrapper: View {
            @State var tutorialPageIndex = 1
            var body: some View {
                TutorialView(
                    selectedTab: .constant(.tutorial),
                    tutorialPageIndex: $tutorialPageIndex
                )
            }
        }
        return PreviewWrapper()
    }

