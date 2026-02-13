# EduFlow Unified Design System

## Overview

This document describes the new unified design system for EduFlow that provides consistent, professional styling across all application portals while maintaining the existing system structure and background design.

## File Structure

```
public/assets/css/
├── unified-design-system.css      # Core design tokens and base styles
├── unified-components.css         # Standardized UI components
├── responsive-utilities.css       # Responsive breakpoints and utility classes
├── accessibility-enhancements.css # WCAG 2.1 AA compliance features
├── styles.css                     # Original styles (legacy)
├── enhanced.css                   # Enhanced styles (legacy)
├── design-system.css              # Original design system (legacy)
└── teacher-portal-enhanced.css    # Teacher portal specific styles
```

## Design Tokens

### Color System

The design system uses a comprehensive color palette organized by purpose:

**Primary Colors:**
- `--brand-primary-*` - Main brand blue colors (50-900 scale)
- `--brand-secondary-*` - Supporting teal/blue colors (50-900 scale)

**Status Colors:**
- `--success-*` - Green colors for positive actions (50-900 scale)
- `--warning-*` - Amber/orange colors for warnings (50-900 scale)
- `--danger-*` - Red colors for errors/danger (50-900 scale)

**Neutral Colors:**
- `--neutral-*` - Gray scale for text, borders, backgrounds (50-900 scale)
- `--background-*` - Page and component backgrounds
- `--text-*` - Text color variations

### Typography

**Font Families:**
- `--font-family-base` - Cairo font stack for Arabic text
- `--font-family-heading` - Same as base for consistency
- `--font-family-mono` - Monospace font for code

**Font Sizes:**
- `--font-size-xs` to `--font-size-5xl` (12px to 48px)
- Semantic sizing for consistent hierarchy

**Font Weights:**
- `--font-weight-thin` to `--font-weight-black` (100-900)

### Spacing System

Uses an 8-point grid system:
- `--spacing-1` = 4px
- `--spacing-2` = 8px
- `--spacing-3` = 12px
- And so on up to `--spacing-96` = 384px

### Other Tokens

- **Border Radius:** `--radius-sm` to `--radius-full`
- **Shadows:** `--shadow-xs` to `--shadow-2xl` plus colored variants
- **Transitions:** `--transition-fast` to `--transition-slow`
- **Breakpoints:** `--breakpoint-xs` to `--breakpoint-2xl`

## Component Classes

### Buttons

**Base Class:** `.btn`

**Variants:**
- `.btn-primary` - Primary action buttons
- `.btn-secondary` - Secondary actions
- `.btn-success` - Success/confirm actions
- `.btn-warning` - Warning actions
- `.btn-danger` - Danger/destructive actions
- `.btn-outline` - Outlined buttons
- `.btn-ghost` - Minimal ghost buttons

**Sizes:**
- `.btn-sm` - Small buttons
- `.btn-lg` - Large buttons
- `.btn-xl` - Extra large buttons

### Cards

**Base Class:** `.card`

**Structure:**
- `.card-header` - Card header section
- `.card-body` - Main card content
- `.card-footer` - Card footer section

### Forms

**Base Classes:**
- `.form-group` - Form field container
- `.form-label` - Form labels
- `.form-control` - Input fields

**States:**
- `.is-valid` - Valid form fields
- `.is-invalid` - Invalid form fields
- `.form-control:focus` - Focused state

### Tables

**Base Class:** `.table`

**Elements:**
- `.th` - Table headers
- `.td` - Table data cells
- Portal-specific variants:
  - `.table-admin-unified`
  - `.table-school-unified`
  - `.table-teacher-unified`
  - `.table-student-unified`

### Headers

**Dashboard Headers:**
- `.dashboard-header` - Main dashboard header
- `.dashboard-header.school` - School-specific styling
- `.dashboard-header.teacher` - Teacher-specific styling
- `.dashboard-header.student` - Student-specific styling

## Utility Classes

### Spacing

**Margin:**
- `.m-*` - All sides (0-12)
- `.mx-*` - Horizontal (0-8)
- `.my-*` - Vertical (0-8)
- `.mt-*`, `.mr-*`, `.mb-*`, `.ml-*` - Individual sides

**Padding:**
- `.p-*` - All sides (0-12)
- `.px-*` - Horizontal (0-8)
- `.py-*` - Vertical (0-8)
- `.pt-*`, `.pr-*`, `.pb-*`, `.pl-*` - Individual sides

### Display

- `.d-none` - Hidden
- `.d-block` - Block display
- `.d-flex` - Flexbox container
- `.d-grid` - Grid container

### Flexbox

