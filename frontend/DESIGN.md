# CopyCat Design System

## Purpose

This document defines the visual design system for the CopyCat frontend.

All frontend UI should follow these design principles unless a specific page requirement states otherwise.

The goal is to create a visual identity that feels:

- Warm
- Minimal
- Editorial
- Sophisticated
- Modern
- Human
- Premium

CopyCat should not look like a generic AI SaaS product.

Avoid typical AI visual clichés such as:

- Neon gradients
- Cyberpunk aesthetics
- Generic dark dashboards
- AI brain illustrations
- Robots
- Excessive glowing effects
- Overuse of glassmorphism
- Excessive cards
- Excessive rounded components

The visual identity should feel like:

> Modern editorial design × premium creative product × intelligent technology.

---

# 1. Core Design Principles

The design should prioritize:

1. Typography
2. Whitespace
3. Visual hierarchy
4. Clear information architecture
5. Warm visual tones
6. Intentional interaction
7. Subtle motion

The interface should not rely on excessive decoration to look premium.

Premium design should come from restraint.

---

# 2. Color System

## Primary Palette

### Main Background

```text
#F4F0E8
```

Warm cream.

Use as the primary background for most pages.

---

### Alternate Background

```text
#EAE4D9
```

Soft warm beige.

Use for:

- Alternate sections
- Sidebars
- Subtle layout separation

---

### Surface

```text
#FAF8F3
```

Light warm surface.

Use for:

- Cards
- Forms
- Elevated content
- Inputs

---

### Dark Surface

```text
#1C1B19
```

Warm near-black.

Use for:

- High-contrast landing page sections
- Product demonstrations
- Occasional visual contrast

Do not make the entire application dark.

---

# 3. Text Colors

## Primary Text

```text
#1C1B19
```

Use for:

- Headings
- Primary content
- Important information

---

## Secondary Text

```text
#625E57
```

Use for:

- Supporting descriptions
- Secondary information

---

## Muted Text

```text
#918B82
```

Use for:

- Metadata
- Less important information
- Captions

Do not use muted text for important content.

---

# 4. Borders

## Default Border

```text
#D6CFC2
```

Use subtle borders to separate content.

Recommended default:

```css
border: 1px solid #d6cfc2;
```

Avoid heavy borders.

The design should primarily use whitespace and layout for separation.

---

# 5. Accent Colors

## Primary Accent

```text
#7D1F2A
```

Deep burgundy.

Use for:

- Primary buttons
- Important actions
- Selected states
- Key highlights

The accent color should be used intentionally.

Do not overuse it.

---

## Accent Hover

```text
#5F1720
```

Use for:

- Primary button hover
- Active interactions

---

## Accent Light

```text
#E7D1D3
```

Use for:

- Subtle highlights
- Selected backgrounds
- Soft accent areas

---

# 6. Functional Colors

Functional colors should remain muted and visually consistent with the warm palette.

## Success

```text
#4F6B52
```

## Warning

```text
#A66A2C
```

## Error

```text
#9E3131
```

## Information

```text
#526A7A
```

Do not introduce bright saturated system colors unless required for accessibility.

---

# 7. Color Usage Rules

The interface should primarily consist of:

```text
CREAM
+
NEAR-BLACK
+
BURGUNDY
```

Accent colors should guide attention.

Do not use multiple bright colors on the same screen.

Avoid random colors.

Every color should have a defined purpose.

---

# 8. Typography

Typography is one of the most important parts of the CopyCat visual identity.

The design should use strong hierarchy and generous scale.

---

## Font Pairing

### Headings

Use:

```text
Manrope
```

Use for:

- Hero text
- Page titles
- Section headings
- Important UI headings

Recommended weights:

```text
600
700
800
```

---

### Body and UI

Use:

```text
Inter
```

Use for:

- Paragraphs
- Buttons
- Form inputs
- Navigation
- Metadata
- Application interface

Recommended weights:

```text
400
500
600
```

---

# 9. Typography Scale

## Hero

```text
clamp(4rem, 9vw, 8rem)
```

Use only for major hero statements.

---

## H1

Desktop:

```text
56px
```

Responsive scaling is allowed.

---

## H2

```text
42px
```

---

## H3

