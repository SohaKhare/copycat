# CopyCat Frontend Specification

## 1. Purpose of This Document

This document is the master frontend specification for the CopyCat project.

All frontend implementation should follow this specification.

The project should be implemented incrementally. Do not attempt to build the entire frontend in one task.

Before implementing a requested phase, inspect the existing codebase and determine how the requested work fits into the current architecture.

Preserve existing working functionality unless a change is explicitly required.

---

# 2. Project Overview

## What is CopyCat?

CopyCat is an AI-powered application that analyzes screen recordings to understand digital workflows.

A user uploads a screen recording showing someone interacting with a computer interface.

The system processes the recording and identifies:

- The user's overall goal
- Actions performed
- Important steps
- The sequence of interactions
- The resulting workflow

CopyCat transforms an unstructured screen recording into structured, understandable information.

---

# 3. Primary User Journey

The main user journey is:

```text
LANDING PAGE
      ↓
TRY IT OUT / SIGN IN
      ↓
APPLICATION DASHBOARD
      ↓
UPLOAD SCREEN RECORDING
      ↓
VIDEO PROCESSING
      ↓
AI ANALYSIS
      ↓
ANALYSIS RESULTS
      ↓
VIEW ACTIONS AND FRAMES
```

---

# 4. Frontend Goals

The frontend must achieve two different goals.

## Landing Page

The landing page should:

- Explain CopyCat clearly
- Make the product feel polished
- Explain why the product is useful
- Demonstrate how it works
- Show what the analysis output looks like
- Encourage users to try the application

The landing page should be visually immersive.

---

## Application Interface

The application should:

- Be easy to understand
- Be functional
- Prioritize usability
- Make uploading simple
- Clearly communicate processing progress
- Present AI analysis results clearly
- Allow users to explore their analysis

The application should be less cinematic than the landing page.

Functionality and clarity should take priority.

---

# 5. Design Philosophy

The overall design should feel:

- Modern
- Premium
- Minimal
- Dark
- Clean
- Intentional
- Typography-focused

The interface should not feel cluttered.

The premium feeling should come primarily from:

```text
SPACING
TYPOGRAPHY
VISUAL HIERARCHY
SUBTLE MOTION
CONSISTENT DESIGN
```

Avoid adding decorative UI elements without a clear purpose.

---

# 6. Visual Design System

## Colors

Primary background:

```text
#080808
```

Secondary background:

```text
#0D0D0D
```

Surface:

```text
#141414
```

Elevated surface:

```text
#1A1A1A
```

Primary text:

```text
#F5F5F5
```

Secondary text:

```text
#A1A1A1
```

Muted text:

```text
#737373
```

Border:

```text
rgba(255,255,255,0.10)
```

---

## Accent Colors

Use accent colors sparingly.

Primary accent:

```text
#D94F4F
```

Secondary accent:

```text
#7C6CF0
```

Do not use accent colors excessively.

The interface should remain primarily dark, neutral, and minimal.

---

# 7. Typography

Use a modern sans-serif font already available in the project.

If a font must be added, prefer a widely available modern font.

Typography should create strong hierarchy.

## Hero Heading

Desktop:

```text
80px – 120px
```

Tablet:

```text
60px – 80px
```

Mobile:

```text
40px – 56px
```

Use:

- Bold or semibold weight
- Tight line height
- Strong contrast

Example:

```text
WATCH.

UNDERSTAND.

REPLICATE.
```

---

## General Typography Rules

Use:

- Large headings
- Short paragraphs
- Strong hierarchy
- Generous spacing

Avoid:

- Long blocks of text
- Tiny unreadable text
- Excessive font weights
- Too many font styles

---

# 8. Motion Design

Animations should be:

- Smooth
- Subtle
- Purposeful
- Performance-conscious

Recommended animations:

- Fade in
- Fade out
- Slight vertical movement
- Scroll reveals
- Small hover transitions
- Subtle transforms

Avoid:

- Bouncing
- Flashing
- Excessive scaling
- Constant unnecessary movement
- Dramatic spinning
- Overly complex transitions

Respect:

```text
prefers-reduced-motion
```

