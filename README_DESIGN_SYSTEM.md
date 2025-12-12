# StockReaderAI - Design System Documentation

## Overview
StockReaderAI adalah platform analisis trading profesional dengan design system lengkap yang mengikuti spesifikasi modern untuk aplikasi finansial.

## Design System

### Color Palette

#### Dark Theme (Default)
- **Primary Dark**: `#0D1B2A` - Background utama
- **Secondary Dark**: `#1B263B` - Cards, panels
- **Tertiary Dark**: `#415A77` - Borders, dividers
- **Accent Blue**: `#4361EE` - Primary actions, highlights
- **Bullish Green**: `#06D6A0` - Up movements, positive values
- **Bearish Red**: `#EF476F` - Down movements, negative values
- **Neutral Yellow**: `#FFD166` - Warnings, sideways movements
- **Text Primary**: `#FFFFFF` - Main text
- **Text Secondary**: `#94A3B8` - Secondary text (70% opacity)
- **Text Muted**: `#64748B` - Muted text (50% opacity)
- **Chart Grid**: `rgba(51, 65, 85, 0.3)` - Grid lines

### Typography

- **Primary Font**: Inter (sans-serif)
  - Headers: Inter Bold (700)
  - Body: Inter Regular (400)
  - Data: Inter Medium (500)

- **Monospace Font**: JetBrains Mono
  - Prices, indicators, code
  - Regular weight

### Spacing Scale

Base: 4px
Scale: 4, 8, 12, 16, 20, 24, 32, 40, 48, 64, 80, 96px

### Shadows

- Small: `0 1px 2px rgba(0, 0, 0, 0.25)`
- Medium: `0 4px 12px rgba(0, 0, 0, 0.3)`
- Large: `0 12px 32px rgba(0, 0, 0, 0.4)`
- Glow: `0 0 20px rgba(67, 97, 238, 0.3)`

### Border Radius

- Small: 6px
- Medium: 12px
- Large: 16px
- Full: 999px

### Animations

- Fast: 150ms ease-in-out
- Medium: 250ms ease-in-out
- Slow: 350ms ease-in-out
- Bounce: cubic-bezier(0.68, -0.55, 0.265, 1.55)

## Component Library

### Header & Navigation
- Fixed header dengan height 64px
- Logo dengan animasi pulse
- Navigation menu dengan active indicator
- Search bar dengan glass icon
- Notification bell dengan badge
- Theme toggle
- User profile dropdown

### Dashboard Widgets
- Grid layout: 4-column system
- Widget sizes: Large (2x2), Medium (1x2), Small (1x1)
- Hover effects dengan border glow
- Resizable dan draggable (future enhancement)

### Charts
- TradingView-style chart container
- Toolbar dengan timeframe selector
- Multiple chart types support
- Indicator library
- Drawing tools
- Compare mode
- Fullscreen toggle

### Data Tables
- Styled dengan zebra striping
- Sortable columns
- Hover effects
- Color-coded rows berdasarkan score
- Responsive design

### Form Controls
- Input fields dengan focus glow
- Primary/Secondary/Danger buttons
- Toggle switches
- Checkboxes & Radio buttons
- Dropdowns dengan custom styling

### Modals & Overlays
- Backdrop dengan blur effect
- Slide-up animation
- Header dengan close button
- Footer dengan action buttons

### Notifications
- Top-right positioning
- Auto-dismiss setelah 5 seconds
- Color-coded by type (success, error, warning, info)
- Slide-in animation

### Loading States
- Skeleton loaders dengan shimmer effect
- Chart skeleton
- Table skeleton
- Text skeleton

### Empty States
- Large icon (80px)
- Title dan description
- Action button

## Pages Structure

### 1. Dashboard (`/`)
- Market Overview Panel
- Personal Watchlist
- Main Analysis Chart
- Market Sentiment Dashboard
- Economic Calendar Highlights
- Correlation Matrix Mini
- Volatility Monitor
- Alerts & Notifications

### 2. Market Scanner (`/scanner`)
- Advanced filtering system
- Technical filters (RSI, MACD, Price vs MA, Volume)
- Fundamental filters (Market Cap, P/E, Dividend Yield)
- Pattern filters
- Custom formula builder
- Results table dengan strength score
- Bulk actions