```text
28px
```

---

## Large Body

```text
20px
```

---

## Standard Body

```text
16px
```

---

## Small Text

```text
14px
```

---

## Caption

```text
12px
```

---

# 10. Typography Rules

Use:

- Large headings
- Short paragraphs
- Strong contrast
- Clear hierarchy
- Tight heading line-height

Avoid:

- Long walls of text
- Too many font styles
- Excessive use of bold text
- Tiny important text

Hero and landing page typography can be expressive.

Application typography should prioritize clarity.

---

# 11. Spacing System

Use a consistent spacing scale.

Base unit:

```text
4px
```

Primary spacing values:

```text
4px
8px
12px
16px
24px
32px
40px
48px
64px
80px
96px
128px
```

Do not introduce arbitrary spacing values without a specific reason.

Prefer the defined spacing system.

---

# 12. Border Radius

The design should avoid overly rounded interfaces.

## Small Components

```text
6px
```

## Inputs

```text
8px
```

## Buttons

```text
8px
```

## Cards

```text
12px
```

## Large Containers

```text
16px
```

Avoid using extreme pill shapes for general UI components.

Use pill shapes only for:

- Tags
- Status indicators
- Filters
- Small badges

---

# 13. Shadows

Use shadows sparingly.

Most components should use:

- Background contrast
- Borders
- Whitespace

rather than strong shadows.

For elevated elements such as modals, use a soft shadow.

Example:

```text
0 8px 30px rgba(28, 27, 25, 0.08)
```

Avoid:

- Dark heavy shadows
- Strong floating effects
- Excessive elevation

---

# 14. Buttons

## Primary Button

Background:

```text
#7D1F2A
```

Text:

```text
#FFFFFF
```

Hover:

```text
#5F1720
```

Example:

```text
TRY IT OUT →
```

Primary buttons should:

- Feel solid
- Have clear contrast
- Have comfortable padding
- Use subtle radius
- Have smooth hover transitions

---

## Secondary Button

Background:

```text
Transparent
```

Border:

```text
1px solid #1C1B19
```

Text:

```text
#1C1B19
```

Hover:

Use a subtle warm beige background.

---

## Button Rules

Buttons should:

- Be clearly distinguishable
- Have sufficient touch targets
- Have visible focus states
- Use consistent sizing

Avoid excessive button styles.

---

# 15. Form Inputs

## Input Background

```text
#FAF8F3
```

## Input Border

```text
#D6CFC2
```

## Focus State

Use a subtle burgundy border or outline.

The focus state must remain clearly visible.

Do not remove browser focus behavior without providing an accessible replacement.

---

# 16. Cards

Cards should not be overused.

Do not turn every section or piece of information into a card.

Use cards only when grouping information provides clarity.

## Card Style

- Background: warm surface
- Thin border
- 12px radius
- Generous padding
- Minimal shadow

Typical uses:

- Analysis items
- Upload areas
- Content groups
- History entries

---

# 17. Landing Page Design

The landing page should feel more expressive than the application interface.

Prioritize:

- Large typography
- Strong composition
- Generous whitespace
- Editorial layouts
- Section contrast

Avoid:

- Repetitive grids
- Excessive cards
- Generic SaaS layouts

The landing page should feel like a continuous story.

---

# 18. Landing Page Background

The default landing page background should primarily use:

```text
#F4F0E8
```

Create visual rhythm by alternating sections.

Possible sequence:

```text
CREAM

↓

LIGHT BEIGE

↓

DARK

↓

CREAM

↓

ACCENT CTA
```

Do not alternate colors randomly.

Each background change should support the visual structure of the page.

---

# 19. Hero Design

The hero should prioritize typography.

Use:

- Large scale
- Generous negative space
- Strong contrast
- Minimal supporting text

The hero should not be cluttered with:

- Large illustrations
- Generic AI imagery
- Excessive animations

For now, do not use a video background.

The hero should work visually with static design alone.

A background animation or video may be added later.

---

# 20. Dark Sections

Dark sections should use:

```text
#1C1B19
```

Text should use warm off-white rather than harsh pure white when appropriate.

Dark sections can be used for:

- Product demonstrations
- Important storytelling moments
- Visual contrast

Do not overuse dark sections.