---

# 9. Responsiveness

The frontend must work correctly on:

```text
DESKTOP

TABLET

MOBILE
```

Responsive design must not simply shrink the desktop layout.

Layouts should adapt appropriately.

On mobile:

- Simplify navigation
- Reduce animation complexity
- Reduce visual density
- Maintain readable typography
- Ensure touch targets are large enough
- Keep primary actions easily accessible

---

# 10. Accessibility

Ensure:

- Good text contrast
- Keyboard-accessible navigation
- Visible focus states
- Semantic HTML
- Clear button labels
- Accessible forms
- Reduced motion support

Do not sacrifice accessibility for visual design.

---

# 11. Application Routes

The target route structure is:

```text
/

Landing Page

/signin

Sign In

/signup

Create Account

/app

Dashboard

/app/upload

Upload Recording

/app/analysis/:id

Analysis Results

/app/history

Analysis History
```

Adapt the route implementation to the existing frontend framework.

Do not unnecessarily change an existing routing system.

---

# 12. Landing Page

The landing page is located at:

```text
/
```

It should contain the following sections:

```text
01 HERO

02 WHAT COPYCAT DOES

03 HOW IT WORKS

04 PRODUCT DEMONSTRATION

05 WHY COPYCAT

06 USE CASES

07 FINAL CTA

08 FOOTER
```

The page should feel like one continuous story.

---

# 13. Landing Page Navigation

Create a fixed navigation bar.

## Left

```text
COPYCAT
```

This should act as the logo/home link.

---

## Center or Right

Navigation links:

```text
How It Works

Use Cases

About
```

These should scroll to appropriate landing page sections.

---

## Right Side

Actions:

```text
Sign In
```

Primary CTA:

```text
Try It Out →
```

The CTA should lead to the appropriate application or authentication route.

---

## Scroll Behavior

Initially:

- Navbar should blend with the background.

After scrolling:

- Add subtle dark background.
- Add subtle border or separation.
- Maintain readability.
- Keep the effect minimal.

---

# 14. Landing Page Hero

The hero should occupy approximately:

```text
100vh
```

The hero should immediately communicate the product.

Suggested structure:

```text
COPYCAT

WATCH.
UNDERSTAND.
REPLICATE.

AI that transforms screen recordings
into structured digital workflows.

[ TRY IT OUT → ]

Learn more ↓
```

The hero should:

- Have generous whitespace.
- Prioritize typography.
- Clearly communicate the product.
- Include a strong CTA.

Do not overcrowd the hero.

---

# 15. Hero Background

For now, DO NOT implement an AI-generated video background.

The hero should look visually strong without requiring video assets.

Use:

- Deep dark background
- Subtle gradients if needed
- Minimal texture
- Optional CSS or SVG ambient effects

Any background effect must remain subtle.

Do not use:

- Heavy particles
- Bright neon
- Sci-fi visuals
- Random technology graphics

The center area should remain visually clean.

A background video may be added in a future phase.

The implementation should make it reasonably easy to add a video layer later.

---

# 16. Section: What CopyCat Does

Section purpose:

Explain the core idea of CopyCat.

Primary heading:

```text
YOUR USERS ALREADY
SHOW YOU HOW THEY WORK.
```

Supporting statement:

```text
CopyCat helps you understand it.
```

Explain briefly that CopyCat analyzes screen recordings and identifies actions, intent, and workflows.

The layout should be minimal.

Use:

- Large typography
- Strong whitespace
- Short explanations

Avoid turning this into a collection of feature cards.

---

# 17. Section: How It Works

Primary heading:

```text
FROM RECORDING
TO UNDERSTANDING.
```

The section should describe four stages.

---

## Stage 01

```text
01

UPLOAD

Upload a screen recording.
```

---

## Stage 02

```text
02

OBSERVE

CopyCat extracts important moments
and interactions.
```

---

## Stage 03

```text
03

UNDERSTAND

AI identifies user actions
and intent.
```

---

## Stage 04

```text
04

STRUCTURE

The workflow becomes clear
and understandable.
```

---

## Design Requirements

Use:

- Large stage numbers
- Strong typography
- Generous vertical spacing
- Scroll-based reveals where appropriate

Do not use four generic feature cards.

The section should feel editorial and story-driven.

---

# 18. Section: Product Demonstration

Primary heading:

```text
SEE WHAT COPYCAT SEES.
```

Show a visual demonstration of the application's output.

The demonstration should resemble the real CopyCat application.

---

## Layout

Use a split or responsive layout.

### Video / Frame Area

Show:

- Video preview
- Selected frame
- Timeline
- Frame markers

This can initially use placeholder or mock data.

---

### Analysis Area

Show:

```text
USER GOAL

Delete unnecessary files
from File Explorer.
```

Then:

```text
ACTIONS DETECTED

01
Open File Explorer

02
Select sem4.zip

03
Delete the file

04
Select New Folder

05
Delete the folder
```

This section should help users understand what CopyCat produces.

---

# 19. Section: Why CopyCat

Primary heading:

```text
WATCHING IS EASY.

UNDERSTANDING IS HARD.
```

Explain the problem CopyCat solves.

Example concepts:

- People generate long screen recordings.
- Manually reviewing recordings takes time.
- Identifying workflows can be difficult.
- CopyCat transforms visual activity into structured information.

Keep this concise.

Use strong editorial typography.

---

# 20. Section: Use Cases

Display the main use cases.

---

## User Research

```text
USER RESEARCH

Understand how people actually
interact with software.
```

---

## Workflow Documentation

```text
WORKFLOW DOCUMENTATION

Turn recorded workflows
into structured processes.
```

---

## UX Analysis

```text
UX ANALYSIS

Discover how users navigate
through digital products.
```

---

## AI Training

```text
AI TRAINING

Transform human interactions
into structured information.
```

---

## Design Requirements

Do not simply create four identical cards.

Prefer:

- Editorial layout
- Large typography
- Dividers
- Scroll interactions
- Alternating layout if appropriate

---

# 21. Final CTA

Create a powerful final landing page section.

Heading:

```text
READY TO
UNDERSTAND
YOUR WORKFLOW?
```

Supporting text:

```text
Upload a recording.

Let CopyCat do the watching.
```

Primary CTA:

```text
TRY COPYCAT →
```

Secondary text:

```text
Sign in to view your previous analyses.
```

Keep the section visually powerful but minimal.

---

# 22. Footer

Create a minimal footer.

Brand:

```text
COPYCAT

AI-powered workflow understanding.
```

Navigation:

```text
Product

How It Works

Use Cases

GitHub
```

Include appropriate copyright information.

---

# 23. Sign In Page

Route:

```text
/signin
```

Create a minimal authentication page.

Required fields:

```text
Email

Password
```

Actions:

```text
Sign In

Forgot Password?

Create an Account
```

The page should visually match the application.

Do not over-design it.

Actual authentication integration may be implemented separately.

---

# 24. Sign Up Page

Route:

```text
/signup
```

Required fields:

```text
Name

Email

Password

Confirm Password
```

Actions:

```text
Create Account

Already have an account? Sign In
```

Actual authentication integration may be implemented separately.

---

# 25. Application Design

The application interface has a different purpose from the landing page.

## Landing Page

Should be:

```text
IMMERSIVE

VISUAL

STORY-FOCUSED
```

## Application

Should be:

```text
CLEAR

FUNCTIONAL

FOCUSED

EASY TO USE
```

Do not make the dashboard overly cinematic.

Prioritize usability.

---

# 26. Application Navigation

Create application navigation.

Desktop layout can use a sidebar.

Navigation items:

```text
Dashboard

Upload

History
```

Optional bottom actions:

```text
Settings

Sign Out
```

The application navigation should clearly indicate the current page.

---

# 27. Dashboard

Route:

```text
/app
```

Purpose:

Give users an overview of their analyses.

Primary heading:

```text
WELCOME BACK
```

Supporting text:

```text
Understand your digital workflows
with CopyCat.
```

Primary action:

```text
+ UPLOAD NEW RECORDING
```

---

## Recent Analyses

Display recent analysis items.

Each item should contain:

- Recording name
- Date
- Processing status
- Detected goal if available
- View analysis action

Example:

```text
FILE EXPLORER RECORDING

Goal:
Delete unnecessary files

Completed

[ VIEW ANALYSIS → ]
```

Do not overload the dashboard with statistics unless meaningful data is available.

---

# 28. Upload Page

Route:

```text
/app/upload
```

Primary heading:

```text
WHAT WOULD YOU LIKE
COPYCAT TO UNDERSTAND?
```

Supporting text:

```text
Upload a screen recording and let
CopyCat analyze the workflow.
```

---

## Upload Area

Create a large drag-and-drop upload area.

Content:

```text
DROP YOUR SCREEN RECORDING HERE

or click to browse

MP4 • MOV • WEBM
```

The component should support:

- Drag and drop
- Click to browse
- File validation
- Upload state
- Error state

Backend integration should follow the existing API architecture.

Do not invent API endpoints.

---

# 29. Upload States

The upload experience should clearly communicate its current state.

Possible states:

```text
IDLE

FILE SELECTED

UPLOADING

UPLOAD COMPLETE

ERROR
```

Provide appropriate visual feedback.

---

# 30. Processing Page / State

After upload, the user should see processing progress.

Do not show only a loading spinner.

Show the processing workflow.

Example:

```text
✓ VIDEO UPLOADED

↓

✓ EXTRACTING FRAMES

↓

ANALYZING ACTIONS

↓

IDENTIFYING USER GOAL

↓

GENERATING WORKFLOW
```

The UI should support real backend status when available.

If backend status information is unavailable, do not fake real-time progress.

Use an appropriate loading state instead.

---

# 31. Analysis Results Page

Route:

```text
/app/analysis/:id
```

This is one of the most important application pages.

The analysis should be easy for a non-technical user to understand.

Do not expose raw JSON as the main interface.

Transform analysis data into clear visual sections.

---

# 32. Analysis Summary

Display:

```text
USER GOAL
```

Show the detected goal prominently.

Example:

```text
Delete unnecessary files
from File Explorer.
```

Additional information may include:

- Recording name
- Processing date
- Number of frames
- Number of actions

Do not prioritize technical metadata over the actual result.

---

# 33. Action Timeline

Display detected actions as an ordered sequence.

Example:

```text
01

Open File Explorer
```

```text
02

Select sem4.zip
```

```text
03

Delete the file
```

```text
04

Select New Folder
```

```text
05

Delete the folder
```

Each action should:

- Have a sequence number.
- Have a clear description.
- Be easy to scan.
- Be connected to the relevant frame or timestamp when available.

---

# 34. Interactive Analysis

When possible, selecting an action should update the related visual evidence.

Example interaction:

```text
USER CLICKS ACTION
        ↓
RELATED FRAME BECOMES SELECTED
        ↓
VIDEO TIMELINE MOVES
        ↓
RELATED MOMENT IS DISPLAYED
```

The implementation should depend on the data available from the backend.

Do not invent data that does not exist.

---

# 35. Frame Viewer

Create an area for reviewing extracted frames.

Layout:

```text
SELECTED FRAME

[ LARGE FRAME DISPLAY ]


FRAME TIMELINE

[ FRAME ] [ FRAME ] [ FRAME ] [ FRAME ]
```

Users should be able to:

- Select a frame.
- Navigate between frames.
- See associated actions.
- View relevant timestamps if available.

Keep interaction intuitive.

---

# 36. Video Viewer

If the original video is available:

Provide a video player.

The video player should support:

- Play
- Pause
- Timeline
- Jumping to relevant moments

Selecting an action may move the video to the associated moment if timestamp data is available.

---

# 37. History Page

Route:

```text
/app/history
```

Display previous analyses.

Each item should include:

- Recording name
- Date
- Status
- Detected goal
- Number of actions when available

Actions:

```text
VIEW ANALYSIS
```

Provide empty states.

Example:

```text
NO ANALYSES YET

Upload your first screen recording
to get started.
```

---

# 38. Reusable Components

Create reusable components where appropriate.

Suggested components:

```text
Navbar

Footer

PrimaryButton

SecondaryButton

SectionHeading

LandingHero

HowItWorks

ProductDemo

UseCases

FinalCTA

AppSidebar

PageHeader

VideoUploader

UploadDropzone

ProcessingStatus

AnalysisSummary

ActionTimeline

ActionItem

FrameViewer

FrameTimeline

VideoViewer

AnalysisCard
```

Do not create unnecessary abstraction.

Only extract reusable components when they provide a real benefit.

---

# 39. State Management

Use the existing state management solution if the project already has one.

Do not introduce a complex state management library unless necessary.

Prefer local component state for isolated UI state.

Use the project's existing data-fetching approach.

---

# 40. API Integration Rules

When integrating with the backend:

1. Inspect existing API services first.
2. Reuse existing API clients.
3. Do not invent API endpoints.
4. Do not modify backend code unless explicitly requested.
5. Handle loading states.
6. Handle errors.
7. Handle missing or incomplete data gracefully.

If an expected API contract is unclear, ask for clarification or inspect existing backend code.

---

# 41. Error Handling

Provide useful error states for:

```text
UPLOAD FAILED

VIDEO PROCESSING FAILED

ANALYSIS NOT AVAILABLE

NETWORK ERROR

INVALID FILE
```

Error messages should be understandable.

Avoid exposing raw technical errors to normal users.

---

# 42. Empty States

Create appropriate empty states.

Examples:

```text
NO ANALYSES YET
```

```text
NO FRAMES AVAILABLE
```

```text
ANALYSIS NOT AVAILABLE
```

Keep empty states visually consistent with the product.

---

# 43. Loading States

Use meaningful loading indicators.

Examples:

```text
Uploading recording...

Extracting frames...

Analyzing interactions...

Understanding workflow...
```

Avoid generic loading indicators when the application can communicate meaningful progress.

---

# 44. Recommended Implementation Phases

The project should be implemented incrementally.

Do not implement every phase at once.

---

## PHASE 1 — Project Inspection

Before implementation:

- Inspect the frontend project.
- Identify framework.
- Identify routing.
- Identify styling.
- Identify existing components.
- Identify dependencies.

Do not make major changes during this phase.

---

## PHASE 2 — Design Foundation

READ DESIGN.MD for this
Implement:

- Global styles
- Color system
- Typography
- Base layout
- Shared buttons
- Shared components

Ensure the existing application is not broken.

---

## PHASE 3 — Landing Page Structure

Implement the static structure for:

```text
Navigation

Hero

What CopyCat Does

How It Works

Product Demonstration

Why CopyCat

Use Cases

Final CTA

Footer
```

Focus on:

- Layout
- Typography
- Spacing
- Responsiveness

Do not add complex animations yet.

---

## PHASE 4 — Landing Page Polish

Add:

- Scroll behavior
- Navbar transitions
- Hover effects
- Section reveal animations
- Subtle motion

Do not over-animate.

---

## PHASE 5 — Application Layout

Goal

Implement the core application structure and navigation.

CopyCat is a voice-first AI agent that learns complex workflows from demonstrations.

The application should feel like a calm, capable assistant rather than a technical developer dashboard.

Do not implement backend functionality in this phase unless existing connections are already straightforward.

Application Shell

Implement:

Application shell
Sidebar navigation
Main content area
Responsive navigation
Page headers
Global voice interaction entry point

The layout should support the following core user journey:

TEACH COPYCAT
↓
COPYCAT LEARNS A WORKFLOW
↓
USER REVIEWS THE SKILL
↓
SKILL IS SAVED
↓
USER SPEAKS A COMMAND
↓
COPYCAT EXECUTES THE WORKFLOW
Sidebar Navigation

Use the following primary navigation:

CopyCat
────────────────

Dashboard

Teach CopyCat

My Skills

Activity

────────────────

Settings

Do not make individual low-level actions such as:

Rename Folder
Move File
Create Folder

into navigation items.

The product is centered around complex workflows and outcomes, not individual atomic actions.

Navigation Behavior

Each navigation item should have:

Icon
Label
Clear active state
Accessible hover and focus states

