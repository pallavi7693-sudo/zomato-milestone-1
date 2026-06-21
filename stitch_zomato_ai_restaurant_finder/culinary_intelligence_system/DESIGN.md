---
name: Culinary Intelligence System
colors:
  surface: '#131313'
  surface-dim: '#131313'
  surface-bright: '#3a3939'
  surface-container-lowest: '#0e0e0e'
  surface-container-low: '#1c1b1b'
  surface-container: '#201f1f'
  surface-container-high: '#2a2a2a'
  surface-container-highest: '#353534'
  on-surface: '#e5e2e1'
  on-surface-variant: '#e4bdbb'
  inverse-surface: '#e5e2e1'
  inverse-on-surface: '#313030'
  outline: '#ab8886'
  outline-variant: '#5b403e'
  surface-tint: '#ffb3af'
  primary: '#ffb3af'
  on-primary: '#68000d'
  primary-container: '#cb202d'
  on-primary-container: '#ffe2e0'
  inverse-primary: '#bc1124'
  secondary: '#ffb3b1'
  on-secondary: '#680011'
  secondary-container: '#a90022'
  on-secondary-container: '#ffb3b0'
  tertiary: '#c8c6c6'
  on-tertiary: '#303030'
  tertiary-container: '#696868'
  on-tertiary-container: '#eae8e7'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#ffdad7'
  primary-fixed-dim: '#ffb3af'
  on-primary-fixed: '#410005'
  on-primary-fixed-variant: '#930017'
  secondary-fixed: '#ffdad8'
  secondary-fixed-dim: '#ffb3b1'
  on-secondary-fixed: '#410007'
  on-secondary-fixed-variant: '#92001c'
  tertiary-fixed: '#e4e2e1'
  tertiary-fixed-dim: '#c8c6c6'
  on-tertiary-fixed: '#1b1c1c'
  on-tertiary-fixed-variant: '#474747'
  background: '#131313'
  on-background: '#e5e2e1'
  surface-variant: '#353534'
typography:
  display-lg:
    fontFamily: Outfit
    fontSize: 48px
    fontWeight: '800'
    lineHeight: '1.1'
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Outfit
    fontSize: 32px
    fontWeight: '700'
    lineHeight: '1.2'
    letterSpacing: -0.01em
  headline-lg-mobile:
    fontFamily: Outfit
    fontSize: 28px
    fontWeight: '700'
    lineHeight: '1.2'
  headline-md:
    fontFamily: Outfit
    fontSize: 24px
    fontWeight: '700'
    lineHeight: '1.3'
  title-lg:
    fontFamily: Outfit
    fontSize: 20px
    fontWeight: '600'
    lineHeight: '1.4'
  label-md:
    fontFamily: Outfit
    fontSize: 14px
    fontWeight: '500'
    lineHeight: '1.2'
    letterSpacing: 0.01em
  body-lg:
    fontFamily: Outfit
    fontSize: 18px
    fontWeight: '400'
    lineHeight: '1.6'
  body-md:
    fontFamily: Outfit
    fontSize: 16px
    fontWeight: '400'
    lineHeight: '1.6'
  body-sm:
    fontFamily: Outfit
    fontSize: 14px
    fontWeight: '400'
    lineHeight: '1.5'
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  base: 4px
  xs: 8px
  sm: 12px
  md: 16px
  lg: 24px
  xl: 32px
  gutter: 16px
  margin-mobile: 16px
  margin-desktop: 40px
---

## Brand & Style
The design system is centered on a "Premium Gastronomy" aesthetic, blending the high-energy utility of a food discovery platform with the sophisticated depth of an AI-driven concierge. The personality is confident, appetizing, and technologically advanced.

The visual style utilizes a **Modern-Glassmorphic** approach. It leverages deep charcoal surfaces to allow vibrant food photography and the signature brand red to command attention. Elements feel like physical layers of polished glass floating over a dark void, providing a sense of focused immersion and high-end quality.