They should create rhythm and emphasis.

---

# 21. Application Interface

The application interface should feel:

- Calm
- Structured
- Clear
- Functional
- Easy to navigate

It should use the same visual identity as the landing page.

However, usability should take priority over visual experimentation.

---

# 22. Application Sidebar

Suggested background:

```text
#EAE4D9
```

The sidebar should feel integrated with the warm design system.

Avoid a generic dark SaaS sidebar.

---

## Navigation States

### Default

- Secondary or primary text
- Minimal styling

### Hover

- Subtle background change

### Active

Use:

- Soft accent background
- Stronger text
- Optional subtle burgundy indicator

Do not make the active state visually aggressive.

---

# 23. Dashboard

The dashboard should feel calm and welcoming.

Use:

- Large page heading
- Clear primary action
- Generous whitespace

Example tone:

```text
GOOD AFTERNOON.

What would you like to
understand today?
```

The primary upload action should be prominent.

Avoid filling the dashboard with meaningless statistics.

---

# 24. Analysis Interface

The analysis results interface should prioritize information hierarchy.

The most important information should appear first.

Recommended hierarchy:

```text
USER GOAL
```

↓

```text
WORKFLOW
```

↓

```text
VISUAL EVIDENCE
```

The user should immediately understand:

1. What the user was trying to do.
2. What actions were detected.
3. What evidence supports the analysis.

---

# 25. Icons

Use one consistent icon system.

Prefer an existing icon library already used in the project.

If no icon library exists, a lightweight consistent icon library may be used.

Icons should:

- Support the interface
- Remain visually simple
- Be used consistently

Do not mix multiple icon styles.

---

# 26. Motion Design

Motion should feel subtle and intentional.

Recommended:

- 150–300ms UI transitions
- Subtle hover effects
- Small opacity transitions
- Gentle content reveals
- Small transform changes

Landing page scroll animations can be slightly more expressive.

Application animations should remain functional.

---

# 27. Motion Rules

Do not use:

- Bouncing animations
- Flashing
- Excessive scaling
- Dramatic rotations
- Constant decorative movement

Respect:

```text
prefers-reduced-motion
```

Motion should support:

- Feedback
- Navigation
- Hierarchy
- User understanding

---

# 28. Responsive Design

All designs must work across:

```text
DESKTOP

TABLET

MOBILE
```

Responsive design should adapt the layout rather than simply shrinking desktop components.

---

## Mobile Rules

On mobile:

- Reduce visual density
- Simplify complex layouts
- Maintain large readable text
- Keep buttons accessible
- Increase touch target consideration
- Reduce unnecessary animation

Do not sacrifice usability to preserve the desktop composition exactly.

---

# 29. Accessibility

All UI should maintain:

- Sufficient contrast
- Keyboard accessibility
- Visible focus states
- Clear interactive states
- Semantic HTML
- Accessible labels

Accessibility should be considered part of the design system.

---

# 30. Component Consistency

When creating new components:

1. Check whether an existing component already solves the problem.
2. Reuse design tokens.
3. Follow established spacing.
4. Follow typography rules.
5. Use defined colors.
6. Maintain consistent interaction patterns.

Do not create visually inconsistent components for individual pages.

---

# 31. Design Decisions for AI Coding Agents

When implementing UI:

- Follow this document.
- Do not invent a different visual style.
- Do not randomly introduce new colors.
- Do not overuse cards.
- Do not add excessive gradients.
- Do not make everything rounded.
- Prioritize whitespace.
- Use typography as a primary visual tool.

When a design decision is unclear:

Prefer the more minimal option.

---

# 32. Final Visual Identity

The CopyCat visual system should communicate:

```text
WARM

CONFIDENT

INTELLIGENT

MINIMAL

HUMAN

PREMIUM
```

The overall feeling should be:

> A thoughtfully designed modern product that feels sophisticated and human, rather than a generic futuristic AI interface.

The primary visual formula is:

```text
WARM CREAM

+

NEAR-BLACK TYPOGRAPHY

+

DEEP BURGUNDY ACCENTS

+

GENEROUS WHITESPACE

+

EDITORIAL TYPOGRAPHY
```

All new frontend work should maintain this visual direction.