### 3. Advanced Charts (`/charts`)
- Multi-chart layout (1, 2, 4, 6, 9 charts)
- Chart type selector
- Indicator library
- Drawing tools
- Compare mode
- Fullscreen support

### 4. Economic Calendar (`/calendar`)
- Month/Week/List views
- Country filter
- Impact filter
- Event details panel
- Historical impact analysis
- Market reaction charts

### 5. Backtesting (`/backtest`)
- Strategy builder
- Entry/Exit conditions
- Position sizing options
- Performance metrics dashboard
- Equity curve visualization
- Trade-by-trade analysis
- Monte Carlo simulation

### 6. Watchlists (`/watchlists`)
- Multiple watchlist groups
- Performance comparison
- Correlation analysis
- Technical score ranking
- Bulk actions
- Export functionality

### 7. Research (`/research`)
- Sector Rotation Analysis
- Seasonality Studies
- Intermarket Analysis
- Market Cycles
- Options Flow Analysis

## Responsive Design

### Breakpoints
- Mobile: 320px - 767px
- Tablet: 768px - 1023px
- Desktop: 1024px - 1439px
- Wide Desktop: 1440px+

### Mobile Adaptations
- Single column layout
- Simplified widgets
- Bottom navigation bar
- Touch-optimized controls
- Swipe gestures
- Pull to refresh

## Accessibility

### Color Contrast
- Text on background: Minimum 4.5:1
- UI Components: Minimum 3:1
- Large Text: Minimum 3:1

### Focus States
- Focus ring: 2px solid #4361EE, offset 2px
- Never remove outline completely
- Logical tab order

### Screen Reader
- ARIA labels untuk semua icons
- Live regions untuk price updates
- Status messages untuk actions
- Semantic HTML structure

### Keyboard Navigation
- Tab melalui semua interactive elements
- Arrow keys untuk chart panning
- Enter/Space untuk actions
- Escape untuk close modals

## File Structure

```
StockerReaderAI/
├── static/
│   └── css/
│       └── design-system.css    # Main design system CSS
├── components/
│   └── ui_components.py         # Reusable UI components
├── pages/
│   ├── scanner.py               # Market Scanner page
│   ├── charts.py                # Advanced Charts page
│   ├── calendar.py              # Economic Calendar page
│   ├── backtest.py              # Backtesting page
│   ├── watchlists.py            # Watchlists page
│   └── research.py              # Research page
└── app.py                       # Main dashboard page
```

## Usage

### Loading Design System
```python
from components.ui_components import load_design_system
load_design_system()
```

### Rendering Header
```python
from components.ui_components import render_header

nav_items = [
    {"label": "Dashboard", "page": "/"},
    {"label": "Scanner", "page": "/scanner"},
    # ... more items
]

render_header(nav_items, "Dashboard")
```

### Creating Widgets
```python
from components.ui_components import render_widget

widget_html = render_widget(
    title="Market Overview",
    content="<p>Widget content here</p>",
    size="large",
    actions=["Settings", "Export"]
)
st.markdown(widget_html, unsafe_allow_html=True)
```

### Rendering Tables
```python
from components.ui_components import render_data_table

headers = ["Symbol", "Price", "Change %"]
rows = [
    ["AAPL", "$175.50", "+1.2%"],
    ["MSFT", "$378.20", "-0.5%"]
]

table_html = render_data_table(headers, rows)
st.markdown(table_html, unsafe_allow_html=True)
```

## Future Enhancements

1. **Drag & Drop**: Implementasi grid layout dengan drag-and-drop untuk widgets
2. **Theme Switching**: Light theme implementation
3. **Custom Indicators**: Builder untuk custom technical indicators
4. **Real-time Updates**: WebSocket integration untuk real-time data
5. **Export Features**: PDF reports, Excel exports
6. **Mobile App**: React Native mobile app
7. **Advanced Analytics**: Machine learning predictions
8. **Social Features**: Share analysis, community insights

## Browser Support

- Chrome/Edge: Latest 2 versions
- Firefox: Latest 2 versions
- Safari: Latest 2 versions
- Mobile browsers: iOS Safari, Chrome Mobile

## Performance Targets

- First Contentful Paint: < 1.5s
- Time to Interactive: < 3s
- Lighthouse Score: > 90

## License

Proprietary - StockReaderAI