The active page should be visually obvious without being overly bright or distracting.

The sidebar should collapse or transform appropriately on smaller screens.

Global Voice Entry Point

CopyCat is voice-first.

Include a prominent microphone interaction entry point in the application shell or dashboard experience.

The microphone should feel intentional and important, but should not constantly obstruct navigation.

Possible behavior:

Tap microphone
↓
Listening state
↓
Voice is transcribed
↓
Command is understood
↓
Relevant workflow is found

Text input should remain available as a fallback.

Do not implement real voice recognition yet unless it already exists in the project.

For now, implement the complete UI states.

Page Headers

Each major page should include:

Page title
Short supporting description when useful
Optional contextual action

Examples:

Teach CopyCat
Teach CopyCat

Show CopyCat how you complete a task.
My Skills
My Skills

Workflows CopyCat has learned from you.
Activity
Activity

Review learning and execution activity.
Dashboard Layout

The dashboard should immediately communicate the primary product interaction.

The most important element should be:

What would you like CopyCat to do?

Include:

Large microphone interaction
"Tap to speak"
Text command fallback

Below this, include:

Quick Actions
Teach CopyCat
View Skills
Recent Activity

Show recent learning or execution activity.

Skills Overview

Show a small preview of learned workflows.

Example:

Organize Semester Files

Prepare Project Workspace

Process Important Emails

These are examples of complex outcomes.

Do not design the dashboard around simple atomic operations.

## PHASE 6 — Teach CopyCat

Goal

Implement the experience where a user teaches CopyCat a workflow through a screen-recorded demonstration.

The central idea is:

Show CopyCat how to do something once.

Later, the user can ask CopyCat to perform the learned workflow.

Upload Page

Page title:

Teach CopyCat

Supporting text:

Show CopyCat how you complete a task by uploading a screen recording.
Main Upload Area

Implement:

Drag and drop
File selection
Supported file information
File validation
Upload progress states
Error states

Suggested conceptual structure:

┌──────────────────────────────────────────────┐
│ │
│ Teach CopyCat │
│ │
│ Show how you complete a task. │
│ │
│ ┌──────────────────────────────────────┐ │
│ │ │ │
│ │ Drop your recording │ │
│ │ │ │
│ │ here │ │
│ │ │ │
│ │ or choose a file │ │
│ │ │ │
│ └──────────────────────────────────────┘ │
│ │
│ Upload a screen recording │
│ │
└──────────────────────────────────────────────┘
Teaching Guidance

Include a subtle section explaining how to record a useful demonstration.

For example:

For best results

1. Start with the task already prepared.
2. Perform the complete workflow naturally.
3. Include important decisions and steps.
4. Avoid unnecessary unrelated actions.

Keep this guidance concise.

Important Product Direction

CopyCat should be presented as learning:

Complex workflows
Multi-step tasks
Repeated digital processes

Examples:

Organize a semester workspace

Prepare a project folder

Process downloaded documents

Complete a browser workflow

Handle a repeated email workflow

Do not emphasize simple one-action tasks.

File Validation

Implement UI for:

Unsupported file type
File too large
Empty or invalid file
Upload failure

Do not invent validation limits that the backend does not enforce.

Inspect the existing upload API before connecting.

Upload States

Implement:

Default
Drop video here
File Selected

Show:

File name
File size if available
Remove option
Upload button
Uploading

Show progress only if real progress data is available.

Otherwise use an indeterminate loading state.

Success

Transition naturally into the processing experience.

Error

Clearly explain what went wrong and allow retrying.

Backend Integration

Before connecting, inspect the existing API implementation.

The existing backend endpoint should be used only according to its actual contract.

Do not invent request or response structures.

## PHASE 7 — Processing Experience

Goal

Create a clear, reassuring experience while CopyCat processes a demonstration and learns a workflow.

The user should understand that CopyCat is doing more than simply uploading a video.

It is:

Understanding the demonstration
↓
Identifying actions
↓
Understanding the workflow
↓
Creating a candidate skill
Processing Screen

Use a dedicated processing state after successful upload.

Main message:

CopyCat is learning from your demonstration

Supporting message:

We're analyzing the workflow and identifying the steps involved.
Processing Stages

Represent the learning process visually.

For example:

✓ Video received

✓ Extracting important moments

◉ Understanding actions

○ Identifying the workflow

○ Creating a reusable skill

The stages should be informative.

Do not falsely represent stages as complete unless backend data confirms completion.

If granular backend progress is unavailable:

Use a general processing state.
Avoid fake percentages.
Use subtle animation to communicate activity.
Video Preview

If the uploaded video is available locally in the browser, show a preview where useful.

The user should be able to confirm:

This is the demonstration I uploaded.

Do not require a backend-generated video URL unless the backend provides one.

Frame Preview

The backend extracts frames from the demonstration.

If frame data or images are available to the frontend, provide a lightweight visual preview.

For example:

Frame 1 → Frame 2 → Frame 3 → Frame 4

Do not expose technical frame file paths.

Transition to Results

Once processing is complete, transition to the learning results.

The user should feel that:

CopyCat learned a new workflow.

Not simply:

Video analysis completed.
PHASE 8 — Learning Results and Skill Review
Goal

Present what CopyCat learned from the demonstration in a human-friendly format.

Do not expose raw JSON as the primary interface.

The most important output is:

A candidate workflow that the user can review before CopyCat uses it autonomously.

Results Page

Primary heading:

CopyCat learned something new

The interface should focus on the complex workflow that was identified.

Learning Summary

Display:

Workflow name
Description
Environment
Confidence
Number of steps
Status

Example:

Organize Semester Workspace

CopyCat learned how to organize academic files
into a structured workspace.

Windows

8 steps

High confidence

Pending review

The actual displayed values must come from backend data.

User Goal

Display the high-level goal CopyCat inferred.

Example:

Goal

Organize downloaded academic materials into
appropriate folders.

This should be visually separate from the detailed steps.

Candidate Workflow

This should be the visual center of the page.

Do not primarily show internal actions such as:

find_file
create_folder
move_file

Instead, present the workflow at a human level.

Example:

WORKFLOW

① Identify relevant files

        ↓

② Create the required folders

        ↓

③ Organize files into categories

        ↓

④ Verify the final workspace

Use the actual learned steps where available.

Detailed Steps

Allow users to inspect individual steps.

Each step can show:

Step number

Action title

Human-readable description

Relevant observed information

Technical implementation details should be secondary.

Environment

Display the environment clearly.

Examples:

Windows

Browser

Gmail

The environment determines which executor may later perform the workflow.

This information should be understandable to non-technical users.

Confidence

Display confidence without overemphasizing AI certainty.

Examples:

High confidence

Medium confidence

Low confidence

If useful, provide a subtle explanation that the workflow was inferred from a demonstration.

Demonstration Timeline

Show the observed progression through the demonstration.

Example:

00:00

Opened the workspace

00:05

Selected relevant files

00:12

Created destination folders

00:18

Moved files into categories

This should be a supporting view.

The main focus remains the learned workflow.

Frame Viewer

If frame images are available, allow users to explore visual evidence.

Possible interaction:

Workflow step
↓
Related frame

The user should be able to understand what CopyCat observed.

Avoid making the page look like a computer vision debugging tool.

Video Viewer

If the backend provides video access, include a video viewer.

Do not implement a fake video URL.

If the uploaded file is available in browser state, a local preview can be used where appropriate.

User Validation

This is a critical part of CopyCat.

CopyCat should not silently turn an inferred workflow into a trusted autonomous workflow.

Provide actions:

Reject

Edit

Accept Skill
Accept

Accepting the skill means:

Candidate workflow
↓
User validates
↓
Available for future execution
Edit

Allow the user to adjust:

Workflow name

Description

Steps

Do not expose raw backend JSON as the editing interface.

Reject

Rejecting should clearly communicate that CopyCat will not use this workflow.

Avoid destructive language.

Status

Use understandable states:

Pending Review

Accepted

Rejected

Status should be visible but not dominate the interface.

PHASE 9 — Skills Library
Goal

Create a library of the complex workflows CopyCat has learned.