## Colors
The palette is dominated by a true "Deep Dark" background to maximize OLED contrast and power efficiency. 

- **Primary Red:** Used exclusively for high-priority actions, brand presence, and critical AI feedback.
- **Surface Hierarchy:** Layering is achieved through incremental lightness in the neutrals (#0D to #1A to #24).
- **Accents:** The red-to-light-red gradient is reserved for primary Call-to-Actions (CTAs) to provide a sense of "glow" and heat, evocative of cooking and energy.
- **Borders:** A consistent #2D2D2D is used for low-contrast containment, ensuring sections are defined without breaking the dark immersion.

## Typography
Outfit is used across all levels to maintain a modern, geometric clarity. 

- **Weight Strategy:** Use ExtraBold (800) for hero sections and AI-generated headlines to create high visual impact. Medium (500) is the standard for functional labels (tabs, buttons, metadata) to ensure legibility against dark backgrounds.
- **Readability:** Body text should maintain a 1.6x line height to prevent "bleeding" of white text on black backgrounds.
- **Scaling:** On mobile devices, tighten letter spacing slightly for large headlines to maintain a compact, premium feel.

## Layout & Spacing
The layout follows an **8px grid system** for consistent rhythm. 

- **Mobile:** A 4-column fluid grid with 16px side margins. 
- **Desktop:** A 12-column fixed-center grid (max-width 1280px).
- **AI Chat Context:** In conversational interfaces, use asymmetrical padding (wider on the leading edge) to distinguish user input from AI restaurant recommendations.
- **Density:** Use "md" (16px) as the standard padding for cards and containers to ensure content feels breathable but information-dense.

## Elevation & Depth
This design system rejects traditional grey shadows in favor of **Tonal Depth and Glassmorphism**.

- **Z-Index Layers:** 
  - Level 0: #0D0D0D (Base)
  - Level 1: #1A1A1A (Cards/Lists)
  - Level 2: #242424 (Floating Menus/Modals)
- **Glassmorphism:** Sidebars and bottom navigation bars must use a 16px backdrop-blur with a 40% opaque #1A1A1A fill. Apply a subtle 1px top border of #FFFFFF (10% opacity) to simulate a light-catching glass edge.
- **AI Glow:** Primary elements or AI-selected "Top Picks" should feature a very soft, diffused outer glow using the primary red (#CB202D) at 15% opacity to signify importance.

## Shapes
A hierarchy of roundedness is used to communicate the "containment" of information:

- **Cards:** 16px (`rounded-lg`) – Provides a friendly, modern frame for restaurant imagery.
- **Buttons/Inputs:** 12px – Strikes a balance between professional and approachable.
- **Tags/Chips/Badges:** 8px – Keeps smaller metadata elements feeling distinct and organized.
- **Interactive States:** On hover, cards should subtly scale (1.02x) with a 300ms cubic-bezier transition.

## Components

### Buttons
- **Primary:** Background uses the red gradient. Text is White. 12px radius. On hover, apply a 4px red glow shadow.
- **Secondary:** Transparent background with a 1px border of #2D2D2D. 12px radius.

### Cards (Restaurant/AI Pick)
- **Surface:** #1A1A1A background, 16px radius.
- **Imagery:** 1:1 or 16:9 aspect ratio with a subtle dark gradient overlay at the bottom for text legibility.
- **Border:** 1px solid #2D2D2D.

### AI Input Field
- **Surface:** #242424. 12px radius.
- **State:** When focused, the border transitions from #2D2D2D to the primary red.

### Chips & Tags
- **Style:** 8px radius. Use #242424 background for inactive tags and Primary Red (10% opacity) with Red text for active/selected filters.

### Sidebars & Overlays
- **Effect:** 16px Backdrop Blur. 0px radius on edges touching the screen boundary. Use a 1px #2D2D2D separator line.

### Selection Controls
- **Checkbox/Radio:** Use primary red for the selected state. Ensure a 2px "gap" between the checkmark and the border for visual clarity in dark mode.