- `.flex` - Display flex
- `.flex-row` / `.flex-col` - Direction
- `.items-center` - Align items center
- `.justify-center` - Justify content center

### Typography

- `.text-center` / `.text-left` / `.text-right` - Text alignment
- `.font-bold` / `.font-semibold` / `.font-medium` - Font weights

## Responsive Design

### Breakpoints

- **Extra Small:** `< 480px` (Mobile phones)
- **Small:** `481px - 768px` (Tablets)
- **Medium:** `769px - 1024px` (Small desktops)
- **Large:** `1025px - 1280px` (Desktops)
- **Extra Large:** `> 1281px` (Large screens)

### Responsive Utilities

Prefix classes with breakpoints:
- `.sm:*` - Small screens and up
- `.md:*` - Medium screens and up
- `.lg:*` - Large screens and up

Example: `.sm:d-none` hides element on small screens

## Accessibility Features

### WCAG 2.1 AA Compliance

- Proper color contrast ratios
- Visible focus indicators
- Keyboard navigation support
- Screen reader compatibility
- ARIA attributes support

### Focus Management

- Custom focus rings using `--focus-ring`
- Skip links for keyboard users
- Focus trapping for modals
- Reduced motion support

### Screen Reader Support

- `.sr-only` class for visually hidden content
- Proper heading hierarchy
- ARIA live regions
- Semantic HTML structure

## Implementation Guide

### 1. HTML Structure

Include the new CSS files in this order:

```html
<link rel="stylesheet" href="assets/css/unified-design-system.css">
<link rel="stylesheet" href="assets/css/unified-components.css">
<link rel="stylesheet" href="assets/css/responsive-utilities.css">
<link rel="stylesheet" href="assets/css/accessibility-enhancements.css">
<!-- Legacy styles -->
<link rel="stylesheet" href="assets/css/styles.css">
<link rel="stylesheet" href="assets/css/enhanced.css">
<link rel="stylesheet" href="assets/css/design-system.css">
```

### 2. Basic Usage

**Creating a Card:**
```html
<div class="card">
  <div class="card-header">
    <h3>Card Title</h3>
  </div>
  <div class="card-body">
    <p>Card content goes here...</p>
  </div>
</div>
```

**Using Buttons:**
```html
<button class="btn btn-primary">Primary Button</button>
<button class="btn btn-secondary btn-lg">Large Secondary Button</button>
<a href="#" class="btn btn-outline">Outline Button</a>
```

**Form Elements:**
```html
<form>
  <div class="form-group">
    <label class="form-label" for="email">Email Address</label>
    <input type="email" id="email" class="form-control" required>
  </div>
  <button type="submit" class="btn btn-primary">Submit</button>
</form>
```

### 3. Responsive Layout

**Grid System:**
```html
<div class="grid-container grid-auto-fit">
  <div class="card">Content 1</div>
  <div class="card">Content 2</div>
  <div class="card">Content 3</div>
</div>
```

**Responsive Utilities:**
```html
<div class="d-flex md:flex-col sm:items-center">
  <div class="w-full md:w-1/2">Column 1</div>
  <div class="w-full md:w-1/2">Column 2</div>
</div>
```

## Migration Guide

### From Old to New Classes

| Old Class | New Class |
|-----------|-----------|
| `.btn-primary` | `.btn.btn-primary` |
| `.btn-secondary` | `.btn.btn-secondary` |
| `.card` | `.card` (same) |
| `.form-group` | `.form-group` (same) |
| `.table-admin` | `.table.table-admin-unified` |

### Best Practices

1. **Use semantic HTML** with proper heading hierarchy
2. **Apply utility classes** for quick styling adjustments
3. **Maintain consistent spacing** using design tokens
4. **Test responsive behavior** across all breakpoints
5. **Verify accessibility** with screen readers and keyboard navigation
6. **Use appropriate ARIA attributes** for dynamic content

## Browser Support

- Chrome 60+
- Firefox 55+
- Safari 12+
- Edge 79+
- Mobile browsers (iOS Safari, Chrome Android)

## Performance Considerations

- CSS files are optimized and minified
- Variables reduce repetition
- Utility classes minimize custom CSS
- Responsive design uses mobile-first approach

## Maintenance

- Update design tokens in `unified-design-system.css`
- Add new components to `unified-components.css`
- Extend utilities in `responsive-utilities.css`
- Update accessibility features in `accessibility-enhancements.css`

## Contributing

When adding new styles:
1. Use existing design tokens when possible
2. Follow the established naming conventions
3. Test across all supported browsers
4. Ensure WCAG 2.1 AA compliance
5. Document new classes in this guide

---

*Last Updated: January 2026*
*Version: 2.0*