This is not a list of low-level automation functions.

It represents:

What CopyCat knows how to do.

Page Header
My Skills

Workflows CopyCat has learned from your demonstrations.
Skills List

Display skills as cards or a structured list.

Each skill should show:

Environment

Skill name

Short description

Number of steps

Confidence

Status

Example:

┌─────────────────────────────────────────────┐
│ 🪟 WINDOWS │
│ │
│ Organize Semester Workspace │
│ │
│ Organizes academic files into a structured │
│ workspace. │
│ │
│ 8 steps · High confidence │
│ │
│ Accepted │
│ │
│ View workflow → │
└─────────────────────────────────────────────┘
Example Voice Commands

Each accepted workflow can show how the user might invoke it.

For example:

Try saying:

"Organize my semester files."

or

"Clean up my project workspace."

These examples are interface guidance.

They should not imply that a hard-coded voice command is required.

Skill Detail Page

Clicking a skill should open a detailed view containing:

Name

Description

Environment

Status

Confidence

Workflow steps

Example commands

Created date

Keep technical data secondary.

Filters

Provide useful filters if there are enough skills.

Possible filters:

All Skills

Pending Review

Accepted

Windows

Browser

Gmail

Filters should reflect actual environments and statuses supported by backend data.

Empty States
No skills yet
CopyCat hasn't learned any workflows yet.

Show CopyCat how you complete a task,
and it can learn the workflow from your demonstration.

[ Teach CopyCat ]
No matching skills
No workflows match your current filters.

Provide a simple way to clear filters.

Design Principle for Skills

Always prioritize:

Outcome
Workflow
Purpose

Over:

Low-level actions
Internal executor commands
Technical implementation

For example:

Good
Organize Semester Workspace
Not ideal as the primary skill name
move_file_create_folder_find_file

---

## PHASE 10 — Authentication

Implement:

- Sign In UI
- Sign Up UI
- Integration with the existing authentication system if available

Do not invent an authentication backend.

---

## PHASE 11 — Final Polish

Review:

- Responsiveness
- Accessibility
- Performance
- Loading states
- Error handling
- Empty states
- Visual consistency

Fix issues without unnecessarily rewriting working code.

---

# 45. Instructions for AI Coding Agents

Before making changes:

1. Read this specification.
2. Inspect the existing project.
3. Identify relevant files.
4. Understand the existing architecture.
5. Implement only the requested phase or task.

Do not attempt to implement the entire specification at once.

When asked to implement a phase:

1. Explain the files that need modification.
2. Explain any new dependencies.
3. Avoid unnecessary dependencies.
4. Preserve working functionality.
5. Follow the existing project architecture.
6. Implement the requested feature.
7. Verify the application still builds successfully.
8. Report the files changed.

---

# 46. General Development Rules

Do not:

- Rewrite unrelated code.
- Delete existing functionality without explanation.
- Change backend logic unless explicitly requested.
- Invent APIs.
- Add unnecessary libraries.
- Build placeholder features presented as functional.
- Implement the entire project in one task.

Do:

- Inspect first.
- Reuse existing patterns.
- Work incrementally.
- Build reusable components where appropriate.
- Maintain responsive behavior.
- Handle loading and errors.
- Keep the design consistent.

---

# 47. Future Features

The following may be considered later but should not be implemented unless requested:

- Background video
- Advanced visualization
- Real-time analysis updates
- Collaborative features
- Advanced filtering
- User settings
- Theme switching
- Advanced analytics
- Exporting workflows

Do not implement future features automatically.

---

# 48. Final Product Vision

CopyCat should feel like a polished AI product that transforms something complex:

```text
A SCREEN RECORDING
```

into something simple:

```text
A CLEAR UNDERSTANDING
OF A DIGITAL WORKFLOW
```

The design should communicate this transformation.

The landing page should make users interested in the product.

The application should make the product easy to use.

The user should always understand:

```text
WHAT IS HAPPENING

WHAT COPYCAT IS DOING

WHAT THE RESULT MEANS

WHAT TO DO NEXT
```

Keep the experience minimal, clear, and intentional.
