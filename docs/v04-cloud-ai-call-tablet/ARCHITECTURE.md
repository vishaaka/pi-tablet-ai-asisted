# V04 Cloud AI Call Tablet Architecture

## Goal

The project direction is now a cloud-powered AI call tablet.

The Raspberry Pi 5 is a thin client. Cloud AI provides the main intelligence. The local PC is used only for development, administration, and emergency intervention.

## Core Architecture

```text
Pi5 Android Tablet
  -> Cloud Gateway
  -> OpenAI or Gemini
  -> Character Engine
  -> Speech and Avatar Services
  -> Pi5 Android Tablet

Optional Local PC
  -> Admin dashboard
  -> logs
  -> configuration
  -> manual intervention
```

## Device Role

Pi5 does not run the large language model locally.

Pi5 handles:

- Android-like phone simulation UI
- contact list
- symbolic numbers
- call screens
- ringtone playback
- microphone capture
- speaker output
- camera stream when enabled
- lightweight avatar rendering
- WebSocket connection to cloud gateway

## Cloud Role

Cloud side handles:

- conversation intelligence
- character behavior
- child-safe response policy
- short-turn dialog flow
- speech-to-text
- text-to-speech
- session memory
- call state sync
- parent-approved contact configuration

## Local PC Role

Local PC is not required for normal usage.

Local PC handles only:

- development
- app build
- GitHub sync
- admin dashboard
- logs
- manual override
- Pi setup and maintenance

## Product Boundary

The app is a simulated phone environment. It must not call real public phone numbers by default.

Contacts use internal symbolic numbers only.

## Recommended Runtime Flow

```text
1. Child opens Rehber.
2. Child selects an AI character.
3. App shows outgoing call screen.
4. Ringtone starts.
5. Cloud gateway creates AI session.
6. Call connects.
7. Audio streams between Pi and cloud.
8. AI answers with short Turkish speech.
9. Avatar/lip-sync events are sent to Pi.
10. Child ends call.
11. Call history is saved.
```

## Target Hardware

```text
Raspberry Pi 5 2GB
Hailo 8 or Hailo 8L
7 inch screen
USB plug-and-play sound card
microphone
speaker
camera
```

## First Milestone

Build a non-real-calling phone simulator with:

- contact list
- fictional AI character profile
- symbolic phone number
- outgoing call screen
- ringing state
- connected state
- end call button
- local fake response mode
- cloud-ready WebSocket protocol
